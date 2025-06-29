"""
User Profile API endpoints for Define Consult
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Annotated, Optional
import logging

from db.database import get_db
from dependencies import get_current_user_id
from models.models import User
from schemas.user import UserProfile, UserProfileUpdate

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["User Profiles"])


# --- Pydantic Models ---
from pydantic import BaseModel
from enum import Enum


class NotificationPreferences(BaseModel):
    email_digest: bool = True
    slack_alerts: bool = False
    in_app_notifications: bool = True
    marketing_emails: bool = False


class BrandTonePreferences(BaseModel):
    formal: float = 0.5
    friendly: float = 0.5
    professional: float = 0.5
    creative: float = 0.5


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    role_at_company: Optional[str] = None
    industry: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    current_plan_id: Optional[str] = None
    billing_customer_id: Optional[str] = None
    usage_stats: Optional[dict] = None
    notification_preferences: Optional[NotificationPreferences] = None
    brand_tone_preferences: Optional[BrandTonePreferences] = None
    created_at: str
    updated_at: str


class UserProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    role_at_company: Optional[str] = None
    industry: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    notification_preferences: Optional[NotificationPreferences] = None
    brand_tone_preferences: Optional[BrandTonePreferences] = None


# --- Endpoints ---


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Get the current user's profile information
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserProfileResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            company_name=user.company_name,
            role_at_company=user.role_at_company,
            industry=user.industry,
            linkedin_profile_url=user.linkedin_profile_url,
            current_plan_id=user.current_plan_id,
            billing_customer_id=user.billing_customer_id,
            usage_stats=user.usage_stats or {},
            notification_preferences=user.notification_preferences
            or NotificationPreferences().dict(),
            brand_tone_preferences=user.brand_tone_preferences
            or BrandTonePreferences().dict(),
            created_at=user.created_at.isoformat(),
            updated_at=(
                user.updated_at.isoformat()
                if user.updated_at
                else user.created_at.isoformat()
            ),
        )

    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user profile")


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_update: UserProfileUpdateRequest,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Update the current user's profile information
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update fields if provided
        if profile_update.name is not None:
            user.name = profile_update.name
        if profile_update.company_name is not None:
            user.company_name = profile_update.company_name
        if profile_update.role_at_company is not None:
            user.role_at_company = profile_update.role_at_company
        if profile_update.industry is not None:
            user.industry = profile_update.industry
        if profile_update.linkedin_profile_url is not None:
            user.linkedin_profile_url = profile_update.linkedin_profile_url
        if profile_update.notification_preferences is not None:
            user.notification_preferences = (
                profile_update.notification_preferences.dict()
            )
        if profile_update.brand_tone_preferences is not None:
            user.brand_tone_preferences = profile_update.brand_tone_preferences.dict()

        db.commit()
        db.refresh(user)

        return UserProfileResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            company_name=user.company_name,
            role_at_company=user.role_at_company,
            industry=user.industry,
            linkedin_profile_url=user.linkedin_profile_url,
            current_plan_id=user.current_plan_id,
            billing_customer_id=user.billing_customer_id,
            usage_stats=user.usage_stats or {},
            notification_preferences=user.notification_preferences
            or NotificationPreferences().dict(),
            brand_tone_preferences=user.brand_tone_preferences
            or BrandTonePreferences().dict(),
            created_at=user.created_at.isoformat(),
            updated_at=(
                user.updated_at.isoformat()
                if user.updated_at
                else user.created_at.isoformat()
            ),
        )

    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")


@router.delete("/me")
async def delete_my_account(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Delete the current user's account (soft delete for GDPR compliance)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Soft delete - mark as inactive but retain for audit/billing
        user.is_active = False
        user.email = f"deleted_{user.id}@deleted.com"  # Anonymize email
        user.name = "Deleted User"
        user.company_name = None
        user.linkedin_profile_url = None
        user.avatar_url = None
        user.notification_preferences = {}
        user.brand_tone_preferences = {}

        db.commit()

        return {"message": "Account deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting user account: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user account")


# --- Test Endpoints (No Auth Required) ---


@router.get("/test/me", response_model=UserProfileResponse)
async def get_test_user_profile():
    """
    Get test user profile (no auth required for development)
    """
    return UserProfileResponse(
        id="rNyWBYC5UjXaufA0h94UVV34hok2",
        email="demo@defineconsult.co",
        name="Demo User",
        avatar_url="https://via.placeholder.com/150",
        company_name="Define Consult Demo",
        role_at_company="Product Manager",
        industry="AI/SaaS",
        linkedin_profile_url="https://linkedin.com/in/demouser",
        current_plan_id="pro",
        billing_customer_id="cus_demo123",
        usage_stats={
            "total_agent_actions_this_month": 150,
            "last_login": "2024-12-29T10:00:00Z",
        },
        notification_preferences=NotificationPreferences().dict(),
        brand_tone_preferences=BrandTonePreferences().dict(),
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-12-29T10:00:00Z",
    )


@router.put("/test/me", response_model=UserProfileResponse)
async def update_test_user_profile(profile_update: UserProfileUpdateRequest):
    """
    Update test user profile (no auth required for development)
    """
    # In a real implementation, this would update the database
    # For testing, we just return the updated values
    return UserProfileResponse(
        id="test-user-123",
        email="test@example.com",
        name=profile_update.name or "Test User",
        avatar_url="https://via.placeholder.com/150",
        company_name=profile_update.company_name or "Test Company",
        role_at_company=profile_update.role_at_company or "Product Manager",
        industry=profile_update.industry or "SaaS",
        linkedin_profile_url=profile_update.linkedin_profile_url
        or "https://linkedin.com/in/testuser",
        current_plan_id="pro",
        billing_customer_id="cus_test123",
        usage_stats={
            "total_agent_actions_this_month": 150,
            "last_login": "2024-12-29T10:00:00Z",
        },
        notification_preferences=(
            profile_update.notification_preferences or NotificationPreferences()
        ).dict(),
        brand_tone_preferences=(
            profile_update.brand_tone_preferences or BrandTonePreferences()
        ).dict(),
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-12-29T10:00:00Z",
    )
