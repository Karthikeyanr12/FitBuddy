from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper storage functions aligned with PDF architecture
def save_user(user_id: int = None, name: str = "", age: int = 0, weight: float = 0.0, goal: str = "", intensity: str = "", gender: str = "Not Specified"):
    db = SessionLocal()
    try:
        import models
        existing = None
        if user_id:
            existing = db.query(models.User).filter_by(id=user_id).first()
        if not existing and name:
            existing = db.query(models.User).filter_by(name=name).first()
            
        if existing:
            existing.name = name or existing.name
            existing.age = age or existing.age
            existing.weight = weight or existing.weight
            existing.goal = goal or existing.goal
            existing.intensity = intensity or existing.intensity
            if gender and gender != "Not Specified":
                existing.gender = gender
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_user = models.User(
                id=user_id if (user_id and user_id > 0) else None,
                name=name,
                age=age,
                gender=gender,
                weight=weight,
                goal=goal,
                intensity=intensity
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
    finally:
        db.close()

def save_plan(user_id: int, plan: str):
    db = SessionLocal()
    try:
        import models
        workout = models.WorkoutPlan(
            user_id=user_id,
            plan_content=plan,
            original_plan=plan
        )
        db.add(workout)
        db.commit()
        db.refresh(workout)
        return workout
    finally:
        db.close()

def update_plan(user_id: int, updated_text: str):
    db = SessionLocal()
    try:
        import models
        workout = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.user_id == user_id).order_by(models.WorkoutPlan.id.desc()).first()
        if workout:
            workout.updated_plan = updated_text
            workout.plan_content = updated_text
            db.commit()
            db.refresh(workout)
            return workout
        return None
    finally:
        db.close()

def get_original_plan(user_id: int):
    db = SessionLocal()
    try:
        import models
        plan = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.user_id == user_id).order_by(models.WorkoutPlan.id.asc()).first()
        return plan.original_plan if plan else None
    finally:
        db.close()

def get_user(user_id: int):
    db = SessionLocal()
    try:
        import models
        return db.query(models.User).filter(models.User.id == user_id).first()
    finally:
        db.close()

def get_all_users():
    db = SessionLocal()
    try:
        import models
        return db.query(models.User).all()
    finally:
        db.close()

def get_all_plans():
    db = SessionLocal()
    try:
        import models
        return db.query(models.WorkoutPlan).all()
    finally:
        db.close()

def delete_user(user_id: int):
    db = SessionLocal()
    try:
        import models
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    finally:
        db.close()

def get_admin_password(db: SessionLocal = None):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    try:
        import models
        setting = db.query(models.AdminSetting).filter_by(key="admin_password").first()
        if not setting:
            setting = models.AdminSetting(key="admin_password", value="1234")
            db.add(setting)
            db.commit()
            db.refresh(setting)
        return setting.value
    finally:
        if should_close:
            db.close()

def set_admin_password(new_password: str, db: SessionLocal = None):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    try:
        import models
        setting = db.query(models.AdminSetting).filter_by(key="admin_password").first()
        if not setting:
            setting = models.AdminSetting(key="admin_password", value=new_password)
            db.add(setting)
        else:
            setting.value = new_password
        db.commit()
        return True
    finally:
        if should_close:
            db.close()

