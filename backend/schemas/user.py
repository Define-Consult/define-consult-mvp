from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict

class UserCreate(BaseModel):
    firebase_uid: str = Field(..., description="The unique Firebase User ID.")
    email: EmailStr
    name: str | None = None
    avatar_url: str | None = None
    company_name: str | None = None
    role_at_company: str | None = None
    industry: str | None = None
    linkedin_profile_url: str | None = None
    current_plan_id: int | None = None
    billing_customer_id: str | None = None
    usage_stats: dict | None = None
    notification_preferences: dict | None = None
    brand_tone_preferences: dict | None = None

class UserResponse(BaseModel):
    id: int
    firebase_uid: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    role_at_company: Optional[str] = None
    industry: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    current_plan_id: Optional[int] = None
    billing_customer_id: Optional[str] = None
    usage_stats: Optional[Dict] = None
    notification_preferences: Optional[Dict] = None
    brand_tone_preferences: Optional[Dict] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    role_at_company: Optional[str] = None
    industry: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    current_plan_id: Optional[int] = None
    billing_customer_id: Optional[str] = None
    usage_stats: Optional[Dict] = None
    notification_preferences: Optional[Dict] = None
    brand_tone_preferences: Optional[Dict] = None