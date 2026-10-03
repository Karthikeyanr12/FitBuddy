from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class FeedbackBase(BaseModel):
    feedback_text: str

class FeedbackCreate(FeedbackBase):
    plan_id: int

class Feedback(FeedbackBase):
    id: int
    plan_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanBase(BaseModel):
    plan_content: Optional[str] = None
    original_plan: Optional[str] = None
    updated_plan: Optional[str] = None

class WorkoutPlanCreate(WorkoutPlanBase):
    pass

class WorkoutPlan(WorkoutPlanBase):
    id: int
    user_id: int
    created_at: datetime
    feedbacks: List[Feedback] = []
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    name: str
    age: int
    gender: Optional[str] = "Not Specified"
    weight: float
    goal: str
    intensity: str

class UserCreate(UserBase):
    id: Optional[int] = None

class User(UserBase):
    id: int
    plans: List[WorkoutPlan] = []
    model_config = ConfigDict(from_attributes=True)


# PDF Schemas
class UserInput(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    name: Optional[str] = None
    age: int
    weight: float
    goal: str
    intensity: str

class FeedbackRequest(BaseModel):
    feedback: str

class WorkoutRequest(BaseModel):
    goal: str
    intensity: str
