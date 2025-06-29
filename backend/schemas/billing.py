from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class BillingPlan(BaseModel):
    """Schema for billing plan response"""

    id: int
    name: str
    stripe_price_id: Optional[str] = None
    monthly_agent_action_limit: int
    price_usd_per_month: float
    is_metered_billing: bool = False
    per_action_cost_usd: Optional[float] = None
    available_integrations: List[str] = []
    priority_support: bool = False
    is_team_plan: bool = False
    features: List[str] = []

    class Config:
        from_attributes = True


class UserUsage(BaseModel):
    """Schema for user usage response"""

    current_period_start: datetime
    current_period_end: datetime
    agent_actions_used: int
    agent_actions_limit: int
    remaining_actions: int
    usage_percentage: float


class BillingInfo(BaseModel):
    """Schema for user billing information"""

    current_plan: BillingPlan
    usage: UserUsage
    subscription_status: Optional[SubscriptionStatus] = None
    trial_end: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None


class CheckoutSessionRequest(BaseModel):
    """Schema for creating Stripe checkout session"""

    price_id: str = Field(..., description="Stripe price ID for the plan")
    success_url: str = Field(
        ..., description="URL to redirect after successful payment"
    )
    cancel_url: str = Field(..., description="URL to redirect after canceled payment")


class CheckoutSessionResponse(BaseModel):
    """Schema for checkout session response"""

    session_id: str
    url: str


class WebhookEvent(BaseModel):
    """Schema for Stripe webhook events"""

    id: str
    object: str
    api_version: Optional[str] = None
    created: int
    data: Dict
    livemode: bool
    pending_webhooks: int
    request: Optional[Dict] = None
    type: str
