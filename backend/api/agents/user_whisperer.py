"""
User Whisperer Agent API

This module handles the User Whisperer agent functionality:
- Upload and process customer feedback transcripts
- Extract problem statements and generate user stories
- Provide actionable insights for product managers
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import Annotated, List
import logging
import uuid
from datetime import datetime

from db.database import get_db
from dependencies import get_current_user_id
from models.ai_models import Transcript, AgentActivity
from models.models import User
from celery_worker import process_transcript_task
from schemas.ai_schemas import (
    TranscriptCreate,
    TranscriptResponse,
    TranscriptProcessRequest,
    AgentActivityResponse,
)
from services.ai_service import user_whisperer
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents/user-whisperer", tags=["User Whisperer Agent"])


@router.post("/upload-transcript", status_code=status.HTTP_201_CREATED)
async def upload_transcript(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    file: UploadFile = File(...),
    title: str = "Customer Feedback",
):
    """
    Upload a customer feedback transcript for processing
    """
    try:
        # Validate file type
        if not file.filename.endswith((".txt", ".md", ".docx")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .txt, .md, and .docx files are supported",
            )

        # Read file content
        content = await file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        # Get user from database
        user = db.query(User).filter(User.firebase_uid == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Create transcript record
        transcript = Transcript(
            user_id=user.id,
            title=title,
            content=content,  # Store content for processing
            file_metadata={
                "original_filename": file.filename,
                "file_size": len(content),
                "upload_timestamp": datetime.utcnow().isoformat(),
            },
            status="uploaded",
        )

        db.add(transcript)
        db.commit()
        db.refresh(transcript)

        # Trigger async processing with Celery
        task = process_transcript_task.delay(transcript.id, user.id)

        logger.info(
            f"Transcript uploaded successfully: {transcript.id}, Task ID: {task.id}"
        )

        return {
            "transcript_id": str(transcript.id),
            "task_id": str(task.id),
            "title": transcript.title,
            "status": transcript.status,
            "file_metadata": transcript.file_metadata,
            "message": "Transcript uploaded and processing started",
        }

    except Exception as e:
        logger.error(f"Error uploading transcript: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload transcript: {str(e)}",
        )


@router.post("/process-transcript/{transcript_id}")
async def process_transcript(
    transcript_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """
    Process an uploaded transcript with the User Whisperer agent
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Get transcript
        transcript = (
            db.query(Transcript)
            .filter(Transcript.id == transcript_id, Transcript.user_id == user.id)
            .first()
        )

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found"
            )

        if transcript.status == "processing":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript is already being processed",
            )

        # Update status to processing
        transcript.status = "processing"
        db.commit()

        # Log agent activity start
        activity = AgentActivity(
            user_id=user.id,
            agent_type="user_whisperer",
            action_type="transcript_processing",
            input_data={"transcript_id": str(transcript_id)},
            status="processing",
        )
        db.add(activity)
        db.commit()

        start_time = datetime.now()

        try:
            # Process with AI agent
            results = await user_whisperer.process_transcript(transcript.content)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Update transcript with results
            transcript.analysis = results
            transcript.insights = results.get("insights")
            transcript.sentiment_score = results.get("sentiment_score")
            transcript.key_themes = results.get("key_themes")
            transcript.pain_points = results.get("pain_points")
            transcript.feature_requests = results.get("feature_requests")
            transcript.status = "completed"

            # Update activity log
            activity.output_data = results
            activity.status = "success"
            activity.processing_time_seconds = processing_time

            db.commit()

            logger.info(f"Transcript processed successfully: {transcript_id}")

            return {
                "transcript_id": str(transcript.id),
                "status": "completed",
                "processing_time_seconds": processing_time,
                "results": results,
            }

        except Exception as processing_error:
            # Update status on error
            transcript.status = "error"
            activity.status = "error"
            activity.error_message = str(processing_error)
            db.commit()

            logger.error(
                f"Error processing transcript {transcript_id}: {processing_error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process transcript: {str(processing_error)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_transcript: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/transcripts")
async def get_user_transcripts(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """
    Get all transcripts for the current user
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Get user's transcripts
        transcripts = (
            db.query(Transcript)
            .filter(Transcript.user_id == user.id)
            .order_by(Transcript.created_at.desc())
            .all()
        )

        return {
            "transcripts": [
                {
                    "id": str(transcript.id),
                    "title": transcript.title,
                    "status": transcript.status,
                    "file_metadata": transcript.file_metadata,
                    "created_at": transcript.created_at,
                    "has_results": transcript.analysis is not None,
                }
                for transcript in transcripts
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching transcripts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transcripts",
        )


@router.get("/transcripts/{transcript_id}")
async def get_transcript(
    transcript_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """
    Get a specific transcript and its analysis results
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Get transcript
        transcript = (
            db.query(Transcript)
            .filter(Transcript.id == transcript_id, Transcript.user_id == user.id)
            .first()
        )

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found"
            )

        return {
            "transcript_id": str(transcript.id),
            "title": transcript.title,
            "content": transcript.content,
            "status": transcript.status,
            "file_metadata": transcript.file_metadata,
            "analysis": transcript.analysis,
            "insights": transcript.insights,
            "sentiment_score": transcript.sentiment_score,
            "key_themes": transcript.key_themes,
            "pain_points": transcript.pain_points,
            "feature_requests": transcript.feature_requests,
            "error_message": transcript.error_message,
            "created_at": transcript.created_at,
            "updated_at": transcript.updated_at,
        }

    except Exception as e:
        logger.error(f"Error getting transcript: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transcript: {str(e)}",
        )


@router.get("/tasks/{task_id}/status")
async def get_task_status(
    task_id: str, current_user_id: Annotated[str, Depends(get_current_user_id)]
):
    """
    Get the status of a Celery task
    """
    try:
        from celery_worker import celery_app

        # Get task result
        task_result = celery_app.AsyncResult(task_id)

        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "message": "Task is waiting to be processed",
            }
        elif task_result.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": task_result.info.get("current", 0),
                "total": task_result.info.get("total", 1),
                "message": task_result.info.get("message", "Processing..."),
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "result": task_result.result,
                "message": "Task completed successfully",
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "error": str(task_result.info),
                "message": "Task failed",
            }

        return response

    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for User Whisperer Agent
    """
    return {
        "status": "healthy",
        "message": "User Whisperer Agent is operational",
        "timestamp": datetime.utcnow().isoformat(),
    }


# === AUTHENTICATED ENDPOINTS ===
@router.post("/upload-transcript", status_code=status.HTTP_201_CREATED)
async def upload_transcript(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    file: UploadFile = File(...),
    title: str = "Customer Feedback",
):
    """
    Upload a customer feedback transcript for processing
    """
    try:
        # Validate file type
        if not file.filename.endswith((".txt", ".md", ".docx")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .txt, .md, and .docx files are supported",
            )

        # Read file content
        content = await file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        # Get user from database
        user = db.query(User).filter(User.firebase_uid == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Create transcript record
        transcript = Transcript(
            user_id=user.id,
            title=title,
            content=content,  # Store content for processing
            file_metadata={
                "original_filename": file.filename,
                "file_size": len(content),
                "upload_timestamp": datetime.utcnow().isoformat(),
            },
            status="uploaded",
        )

        db.add(transcript)
        db.commit()
        db.refresh(transcript)

        # Trigger async processing with Celery
        task = process_transcript_task.delay(transcript.id, user.id)

        logger.info(
            f"Transcript uploaded successfully: {transcript.id}, Task ID: {task.id}"
        )

        return {
            "transcript_id": str(transcript.id),
            "task_id": str(task.id),
            "title": transcript.title,
            "status": transcript.status,
            "file_metadata": transcript.file_metadata,
            "message": "Transcript uploaded and processing started",
        }

    except Exception as e:
        logger.error(f"Error uploading transcript: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload transcript: {str(e)}",
        )


@router.post("/process-transcript/{transcript_id}")
async def process_transcript(
    transcript_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """
    Process an uploaded transcript with the User Whisperer agent
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Get transcript
        transcript = (
            db.query(Transcript)
            .filter(Transcript.id == transcript_id, Transcript.user_id == user.id)
            .first()
        )

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found"
            )

        if transcript.status == "processing":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript is already being processed",
            )

        # Update status to processing
        transcript.status = "processing"
        db.commit()

        # Log agent activity start
        activity = AgentActivity(
            user_id=user.id,
            agent_type="user_whisperer",
            action_type="transcript_processing",
            input_data={"transcript_id": str(transcript_id)},
            status="processing",
        )
        db.add(activity)
        db.commit()

        start_time = datetime.now()

        try:
            # Process with AI agent
            results = await user_whisperer.process_transcript(transcript.content)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Update transcript with results
            transcript.analysis = results
            transcript.insights = results.get("insights")
            transcript.sentiment_score = results.get("sentiment_score")
            transcript.key_themes = results.get("key_themes")
            transcript.pain_points = results.get("pain_points")
            transcript.feature_requests = results.get("feature_requests")
            transcript.status = "completed"

            # Update activity log
            activity.output_data = results
            activity.status = "success"
            activity.processing_time_seconds = processing_time

            db.commit()

            logger.info(f"Transcript processed successfully: {transcript_id}")

            return {
                "transcript_id": str(transcript.id),
                "status": "completed",
                "processing_time_seconds": processing_time,
                "results": results,
            }

        except Exception as processing_error:
            # Update status on error
            transcript.status = "error"
            activity.status = "error"
            activity.error_message = str(processing_error)
            db.commit()

            logger.error(
                f"Error processing transcript {transcript_id}: {processing_error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process transcript: {str(processing_error)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_transcript: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/transcripts")
async def get_user_transcripts(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """
    Get all transcripts for the current user
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Get user's transcripts
        transcripts = (
            db.query(Transcript)
            .filter(Transcript.user_id == user.id)
            .order_by(Transcript.created_at.desc())
            .all()
        )

        return {
            "transcripts": [
                {
                    "id": str(transcript.id),
                    "title": transcript.title,
                    "status": transcript.status,
                    "file_metadata": transcript.file_metadata,
                    "created_at": transcript.created_at,
                    "has_results": transcript.analysis is not None,
                }
                for transcript in transcripts
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching transcripts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transcripts",
        )


@router.get("/transcripts/{transcript_id}")
async def get_transcript(
    transcript_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """
    Get a specific transcript and its analysis results
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Get transcript
        transcript = (
            db.query(Transcript)
            .filter(Transcript.id == transcript_id, Transcript.user_id == user.id)
            .first()
        )

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found"
            )

        return {
            "transcript_id": str(transcript.id),
            "title": transcript.title,
            "content": transcript.content,
            "status": transcript.status,
            "file_metadata": transcript.file_metadata,
            "analysis": transcript.analysis,
            "insights": transcript.insights,
            "sentiment_score": transcript.sentiment_score,
            "key_themes": transcript.key_themes,
            "pain_points": transcript.pain_points,
            "feature_requests": transcript.feature_requests,
            "error_message": transcript.error_message,
            "created_at": transcript.created_at,
            "updated_at": transcript.updated_at,
        }

    except Exception as e:
        logger.error(f"Error getting transcript: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transcript: {str(e)}",
        )


@router.get("/tasks/{task_id}/status")
async def get_task_status(
    task_id: str, current_user_id: Annotated[str, Depends(get_current_user_id)]
):
    """
    Get the status of a Celery task
    """
    try:
        from celery_worker import celery_app

        # Get task result
        task_result = celery_app.AsyncResult(task_id)

        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "message": "Task is waiting to be processed",
            }
        elif task_result.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": task_result.info.get("current", 0),
                "total": task_result.info.get("total", 1),
                "message": task_result.info.get("message", "Processing..."),
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "result": task_result.result,
                "message": "Task completed successfully",
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "error": str(task_result.info),
                "message": "Task failed",
            }

        return response

    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}",
        )


# === TEST ENDPOINTS (NO AUTH REQUIRED) ===
@router.post("/test/upload-transcript", status_code=status.HTTP_201_CREATED)
async def test_upload_transcript(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
    title: str = "Customer Feedback",
    test_user_id: str = "test-user-123",
):
    """
    TEST ENDPOINT: Upload a transcript without authentication
    """
    try:
        # Validate file type
        if not file.filename.endswith((".txt", ".md", ".docx")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .txt, .md, and .docx files are supported",
            )

        # Read file content
        content = await file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        # Get or create test user
        user = db.query(User).filter(User.firebase_uid == test_user_id).first()
        if not user:
            user = User(
                firebase_uid=test_user_id,
                email="testuser@example.com",
                name="Test User",
                company_name="Test Company",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create transcript record
        transcript = Transcript(
            user_id=user.id,
            title=title,
            content=content,
            file_metadata={
                "original_filename": file.filename,
                "file_size": len(content),
                "upload_timestamp": datetime.utcnow().isoformat(),
            },
            status="uploaded",
        )

        db.add(transcript)
        db.commit()
        db.refresh(transcript)

        # Trigger async processing with Celery
        task = process_transcript_task.delay(transcript.id, user.id)

        logger.info(
            f"TEST: Transcript uploaded successfully: {transcript.id}, Task ID: {task.id}"
        )

        return {
            "transcript_id": str(transcript.id),
            "task_id": str(task.id),
            "title": transcript.title,
            "status": transcript.status,
            "file_metadata": transcript.file_metadata,
            "message": "Transcript uploaded and processing started",
        }

    except Exception as e:
        logger.error(f"Error uploading transcript: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload transcript: {str(e)}",
        )


@router.get("/test/transcripts")
async def test_get_user_transcripts(
    db: Annotated[Session, Depends(get_db)], test_user_id: str = "test-user-123"
):
    """
    TEST ENDPOINT: Get all transcripts for test user
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == test_user_id).first()
        if not user:
            return {"transcripts": []}

        # Get user's transcripts
        transcripts = (
            db.query(Transcript)
            .filter(Transcript.user_id == user.id)
            .order_by(Transcript.created_at.desc())
            .all()
        )

        return {
            "transcripts": [
                {
                    "id": str(transcript.id),
                    "title": transcript.title,
                    "status": transcript.status,
                    "file_metadata": transcript.file_metadata,
                    "created_at": transcript.created_at,
                    "has_results": transcript.analysis is not None,
                }
                for transcript in transcripts
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching transcripts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transcripts",
        )


@router.get("/test/transcripts/{transcript_id}")
async def test_get_transcript(
    transcript_id: str,
    db: Annotated[Session, Depends(get_db)],
    test_user_id: str = "test-user-123",
):
    """
    TEST ENDPOINT: Get a specific transcript and its analysis results
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == test_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Get transcript
        transcript = (
            db.query(Transcript)
            .filter(Transcript.id == transcript_id, Transcript.user_id == user.id)
            .first()
        )

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found"
            )

        return {
            "transcript_id": str(transcript.id),
            "title": transcript.title,
            "content": transcript.content,
            "status": transcript.status,
            "file_metadata": transcript.file_metadata,
            "analysis": transcript.analysis,
            "insights": transcript.insights,
            "sentiment_score": transcript.sentiment_score,
            "key_themes": transcript.key_themes,
            "pain_points": transcript.pain_points,
            "feature_requests": transcript.feature_requests,
            "error_message": transcript.error_message,
            "created_at": transcript.created_at,
            "updated_at": transcript.updated_at,
        }

    except Exception as e:
        logger.error(f"Error getting transcript: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transcript: {str(e)}",
        )


@router.get("/test/tasks/{task_id}/status")
async def test_get_task_status(task_id: str):
    """
    TEST ENDPOINT: Get the status of a Celery task (no auth)
    """
    try:
        from celery_worker import celery_app

        # Get task result
        task_result = celery_app.AsyncResult(task_id)

        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "message": "Task is waiting to be processed",
            }
        elif task_result.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": task_result.info.get("current", 0),
                "total": task_result.info.get("total", 1),
                "message": task_result.info.get("message", "Processing..."),
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "result": task_result.result,
                "message": "Task completed successfully",
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "error": str(task_result.info),
                "message": "Task failed",
            }

        return response

    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}",
        )


# === END TEST ENDPOINTS ===
