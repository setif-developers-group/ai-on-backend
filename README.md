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

### Other Modules

-   **AI Core:** `/api/ai_core/`
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

-   **Advisor:** `/api/advisor/`
-   **Forecast:** `/api/forecast/`
-   **Chat:** `/api/chat/`
-   **Notify:** `/api/notify/`

Check the Swagger docs (`/api/docs/`) for details on these endpoints.