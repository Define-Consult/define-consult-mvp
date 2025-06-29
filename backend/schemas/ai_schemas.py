"""
Pydantic schemas for AI Agent operations
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid


# --- Transcript Schemas ---
class TranscriptCreate(BaseModel):
    title: str = Field(..., description="Title for the transcript")
    content: str = Field(..., description="Raw transcript content")


class TranscriptResponse(BaseModel):
    id: str
    title: str
    status: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    has_results: bool = False

    class Config:
        from_attributes = True


class TranscriptProcessRequest(BaseModel):
    transcript_id: str = Field(..., description="ID of the transcript to process")


class TranscriptDetailResponse(BaseModel):
    id: str
    title: str
    status: str
    file_name: Optional[str] = None
    original_content: str
    processed_content: Optional[Dict] = None
    problem_statements: Optional[Dict] = None
    user_stories: Optional[Dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# --- Competitive Intelligence Schemas ---
class CompetitorWatchCreate(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    website_url: str = Field(..., description="Competitor's website URL")
    check_frequency: str = Field(default="daily", description="How often to check")


class CompetitorWatchResponse(BaseModel):
    id: str
    competitor_name: str
    website_url: str
    is_active: bool
    check_frequency: str
    last_checked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CompetitorUpdateResponse(BaseModel):
    id: str
    competitor_name: str
    update_type: str
    title: str
    description: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_impact_analysis: Optional[str] = None
    status: str
    detected_at: datetime

    class Config:
        from_attributes = True


# --- Content Generation Schemas ---
class ContentGenerationRequest(BaseModel):
    content_type: str = Field(..., description="Type of content to generate")
    platform: str = Field(default="linkedin", description="Target platform")
    input_text: str = Field(..., description="Description or context for content")


class GeneratedContentResponse(BaseModel):
    id: str
    content_type: str
    platform: Optional[str] = None
    title: Optional[str] = None
    content: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContentUpdateRequest(BaseModel):
    status: str = Field(..., description="New status for the content")
    user_edits: Optional[str] = Field(None, description="User's edits to the content")
    final_version: Optional[str] = Field(None, description="Final version of content")


# --- Agent Activity Schemas ---
class AgentActivityResponse(BaseModel):
    id: str
    agent_type: str
    action_type: str
    status: str
    processing_time_seconds: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Dashboard Schemas ---
class DashboardStatsResponse(BaseModel):
    total_transcripts: int
    completed_transcripts: int
    active_competitor_watches: int
    recent_competitor_updates: int
    generated_content_pieces: int
    agent_activities_today: int


class RecentActivityResponse(BaseModel):
    activity_type: str
    title: str
    description: str
    created_at: datetime
    status: str


# --- User Whisperer Specific Schemas ---
class ProblemStatement(BaseModel):
    title: str
    description: str
    priority: str
    frequency_mentioned: int


class UserStory(BaseModel):
    title: str
    story: str
    acceptance_criteria: List[str]
    priority: str
    estimated_effort: str


class ProcessedTranscriptResults(BaseModel):
    problem_statements: List[ProblemStatement]
    user_stories: List[UserStory]
    summary: str
    confidence_score: float = Field(default=0.8, description="AI confidence in results")


# --- Market Maven Specific Schemas ---
class CompetitorAnalysis(BaseModel):
    features: List[str]
    pricing_insights: str
    target_audience: str
    positioning: str
    threat_level: str
    opportunities: List[str]
    recommended_actions: List[str]


# --- Narrative Architect Specific Schemas ---
class SocialMediaVariation(BaseModel):
    content: str
    hashtags: List[str]
    cta: str


class SocialMediaContent(BaseModel):
    platform: str
    variations: List[SocialMediaVariation]
