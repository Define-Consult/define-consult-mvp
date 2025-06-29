from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from models.models import User
from schemas.user import UserCreate, UserResponse, UserUpdate
from dependencies import get_db, get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


# --- User Profile Endpoints ---
@router.post("", status_code=status.HTTP_201_CREATED)
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

    new_user_profile = User(**user_data.model_dump())
    db.add(new_user_profile)
    db.commit()
    db.refresh(new_user_profile)

    return new_user_profile


@router.get("/{firebase_uid}", response_model=UserResponse)
async def get_user_by_firebase_uid(firebase_uid: str, db: Session = Depends(get_db)):
    """
    Retrieves a single user from the database by their Firebase UID.
    """
    db_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return db_user


@router.patch("/{firebase_uid}", response_model=UserResponse)
async def update_user_by_firebase_uid(
    firebase_uid: str, user_data: UserUpdate, db: Annotated[Session, Depends(get_db)]
):
    """
    Updates an existing user's details in the database by their Firebase UID.
    """
    db_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    logger.info(f"User with firebase_uid: {firebase_uid} updated successfully.")

    return db_user


@router.delete("/{firebase_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_firebase_uid(
    firebase_uid: str, db: Annotated[Session, Depends(get_db)]
):
    """
    Deletes a user from the database by their Firebase UID.
    """
    db_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(db_user)
    db.commit()

    logger.info(f"User with firebase_uid: {firebase_uid} deleted successfully.")

    return


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_user_profile(
    user_data: UserCreate, db: Annotated[Session, Depends(get_db)]
):
    """
    Endpoint to sync (upsert) a user profile in the database.
    Creates if doesn't exist, updates if exists.
    """
    existing_user = (
        db.query(User).filter(User.firebase_uid == user_data.firebase_uid).first()
    )

    if existing_user:
        # Update existing user
        for key, value in user_data.model_dump(exclude_unset=True).items():
            if value is not None:  # Only update non-null values
                setattr(existing_user, key, value)

        db.commit()
        db.refresh(existing_user)
        logger.info(
            f"User with firebase_uid: {user_data.firebase_uid} updated successfully."
        )
        return {"status": "updated", "user": existing_user}
    else:
        # Create new user
        new_user_profile = User(**user_data.model_dump())
        db.add(new_user_profile)
        db.commit()
        db.refresh(new_user_profile)
        logger.info(
            f"User with firebase_uid: {user_data.firebase_uid} created successfully."
        )
        return {"status": "created", "user": new_user_profile}
