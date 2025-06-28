from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, File, UploadFile
import logging
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Annotated
import firebase_admin
from firebase_admin import credentials, auth
import os
import time

from celery import Celery 

from db.database import Base, engine, get_db
from sqlalchemy.orm import Session

from models.models import User, Plan 

from schemas.user import UserCreate, UserResponse, UserUpdate
from schemas.plans import PlanCreate, PlanResponse, PlanUpdate

from users.auth import router as auth_router
from agents.user_whisperer import create_user_whisperer_chain


# --- Logger Initialization ---
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Define Consult Backend API",
    description="API for user management, authentication, and core data processing."
)
user_whisperer_chain = create_user_whisperer_chain()

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

# --- Celery Configuration ---
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery_app.task(name="process_transcript_task")
def process_transcript_task(file_content_id: str):
    """
    Simulates processing a transcript in a background task.
    """
    logger.info(f"Received task to process file with ID: {file_content_id}")
    time.sleep(10) # Simulate a long-running task
    logger.info(f"Finished processing file with ID: {file_content_id}")
    return {"status": "completed", "file_id": file_content_id}


# --- Database Startup Event ---
@app.on_event("startup")
def on_startup():
    """
    Create all database tables when the application starts up.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


# --- Authentication Logic ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Dependency to get the current user's ID from a Firebase ID token.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- API Routers ---
# User endpoints directly on app, as per last request
app.include_router(auth_router)

# NEW: Router for Plans
plan_router = APIRouter(prefix="/api/v1/plans", tags=["Plans"])
app.include_router(plan_router)


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

@app.post("/user-whisperer/generate-user-story")
async def generate_user_story(
    feedback: dict, 
):
    """
    Endpoint to trigger the User Whisperer agent to generate a user story from feedback.
    """
    user_feedback = feedback.get("user_feedback")
    if not user_feedback:
        raise HTTPException(status_code=400, detail="User feedback is required.")

    print(f"Received feedback: {user_feedback[:50]}...")

    try:
        result = user_whisperer_chain.invoke({"user_feedback": user_feedback})
        return {"generated_output": result}
    except Exception as e:
        print(f"Error invoking chain: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate output.")

@app.post("/api/v1/upload-transcript")
async def upload_transcript(file: UploadFile = File(...)):
    """
    Dispatches a background task to process a transcript file.
    """
    file_content_id = f"file_{int(time.time())}"
    
    process_transcript_task.delay(file_content_id)
    
    logger.info(f"Transcript uploaded and task dispatched for file ID: {file_content_id}")
    
    return {"message": "Transcript uploaded successfully. Processing will begin shortly.", "file_id": file_content_id}


# --- User Profile Endpoints ---
@app.post("/api/v1/users", status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    user_data: UserCreate, db: Annotated[Session, Depends(get_db)]
):
    """
    Endpoint to create a new user profile in the database.
    """
    existing_user = (
        db.query(User).filter(User.firebase_uid == user_data.firebase_uid).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this UID already exists",
        )

    # Use UserCreate to instantiate the database model
    new_user_profile = User(**user_data.model_dump())
    db.add(new_user_profile)
    db.commit()
    db.refresh(new_user_profile)

    return new_user_profile

@app.get("/api/v1/users/{firebase_uid}", response_model=UserResponse)
async def get_user_by_firebase_uid(
    firebase_uid: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves a single user from the database by their Firebase UID.
    """
    db_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return db_user

@app.patch("/api/v1/users/{firebase_uid}", response_model=UserResponse)
async def update_user_by_firebase_uid(
    firebase_uid: str,
    user_data: UserUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Updates an existing user's details in the database by their Firebase UID.
    """
    db_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User with firebase_uid: {firebase_uid} updated successfully.")
    
    return db_user

@app.delete("/api/v1/users/{firebase_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_firebase_uid(
    firebase_uid: str,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Deletes a user from the database by their Firebase UID.
    """
    db_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    db.delete(db_user)
    db.commit()

    logger.info(f"User with firebase_uid: {firebase_uid} deleted successfully.")
    
    return


# ---  Plan Endpoints ---
@app.post("/api/v1/plans", status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PlanCreate, db: Annotated[Session, Depends(get_db)]
):
    """
    Creates a new plan in the database.
    """
    new_plan = Plan(**plan_data.model_dump())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

@app.get("/api/v1/plans", response_model=list[PlanResponse])
async def get_all_plans(db: Annotated[Session, Depends(get_db)]):
    """
    Retrieves all plans from the database.
    """
    plans = db.query(Plan).all()
    return plans

@app.get("/api/v1/plans/{plan_id}", response_model=PlanResponse)
async def get_plan_by_id(
    plan_id: int, db: Annotated[Session, Depends(get_db)]
):
    """
    Retrieves a single plan by its ID.
    """
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return db_plan

@app.patch("/api/v1/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Updates an existing plan's details.
    """
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    for key, value in plan_data.model_dump(exclude_unset=True).items():
        setattr(db_plan, key, value)
    
    db.commit()
    db.refresh(db_plan)
    logger.info(f"Plan with ID: {plan_id} updated successfully.")
    return db_plan

@app.delete("/api/v1/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int, db: Annotated[Session, Depends(get_db)]
):
    """
    Deletes a plan from the database.
    """
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    db.delete(db_plan)
    db.commit()
    logger.info(f"Plan with ID: {plan_id} deleted successfully.")
    return