# AI-On Backend

This is the backend repository for the AI-On project, built with Django and Django REST Framework. It provides API endpoints for user authentication, AI-driven onboarding, and other core features.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd ai-on-backend
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, ensure you have `django`, `djangorestframework`, `djangorestframework-simplejwt`, `drf-spectacular`, and `google-generativeai` installed.)*

4.  **Apply database migrations:**

    ```bash
    cd ai-on
    python manage.py migrate
    ```

5.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

    The server will start at `http://localhost:8000/`.

## 📚 API Documentation

Interactive API documentation (Swagger UI) is available at:
**[http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)**

This UI allows you to explore all endpoints and test them directly from the browser.

## 🔑 Authentication

The API uses JWT (JSON Web Token) authentication.

-   **Obtain Token:** `POST /api/token/`
    -   Body: `{"username": "...", "password": "..."}`
    -   Response: `{"access": "...", "refresh": "..."}`
-   **Refresh Token:** `POST /api/token/refresh/`
    -   Body: `{"refresh": "..."}`

Include the access token in the `Authorization` header for protected endpoints:
`Authorization: Bearer <your_access_token>`

## 🛠️ Main Endpoints (For Frontend Developers)

### Users

-   **Sign Up:** `POST /api/users/create/`
    -   Create a new user account.
    -   Body: `{"username": "...", "password": "...", "email": "..."}`
-   **Get Profile:** `GET /api/users/me/`
    -   Returns current user details, including `onboarding_status`.

### Onboarding

The onboarding process is an interactive chat with an AI agent.

-   **Start / Get Current Question:** `GET /api/onboarding/`
    -   Starts the onboarding process if not started, or retrieves the current question.
    -   **Response:** Returns a question object (see "Response (Question)" below).

-   **Submit Answer / Get Next Question:** `POST /api/onboarding/`
    -   **Request Body:**
        ```json
        {
          "answer": "User's answer here"
        }
        ```
        *Note: For 'checkboxes' questions, `answer` should be a list of strings.*
    -   **Response (Question):**
        ```json
        {
          "question": "What is your main goal?",
          "question_type": "radio",
          "options": ["Goal A", "Goal B"]
        }
        ```
        *`question_type` can be: `direct` (text input), `radio` (single select), `checkboxes` (multi select).*
    -   **Response (Finished):**
        ```json
        {
          "type": "finsh"
        }
        ```
        When the onboarding is complete, the API returns this specific JSON. You can also check `/api/users/me/` for `onboarding_status`.

-   **Reset Onboarding:** `POST /api/onboarding/reset/`
    -   Clears the current onboarding session and starts over.

### Chatbot

The Chatbot is the primary conversational interface for AION, powered by **Gemini 2.5 Flash-Lite**.

-   **Send Message:** `POST /api/chat/`
    -   Send a message to the chatbot and receive a conversational response.
    -   **Request Body:**
        ```json
        {
          "msg": "Hello! I want to create a budget"
        }
        ```
    -   **Response:**
        ```json
        {
          "msg": "Hi there! I'd be happy to help you create a budget..."
        }
        ```
    -   **Capabilities:**
        -   General conversation and financial advice
        -   Update user profile (income, savings, debts, etc.)
        -   Track expenses ("I spent 500 at a coffee shop")
        -   Manage budgets (create, update, delete budget categories)
        -   Delegate complex tasks to specialized agents (forecasts, reports, etc.)
        -   Personalized responses based on user profile

-   **Get Chat History:** `GET /api/chat/history/`
    -   Retrieve the conversation history (excludes function calls).
    -   **Response:**
        ```json
        [
          {
            "role": "user",
            "msg": "Hello!"
          },
          {
            "role": "model",
            "msg": "Hi there! How can I help you today?"
          }
        ]
        ```

-   **Reset Chat:** `POST /api/chat/reset/`
    -   Clear the conversation history and start fresh.
    -   **Response:**
        ```json
        {
          "message": "Chat history cleared successfully"
        }
        ```

### Budget

The Budget module uses an **Event-Driven AI Agent** to manage and generate budgets.

-   **Generate Budgets (AI):** `POST /api/budget/generate/`
    -   Triggers the AI to generate a personalized budget based on the user's profile and financial history.
    -   **Request Body:** None (Empty JSON `{}`).
    -   **Response:**
        ```json
        {
          "message": "Here is your proposed budget...",
          "budgets": [
            {
              "title": "Groceries",
              "budget": 20000.00,
              "spent": 0.00,
              "description": "## Groceries\n* Milk\n* Bread..."
            }
          ]
        }
        ```

-   **List Budgets:** `GET /api/budget/`
    -   Returns a list of all budget categories for the user.

-   **Get Budget Details:** `GET /api/budget/{id}/`
    -   Returns full details of a specific budget, including the Markdown description.

-   **Update Budget:** `PATCH /api/budget/{id}/`
    -   Update `budget` (allocated amount) or `spent` amount.
    -   **Event-Driven Behavior:**
        -   **Changing `budget`**: Triggers the AI to **rebalance** other categories to maintain logical consistency.
        -   **Overspending (`spent` > `budget`)**: Triggers the AI to update the description with a warning and advice.
    -   **Request Body:** `{"budget": 25000}` or `{"spent": 5000}`.
    -   *Note: `title` and `description` are read-only and managed by the AI.*

-   **Delete Budget:** `DELETE /api/budget/{id}/`
    -   Deletes a category.
    -   **Event-Driven Behavior:** Triggers the AI to **rebalance** the remaining funds into other categories or savings.

### Expense Manager

The Expense Manager handles multi-modal expense tracking and reporting using **Gemini 2.5 Flash**. AI automatically extracts expense details from natural language or files.

-   **Add Expense:** `POST /api/expenses/`
    -   **AI-Powered Extraction:** Send natural language text or upload receipt images/PDFs. The AI extracts amount, category, product name, and description automatically.
    -   **Request Body (Text):**
        ```json
        {
          "message": "I spent 500 DZD at a coffee shop"
        }
        ```
    -   **Request (File):** `multipart/form-data` with `file` (image/PDF) and optional `message`.
    -   **Response:**
        ```json
        {
          "message": "Processed 1 expenses.",
          "expenses": [{"product": "Coffee shop purchase", "amount": 500.0, "category": "Food & Dining"}],
          "alerts": []
        }
        ```
    -   **Note:** The AI matches expenses to existing budget categories automatically.

-   **List Expenses:** `GET /api/expenses/`
    -   Returns a list of all recorded expenses.

-   **Generate Report:** `POST /api/expenses/report/`
    -   Generates a comprehensive financial report in Markdown.
    -   **Request Body:** `{"message": "Generate a monthly report"}`.
    -   **Response:** `{"report": "# Financial Report..."}`.

### Advisor

The Advisor module provides smart product recommendations and purchase guidance using **Gemini 2.5 Flash**. AI analyzes your budget and spending patterns to help you make informed purchasing decisions.

-   **Product Recommendations:** `POST /api/advisor/recommend/`
    -   Get AI-powered product recommendations based on your budget and preferences.
    -   **Request Body:**
        ```json
        {
          "message": "Recommend a laptop for programming under 50000 DZD"
        }
        ```
    -   **Response:**
        ```json
        {
          "advice": "# Laptop Recommendations...",
          "session_id": 123
        }
        ```
    -   **Note:** The AI considers your budget constraints and suggests alternatives if needed.

-   **Purchase Analysis:** `POST /api/advisor/analyze-purchase/`
    -   Analyze if a specific purchase fits your financial situation.
    -   **Request Body:**
        ```json
        {
          "message": "Should I buy a phone for 80000 DZD?"
        }
        ```
    -   **Response:**
        ```json
        {
          "advice": "# Purchase Analysis...",
          "session_id": 124
        }
        ```
    -   **Analysis includes:** Budget impact, category fit, overspending risk, alternatives.

-   **Product Comparison:** `POST /api/advisor/compare/`
    -   Compare multiple products and get a budget-aware recommendation.
    -   **Request Body:**
        ```json
        {
          "message": "Compare iPhone 15 vs Samsung S24"
        }
        ```
    -   **Response:**
        ```json
        {
          "advice": "# Product Comparison...",
          "session_id": 125
        }
        ```

-   **Advisor History:** `GET /api/advisor/history/`
    -   Retrieve your past advisor sessions and recommendations.

-   **Chatbot Integration:**
    -   The advisor is fully integrated with the chatbot. Simply ask product-related questions:
        -   "Should I buy this laptop?"
        -   "Recommend a phone under 30000"
        -   "Compare these two products"

### Notify

The Notify module is a centralized notification system that all agents use to create and manage user notifications.

-   **List Notifications:** `GET /api/notify/`
    -   Get all notifications with optional filtering by read status.
    -   **Query Parameters:**
        -   `?read=true` - Show only read notifications
        -   `?read=false` - Show only unread notifications
        -   No parameter - Show all notifications
    -   **Response:**
        ```json
        [
          {
            "id": 1,
            "notification_type": "budget_alert",
            "priority": "high",
            "title": "⚠️ Overspending in Groceries",
            "message": "You have exceeded your budget...",
            "is_read": false,
            "created_at": "2025-11-22T03:00:00Z",
            "related_budget_id": 5
          }
        ]
        ```

-   **Get Notification Details:** `GET /api/notify/{id}/`
    -   Get a specific notification. **Automatically marks it as read**.

-   **Mark as Read:** `PATCH /api/notify/{id}/read/`
    -   Manually mark a specific notification as read.

-   **Mark All as Read:** `POST /api/notify/mark-all-read/`
    -   Mark all unread notifications as read.
    -   **Response:** `{"marked_count": 5}`

-   **Unread Count:** `GET /api/notify/unread-count/`
    -   Get the count of unread notifications (useful for badge display).
    -   **Response:** `{"unread_count": 3}`

-   **Delete Notification:** `DELETE /api/notify/{id}/delete/`
    -   Delete a specific notification.

-   **Notification Types:**
    -   `budget_alert` - Budget-related alerts (overspending)
    -   `expense_alert` - Expense warnings (approaching limit)
    -   `advisor_tip` - Tips from the advisor
    -   `goal_milestone` - Goal achievements
    -   `system` - System notifications

-   **Priority Levels:** `low`, `medium`, `high`, `urgent`

-   **Automatic Notifications:**
    -   Overspending alerts (high priority) when budget is exceeded
    -   Budget warnings (medium priority) when 80% of budget is used

### Other Modules

Additional modules are available but not yet fully documented:

-   **AI Core:** `/api/ai_core/` - Main AI Coordinator (agent-to-agent only, no direct user access)
-   **Forecast:** `/api/forecast/` - Financial forecasting agent

Check the Swagger docs (`/api/docs/`) for details on these endpoints.