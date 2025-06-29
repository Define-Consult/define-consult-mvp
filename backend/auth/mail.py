"""
Email-related authentication endpoints.

This module handles all email operations including:
- Password reset emails
- Verification emails
- Test emails for debugging

Firebase and OAuth functionality is handled in firebase_auth.py for proper separation of concerns.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import os
import logging
from dotenv import load_dotenv

from firebase_admin import auth
from firebase_admin.auth import ActionCodeSettings

from utils.email_sender import (
    send_password_reset_email,
    send_welcome_email,
    send_email_with_mailjet,
)

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")
LOGO_URL = os.getenv(
    "LOGO_URL",
    "https://define-consult-assets.s3.eu-north-1.amazonaws.com/define-consult-logo.png",
)


# --- Pydantic Models for Email Operations ---
class EmailRequest(BaseModel):
    email: EmailStr


def get_action_code_settings(redirect_path: str):
    """
    Generates the ActionCodeSettings for email actions with a dynamic redirect URL.
    """
    if not FRONTEND_URL:
        logging.error(
            "FRONTEND_URL not set in .env. Cannot generate email action links."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Frontend URL is not configured.",
        )

    return ActionCodeSettings(
        url=f"{FRONTEND_URL}{redirect_path}",
        handle_code_in_app=True,
    )


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/send-reset-password", status_code=status.HTTP_200_OK)
async def send_reset_password(request: EmailRequest):
    """
    Sends a password reset email using Mailjet.
    """
    try:
        reset_link = auth.generate_password_reset_link(
            request.email,
            action_code_settings=get_action_code_settings("/reset-password"),
        )

        email_sent = send_password_reset_email(request.email, reset_link)

        if not email_sent:
            logging.error(
                f"Failed to send password reset email via Mailjet to {request.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email.",
            )

        logging.info(f"Password reset email sent successfully to {request.email}")
        return {"message": "Password reset email sent successfully."}

    except auth.UserNotFoundError:
        logging.warning(
            f"Password reset requested for non-existent email: {request.email}"
        )
        # Return success message even for non-existent users for security
        return {
            "message": "If a user with that email exists, a password reset link has been sent."
        }
    except Exception as e:
        logging.error(f"Error sending password reset email to {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while sending the password reset email.",
        )


@auth_router.post("/send-verification-email", status_code=status.HTTP_200_OK)
async def send_verification_email(request: EmailRequest):
    """
    Sends a custom verification/welcome email to a user.
    """
    try:
        user = auth.get_user_by_email(request.email)

        if user.email_verified:
            return {"message": "Email is already verified."}

        verification_link = auth.generate_email_verification_link(
            user.email, action_code_settings=get_action_code_settings("/dashboard")
        )

        email_sent = send_welcome_email(user.email, verification_link)

        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email.",
            )

        return {"message": "Verification email sent successfully."}

    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    except Exception as e:
        logging.error(f"Error sending verification email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )


@auth_router.post("/test-email", status_code=status.HTTP_200_OK)
async def test_email_configuration(request: EmailRequest):
    """
    Test endpoint to debug email configuration.
    """
    try:
        logging.info(f"Testing email configuration for {request.email}")

        # Test email content
        subject = "Test Email from Define Consult"
        html_content = """
        <html>
        <body>
            <h1>Test Email</h1>
            <p>This is a test email to verify the email configuration.</p>
            <p>If you receive this, email sending is working correctly!</p>
        </body>
        </html>
        """

        email_sent = send_email_with_mailjet(request.email, subject, html_content)

        if email_sent:
            return {"message": "Test email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test email",
            )

    except Exception as e:
        logging.error(f"Error in test email endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test email failed: {e}",
        )
