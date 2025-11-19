"""
Budget Agent Service

Handles the creation and management of the Budget AI agent.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from agents.models import agentModel
from agents.services import build_config, get_agent_history, add_to_history
from django.contrib.auth.models import User
from google import genai
from google.genai import types
from decouple import config
from .models import Budget

API_KEY = config('GEMINI_API_KEY')

# Pydantic Models for Structured Output
class BudgetItem(BaseModel):
    title: str = Field(..., description="The title of the budget category (e.g., 'Groceries', 'Rent').")
    budget: float = Field(..., description="The allocated budget amount for this category.")
    spent: float = Field(0.0, description="The amount already spent in this category (usually 0 for new budgets).")
    description: str = Field(..., description="A detailed description in Markdown format, suitable for a Flutter mobile app. Should include what to buy, estimated costs, and tips.")

class BudgetGenerationResponse(BaseModel):
    budgets: List[BudgetItem] = Field(..., description="A list of generated budget items.")
    message: str = Field(..., description="A message to the user or coordinator explaining the generated budgets or asking for clarification.")

BUDGET_SYSTEM_INSTRUCTION = '''
IDENTITY
You are the **Budget Agent** in the AION personal finance management system. Your responsibility is to create detailed, realistic, and personalized budgets for users based on their financial data and goals.

YOUR GOAL
Generate a comprehensive set of budget categories and allocations.

OUTPUT FORMAT
You must output a structured JSON response containing:
1.  `budgets`: A list of budget items, each with a title, allocated amount, spent amount (default 0), and a rich Markdown description.
2.  `message`: A conversational message to the user or the Main AI Coordinator.

MARKDOWN GUIDELINES (CRITICAL)
The `description` field for each budget item will be displayed in a **Flutter mobile application**.
*   Use clear, concise headings (##).
*   Use bullet points for lists.
*   Use bold text (**text**) for emphasis.
*   Avoid complex HTML or unsupported Markdown features.
*   Ensure the content looks great on a small screen.
*   Include details on what to buy, price estimates, and money-saving tips within the description.

USAGE SCENARIOS
1.  **User Request**: The user directly asks to generate a budget (e.g., "Make me a budget for next month").
2.  **Coordinator Request**: The Main AI Coordinator delegates the task to you after analyzing the user's profile.
3.  **Event-Driven Re-budgeting**: The Main AI Coordinator or another agent detects a significant change (e.g., income change, new debt, overspending) and requests a budget update. In this case, you should analyze the new context and propose necessary adjustments to the existing budget categories or amounts.
4.  **Manual Update/Rebalance**: The user manually changes a budget amount or deletes a category. You must rebalance the remaining categories to maintain the total budget or adjust logically.
5.  **Overspending Alert**: The user spends more than allocated. You must acknowledge this, update the description with a warning/advice, and potentially suggest rebalancing other categories to cover the deficit.

BEHAVIOR
*   Analyze the provided context (user messages, history) to determine the appropriate budget categories.
*   If you lack sufficient information, use the `message` field to ask for clarification, but try to generate a draft budget based on general best practices if possible.
*   Be realistic with amounts.
*   The `spent` field should generally be 0 for new budgets, unless you are processing historical data.
'''

def get_or_create_budget_agent() -> agentModel:
    """
    Get or create the budget agent.
    """
    agent, created = agentModel.objects.get_or_create(
        name="budget_agent",
        defaults={
            "description": "Generates and manages user budgets and categories.",
            "system_instruction": BUDGET_SYSTEM_INSTRUCTION,
            "gemini_model": "gemini-2.5-pro",
            "thinking_budget": 1
        }
    )
    # Update model if it exists but is different (optional, but good for dev)
    if not created and (agent.gemini_model != "gemini-2.5-pro" or agent.thinking_budget != 1):
        agent.gemini_model = "gemini-2.5-pro"
        agent.thinking_budget = 1
        agent.save()
        
    return agent

def get_user_financial_profile(user: User) -> str:
    """
    Fetches and formats the user's financial profile.
    """
    try:
        profile = user.user_profile
        return f"""
        USER FINANCIAL PROFILE:
        - Monthly Income: {profile.monthly_income}
        - Savings: {profile.savings}
        - Investments: {profile.investments}
        - Debts: {profile.debts}
        - Currency: {profile.personal_info.get('preferred_currency', 'DZD') if profile.personal_info else 'DZD'}
        - Location: {profile.personal_info.get('location_context', 'Unknown') if profile.personal_info else 'Unknown'}
        - AI Preferences: {profile.user_ai_preferences}
        - Extra Info: {profile.extra_info}
        - Summary: {profile.ai_summary}
        """
    except Exception:
        return "User profile not found or incomplete."

def _execute_agent_task(user: User, prompt: str, agent: agentModel) -> dict:
    """
    Helper to execute a task with the Budget Agent.
    """
    history = get_agent_history(agent, user)
    
    # Inject User Profile if history is empty
    if not history:
        profile_context = get_user_financial_profile(user)
        initial_msg = f"{profile_context}\n\nTASK: {prompt}"
        
        add_to_history(
            agent=agent,
            user=user,
            part={"parts": [{"text": initial_msg}]},
            role="user"
        )
        history.append(types.Content(
            role="user",
            parts=[types.Part(text=initial_msg)]
        ))
    else:
        # Just add the new prompt
        add_to_history(
            agent=agent,
            user=user,
            part={"parts": [{"text": prompt}]},
            role="user"
        )
        history.append(types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        ))

    config_obj = types.GenerateContentConfig(
        system_instruction=agent.system_instruction,
        response_mime_type="application/json",
        response_schema=BudgetGenerationResponse,
        temperature=0.7,
    )
    
    client = genai.Client(api_key=API_KEY)
    
    # try:
    response = client.models.generate_content(
        model=agent.gemini_model,
        contents=history,
        config=config_obj
    )
    
    generated_content = response.parsed
    
    add_to_history(
        agent=agent,
        user=user,
        part={"parts": [{"text": response.text}]},
        role="model"
    )
    
    # Update/Create budgets in DB
    if generated_content and generated_content.budgets:
        existing_budgets = {b.title: b for b in Budget.objects.filter(user=user)}
        
        for item in generated_content.budgets:
            if item.title in existing_budgets:
                # Update
                b = existing_budgets[item.title]
                b.budget = item.budget
                b.spent = item.spent
                b.description = item.description
                b.save()
            else:
                # Create
                Budget.objects.create(
                    user=user,
                    title=item.title,
                    budget=item.budget,
                    spent=item.spent,
                    description=item.description
                )
        
    return {
        "type": "success",
        "data": {
            "message": generated_content.message if generated_content else "Budget updated.",
            "budgets": [b.dict() for b in generated_content.budgets] if generated_content else []
        }
    }


def process_budget_generation(user: User, user_message: str = None) -> dict:
    """
    Process a request to generate budgets.
    """
    agent = get_or_create_budget_agent()
    prompt = user_message if user_message else "Generate budget based on available info."
    return _execute_agent_task(user, prompt, agent)


def process_budget_update(user: User, budget_item: Budget, change_type: str) -> dict:
    """
    Handle budget updates (rebalancing or overspending).
    """
    agent = get_or_create_budget_agent()
    
    # Fetch all current budgets to give context
    all_budgets = Budget.objects.filter(user=user)
    budget_list_str = "\n".join([f"- {b.title}: Budget={b.budget}, Spent={b.spent}" for b in all_budgets])
    
    if change_type == 'budget_change':
        prompt = f"""
        EVENT: Budget Allocation Change
        The user manually updated the budget for '{budget_item.title}' to {budget_item.budget}.
        
        CURRENT STATE OF BUDGETS (After User Update):
        {budget_list_str}
        
        TASK:
        1. Analyze the new total budget.
        2. Rebalance the *other* categories if necessary to maintain a logical distribution or the previous total (if applicable).
        3. If the change seems isolated, just confirm.
        4. Update the descriptions if the context changes.
        
        OUTPUT:
        Return the full list of budgets (including the modified one) with updated amounts and descriptions.
        """
    elif change_type == 'overspending':
        prompt = f"""
        EVENT: Overspending Alert
        The user has spent {budget_item.spent} on '{budget_item.title}', which exceeds the budget of {budget_item.budget}.
        
        CURRENT STATE OF BUDGETS:
        {budget_list_str}
        
        TASK:
        1. Acknowledge the overspending.
        2. Update the description of '{budget_item.title}' to include a warning and advice.
        3. Suggest adjustments to other budgets to cover the deficit if possible (rebalancing).
        
        OUTPUT:
        Return the full list of budgets with updated amounts and descriptions.
        """
    else:
        prompt = "Analyze current budget state."

    return _execute_agent_task(user, prompt, agent)


def process_budget_deletion(user: User) -> dict:
    """
    Handle budget deletion.
    """
    agent = get_or_create_budget_agent()
    
    all_budgets = Budget.objects.filter(user=user)
    budget_list_str = "\n".join([f"- {b.title}: Budget={b.budget}, Spent={b.spent}" for b in all_budgets])
    
    prompt = f"""
    EVENT: Budget Category Deleted
    The user deleted a budget category.
    
    CURRENT STATE OF REMAINING BUDGETS:
    {budget_list_str}
    
    TASK:
    1. Analyze the remaining budgets.
    2. Rebalance the funds from the deleted category into the remaining ones (or savings) if appropriate.
    3. Update descriptions.
    
    OUTPUT:
    Return the full list of budgets with updated amounts and descriptions.
    """
    
    return _execute_agent_task(user, prompt, agent)
