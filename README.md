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
-   **Budget:** `/api/budget/`
-   **Advisor:** `/api/advisor/`
-   **Forecast:** `/api/forecast/`
-   **Chat:** `/api/chat/`
-   **Notify:** `/api/notify/`

Check the Swagger docs (`/api/docs/`) for details on these endpoints.