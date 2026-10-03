from fastapi import FastAPI, Depends, Request, Form, HTTPException, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import os

import database, models, schemas, crud
import ai_service

# Initialize database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="Personalized 7-day workout plans and nutrition tips powered by Google Gemini AI",
    version="2.0.0"
)

# Ensure directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/images", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def render_template(template_name: str, context: dict, request: Request):
    """Robust template renderer supporting all Starlette/FastAPI versions"""
    context["request"] = request
    try:
        return templates.TemplateResponse(request=request, name=template_name, context=context)
    except TypeError:
        return templates.TemplateResponse(template_name, context)

# --- Page Routes --- #

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """Home page: Displays user input form"""
    users = db.query(models.User).all()
    return render_template("index.html", {
        "users": users,
        "page_title": "FitBuddy - AI Workout Generator"
    }, request)

# --- Admin Authentication & Dashboard Routes --- #

@app.get("/admin-login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    if request.cookies.get("admin_session") == "authenticated":
        return RedirectResponse(url="/view-all-users", status_code=303)
    return render_template("admin_login.html", {
        "error": None,
        "page_title": "Admin Verification - FitBuddy"
    }, request)

@app.post("/admin-login", response_class=HTMLResponse)
async def process_admin_login(request: Request, password: str = Form(...), db: Session = Depends(get_db)):
    """Authenticate admin password"""
    current_admin_pwd = database.get_admin_password(db)
    if password.strip() == current_admin_pwd:
        response = RedirectResponse(url="/view-all-users", status_code=303)
        response.set_cookie(key="admin_session", value="authenticated", httponly=True, samesite="lax")
        return response
    else:
        return render_template("admin_login.html", {
            "error": "Incorrect password. Default is 1234 unless previously changed.",
            "page_title": "Admin Verification - FitBuddy"
        }, request)

@app.get("/admin/logout")
async def admin_logout(request: Request):
    """Log out admin session"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="admin_session")
    return response

@app.get("/view-all-users", response_class=HTMLResponse)
async def view_all_users(request: Request, db: Session = Depends(get_db)):
    """Admin dashboard: Displays all registered users and their original & updated plans (Protected)"""
    if request.cookies.get("admin_session") != "authenticated":
        return render_template("admin_login.html", {
            "error": None,
            "page_title": "Admin Verification - FitBuddy"
        }, request)

    users = db.query(models.User).order_by(models.User.id.desc()).all()
    user_data = []
    
    for u in users:
        latest_plan = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.user_id == u.id).order_by(models.WorkoutPlan.id.desc()).first()
        user_data.append({
            "id": u.id,
            "name": u.name,
            "age": u.age,
            "gender": u.gender or "Not Specified",
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "original_plan": latest_plan.original_plan if latest_plan and latest_plan.original_plan else (latest_plan.plan_content if latest_plan else "N/A"),
            "updated_plan": latest_plan.updated_plan if latest_plan and latest_plan.updated_plan else "Not updated",
            "plan_id": latest_plan.id if latest_plan else None
        })

    return render_template("all_users.html", {
        "users": user_data,
        "total_users": len(user_data),
        "pwd_success": None,
        "pwd_error": None
    }, request)

@app.post("/admin/change-password", response_class=HTMLResponse)
async def change_admin_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Change admin password while logged in"""
    if request.cookies.get("admin_session") != "authenticated":
        return RedirectResponse(url="/admin-login", status_code=303)

    stored_pwd = database.get_admin_password(db)
    
    # Fetch users for rendering dashboard
    users = db.query(models.User).order_by(models.User.id.desc()).all()
    user_data = []
    for u in users:
        latest_plan = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.user_id == u.id).order_by(models.WorkoutPlan.id.desc()).first()
        user_data.append({
            "id": u.id,
            "name": u.name,
            "age": u.age,
            "gender": u.gender or "Not Specified",
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "original_plan": latest_plan.original_plan if latest_plan and latest_plan.original_plan else (latest_plan.plan_content if latest_plan else "N/A"),
            "updated_plan": latest_plan.updated_plan if latest_plan and latest_plan.updated_plan else "Not updated",
            "plan_id": latest_plan.id if latest_plan else None
        })

    # Validate current password
    if current_password.strip() != stored_pwd:
        return render_template("all_users.html", {
            "users": user_data,
            "total_users": len(user_data),
            "pwd_success": None,
            "pwd_error": "Current password does not match. Please try again."
        }, request)

    # Validate new password match
    if new_password != confirm_password:
        return render_template("all_users.html", {
            "users": user_data,
            "total_users": len(user_data),
            "pwd_success": None,
            "pwd_error": "New password and Confirm password do not match."
        }, request)

    if len(new_password.strip()) < 4:
        return render_template("all_users.html", {
            "users": user_data,
            "total_users": len(user_data),
            "pwd_success": None,
            "pwd_error": "New password must be at least 4 characters long."
        }, request)

    # Save new password in database
    database.set_admin_password(new_password.strip(), db)

    return render_template("all_users.html", {
        "users": user_data,
        "total_users": len(user_data),
        "pwd_success": "Admin password updated successfully! Please remember your new password.",
        "pwd_error": None
    }, request)

# --- Workout Generation Routes (Supports both PDF /generate-workout and Repomix /generate_plan) --- #

async def handle_generate_workout(
    request: Request,
    name: Optional[str],
    username: Optional[str],
    user_id: Optional[int],
    age: int,
    gender: Optional[str],
    weight: float,
    goal: str,
    intensity: str,
    db: Session
):
    final_name = name or username or f"Athlete_{user_id or 1}"
    final_gender = gender or "Not Specified"
    
    # 1. Save or update user in database
    db_user = None
    if user_id and user_id > 0:
        db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        db_user = crud.get_user_by_name(db, name=final_name)
        
    user_create_data = schemas.UserCreate(
        id=user_id if (user_id and user_id > 0) else None,
        name=final_name,
        age=age,
        gender=final_gender,
        weight=weight,
        goal=goal,
        intensity=intensity
    )
    
    if db_user:
        db_user = crud.update_user(db, db_user, user_create_data)
    else:
        db_user = crud.create_user(db, user_create_data)
        
    # 2. Call Gemini AI Services
    workout_plan_text = ai_service.generate_workout_plan(
        name=db_user.name,
        age=db_user.age,
        gender=db_user.gender,
        weight=db_user.weight,
        goal=db_user.goal,
        intensity=db_user.intensity
    )
    
    nutrition_tip_text = ai_service.generate_nutrition_tip(goal=db_user.goal)
    
    # 3. Store workout plan
    db_plan = crud.create_workout_plan(db, plan_content=workout_plan_text, user_id=db_user.id)

    # 4. Check whether client wants HTML (regular form submit) or JSON (AJAX)
    accept_header = request.headers.get("accept", "")
    is_ajax = "application/json" in accept_header or request.headers.get("x-requested-with") == "XMLHttpRequest"
    
    if is_ajax:
        return JSONResponse({
            "status": "success",
            "user_id": db_user.id,
            "plan_id": db_plan.id,
            "plan": workout_plan_text,
            "workout_plan": workout_plan_text,
            "nutrition_tip": nutrition_tip_text
        })
    
    return render_template("result.html", {
        "username": db_user.name,
        "name": db_user.name,
        "user_id": db_user.id,
        "age": db_user.age,
        "gender": db_user.gender,
        "weight": db_user.weight,
        "goal": db_user.goal,
        "intensity": db_user.intensity,
        "workout_plan": workout_plan_text,
        "nutrition_tip": nutrition_tip_text,
        "plan_id": db_plan.id,
        "updated_message": None
    }, request)

@app.post("/generate-workout")
async def generate_workout(
    request: Request,
    name: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None),
    age: int = Form(...),
    gender: Optional[str] = Form("Not Specified"),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db)
):
    return await handle_generate_workout(request, name, username, user_id, age, gender, weight, goal, intensity, db)

@app.post("/generate_plan")
async def generate_plan_alias(
    request: Request,
    name: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None),
    age: int = Form(...),
    gender: Optional[str] = Form("Not Specified"),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db)
):
    return await handle_generate_workout(request, name, username, user_id, age, gender, weight, goal, intensity, db)

# --- Regenerate Plan Routes (Ask username -> Display old plan -> Accept feedback -> Modify) --- #

@app.get("/regenerate-plan", response_class=HTMLResponse)
async def regenerate_plan_page(
    request: Request,
    username: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Regenerate Plan Page: Search for username, view old plan, and accept feedback"""
    user = None
    latest_plan = None
    lookup_error = None
    user_found = False
    
    query = (username or "").strip()
    if query:
        # Check if query is numeric user_id
        if query.isdigit():
            user = crud.get_user(db, user_id=int(query))
        if not user:
            user = crud.get_user_by_name(db, name=query)
            
        if user:
            user_found = True
            latest_plan = crud.get_latest_workout_plan(db, user_id=user.id)
            if not latest_plan:
                lookup_error = f"Athlete '{user.name}' found, but no workout routine has been generated yet. Please generate one first!"
                user_found = False
        else:
            lookup_error = f"No athlete found matching '{query}'. Please check the username or register on the Home page."
    elif user_id and user_id > 0:
        user = crud.get_user(db, user_id=user_id)
        if user:
            user_found = True
            latest_plan = crud.get_latest_workout_plan(db, user_id=user.id)
            if not latest_plan:
                lookup_error = f"Athlete '{user.name}' found, but no workout routine has been generated yet."
                user_found = False
        else:
            lookup_error = f"No athlete found with User ID #{user_id}."

    current_plan_text = ""
    if latest_plan:
        current_plan_text = latest_plan.updated_plan or latest_plan.plan_content or latest_plan.original_plan or ""

    return render_template("regenerate_plan.html", {
        "user_found": user_found,
        "user": user,
        "latest_plan": latest_plan,
        "current_plan_text": current_plan_text,
        "newly_updated_plan": None,
        "updated_message": None,
        "lookup_error": lookup_error,
        "target_username": query or (str(user_id) if user_id else ""),
        "page_title": "Regenerate Plan - FitBuddy"
    }, request)

@app.post("/regenerate-plan", response_class=HTMLResponse)
async def process_regenerate_plan(
    request: Request,
    user_id: Optional[int] = Form(None),
    username: Optional[str] = Form(None),
    feedback_text: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process feedback, update workout plan via AI, and display both old and updated plans"""
    user = None
    if user_id and user_id > 0:
        user = crud.get_user(db, user_id=user_id)
    if not user and username:
        user = crud.get_user_by_name(db, name=username.strip())
        
    if not user:
        return render_template("regenerate_plan.html", {
            "user_found": False,
            "lookup_error": "User could not be identified. Please search your username again.",
            "page_title": "Regenerate Plan - FitBuddy"
        }, request)
        
    latest_plan = crud.get_latest_workout_plan(db, user_id=user.id)
    if not latest_plan:
        return render_template("regenerate_plan.html", {
            "user_found": False,
            "lookup_error": "No existing workout plan found to revise.",
            "page_title": "Regenerate Plan - FitBuddy"
        }, request)
        
    old_content = latest_plan.updated_plan or latest_plan.plan_content or latest_plan.original_plan or ""
    
    # Save feedback record
    crud.create_feedback(db, schemas.FeedbackCreate(plan_id=latest_plan.id, feedback_text=feedback_text.strip()))
    
    # Revise plan with AI
    new_plan_text = ai_service.revise_workout_plan(current_plan=old_content, feedback=feedback_text.strip())
    
    # Update workout plan in DB
    latest_plan = crud.update_workout_plan(db, latest_plan, new_plan_text)
    
    return render_template("regenerate_plan.html", {
        "user_found": True,
        "user": user,
        "latest_plan": latest_plan,
        "current_plan_text": old_content,
        "newly_updated_plan": new_plan_text,
        "updated_message": "Your plan has been updated based on your feedback!",
        "lookup_error": None,
        "target_username": user.name,
        "page_title": "Plan Updated - FitBuddy"
    }, request)

# --- Feedback & Plan Revision Routes --- #

async def handle_submit_feedback(
    request: Request,
    user_id: Optional[int],
    plan_id: Optional[int],
    feedback_text: Optional[str],
    feedback: Optional[str],
    db: Session
):
    final_feedback = feedback_text or feedback or ""
    if not final_feedback.strip():
        raise HTTPException(status_code=400, detail="Feedback text cannot be empty.")
        
    db_plan = None
    db_user = None
    
    if plan_id and plan_id > 0:
        db_plan = crud.get_workout_plan(db, plan_id=plan_id)
        if db_plan:
            db_user = crud.get_user(db, user_id=db_plan.user_id)
            
    if not db_plan and user_id and user_id > 0:
        db_user = crud.get_user(db, user_id=user_id)
        db_plan = crud.get_latest_workout_plan(db, user_id=user_id)
        
    if not db_plan:
        raise HTTPException(status_code=404, detail="Original plan not found for this user/plan ID.")
    if not db_user:
        db_user = crud.get_user(db, user_id=db_plan.user_id)
        
    # Save feedback record
    crud.create_feedback(db, schemas.FeedbackCreate(plan_id=db_plan.id, feedback_text=final_feedback))
    
    # Revise plan with Gemini Pro
    current_content = db_plan.updated_plan or db_plan.plan_content or db_plan.original_plan or ""
    new_plan_text = ai_service.revise_workout_plan(
        current_plan=current_content,
        feedback=final_feedback
    )
    
    # Update workout plan
    db_plan = crud.update_workout_plan(db, db_plan, new_plan_text)
    nutrition_tip_text = ai_service.generate_nutrition_tip(goal=db_user.goal if db_user else "wellness")

    accept_header = request.headers.get("accept", "")
    is_ajax = "application/json" in accept_header or request.headers.get("x-requested-with") == "XMLHttpRequest"
    
    if is_ajax:
        return JSONResponse({
            "status": "success",
            "plan_id": db_plan.id,
            "user_id": db_user.id if db_user else user_id,
            "plan": new_plan_text,
            "workout_plan": new_plan_text,
            "nutrition_tip": nutrition_tip_text,
            "message": "Your plan has been updated based on your feedback!"
        })

    return render_template("result.html", {
        "username": db_user.name if db_user else "Athlete",
        "name": db_user.name if db_user else "Athlete",
        "user_id": db_user.id if db_user else user_id,
        "age": db_user.age if db_user else 25,
        "gender": db_user.gender if db_user else "Not Specified",
        "weight": db_user.weight if db_user else 70.0,
        "goal": db_user.goal if db_user else "Wellness",
        "intensity": db_user.intensity if db_user else "Medium",
        "workout_plan": new_plan_text,
        "nutrition_tip": nutrition_tip_text,
        "plan_id": db_plan.id,
        "updated_message": "Your plan has been updated based on your feedback!"
    }, request)

@app.post("/submit-feedback")
async def submit_feedback(
    request: Request,
    user_id: Optional[int] = Form(None),
    plan_id: Optional[int] = Form(None),
    feedback_text: Optional[str] = Form(None),
    feedback: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    return await handle_submit_feedback(request, user_id, plan_id, feedback_text, feedback, db)

@app.post("/update_plan")
async def update_plan_alias(
    request: Request,
    user_id: Optional[int] = Form(None),
    plan_id: Optional[int] = Form(None),
    feedback_text: Optional[str] = Form(None),
    feedback: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    return await handle_submit_feedback(request, user_id, plan_id, feedback_text, feedback, db)

# --- Nutrition Tip API Routes --- #

@app.get("/nutrition-tip")
def get_nutrition_tip_route(goal: str):
    tip = ai_service.generate_nutrition_tip(goal)
    return {"goal": goal, "tip": tip, "nutrition_tip": tip}

@app.get("/nutrition_tip")
def get_nutrition_tip_alias(goal: str):
    tip = ai_service.generate_nutrition_tip(goal)
    return {"goal": goal, "tip": tip, "nutrition_tip": tip}

# --- User Management API Routes --- #

@app.post("/users", response_model=schemas.User)
def create_or_update_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name)
    if db_user:
        db_user = crud.update_user(db, db_user, user)
    else:
        db_user = crud.create_user(db=db, user=user)
    return db_user

@app.get("/users/{user_id}/latest_plan")
def get_user_latest_plan(user_id: int, db: Session = Depends(get_db)):
    db_plan = crud.get_latest_workout_plan(db, user_id=user_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    content = db_plan.updated_plan or db_plan.plan_content or db_plan.original_plan
    return {"plan_id": db_plan.id, "plan_content": content, "original_plan": db_plan.original_plan, "updated_plan": db_plan.updated_plan}

@app.post("/delete-user/{user_id}")
def delete_user_route(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(db, user_id=user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)

@app.delete("/users/{user_id}")
def delete_user_api(user_id: int, db: Session = Depends(get_db)):
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": f"User {user_id} deleted"}
