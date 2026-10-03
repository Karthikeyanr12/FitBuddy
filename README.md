# FitBuddy - AI Fitness Plan Generator using Gemini Models

FitBuddy is an intelligent, full-stack fitness web application that generates personalized 7-day workout plans and nutrition tips using Google Gemini AI models (**Gemini 1.5 Pro** and **Gemini Flash**). Built with FastAPI, SQLAlchemy, SQLite, and modern Jinja2 templates, FitBuddy features dynamic plan generation, iterative feedback revision, and a centralized admin dashboard.

---

## 🚀 Key Features (Aligned with Project Milestones)

- **Scenario 1: Personalized 7-Day Workout Routine Generation**
  - Tailors exercise selection, sets, reps, warm-ups, and cooldowns based on Name, User ID, Age, Weight, Fitness Goal, and Intensity.
  - Powered by **Google Gemini Pro** (with automated fallback).
- **Scenario 2: Dedicated Regenerate Plan Page (`/regenerate-plan`)**
  - Instead of cluttering the initial generation page with immediate feedback forms, users visit the dedicated **Regenerate Plan** page.
  - Step 1: Athlete enters their registered **Username** or **User ID** to look up and inspect their **current/old workout plan**.
  - Step 2: Athlete enters specific feedback (with 1-click suggested chips like *"+ 15m Cardio"*, *"+ Restorative Yoga"*).
  - Step 3: Google Gemini AI revises the routine accordingly, updates the database, and displays the **newly modified plan** alongside the confirmation banner: `✅ Your plan has been updated based on your feedback!`.
- **Scenario 3: AI Nutrition & Recovery Tips**
  - Delivers targeted, actionable dietary guidance aligned with the athlete's primary goal using **Gemini Flash**.
  - Dynamic on-page refresh button to generate alternative nutrition advice.
- **Scenario 4: Centralized Admin Dashboard (`/view-all-users`)**
  - **Password Protection:** Visiting `/view-all-users` prompts for the admin password (default: `1234`).
  - **Change Password:** Once authenticated, the admin can change their password anytime via the modal dialog, which persists in SQLite.
  - Real-time athlete overview displaying User ID, Name, Age, Weight, Goal, Intensity, Original Plan, and Updated Plan side-by-side.
  - Includes real-time athlete search filter and delete management.
  - Dedicated **Logout** button to clear the admin session.

---

## 🛠️ Tech Stack & Architecture

- **Backend:** FastAPI, Uvicorn, Python 3.10+
- **Database:** SQLite with SQLAlchemy ORM (`fitbuddy.db`)
- **AI Engine:** Google Gemini Generative AI SDK (`google-generativeai`)
- **Frontend:** HTML5, Modern CSS (Glassmorphism, Dark Mode, Responsive Design), Jinja2 Templating, FontAwesome, Marked.js

---

## 📋 Required Environment Variables (`.env`)

To enable live AI generation with Google Gemini, create or edit the `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### How to get your API Key:
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** and create a new key.
4. Paste the key into `.env` as shown above.

> **Note:** If `GOOGLE_API_KEY` is not provided or quota is exceeded, FitBuddy automatically uses an intelligent built-in generator template so that all UI workflows, database persistence, and feedback loops remain 100% testable and operable without server crashes.

---

## 💻 Installation & Local Setup

### 1. Clone or Open Project
```powershell
cd K:\FitBuddy
```

### 2. Set Up Virtual Environment (Optional but Recommended)
```powershell
python -m venv fitbuddy-env
fitbuddy-env\Scripts\activate
```

### 3. Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Start the Application Server
Run either:
```powershell
uvicorn main:app --reload
```
or (as per the PDF specification):
```powershell
uvicorn app.main:app --reload
```

### 5. Access the Web Pages
- **Workout Generator Form:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Dashboard (All Users):** [http://127.0.0.1:8000/view-all-users](http://127.0.0.1:8000/view-all-users)
- **FastAPI Interactive API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📁 Project Structure

```text
FitBuddy/
├── .env                       # Environment variables (Gemini API Key)
├── .env.example               # Template for environment configuration
├── requirements.txt           # Project dependencies
├── database.py                # SQLite database configuration & ORM operations
├── models.py                  # SQLAlchemy models (User, WorkoutPlan, Feedback)
├── schemas.py                 # Pydantic validation schemas
├── crud.py                    # Database CRUD operations
├── ai_service.py              # Gemini AI integration (Pro & Flash) with fallback
├── main.py                    # Main FastAPI server & route handlers
├── test_models.py             # Script to verify available Gemini models
├── app/                       # Modular package aligned with PDF Milestone 2/3
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   └── updated_plan.py
├── services/                  # Services package alias
│   ├── __init__.py
│   └── ai_service.py
├── static/
│   ├── css/
│   │   └── styles.css         # Modern fitness UI styling & animations
│   ├── js/
│   │   └── main.js            # Frontend interactivity & loading indicators
│   └── images/
│       ├── gym-bg.svg         # Athletic gym background pattern
│       └── gym-bg.jpg         # Gym-themed visual asset
└── templates/
    ├── index.html             # Homepage & user details input form
    ├── result.html            # 7-day workout plan, nutrition tip, feedback form
    └── all_users.html         # Admin dashboard table for all users & plans
```
