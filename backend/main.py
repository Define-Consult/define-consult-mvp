from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import firebase_admin
from firebase_admin import credentials, auth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

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

# --- Authentication Logic ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Dependency to get the current user's ID from a Firebase ID token.
    """
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Simple protected endpoint for testing auth ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to Define Consult API"}


@app.get("/protected")
async def protected_route(user_id: Annotated[str, Depends(get_current_user_id)]):
    """
    A route that requires authentication.
    """
    return {"message": f"Hello, authenticated user! Your UID is {user_id}"}


# --- Status Endpoint ---
@app.get("/status")
async def get_status():
    """
    Check if the API is running.
    """
    return {"status": "ok"}
