from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends
import logging
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import firebase_admin
from firebase_admin import credentials, auth

from celery_worker import celery_app
from sqlalchemy.orm import Session

from db.database import Base, engine

from dependencies import get_db, get_current_user_id

# Routers
from auth.mail import auth_router
from auth.firebase_auth import firebase_router
from api.users.users import router as users_router
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
