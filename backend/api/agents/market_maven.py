"""
Market Maven Agent API endpoints for competitor monitoring and analysis
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, File, UploadFile
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
import uuid
from datetime import datetime
import json
import logging

from db.database import get_db
from dependencies import get_current_user_id
from models.ai_models import CompetitorWatch, CompetitorUpdate, AgentActivity
from agents.market_maven import create_market_maven_chain
from celery_worker import process_competitor_analysis_task

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents/market-maven", tags=["Market Maven Agent"])

# Initialize Market Maven AI chain
market_maven_chain = create_market_maven_chain()


# --- Pydantic Models ---
from pydantic import BaseModel, HttpUrl


class CompetitorWatchCreate(BaseModel):
    competitor_name: str
    website_url: HttpUrl
    check_frequency: str = "daily"  # daily, weekly


class CompetitorAnalysisRequest(BaseModel):
    competitor_data: str


class CompetitorUpdateResponse(BaseModel):
    id: str
    competitor_name: str
    update_type: str
    title: str
    ai_summary: Optional[str]
    ai_impact_analysis: Optional[str]
    status: str
    detected_at: datetime


class CompetitorWatchResponse(BaseModel):
    id: str
    competitor_name: str
    website_url: str
    is_active: bool
    check_frequency: str
    last_checked_at: Optional[datetime]
    created_at: datetime


# --- Main Agent Endpoints ---


@router.post("/competitor-watches", response_model=CompetitorWatchResponse)
async def create_competitor_watch(
    watch_data: CompetitorWatchCreate,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Create a new competitor watch for monitoring.
    """
    try:
        # Create competitor watch record
        competitor_watch = CompetitorWatch(
            user_id=int(user_id),
            competitor_name=watch_data.competitor_name,
            website_url=str(watch_data.website_url),
            check_frequency=watch_data.check_frequency,
            is_active=True,
        )

        db.add(competitor_watch)
        db.commit()
        db.refresh(competitor_watch)

        # Log agent activity
        activity = AgentActivity(
            user_id=int(user_id),
            agent_type="market_maven",
            action="competitor_watch_created",
            status="success",
            activity_metadata={
                "competitor_watch_id": str(competitor_watch.id),
                "competitor_name": watch_data.competitor_name,
                "website_url": str(watch_data.website_url),
            },
        )
        db.add(activity)
        db.commit()

        return CompetitorWatchResponse(
            id=str(competitor_watch.id),
            competitor_name=competitor_watch.competitor_name,
            website_url=competitor_watch.website_url,
            is_active=competitor_watch.is_active,
            check_frequency=competitor_watch.check_frequency,
            last_checked_at=competitor_watch.last_checked_at,
            created_at=competitor_watch.created_at,
        )

    except Exception as e:
        logger.error(f"Error creating competitor watch: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create competitor watch: {str(e)}"
        )


@router.get("/competitor-watches", response_model=List[CompetitorWatchResponse])
async def list_competitor_watches(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    List all competitor watches for the authenticated user.
    """
    try:
        watches = (
            db.query(CompetitorWatch)
            .filter(CompetitorWatch.user_id == int(user_id))
            .order_by(CompetitorWatch.created_at.desc())
            .all()
        )

        return [
            CompetitorWatchResponse(
                id=str(watch.id),
                competitor_name=watch.competitor_name,
                website_url=watch.website_url,
                is_active=watch.is_active,
                check_frequency=watch.check_frequency,
                last_checked_at=watch.last_checked_at,
                created_at=watch.created_at,
            )
            for watch in watches
        ]

    except Exception as e:
        logger.error(f"Error listing competitor watches: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list competitor watches: {str(e)}"
        )


@router.post("/analyze")
async def analyze_competitor_data(
    analysis_request: CompetitorAnalysisRequest,
    background_tasks: BackgroundTasks,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Analyze competitor data using the Market Maven AI agent.
    """
    try:
        # Log the start of analysis
        activity = AgentActivity(
            user_id=int(user_id),
            agent_type="market_maven",
            action="competitor_analysis_started",
            status="processing",
            activity_metadata={
                "data_length": len(analysis_request.competitor_data),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        # Queue the background task for analysis
        task = process_competitor_analysis_task.delay(
            str(activity.id), analysis_request.competitor_data, int(user_id)
        )

        return {
            "activity_id": str(activity.id),
            "task_id": str(task.id),
            "status": "processing",
            "message": "Competitor analysis started. Use the activity_id to check status.",
        }

    except Exception as e:
        logger.error(f"Error starting competitor analysis: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start competitor analysis: {str(e)}"
        )


@router.get("/analysis/{activity_id}/status")
async def get_analysis_status(
    activity_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Get the status of a competitor analysis task.
    """
    try:
        activity = (
            db.query(AgentActivity)
            .filter(
                AgentActivity.id == uuid.UUID(activity_id),
                AgentActivity.user_id == int(user_id),
            )
            .first()
        )

        if not activity:
            raise HTTPException(status_code=404, detail="Analysis activity not found")

        return {
            "activity_id": str(activity.id),
            "status": activity.status,
            "action": activity.action,
            "created_at": activity.created_at,
            "processing_time_seconds": activity.processing_time_seconds,
            "error_message": activity.error_message,
            "metadata": activity.activity_metadata,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid activity ID format")
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get analysis status: {str(e)}"
        )


@router.get("/analysis/{activity_id}/results")
async def get_analysis_results(
    activity_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Get the results of a completed competitor analysis.
    """
    try:
        activity = (
            db.query(AgentActivity)
            .filter(
                AgentActivity.id == uuid.UUID(activity_id),
                AgentActivity.user_id == int(user_id),
            )
            .first()
        )

        if not activity:
            raise HTTPException(status_code=404, detail="Analysis activity not found")

        if activity.status != "success":
            raise HTTPException(
                status_code=400,
                detail=f"Analysis not completed. Current status: {activity.status}",
            )

        # Extract results from metadata
        results = activity.activity_metadata.get("analysis_results", {})

        return {
            "activity_id": str(activity.id),
            "status": activity.status,
            "results": results,
            "processing_time_seconds": activity.processing_time_seconds,
            "tokens_used": activity.tokens_used,
            "created_at": activity.created_at,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid activity ID format")
    except Exception as e:
        logger.error(f"Error getting analysis results: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get analysis results: {str(e)}"
        )


@router.get("/updates", response_model=List[CompetitorUpdateResponse])
async def list_competitor_updates(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
    status: Optional[str] = None,
    limit: int = 20,
):
    """
    List recent competitor updates for the user.
    """
    try:
        query = db.query(CompetitorUpdate).filter(
            CompetitorUpdate.user_id == int(user_id)
        )

        if status:
            query = query.filter(CompetitorUpdate.status == status)

        updates = query.order_by(CompetitorUpdate.detected_at.desc()).limit(limit).all()

        # Get competitor names from watches
        watch_ids = [update.competitor_watch_id for update in updates]
        watches = (
            db.query(CompetitorWatch).filter(CompetitorWatch.id.in_(watch_ids)).all()
        )
        watch_map = {watch.id: watch.competitor_name for watch in watches}

        return [
            CompetitorUpdateResponse(
                id=str(update.id),
                competitor_name=watch_map.get(update.competitor_watch_id, "Unknown"),
                update_type=update.update_type,
                title=update.title,
                ai_summary=update.ai_summary,
                ai_impact_analysis=update.ai_impact_analysis,
                status=update.status,
                detected_at=update.detected_at,
            )
            for update in updates
        ]

    except Exception as e:
        logger.error(f"Error listing competitor updates: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list competitor updates: {str(e)}"
        )


# --- Test Endpoints (No Authentication Required) ---


@router.post("/test/analyze")
async def test_analyze_competitor_data(
    analysis_request: CompetitorAnalysisRequest, db: Annotated[Session, Depends(get_db)]
):
    """
    Test endpoint for analyzing competitor data without authentication.
    """
    try:
        # Create or get test user
        from models.models import User

        test_user = db.query(User).filter(User.email == "test@defineconsult.co").first()
        if not test_user:
            test_user = User(
                firebase_uid="test-market-maven-user",
                email="test@defineconsult.co",
                name="Market Maven Test User",
                current_plan_id=1,  # Assuming a plan exists
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)

        # Log test activity
        activity = AgentActivity(
            user_id=test_user.id,
            agent_type="market_maven",
            action="test_competitor_analysis_started",
            status="processing",
            activity_metadata={
                "test_mode": True,
                "data_length": len(analysis_request.competitor_data),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        # Queue the background task for analysis
        task = process_competitor_analysis_task.delay(
            str(activity.id), analysis_request.competitor_data, test_user.id
        )

        return {
            "activity_id": str(activity.id),
            "task_id": str(task.id),
            "status": "processing",
            "message": "Test competitor analysis started. Use the activity_id to check status.",
            "test_mode": True,
            "user_id": test_user.id,
        }

    except Exception as e:
        logger.error(f"Error in test competitor analysis: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start test analysis: {str(e)}"
        )


@router.get("/test/analysis/{activity_id}/status")
async def test_get_analysis_status(
    activity_id: str, db: Annotated[Session, Depends(get_db)]
):
    """
    Test endpoint to get analysis status without authentication.
    """
    try:
        activity = (
            db.query(AgentActivity)
            .filter(AgentActivity.id == uuid.UUID(activity_id))
            .first()
        )

        if not activity:
            raise HTTPException(status_code=404, detail="Analysis activity not found")

        return {
            "activity_id": str(activity.id),
            "status": activity.status,
            "action": activity.action,
            "created_at": activity.created_at,
            "processing_time_seconds": activity.processing_time_seconds,
            "error_message": activity.error_message,
            "metadata": activity.activity_metadata,
            "test_mode": True,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid activity ID format")
    except Exception as e:
        logger.error(f"Error getting test analysis status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get test analysis status: {str(e)}"
        )


@router.get("/test/analysis/{activity_id}/results")
async def test_get_analysis_results(
    activity_id: str, db: Annotated[Session, Depends(get_db)]
):
    """
    Test endpoint to get analysis results without authentication.
    """
    try:
        activity = (
            db.query(AgentActivity)
            .filter(AgentActivity.id == uuid.UUID(activity_id))
            .first()
        )

        if not activity:
            raise HTTPException(status_code=404, detail="Analysis activity not found")

        if activity.status != "success":
            raise HTTPException(
                status_code=400,
                detail=f"Analysis not completed. Current status: {activity.status}",
            )

        # Extract results from metadata
        results = activity.activity_metadata.get("analysis_results", {})

        return {
            "activity_id": str(activity.id),
            "status": activity.status,
            "results": results,
            "processing_time_seconds": activity.processing_time_seconds,
            "tokens_used": activity.tokens_used,
            "created_at": activity.created_at,
            "test_mode": True,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid activity ID format")
    except Exception as e:
        logger.error(f"Error getting test analysis results: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get test analysis results: {str(e)}"
        )


# --- Health Check ---
@router.get("/health")
async def health_check():
    """
    Health check endpoint for Market Maven agent.
    """
    try:
        # Test AI chain initialization
        test_chain = create_market_maven_chain()
        return {
            "status": "healthy",
            "agent": "market_maven",
            "ai_chain": "initialized",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Market Maven agent unhealthy: {str(e)}"
        )
