from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from models.models import Plan
from schemas.plans import PlanCreate, PlanResponse, PlanUpdate
from dependencies import get_db 
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plans", tags=["Plans"])

# ---  Plan Endpoints ---
@router.post("", status_code=status.HTTP_201_CREATED)
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

@router.get("", response_model=list[PlanResponse])
async def get_all_plans(db: Annotated[Session, Depends(get_db)]):
    """
    Retrieves all plans from the database.
    """
    plans = db.query(Plan).all()
    return plans

@router.get("/{plan_id}", response_model=PlanResponse)
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

@router.patch("/{plan_id}", response_model=PlanResponse)
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

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
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