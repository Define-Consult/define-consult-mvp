"""
AI Agent related database models for Define Consult MVP
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from db.database import Base
import uuid


# --- Transcript Model ---
class Transcript(Base):
    __tablename__ = "transcripts"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.Text, nullable=False)  # Main transcript content
    file_metadata = sa.Column(JSONB, nullable=True)  # File info, upload details
    status = sa.Column(
        sa.String, default="uploaded", nullable=False
    )  # uploaded, processing, completed, failed

    # AI Processing Results
    analysis = sa.Column(JSONB, nullable=True)  # Full AI analysis results
    insights = sa.Column(JSONB, nullable=True)  # Key insights
    sentiment_score = sa.Column(sa.Float, nullable=True)  # Sentiment analysis
    key_themes = sa.Column(JSONB, nullable=True)  # Main themes
    pain_points = sa.Column(JSONB, nullable=True)  # Customer pain points
    feature_requests = sa.Column(JSONB, nullable=True)  # Feature requests

    # Error handling
    error_message = sa.Column(sa.Text, nullable=True)

    # Metadata
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())


# --- Competitive Intelligence Model ---
class CompetitorWatch(Base):
    __tablename__ = "competitor_watches"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    competitor_name = sa.Column(sa.String, nullable=False)
    website_url = sa.Column(sa.String, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)

    # Monitoring settings
    check_frequency = sa.Column(
        sa.String, default="daily", nullable=False
    )  # daily, weekly
    last_checked_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    # Latest snapshot
    latest_snapshot = sa.Column(JSONB, nullable=True)

    # Metadata
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())


# --- Competitive Intelligence Updates ---
class CompetitorUpdate(Base):
    __tablename__ = "competitor_updates"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    competitor_watch_id = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("competitor_watches.id"), nullable=False
    )
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)

    # Update details
    update_type = sa.Column(
        sa.String, nullable=False
    )  # feature_launch, pricing_change, content_update
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    ai_summary = sa.Column(sa.Text, nullable=True)
    ai_impact_analysis = sa.Column(sa.Text, nullable=True)

    # Raw data
    raw_data = sa.Column(JSONB, nullable=True)

    # Status
    status = sa.Column(
        sa.String, default="new", nullable=False
    )  # new, reviewed, archived
    user_action_taken = sa.Column(
        sa.String, nullable=True
    )  # ignored, noted, action_planned

    # Metadata
    detected_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    reviewed_at = sa.Column(sa.DateTime(timezone=True), nullable=True)


# --- Content Generation Model ---
class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)

    # Content details
    content_type = sa.Column(
        sa.String, nullable=False
    )  # social_post, blog_draft, prd_draft
    platform = sa.Column(sa.String, nullable=True)  # twitter, linkedin, medium
    title = sa.Column(sa.String, nullable=True)
    content = sa.Column(sa.Text, nullable=False)

    # Generation context
    prompt_used = sa.Column(sa.Text, nullable=True)
    source_data = sa.Column(
        JSONB, nullable=True
    )  # Reference to transcript, competitor update, etc.

    # User interaction
    status = sa.Column(
        sa.String, default="draft", nullable=False
    )  # draft, approved, published, rejected
    user_edits = sa.Column(sa.Text, nullable=True)
    final_version = sa.Column(sa.Text, nullable=True)

    # Metadata
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())


# --- AI Agent Activity Log ---
class AgentActivity(Base):
    __tablename__ = "agent_activities"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)

    # Agent details
    agent_type = sa.Column(
        sa.String, nullable=False
    )  # user_whisperer, market_maven, narrative_architect
    action = sa.Column(
        sa.String, nullable=False
    )  # transcript_processing_started, completed, failed

    # Activity details
    activity_metadata = sa.Column(JSONB, nullable=True)  # Flexible metadata storage
    status = sa.Column(sa.String, nullable=True)  # success, error, partial
    error_message = sa.Column(sa.Text, nullable=True)

    # Performance metrics
    processing_time_seconds = sa.Column(sa.Float, nullable=True)
    tokens_used = sa.Column(sa.Integer, nullable=True)

    # Metadata
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
