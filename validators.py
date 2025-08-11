from pydantic import BaseModel, Field
from typing import List, Optional

class UserRequest(BaseModel):
    age: Optional[int] = Field(default=None, ge=0, le=120)
    weight_kg: Optional[float] = Field(default=None, ge=1, le=400)
    height_cm: Optional[float] = Field(default=None, ge=30, le=250)
    sex: Optional[str] = Field(default=None)
    pain_level: Optional[int] = Field(default=None, ge=0, le=10)
    notes: Optional[str] = None  # Optional field for user notes
    symptoms: List[str]
    allergies: List[str] = []
    conditions: List[str] = []

class AIRecommendation(BaseModel):
    drug_name: str
    dosage: str
    frequency: str
    side_effects: str

class AITriage(BaseModel):
    triage_alert: str
    message: str

class APIError(BaseModel):
    error: str
