"""
Narrative Architect Agent API endpoints for content generation and product evangelism
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
import uuid
from datetime import datetime
import json
import logging

from db.database import get_db
from dependencies import get_current_user_id
from models.ai_models import GeneratedContent, AgentActivity
from agents.narrative_architect import create_narrative_architect_chain
from celery_worker import process_content_generation_task

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agents/narrative-architect", tags=["Narrative Architect Agent"]
)

# Initialize Narrative Architect AI chain
narrative_architect_chain = create_narrative_architect_chain()


# --- Pydantic Models ---
from pydantic import BaseModel
from enum import Enum


class PlatformType(str, Enum):
    linkedin = "linkedin"
    twitter = "twitter"
    medium = "medium"
    blog = "blog"
    email = "email"
    general = "general"


class ContentType(str, Enum):
    feature_announcement = "feature_announcement"
    product_update = "product_update"
    thought_leadership = "thought_leadership"
    social_post = "social_post"
    blog_post = "blog_post"
    press_release = "press_release"
    case_study = "case_study"
    newsletter = "newsletter"


class ContentGenerationRequest(BaseModel):
    platform: PlatformType
    content_type: ContentType
    source_material: str
    context: Optional[str] = ""
    target_audience: Optional[str] = "product managers and tech professionals"
    brand_tone: Optional[str] = "professional, innovative, approachable"


class ContentGenerationResponse(BaseModel):
    id: str
    user_id: int
    platform: str
    content_type: str
    status: str
    created_at: datetime


class GeneratedContentResponse(BaseModel):
    id: str
    platform: str
    content_type: str
    title: Optional[str]
    content: str
    status: str
    created_at: datetime


# --- Main Agent Endpoints ---


@router.post("/generate", response_model=dict)
async def generate_content(
    generation_request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Generate content using the Narrative Architect AI agent.
    """
    try:
        # Create initial content record
        content_record = GeneratedContent(
            user_id=int(user_id),
            content_type=generation_request.content_type.value,
            platform=generation_request.platform.value,
            content="Processing...",
            prompt_used=f"Platform: {generation_request.platform.value}, Type: {generation_request.content_type.value}",
            source_data={
                "source_material": generation_request.source_material,
                "context": generation_request.context,
                "target_audience": generation_request.target_audience,
                "brand_tone": generation_request.brand_tone,
            },
            status="processing",
        )

        db.add(content_record)
        db.commit()
        db.refresh(content_record)

        # Log agent activity
        activity = AgentActivity(
            user_id=int(user_id),
            agent_type="narrative_architect",
            action="content_generation_started",
            status="processing",
            activity_metadata={
                "content_id": str(content_record.id),
                "platform": generation_request.platform.value,
                "content_type": generation_request.content_type.value,
                "source_length": len(generation_request.source_material),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        # Queue the background task for content generation
        task = process_content_generation_task.delay(
            str(activity.id),
            str(content_record.id),
            generation_request.dict(),
            int(user_id),
        )

        return {
            "content_id": str(content_record.id),
            "activity_id": str(activity.id),
            "task_id": str(task.id),
            "status": "processing",
            "message": "Content generation started. Use the content_id to check status.",
        }

    except Exception as e:
        logger.error(f"Error starting content generation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start content generation: {str(e)}"
        )


@router.get("/content/{content_id}/status")
async def get_content_status(
    content_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Get the status of a content generation task.
    """
    try:
        content = (
            db.query(GeneratedContent)
            .filter(
                GeneratedContent.id == uuid.UUID(content_id),
                GeneratedContent.user_id == int(user_id),
            )
            .first()
        )

        if not content:
            raise HTTPException(status_code=404, detail="Content generation not found")

        return {
            "content_id": str(content.id),
            "status": content.status,
            "platform": content.platform,
            "content_type": content.content_type,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID format")
    except Exception as e:
        logger.error(f"Error getting content status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get content status: {str(e)}"
        )


@router.get("/content/{content_id}")
async def get_generated_content(
    content_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Get the generated content results.
    """
    try:
        content = (
            db.query(GeneratedContent)
            .filter(
                GeneratedContent.id == uuid.UUID(content_id),
                GeneratedContent.user_id == int(user_id),
            )
            .first()
        )

        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        return {
            "content_id": str(content.id),
            "platform": content.platform,
            "content_type": content.content_type,
            "title": content.title,
            "content": content.content,
            "status": content.status,
            "source_data": content.source_data,
            "user_edits": content.user_edits,
            "final_version": content.final_version,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID format")
    except Exception as e:
        logger.error(f"Error getting generated content: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get generated content: {str(e)}"
        )


@router.get("/content", response_model=List[GeneratedContentResponse])
async def list_generated_content(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
    platform: Optional[str] = None,
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
):
    """
    List generated content for the authenticated user.
    """
    try:
        query = db.query(GeneratedContent).filter(
            GeneratedContent.user_id == int(user_id)
        )

        if platform:
            query = query.filter(GeneratedContent.platform == platform)
        if content_type:
            query = query.filter(GeneratedContent.content_type == content_type)
        if status:
            query = query.filter(GeneratedContent.status == status)

        contents = query.order_by(GeneratedContent.created_at.desc()).limit(limit).all()

        return [
            GeneratedContentResponse(
                id=str(content.id),
                platform=content.platform,
                content_type=content.content_type,
                title=content.title,
                content=(
                    content.content[:200] + "..."
                    if len(content.content) > 200
                    else content.content
                ),
                status=content.status,
                created_at=content.created_at,
            )
            for content in contents
        ]

    except Exception as e:
        logger.error(f"Error listing generated content: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list generated content: {str(e)}"
        )


@router.put("/content/{content_id}")
async def update_content(
    content_id: str,
    content_update: dict,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Update generated content (user edits, status changes).
    """
    try:
        content = (
            db.query(GeneratedContent)
            .filter(
                GeneratedContent.id == uuid.UUID(content_id),
                GeneratedContent.user_id == int(user_id),
            )
            .first()
        )

        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        # Update allowed fields
        if "status" in content_update:
            content.status = content_update["status"]
        if "user_edits" in content_update:
            content.user_edits = content_update["user_edits"]
        if "final_version" in content_update:
            content.final_version = content_update["final_version"]
        if "title" in content_update:
            content.title = content_update["title"]

        db.commit()

        return {
            "content_id": str(content.id),
            "status": content.status,
            "message": "Content updated successfully",
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID format")
    except Exception as e:
        logger.error(f"Error updating content: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update content: {str(e)}"
        )


# --- Test Endpoints (No Authentication Required) ---


@router.post("/test/generate")
async def test_generate_content(
    generation_request: ContentGenerationRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Test endpoint for generating content without authentication.
    """
    try:
        # Get or create test user
        from models.models import User

        test_user = db.query(User).filter(User.firebase_uid == "test-user-123").first()
        if not test_user:
            test_user = User(
                firebase_uid="test-user-123",
                email="testuser@example.com",
                name="Test User",
                company_name="Test Company",
                current_plan_id=None,
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)

        # Create test content record
        content_record = GeneratedContent(
            user_id=test_user.id,  # Test user ID
            content_type=generation_request.content_type.value,
            platform=generation_request.platform.value,
            content="Processing...",
            prompt_used=f"Test: Platform: {generation_request.platform.value}, Type: {generation_request.content_type.value}",
            source_data={
                "source_material": generation_request.source_material,
                "context": generation_request.context,
                "target_audience": generation_request.target_audience,
                "brand_tone": generation_request.brand_tone,
                "test_mode": True,
            },
            status="processing",
        )

        db.add(content_record)
        db.commit()
        db.refresh(content_record)

        # Log test activity
        activity = AgentActivity(
            user_id=test_user.id,  # Test user ID
            agent_type="narrative_architect",
            action="test_content_generation_started",
            status="processing",
            activity_metadata={
                "content_id": str(content_record.id),
                "platform": generation_request.platform.value,
                "content_type": generation_request.content_type.value,
                "source_length": len(generation_request.source_material),
                "test_mode": True,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        # Queue the background task for content generation
        task = process_content_generation_task.delay(
            str(activity.id),
            str(content_record.id),
            generation_request.dict(),
            test_user.id,  # Test user ID
        )

        return {
            "content_id": str(content_record.id),
            "activity_id": str(activity.id),
            "task_id": str(task.id),
            "status": "processing",
            "message": "Test content generation started. Use the content_id to check status.",
            "test_mode": True,
        }

    except Exception as e:
        logger.error(f"Error in test content generation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start test content generation: {str(e)}"
        )


@router.get("/test/content/{content_id}/status")
async def test_get_content_status(
    content_id: str, db: Annotated[Session, Depends(get_db)]
):
    """
    Test endpoint to get content generation status without authentication.
    """
    try:
        content = (
            db.query(GeneratedContent)
            .filter(GeneratedContent.id == uuid.UUID(content_id))
            .first()
        )

        if not content:
            raise HTTPException(status_code=404, detail="Content generation not found")

        return {
            "content_id": str(content.id),
            "status": content.status,
            "platform": content.platform,
            "content_type": content.content_type,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            "test_mode": True,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID format")
    except Exception as e:
        logger.error(f"Error getting test content status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get test content status: {str(e)}"
        )


@router.get("/test/content/{content_id}")
async def test_get_generated_content(
    content_id: str, db: Annotated[Session, Depends(get_db)]
):
    """
    Test endpoint to get generated content without authentication.
    """
    try:
        content = (
            db.query(GeneratedContent)
            .filter(GeneratedContent.id == uuid.UUID(content_id))
            .first()
        )

        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        return {
            "content_id": str(content.id),
            "platform": content.platform,
            "content_type": content.content_type,
            "title": content.title,
            "content": content.content,
            "status": content.status,
            "source_data": content.source_data,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            "test_mode": True,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID format")
    except Exception as e:
        logger.error(f"Error getting test generated content: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get test generated content: {str(e)}"
        )


@router.get("/test/content")
async def test_list_generated_content(
    platform: Optional[str] = None,
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
):
    """
    TEST ENDPOINT: List generated content without authentication
    """
    try:
        # Return mock generated content for testing
        mock_content = [
            {
                "id": "content-001",
                "platform": "linkedin",
                "content_type": "feature_announcement",
                "title": "Exciting New AI Feature Launch",
                "content": "We're thrilled to announce our latest AI-powered feature that will revolutionize how you analyze customer feedback...",
                "status": "published",
                "created_at": "2024-12-28T10:00:00Z",
            },
            {
                "id": "content-002",
                "platform": "twitter",
                "content_type": "product_update",
                "title": "User Whisperer 2.0 Update",
                "content": "🚀 User Whisperer 2.0 is here! New features: Real-time sentiment analysis, Advanced PRD generation, Smart tagging...",
                "status": "draft",
                "created_at": "2024-12-27T15:30:00Z",
            },
            {
                "id": "content-003",
                "platform": "medium",
                "content_type": "thought_leadership",
                "title": "The Future of AI in Product Management",
                "content": "As AI continues to evolve, product managers are finding new ways to leverage these tools for better decision making...",
                "status": "scheduled",
                "created_at": "2024-12-26T09:15:00Z",
            },
        ]

        # Apply filters if provided
        if platform:
            mock_content = [c for c in mock_content if c["platform"] == platform]
        if content_type:
            mock_content = [
                c for c in mock_content if c["content_type"] == content_type
            ]
        if status:
            mock_content = [c for c in mock_content if c["status"] == status]

        return mock_content[:limit]

    except Exception as e:
        logger.error(f"Error in test list generated content: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list test generated content: {str(e)}"
        )


# --- Health Check ---
@router.get("/health")
async def health_check():
    """
    Health check endpoint for Narrative Architect agent.
    """
    try:
        # Test AI chain initialization
        test_chain = create_narrative_architect_chain()
        return {
            "status": "healthy",
            "agent": "narrative_architect",
            "ai_chain": "initialized",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Narrative Architect agent unhealthy: {str(e)}"
        )
