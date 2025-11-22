import json
import os
from django.contrib.auth.models import User
from django.conf import settings
from .models import Expense
from budget.models import Budget
from agents.models import agentModel
from agents.services import get_agent_history, add_to_history
from google import genai
from google.genai import types
from decouple import config
from decimal import Decimal
from datetime import datetime

API_KEY = config('GEMINI_API_KEY')

EXPENSE_MANAGER_SYSTEM_INSTRUCTION = """
IDENTITY
You are the **Expense Manager Agent**. Your role is to process expenses from text, images, or PDFs.

YOUR TASKS
1.  **Extract Information**: Identify the following from the input:
    *   **Budget Category**: The category this expense belongs to (e.g., "Groceries", "Transport").
    *   **Product Name**: What was purchased.
    *   **Price/Spent**: The amount spent.
    *   **Description**: Any additional details.
2.  **Match Category**: Try to match the extracted category with the user's existing budgets.
3.  **Output Structure**: Return the extracted data in a strict JSON format.

OUTPUT FORMAT
{
    "expenses": [
        {
            "category": "Category Name",
            "product_name": "Product Name",
            "amount": 123.45,
            "description": "Description"
        }
    ]
}
"""

REPORT_AGENT_SYSTEM_INSTRUCTION = """
IDENTITY
You are the **Report Agent**. Your role is to generate comprehensive financial reports.

YOUR TASKS
1.  **Analyze Data**: Review the user's expenses and budgets.
2.  **Compare**: Compare actual spending against budget goals.
3.  **Insights**: Identify trends, overspending, and saving opportunities.
4.  **Format**: Generate a Markdown report suitable for a mobile app.

OUTPUT FORMAT
Return the report in Markdown.
"""

def get_or_create_expense_agent() -> agentModel:
    agent, created = agentModel.objects.get_or_create(
        name="expense_manager",
        defaults={
            "description": "Agent that manages expenses and extracts info from receipts",
            "system_instruction": EXPENSE_MANAGER_SYSTEM_INSTRUCTION,
            "gemini_model": "gemini-2.5-flash",
            "thinking_budget": 0
        }
    )
    if not created and agent.gemini_model != "gemini-2.5-flash":
        agent.gemini_model = "gemini-2.5-flash"
        agent.save()
    return agent

def get_or_create_report_agent() -> agentModel:
    agent, created = agentModel.objects.get_or_create(
        name="report_agent",
        defaults={
            "description": "Agent that generates financial reports",
            "system_instruction": REPORT_AGENT_SYSTEM_INSTRUCTION,
            "gemini_model": "gemini-2.5-flash",
            "thinking_budget": 0
        }
    )
    if not created and agent.gemini_model != "gemini-2.5-flash":
        agent.gemini_model = "gemini-2.5-flash"
        agent.save()
    return agent

def process_expense_management(user: User, message: str, file_path: str = None, manual_data: dict = None) -> dict:
    """
    Process an expense request.
    The message might contain a file path if it came from an API upload,
    or the message string itself might contain info.
    If manual_data is provided (amount, product_name), it bypasses AI extraction.
    """
    print(f"DEBUG: Expense Manager Agent is running now... processing message: {message}, file_path: {file_path}, manual_data: {manual_data}")
    agent = get_or_create_expense_agent()
    
    expenses_data = []
    
    # Check for manual data override
    if manual_data and manual_data.get('amount') and manual_data.get('product_name'):
        print("DEBUG: Using manual data, skipping Gemini extraction.")
        expenses_data.append({
            "category": None, # Will be handled by budget_id lookup
            "product_name": manual_data.get('product_name'),
            "amount": float(manual_data.get('amount')),
            "description": manual_data.get('description', ''),
            "budget_id": manual_data.get('budget_id')
        })
    else:
        # Prepare content for Gemini
        contents = []
        if file_path:
            # Load file
            try:
                with open(file_path, "rb") as f:
                    file_content = f.read()
                    # Determine mime type based on extension
                    mime_type = "application/pdf" if file_path.endswith(".pdf") else "image/jpeg"
                    contents.append(types.Part.from_bytes(data=file_content, mime_type=mime_type))
            except Exception as e:
                return {"type": "error", "data": {"error": f"Failed to read file: {str(e)}"}}
                
        contents.append(types.Part.from_text(text=message))
        
        # Add user's existing budgets to context
        budgets = Budget.objects.filter(user=user)
        budget_list = ", ".join([b.title for b in budgets])
        context_msg = f"User's existing budget categories: {budget_list}. Try to match these."
        contents.append(types.Part.from_text(text=context_msg))

        client = genai.Client(api_key=API_KEY)
        
        try:
            response = client.models.generate_content(
                model=agent.gemini_model,
                contents=[types.Content(role="user", parts=contents)],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    system_instruction=agent.system_instruction
                )
            )
            
            result_json = json.loads(response.text)
            print(f"DEBUG: Gemini response for expenses: {result_json}")
            expenses_data = result_json.get("expenses", [])
            
        except Exception as e:
            print(f"DEBUG: Error in process_expense_management: {str(e)}")
            return {"type": "error", "data": {"error": str(e)}}

    # Process extracted or manual expenses
    try:
        processed_expenses = []
        alerts = []
        
        for item in expenses_data:
            category_name = item.get("category")
            product_name = item.get("product_name", "Unknown Product")
            amount = Decimal(str(item.get("amount", 0)))
            description = item.get("description", "")
            
            # Find or create budget
            budget = None
            if item.get("budget_id"):
                budget = Budget.objects.filter(user=user, id=item.get("budget_id")).first()
            elif category_name:
                budget = Budget.objects.filter(user=user, title__iexact=category_name).first()
            
            # Create Expense
            expense = Expense.objects.create(
                user=user,
                budget=budget,
                product_name=product_name,
                amount=amount,
                description=description
            )
            
            # Update Budget Spent
            if budget:
                budget.spent += amount
                budget.save()
                
                # Create notifications for budget alerts
                from notify.services import create_notification
                
                # Check for overspending
                if budget.spent > budget.budget:
                    alerts.append(f"Overspending detected in {budget.title}. Budget: {budget.budget}, Spent: {budget.spent}")
                    
                    # Create high-priority notification for overspending
                    create_notification(
                        user=user,
                        notification_type='budget_alert',
                        priority='high',
                        title=f'⚠️ Overspending in {budget.title}',
                        message=f'You have exceeded your budget for {budget.title}. Budget: {budget.budget} DZD, Spent: {budget.spent} DZD',
                        related_budget_id=budget.id,
                        action_url=f'/budget/{budget.id}'
                    )
                
                # Check for budget warnings (80% threshold)
                elif budget.spent >= budget.budget * 0.8 and budget.spent <= budget.budget:
                    percentage = (budget.spent / budget.budget) * 100
                    create_notification(
                        user=user,
                        notification_type='expense_alert',
                        priority='medium',
                        title=f'📊 Approaching budget limit: {budget.title}',
                        message=f'You have used {percentage:.0f}% of your {budget.title} budget. Remaining: {budget.budget - budget.spent} DZD',
                        related_budget_id=budget.id,
                        action_url=f'/budget/{budget.id}'
                    )
            
            processed_expenses.append({
                "id": expense.id,
                "product": product_name,
                "amount": float(amount),
                "category": budget.title if budget else "Uncategorized"
            })
            
        return {
            "type": "response",
            "data": {
                "message": f"Processed {len(processed_expenses)} expenses.",
                "expenses": processed_expenses,
                "alerts": alerts
            }
        }
        
    except Exception as e:
        print(f"DEBUG: Error in process_expense_management: {str(e)}")
        return {"type": "error", "data": {"error": str(e)}}

def process_report_generation(user: User, message: str) -> dict:
    print(f"DEBUG: Report Agent is running now... processing message: {message}")
    agent = get_or_create_report_agent()
    
    # Gather data
    expenses = Expense.objects.filter(user=user).order_by('-date')
    budgets = Budget.objects.filter(user=user)
    
    expense_summary = "\n".join([f"- {e.date.date()}: {e.product_name} ({e.amount}) - {e.budget.title if e.budget else 'No Category'}" for e in expenses])
    budget_summary = "\n".join([f"- {b.title}: Budget {b.budget}, Spent {b.spent}" for b in budgets])
    
    prompt = f"""
    Generate a financial report for the user based on the following data:
    
    Budgets (Goals):
    {budget_summary}
    
    Recent Expenses:
    {expense_summary}
    
    User Request: {message}
    """
    
    client = genai.Client(api_key=API_KEY)
    response = client.models.generate_content(
        model=agent.gemini_model,
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
        config=types.GenerateContentConfig(
            system_instruction=agent.system_instruction
        )
    )
    
    return {
        "type": "response",
        "data": {
            "report": response.text
        }
    }
