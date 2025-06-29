from celery import Celery
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from sqlalchemy.orm import Session

load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# Import after celery_app is created to avoid circular imports
from db.database import SessionLocal
from models.ai_models import Transcript, AgentActivity
from services.ai_service import AIService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_transcript_task(self, transcript_id: int, user_id: str) -> Dict[str, Any]:
    """
    Process a transcript using AI analysis
    """
    db = SessionLocal()
    ai_service = AIService()

    try:
        # Get transcript from database
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        if not transcript:
            raise ValueError(f"Transcript {transcript_id} not found")

        # Update status to processing
        transcript.status = "processing"
        db.commit()

        # Log agent activity
        activity = AgentActivity(
            agent_type="user_whisperer",
            action="transcript_processing_started",
            user_id=user_id,
            activity_metadata={
                "transcript_id": str(transcript_id),  # Convert UUID to string
                "original_filename": (
                    transcript.file_metadata.get("original_filename", "")
                    if transcript.file_metadata
                    else ""
                ),
                "file_size": (
                    transcript.file_metadata.get("file_size", 0)
                    if transcript.file_metadata
                    else 0
                ),
            },
            status="processing",
        )
        db.add(activity)
        db.commit()

        # Perform AI analysis
        analysis_result = ai_service.analyze_transcript(
            content=transcript.content,
            context={
                "title": transcript.title or "Customer Feedback",
                "user_id": user_id,
                "transcript_id": transcript_id,
            },
        )

        # Update transcript with analysis results
        transcript.analysis = analysis_result
        transcript.status = "completed"
        transcript.insights = analysis_result.get("insights", [])
        transcript.sentiment_score = analysis_result.get("sentiment_score")
        transcript.key_themes = analysis_result.get("key_themes", [])
        transcript.pain_points = analysis_result.get("pain_points", [])
        transcript.feature_requests = analysis_result.get("feature_requests", [])

        db.commit()

        # Log completion
        completion_activity = AgentActivity(
            agent_type="user_whisperer",
            action="transcript_processing_completed",
            user_id=user_id,
            activity_metadata={
                "transcript_id": str(transcript_id),  # Convert UUID to string
                "insights_count": len(transcript.insights or []),
                "sentiment_score": transcript.sentiment_score,
                "themes_count": len(transcript.key_themes or []),
            },
            status="success",
        )
        db.add(completion_activity)
        db.commit()

        return {
            "status": "completed",
            "transcript_id": str(transcript_id),  # Convert UUID to string
            "insights_count": len(transcript.insights or []),
            "sentiment_score": transcript.sentiment_score,
            "message": "Transcript processed successfully",
        }

    except Exception as e:
        logger.error(f"Error processing transcript {transcript_id}: {str(e)}")

        # Update transcript status to failed
        if "transcript" in locals():
            transcript.status = "failed"
            transcript.error_message = str(e)
            db.commit()

        # Log error activity
        error_activity = AgentActivity(
            agent_type="user_whisperer",
            action="transcript_processing_failed",
            user_id=user_id,
            activity_metadata={
                "transcript_id": str(transcript_id),  # Convert UUID to string
                "error": str(e),
            },
            status="error",
            error_message=str(e),
        )
        db.add(error_activity)
        db.commit()

        # Re-raise for Celery to handle
        raise self.retry(exc=e, countdown=60, max_retries=3)

    finally:
        db.close()


@celery_app.task(bind=True)
def process_competitor_analysis_task(
    self, activity_id: str, competitor_data: str, user_id: int
) -> Dict[str, Any]:
    """
    Process competitor data using Market Maven AI analysis
    """
    db = SessionLocal()
    ai_service = AIService()

    try:
        # Get the activity record
        from uuid import UUID

        activity = (
            db.query(AgentActivity)
            .filter(AgentActivity.id == UUID(activity_id))
            .first()
        )
        if not activity:
            raise ValueError(f"Activity {activity_id} not found")

        # Update status to processing
        activity.status = "processing"
        activity.activity_metadata = {
            **activity.activity_metadata,
            "processing_started": True,
        }
        db.commit()

        # Perform Market Maven AI analysis
        analysis_result = ai_service.analyze_competitor_data(
            competitor_data=competitor_data,
            context={
                "user_id": user_id,
                "activity_id": activity_id,
                "analysis_type": "competitor_intelligence",
            },
        )

        # Update activity with analysis results
        activity.status = "success"
        activity.activity_metadata = {
            **activity.activity_metadata,
            "analysis_results": analysis_result,
            "processing_completed": True,
        }

        db.commit()

        logger.info(f"Market Maven analysis completed for activity {activity_id}")

        return {
            "status": "completed",
            "activity_id": activity_id,
            "analysis_summary": analysis_result.get("summary", "Analysis completed"),
            "message": "Competitor analysis processed successfully",
        }

    except Exception as e:
        logger.error(f"Error processing competitor analysis {activity_id}: {str(e)}")

        # Update activity status to failed
        if "activity" in locals():
            activity.status = "error"
            activity.error_message = str(e)
            activity.activity_metadata = {
                **activity.activity_metadata,
                "error": str(e),
                "processing_failed": True,
            }
            db.commit()

        # Re-raise for Celery to handle
        raise self.retry(exc=e, countdown=60, max_retries=3)

    finally:
        db.close()


@celery_app.task
def health_check():
    """Simple health check task"""
    return {"status": "healthy", "message": "Celery worker is running"}
