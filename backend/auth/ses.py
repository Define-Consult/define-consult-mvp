# auth.py (updated code)
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import boto3
import os
import logging
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import auth
from firebase_admin.auth import ActionCodeSettings
from firebase_admin import credentials

load_dotenv()
print(
    f"DEBUG: AWS_SES_SENDER_EMAIL loaded from .env is: '{os.getenv('AWS_SES_SENDER_EMAIL')}'"
)

# --- AWS SES Configuration ---
AWS_REGION = os.getenv("AWS_REGION")
AWS_SES_SENDER_EMAIL = os.getenv("AWS_SES_SENDER_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL")  # Get the new variable

if not all(
    [
        AWS_REGION,
        AWS_SES_SENDER_EMAIL,
        os.getenv("AWS_ACCESS_KEY_ID"),
        os.getenv("AWS_SECRET_ACCESS_KEY"),
        FRONTEND_URL,  # Check for the new variable
    ]
):
    logging.error(
        "FATAL: Required environment variables are not set correctly. Please check your .env file."
    )
    # Default values for safe startup
    AWS_REGION = "us-east-1"
    AWS_SES_SENDER_EMAIL = "your-email@example.com"
    FRONTEND_URL = "http://localhost:3000"

ses_client = boto3.client("ses", region_name=AWS_REGION)


# --- Pydantic Model for the request body ---
class PasswordResetRequest(BaseModel):
    email: EmailStr


# --- API Router ---
router = APIRouter()


@router.post("/send-reset-password", status_code=status.HTTP_200_OK)
async def send_password_reset_email_endpoint(request_body: PasswordResetRequest):
    """
    Sends a password reset email to the specified user via AWS SES.
    It uses the Firebase Admin SDK to generate a secure reset link.
    """
    email = request_body.email
    logging.info(f"Received request to send password reset email to: {email}")

    try:
        # --- NEW: Configure the redirect URL for the password reset link ---
        reset_url = f"{FRONTEND_URL}/reset-password"

        action_code_settings = ActionCodeSettings(
            url=reset_url,
            handle_code_in_app=True,
            # We don't need a dynamic link for this, but it's an option.
            # dynamic_link_domain="your-dynamic-link-domain"
        )

        reset_link = auth.generate_password_reset_link(email, action_code_settings)
        logging.info(f"Generated Firebase password reset link for {email}.")

        subject = "Password Reset Request for Your Define Consult Account"
        body_html = f"""
        <html>
        <head></head>
        <body>
          <h1>Password Reset Request</h1>
          <p>Hello,</p>
          <p>We received a request to reset the password for your account.</p>
          <p>
            Click the link below to reset your password:
          </p>
          <p>
            <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #ffffff; background-color: #007bff; text-decoration: none; border-radius: 5px;">
              Reset Your Password
            </a>
          </p>
          <p>If you did not request a password reset, please ignore this email.</p>
          <p>Thank you,<br>The Define Consult Team</p>
        </body>
        </html>
        """
        body_text = f"Click the link to reset your password: {reset_link}"

        # logging.info(f"DEBUG: About to send email from source: {AWS_SES_SENDER_EMAIL}")

        response = ses_client.send_email(
            Source=AWS_SES_SENDER_EMAIL,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body_text}, "Html": {"Data": body_html}},
            },
        )
        logging.info(
            f"Password reset email sent to {email}. MessageId: {response['MessageId']}"
        )

        return {
            "message": "If the email is registered in our system, a password reset link has been sent."
        }

    except firebase_admin.exceptions.FirebaseError as e:
        logging.warning(f"Firebase user not found for email {email}: {e}")
        return {
            "message": "If the email is registered in our system, a password reset link has been sent."
        }
    except Exception as e:
        logging.error(f"Failed to send email to {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email. Please try again later.",
        )
