from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.orm import Session
from firebase_admin import auth
from db.database import get_db

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