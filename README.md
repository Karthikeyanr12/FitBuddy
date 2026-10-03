# FitBuddy - AI Fitness Plan Generator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-005571?style=for-the-badge&logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Pro%20%26%20Flash-8E75B2?style=for-the-badge&logo=google)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge&logo=sqlalchemy)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite)

<p align="center">
  <strong>An enterprise-grade, AI-driven wellness platform delivering personalized 7-day training periodization, goal-aligned nutrition intelligence, and iterative plan refinement.</strong>
</p>

</div>

---

## 📌 Executive Summary

**FitBuddy** is a full-stack health-tech web application engineered to bridge conversational generative artificial intelligence with practical exercise science. By evaluating individual biometric profiles, fitness goals, and training experience levels, FitBuddy generates structured, day-by-day regimens accompanied by tailored nutritional guidance.

The platform implements an asynchronous feedback loop allowing athletes to submit continuous adjustments to their active plan, alongside a protected administrative management console for trainer oversight and progress comparison.

---

## 🏛️ System Architecture

```text
┌────────────────┐          HTTP Requests         ┌────────────────────────┐
│  User Browser  │ ◄────────────────────────────► │     FastAPI Engine     │
└────────────────┘                                └───────────┬────────────┘
        │                                                     │
   Jinja2 + CSS                                       SQLAlchemy ORM
        ▼                                                     ▼
┌────────────────────────┐                        ┌────────────────────────┐
│  Modern Frontend UI    │                        │  SQLite Persistence    │
│  - index.html          │                        │  (fitbuddy.db)         │
│  - result.html         │                        │  - Users Table         │
│  - regenerate_plan.html│                        │  - WorkoutPlan Table   │
│  - all_users.html      │                        │  - Feedback Table      │
│  - admin_login.html    │                        │  - AdminSetting Table  │
└────────────────────────┘                        └────────────────────────┘
                                                              │
                                                      Google Generative AI
                                                              ▼
                                                  ┌────────────────────────┐
                                                  │ Gemini 1.5 Pro / Flash │
                                                  │ - Workout Generation   │
                                                  │ - Plan Refinement      │
                                                  │ - Nutrition Advisory   │
                                                  └────────────────────────┘
```

---

## ✨ Core Capabilities

### 1. Personalized 7-Day Workout Periodization
- Synthesizes user biometrics (**Name**, **User ID**, **Age**, **Weight**, **Gender**, **Fitness Goal**, and **Intensity Level**).
- Builds day-by-day training routines featuring structured **Warm-ups (5–10 mins)**, **Main Workouts** (with targeted sets, reps, and recommended rest intervals), and **Cooldown Protocols**.

### 2. Dedicated Plan Regeneration Workflow (`/regenerate-plan`)
- Separates the workout consultation from initial generation for improved usability.
- **Lookup & Inspection:** Athletes query by registered Username or User ID to review their active baseline routine.
- **AI Modification:** Accepts custom athlete feedback (*e.g., "Add 15 minutes of cardio", "Adjust for limited home equipment"*) and dynamically rewrites the schedule while preserving unchanged days.
- Displays the updated routine with an instant confirmation indicator.

### 3. Precision Nutrition & Recovery Intelligence
- Generates concise, actionable dietary guidance aligned with the user's specific fitness goal via **Gemini Flash**.
- Features client-side asynchronous tip refresh without requiring a full page reload.

### 4. Protected Central Administrator Console (`/view-all-users`)
- **Credential Protection:** Requires administrative verification prior to accessing platform metrics and athlete records.
- **In-Session Password Management:** Allows administrators to modify access credentials dynamically from within the dashboard, persisting changes directly in SQLite.
- **Comparative Audit:** Displays user profiles with original plans and updated feedback plans side-by-side.
- **Data Management:** Includes real-time athlete search filtering and profile deletion controls.

---

## ⚙️ Configuration & Environment Setup

FitBuddy requires a Google Gemini API key to interact with live generative models.

1. Create a `.env` file in the project root (a template is available at [`.env.example`](.env.example)):

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

2. Acquire your API key and populate the `GOOGLE_API_KEY` variable above.

> **Resilience Architecture:** If `GOOGLE_API_KEY` is omitted or quota is exceeded, FitBuddy automatically invokes an intelligent internal fallback template. All user interfaces, database persistence operations, and revision endpoints remain 100% functional and testable without runtime exceptions.

---

## 🚀 Installation & Local Deployment

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/fitbuddy.git
cd fitbuddy
```

### 2. Initialize Virtual Environment
```bash
# Windows
python -m venv fitbuddy-env
fitbuddy-env\Scripts\activate

# Linux / macOS
python3 -m venv fitbuddy-env
source fitbuddy-env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch Application Server
Execute using Uvicorn:
```bash
python -m uvicorn main:app --reload --port 8000
```
*Or on Windows using the included launcher:*
```powershell
.\run.bat
```

### 5. Access Endpoints
- **Workout Generator Form:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Plan Regeneration Portal:** [http://127.0.0.1:8000/regenerate-plan](http://127.0.0.1:8000/regenerate-plan)
- **Admin Dashboard:** [http://127.0.0.1:8000/view-all-users](http://127.0.0.1:8000/view-all-users) *(Default password: `1234`)*
- **Interactive Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔌 API Specification

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Renders user registration & workout generator form | Public |
| `POST` | `/generate-workout` | Processes profile inputs, invokes Gemini AI, returns workout regimen | Public |
| `GET` | `/regenerate-plan` | Renders username lookup and active workout review portal | Public |
| `POST` | `/regenerate-plan` | Revises active plan according to submitted athlete feedback | Public |
| `GET` | `/nutrition-tip` | Returns targeted nutritional advice based on fitness goal | Public |
| `GET` | `/admin-login` | Renders administrative verification screen | Public |
| `POST` | `/admin-login` | Authenticates administrator credentials and issues session cookie | Public |
| `GET` | `/admin/logout` | Clears administrative session cookie and redirects home | Protected |
| `POST` | `/admin/change-password` | Updates administrative password in SQLite configuration table | Protected |
| `GET` | `/view-all-users` | Displays centralized athlete records, plans, and revision history | Protected |
| `POST` | `/delete-user/{id}` | Removes athlete record and associated workout history | Protected |
| `GET` | `/users/{id}/latest_plan` | REST endpoint returning latest plan content for user | Public |

---

## 📂 Repository Structure

```text
FitBuddy/
├── .env                       # Environment configuration (Gemini API Key)
├── .env.example               # Template environment variables
├── .gitignore                 # Version control exclusions
├── requirements.txt           # Project package dependencies
├── run.bat                    # One-click startup script for Windows
├── database.py                # Database connection engine & helper operations
├── models.py                  # SQLAlchemy ORM declarations (User, Plan, Feedback, Admin)
├── schemas.py                 # Pydantic data validation schemas
├── crud.py                    # Database CRUD operations
├── ai_service.py              # Gemini generative engine & graceful fallback logic
├── main.py                    # FastAPI application, route handlers, and middleware
├── test_models.py             # Diagnostic script for checking Gemini model availability
├── app/                       # Package structure aligned with project specifications
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   └── updated_plan.py
├── services/                  # Service layer package alias
│   ├── __init__.py
│   └── ai_service.py
├── static/
│   ├── css/
│   │   └── styles.css         # Modern fitness UI styling & animations
│   ├── js/
│   │   └── main.js            # Frontend interactivity & state management
│   └── images/
│       ├── gym-bg.svg         # Geometric gym background graphic
│       └── gym-bg.jpg         # Background fallback image
└── templates/
    ├── index.html             # Homepage: biometric input & demo profiles
    ├── result.html            # Results: generated plan & nutrition advisory
    ├── regenerate_plan.html   # Dedicated portal: plan lookup & AI revision
    ├── all_users.html         # Admin dashboard: athlete table & management
    └── admin_login.html       # Protected administrative verification page
```

---

## 🛡️ Security & Authentication

- Administrative endpoints are shielded with HTTP-only, SameSite session cookies (`admin_session`).
- The default administrative password is set to `1234` upon initial database bootstrap and can be updated securely at any time from within the dashboard.
- Sensitive environment files (`.env`) and local database binaries (`*.db`) are excluded from source control via `.gitignore`.
