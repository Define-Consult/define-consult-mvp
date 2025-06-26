# Load environment variables
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import firebase_admin
from firebase_admin import credentials, auth
import os


from agents.user_whisperer import create_user_whisperer_chain

# Initialize the User Whisperer chain once at startup
user_whisperer_chain = create_user_whisperer_chain()


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


# --- AI Agent Endpoints ---
@app.post("/user-whisperer/generate-user-story")
async def generate_user_story(
    feedback: dict,  # Expects a JSON body like {"user_feedback": "..."}
    # We will add the user authentication dependency later
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
        # Invoke the LangChain agent with the user's input
        result = user_whisperer_chain.invoke({"user_feedback": user_feedback})
        return {"generated_output": result}
    except Exception as e:
        print(f"Error invoking chain: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate output.")
