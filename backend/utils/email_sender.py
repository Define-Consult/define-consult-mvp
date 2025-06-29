import os
from mailjet_rest import Client
from dotenv import load_dotenv
import logging
from typing import Optional


load_dotenv()

# --- Configuration ---
api_key = os.getenv("MAILJET_API_KEY")
api_secret = os.getenv("MAILJET_SECRET_KEY")
sender_email = os.getenv("MAILJET_SENDER_EMAIL")
# Add a placeholder for your logo URL
LOGO_URL = os.getenv(
    "LOGO_URL",
    "https://define-consult-assets.s3.eu-north-1.amazonaws.com/define-consult-logo.png",
)

# Initialize Mailjet client
mailjet = None
if api_key and api_secret:
    try:
        mailjet = Client(auth=(api_key, api_secret), version="v3.1")
    except Exception as e:
        logging.error(f"Failed to initialize Mailjet client: {e}")
else:
    logging.warning("Mailjet credentials not found. Email sending is disabled.")


def send_email_with_mailjet(recipient_email: str, subject: str, html_content: str):
    """
    Sends an email using the Mailjet API.
    """
    if not mailjet:
        logging.error(
            f"Cannot send email to {recipient_email}: Mailjet client is not initialized."
        )
        logging.error(
            "Please check MAILJET_API_KEY and MAILJET_SECRET_KEY in your .env file"
        )
        return False

    if not sender_email:
        logging.error("Sender email not configured in .env.")
        logging.error("Please set MAILJET_SENDER_EMAIL in your .env file")
        return False

    logging.info(f"Attempting to send email to {recipient_email} from {sender_email}")

    data = {
        "Messages": [
            {
                "From": {"Email": sender_email, "Name": "Shaq from Define Consult"},
                "To": [{"Email": recipient_email, "Name": "User"}],
                "Subject": subject,
                "HTMLPart": html_content,
            }
        ]
    }

    try:
        logging.info(f"Sending email via Mailjet API...")
        result = mailjet.send.create(data=data)
        logging.info(f"Mailjet API response status: {result.status_code}")

        if result.status_code == 200:
            logging.info(f"Email sent successfully to {recipient_email} via Mailjet.")
            logging.info(f"Mailjet response: {result.json()}")
            return True
        else:
            logging.error(
                f"Failed to send email to {recipient_email}. Status: {result.status_code}"
            )
            logging.error(f"Mailjet error response: {result.json()}")
            return False
    except Exception as e:
        logging.error(f"An error occurred while sending email via Mailjet: {e}")
        logging.error(f"Exception type: {type(e).__name__}")
        return False


def send_welcome_email(recipient_email: str, verification_link: str):
    """
    Sends a welcome and email verification email with a beautiful template
    tailored to the product management and startup audience.
    """
    subject = "Welcome to Define Consult! Let's elevate your product strategy."

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 20px 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); border: 1px solid #e0e0e0; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 1px solid #e0e0e0; }}
            .header img {{ max-width: 150px; height: auto; }}
            .content {{ padding: 30px 0; color: #333333; line-height: 1.6; }}
            .content h1 {{ font-size: 28px; color: #1a1a1a; margin-top: 0; }}
            .content p {{ font-size: 16px; margin: 15px 0; }}
            .button {{ text-align: center; margin: 30px 0; }}
            .button a {{ display: inline-block; padding: 15px 25px; background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 18px; }}
            .footer {{ text-align: center; font-size: 12px; color: #999999; padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{LOGO_URL}" alt="Define Consult Logo">
            </div>
            <div class="content">
                <h1>Welcome to Define Consult!</h1>
                <p>Welcome aboard! We're excited to empower your product team and help you turn raw conversational data into structured insights and actionable plans.</p>
                <p>Define Consult leverages autonomous AI agents to analyze meetings, customer interviews, and strategic discussions to drive faster product-market fit and sustained growth.</p>
                <p>To unlock the full power of your AI-powered co-pilot, please verify your email address by clicking the button below:</p>
                <div class="button">
                    <a href="{verification_link}">Verify My Email Address</a>
                </div>
                <p>If you didn't create an account, no worries! Just ignore this email.</p>
                <p>The Define Consult Team</p>
            </div>
            <div class="footer">
                <p>&copy; {2025} Define Consult. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email_with_mailjet(recipient_email, subject, html_content)


def send_password_reset_email(recipient_email: str, reset_link: str):
    """
    Sends a password reset email with a beautiful template.
    """
    subject = "Define Consult: Reset Your Password"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 20px 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); border: 1px solid #e0e0e0; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 1px solid #e0e0e0; }}
            .header img {{ max-width: 150px; height: auto; }}
            .content {{ padding: 30px 0; color: #333333; line-height: 1.6; }}
            .content h1 {{ font-size: 28px; color: #1a1a1a; margin-top: 0; }}
            .content p {{ font-size: 16px; margin: 15px 0; }}
            .button {{ text-align: center; margin: 30px 0; }}
            .button a {{ display: inline-block; padding: 15px 25px; background-color: #ff5722; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 18px; }}
            .footer {{ text-align: center; font-size: 12px; color: #999999; padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{LOGO_URL}" alt="Define Consult Logo">
            </div>
            <div class="content">
                <h1>Password Reset Request</h1>
                <p>You recently requested to reset the password for your Define Consult account. Click the button below to proceed:</p>
                <div class="button">
                    <a href="{reset_link}">Reset My Password</a>
                </div>
                <p>This link is valid for a limited time. If you did not request this password reset, please ignore this email.</p>
                <p>The Define Consult Team</p>
            </div>
            <div class="footer">
                <p>&copy; {2025} Define Consult. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email_with_mailjet(recipient_email, subject, html_content)
