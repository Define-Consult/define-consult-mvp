import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from db.database import Base


from models.ai_models import (
    Transcript,
    CompetitorWatch,
    CompetitorUpdate,
    GeneratedContent,
    AgentActivity,
)


# --- Plan Model ---
class Plan(Base):
    __tablename__ = "plans"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, index=True, nullable=False)
    stripe_price_id = sa.Column(sa.String, nullable=True)
    monthly_agent_action_limit = sa.Column(sa.Integer, nullable=False)
    price_usd_per_month = sa.Column(sa.Numeric(10, 2), nullable=False)
    is_metered_billing = sa.Column(sa.Boolean, default=False, nullable=False)
    per_action_cost_usd = sa.Column(sa.Numeric(10, 4), nullable=True)
    available_integrations = sa.Column(JSONB, nullable=False, default=[])
    priority_support = sa.Column(sa.Boolean, default=False, nullable=False)
    is_team_plan = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())


# --- User Model ---
class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    firebase_uid = sa.Column(sa.String, unique=True, index=True, nullable=False)
    email = sa.Column(sa.String, unique=True, index=True, nullable=False)
    name = sa.Column(sa.String)
    avatar_url = sa.Column(sa.String)
    company_name = sa.Column(sa.String)
    role_at_company = sa.Column(sa.String)
    industry = sa.Column(sa.String)
    linkedin_profile_url = sa.Column(sa.String)
    current_plan_id = sa.Column(sa.Integer, sa.ForeignKey("plans.id"))
    billing_customer_id = sa.Column(sa.String)
    usage_stats = sa.Column(JSONB)
    notification_preferences = sa.Column(JSONB)
    brand_tone_preferences = sa.Column(JSONB)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())
