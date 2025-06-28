# Load environment variables
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
import logging
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Annotated
import firebase_admin
from firebase_admin import credentials, auth
import os

from db.database import Base, engine, get_db
from sqlalchemy.orm import Session

from models.models import User
from schemas.user import UserCreate, UserResponse, UserUpdate

from users.auth import router as auth_router
from agents.user_whisperer import create_user_whisperer_chain


user_whisperer_chain = create_user_whisperer_chain()


# Initialize FastAPI app
app = FastAPI()

app.include_router(auth_router)

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


# --- Pydantic Model for creating a user profile ---
class UserProfileCreate(BaseModel):
    firebase_uid: str
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


# --- User Profile Endpoints ---
user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    user_data: UserProfileCreate, db: Annotated[Session, Depends(get_db)]
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

    new_user_profile = User(**user_data.model_dump())

    db.add(new_user_profile)
    db.commit()
    db.refresh(new_user_profile)

    return new_user_profile


app.include_router(user_router)


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


# --- Status Endpoint ---
@app.get("/status")
async def get_status():
    """
    Check if the API is running.
    """
    return {"status": "ok"}


# --- AI Agent Endpoints ---
@app.post("/user-whisperer/generate-user-story")
async def generate_user_story(
    feedback: dict,  # Expects a JSON body like {"user_feedback": "..."}
    # TODO:I'll add the user authentication dependency later
    # user_id: Annotated[str, Depends(get_current_user_id)]
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


logger = logging.getLogger(__name__)

@app.post("/api/v1/users", status_code=status.HTTP_201_CREATED)
async def create_user_in_db(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new user record in the PostgreSQL database.
    This endpoint should be called by the frontend after a user signs up with Firebase.
    """
    db_user = db.query(User).filter(User.firebase_uid == user_data.firebase_uid).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this Firebase UID already exists"
        )
    
    # Create the new user record in the database
    new_user = User(
        firebase_uid=user_data.firebase_uid,
        email=user_data.email,
        name=user_data.name,
        avatar_url=user_data.avatar_url
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user created in DB with firebase_uid: {new_user.firebase_uid}")
    
    return {"message": "User record created successfully", "user_id": new_user.id}

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
    db: Session = Depends(get_db)
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
        
    # Update only the fields that are provided in the request body
    if user_data.name is not None:
        db_user.name = user_data.name
    if user_data.avatar_url is not None:
        db_user.avatar_url = user_data.avatar_url
        
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User with firebase_uid: {firebase_uid} updated successfully.")
    
    return db_user

@app.delete("/api/v1/users/{firebase_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_firebase_uid(
    firebase_uid: str,
    db: Session = Depends(get_db)
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