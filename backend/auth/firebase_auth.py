"""
Firebase Authentication and OAuth Management.

This module handles:
- Firebase user creation for OAuth providers (Google, etc.)
- Firebase Admin SDK operations
- OAuth user synchronization with Firebase

Email-related functionality is handled in mail.py for proper separation of concerns.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import logging
import firebase_admin
from firebase_admin import auth


# --- Pydantic Models ---
class FirebaseUserRequest(BaseModel):
    email: EmailStr
    name: str = None
    avatar_url: str = None
    provider: str
    provider_id: str


class GoogleUserRequest(BaseModel):
    email: EmailStr
    name: str | None = None
    avatar_url: str | None = None
    provider: str = "google"
    provider_id: str


# --- Router ---
firebase_router = APIRouter(prefix="/auth", tags=["Firebase Authentication"])


@firebase_router.post("/create-or-get-firebase-user", status_code=status.HTTP_200_OK)
async def create_or_get_firebase_user(request: FirebaseUserRequest):
    """
    Creates or gets a Firebase user for OAuth providers (like Google).
    This is needed because OAuth users need to exist in Firebase for our auth system.
    """
    try:
        # Try to get the user first
        try:
            firebase_user = auth.get_user_by_email(request.email)
            logging.info(
                f"Firebase user already exists for {request.email}: {firebase_user.uid}"
            )
            return {
                "firebase_uid": firebase_user.uid,
                "email": firebase_user.email,
                "status": "existing",
            }
        except auth.UserNotFoundError:
            # User doesn't exist, create them
            logging.info(f"Creating new Firebase user for {request.email}")

            firebase_user = auth.create_user(
                email=request.email,
                display_name=request.name,
                photo_url=request.avatar_url,
                email_verified=True,  # OAuth users are pre-verified
            )
            logging.info(
                f"Created Firebase user for {request.email}: {firebase_user.uid}"
            )

            return {
                "firebase_uid": firebase_user.uid,
                "email": firebase_user.email,
                "status": "created",
            }

    except Exception as e:
        logging.error(f"Error creating/getting Firebase user for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create/get Firebase user: {e}",
        )


@firebase_router.get("/test-firebase", status_code=status.HTTP_200_OK)
async def test_firebase_connection():
    """
    Test endpoint to verify Firebase Admin SDK is working.
    """
    try:
        # Try to list some users (limited to 1 to avoid large responses)
        users = auth.list_users(max_results=1)

        return {
            "message": "Firebase connection successful",
            "user_count": len(users.users) if users.users else 0,
            "firebase_project": "define-consult",
        }
    except Exception as e:
        logging.error(f"Firebase connection test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Firebase connection failed: {e}",
        )
