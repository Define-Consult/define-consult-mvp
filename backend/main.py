from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
import logging
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import firebase_admin
from firebase_admin import credentials, auth
import requests

from celery_worker import celery_app
from sqlalchemy.orm import Session

from db.database import Base, engine

from dependencies import get_db, get_current_user_id

# Routers
from auth.mail import auth_router
from auth.firebase_auth import firebase_router
from api.users.users import router as users_router
from api.users.profile import router as profile_router
from api.billing.billing import router as billing_router
from api.plans.plans import router as plans_router
from api.features.user_whisperer import router as user_whisperer_router
from api.features.transcripts import router as transcripts_router
from api.agents.user_whisperer import router as user_whisperer_agent_router
from api.agents.market_maven import router as market_maven_agent_router
from api.agents.narrative_architect import router as narrative_architect_agent_router

# --- Logger Initialization ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Define Consult Backend API",
    description="API for user management, authentication, and core data processing.",
)

# --- CORS Middleware ---
origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Firebase Admin SDK Initialization ---
try:
    cred = credentials.Certificate("firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")


# --- Database Startup Event ---
@app.on_event("startup")
def on_startup():
    """
    Create all database tables when the application starts up.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


# --- API Routers ---
app.include_router(auth_router, prefix="/api/v1")
app.include_router(firebase_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(plans_router, prefix="/api/v1")
app.include_router(user_whisperer_router, prefix="/api/v1")
app.include_router(transcripts_router, prefix="/api/v1")
app.include_router(user_whisperer_agent_router, prefix="/api/v1")
app.include_router(market_maven_agent_router, prefix="/api/v1")
app.include_router(narrative_architect_agent_router, prefix="/api/v1")


# --- General API Endpoints ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to Define Consult API"}


@app.get("/health")
async def health_check():
    """General health check endpoint"""
    return {"status": "healthy", "service": "Define Consult API"}


@app.get("/api/v1/health")
async def api_health_check():
    """API v1 health check endpoint"""
    return {"status": "healthy", "version": "v1"}


@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get dashboard statistics for the current user"""
    try:
        # Get stats from database
        # For now, return mock data - these would be real queries in production
        return {
            "total_transcripts": 0,
            "completed_transcripts": 0,
            "active_competitor_watches": 0,
            "recent_competitor_updates": 0,
            "generated_content_pieces": 0,
            "agent_activities_today": 0,
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve dashboard statistics"
        )


@app.get("/protected")
async def protected_route(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    A route that requires authentication and a database connection.
    """
    return {"message": f"Hello, authenticated user! Your UID is {user_id}"}


@app.get("/status")
async def get_status():
    """
    Check if the API is running.
    """
    return {"status": "ok"}


@app.get("/api/v1/agents/health")
async def get_all_agents_health():
    """Get health status of all AI agents"""
    try:
        health_status = {
            "user_whisperer": False,
            "market_maven": False,
            "narrative_architect": False,
        }

        # Check each agent's health internally
        try:
            # These are internal health checks - we can call the endpoints directly
            base_url = "http://localhost:8000"

            # Check User Whisperer
            try:
                response = requests.get(
                    f"{base_url}/api/v1/agents/user-whisperer/health", timeout=5
                )
                health_status["user_whisperer"] = response.status_code == 200
            except:
                health_status["user_whisperer"] = False

            # Check Market Maven
            try:
                response = requests.get(
                    f"{base_url}/api/v1/agents/market-maven/health", timeout=5
                )
                health_status["market_maven"] = response.status_code == 200
            except:
                health_status["market_maven"] = False

            # Check Narrative Architect
            try:
                response = requests.get(
                    f"{base_url}/api/v1/agents/narrative-architect/health", timeout=5
                )
                health_status["narrative_architect"] = response.status_code == 200
            except:
                health_status["narrative_architect"] = False

        except Exception as e:
            logger.error(f"Error checking agent health: {e}")

        return health_status

    except Exception as e:
        logger.error(f"Error in agents health check: {e}")
        raise HTTPException(status_code=500, detail="Failed to check agent health")


# --- Test Endpoints (No Auth Required) ---
@app.get("/api/v1/test/dashboard/stats")
async def get_test_dashboard_stats():
    """Get test dashboard statistics (no auth required)"""
    return {
        "total_transcripts": 5,
        "completed_transcripts": 3,
        "active_competitor_watches": 2,
        "recent_competitor_updates": 7,
        "generated_content_pieces": 12,
        "agent_activities_today": 8,
    }


@app.get("/api/v1/test/agents/health")
async def get_test_all_agents_health():
    """Get test health status of all AI agents (no auth required)"""
    return {
        "user_whisperer": True,
        "market_maven": True,
        "narrative_architect": True,
    }


@app.get("/api/v1/test/agents/market-maven/updates")
async def get_test_market_maven_updates():
    """Get test market maven updates (no auth required)"""
    return [
        {
            "id": "test-1",
            "competitor_name": "TechCorp",
            "title": "New AI Feature Announced",
            "detected_at": "2024-12-29T10:00:00Z",
            "status": "new",
        },
        {
            "id": "test-2",
            "competitor_name": "InnovateCo",
            "title": "Pricing Strategy Update",
            "detected_at": "2024-12-29T08:30:00Z",
            "status": "new",
        },
    ]


@app.get("/api/v1/test/users/profile")
async def get_test_user_profile():
    """Get test user profile (no auth required)"""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "avatar_url": None,
        "company_name": "Test Company",
        "role_at_company": "Product Manager",
        "industry": "SaaS",
        "linkedin_profile_url": None,
        "current_plan_id": "pro",
        "billing_customer_id": "cus_test123",
        "usage_stats": {
            "total_agent_actions_this_month": 25,
            "last_login": "2024-12-29T10:00:00Z",
        },
        "notification_preferences": {
            "email_digest": True,
            "slack_alerts": False,
            "in_app_notifications": True,
            "marketing_emails": False,
        },
        "brand_tone_preferences": {
            "formal": 0.3,
            "friendly": 0.7,
            "professional": 0.6,
            "creative": 0.4,
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-12-29T10:00:00Z",
    }


@app.get("/api/v1/test/billing/plans")
async def get_test_billing_plans():
    """Get test billing plans (no auth required)"""
    return [
        {
            "id": "free",
            "name": "Free",
            "price_usd_per_month": 0.0,
            "monthly_agent_action_limit": 25,
            "stripe_price_id": "price_test_free",
            "is_metered_billing": False,
            "available_integrations": ["slack"],
            "priority_support": False,
            "is_team_plan": False,
        },
        {
            "id": "pro",
            "name": "Pro",
            "price_usd_per_month": 74.0,
            "monthly_agent_action_limit": 500,
            "stripe_price_id": "price_test_pro",
            "is_metered_billing": False,
            "available_integrations": ["slack", "zoom", "notion"],
            "priority_support": True,
            "is_team_plan": False,
        },
        {
            "id": "team",
            "name": "Team",
            "price_usd_per_month": 349.0,
            "monthly_agent_action_limit": 5000,
            "stripe_price_id": "price_test_team",
            "is_metered_billing": False,
            "available_integrations": ["slack", "zoom", "notion", "jira", "zendesk"],
            "priority_support": True,
            "is_team_plan": True,
        },
    ]


@app.get("/api/v1/test/billing/usage")
async def get_test_billing_usage():
    """Get test billing usage (no auth required)"""
    return {
        "current_plan": "Pro",
        "agent_actions_used": 235,
        "agent_actions_limit": 500,
        "billing_period_start": "2024-12-01T00:00:00Z",
        "billing_period_end": "2024-12-31T23:59:59Z",
        "estimated_cost": 74.0,
    }


@app.post("/api/v1/demo/setup-user")
async def setup_demo_user(db: Annotated[Session, Depends(get_db)]):
    """Setup/create the demo user account for testing"""
    from models.models import User

    demo_email = "demo@defineconsult.co"
    firebase_uid = "demo-user-defineconsult"

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == demo_email).first()

    if existing_user:
        # Update existing user
        existing_user.name = "Demo User"
        existing_user.company_name = "Define Consult Demo"
        existing_user.role_at_company = "Product Manager"
        existing_user.industry = "AI/SaaS"
        existing_user.linkedin_profile_url = "https://linkedin.com/in/defineconsultdemo"
        existing_user.usage_stats = {
            "total_agent_actions_this_month": 45,
            "last_login": "2024-12-29T15:30:00Z",
        }
        existing_user.notification_preferences = {
            "email_digest": True,
            "slack_alerts": True,
            "in_app_notifications": True,
            "marketing_emails": False,
        }
        existing_user.brand_tone_preferences = {
            "formal": 0.3,
            "friendly": 0.7,
            "professional": 0.8,
            "creative": 0.6,
        }
        db.commit()
        db.refresh(existing_user)
        return {
            "message": "Demo user updated successfully",
            "user_id": existing_user.id,
        }
    else:
        # Create new user
        new_user = User(
            firebase_uid=firebase_uid,
            email=demo_email,
            name="Demo User",
            company_name="Define Consult Demo",
            role_at_company="Product Manager",
            industry="AI/SaaS",
            linkedin_profile_url="https://linkedin.com/in/defineconsultdemo",
            usage_stats={
                "total_agent_actions_this_month": 45,
                "last_login": "2024-12-29T15:30:00Z",
            },
            notification_preferences={
                "email_digest": True,
                "slack_alerts": True,
                "in_app_notifications": True,
                "marketing_emails": False,
            },
            brand_tone_preferences={
                "formal": 0.3,
                "friendly": 0.7,
                "professional": 0.8,
                "creative": 0.6,
            },
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Demo user created successfully", "user_id": new_user.id}
