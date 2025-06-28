from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import datetime

class PlanCreate(BaseModel):
    name: str = Field(..., description="Name of the plan (e.g., 'Free', 'Pro', 'Team').")
    stripe_price_id: Optional[str] = Field(None, description="Stripe Price ID for this plan.")
    monthly_agent_action_limit: int = Field(..., description="Monthly limit of agent actions.")
    price_usd_per_month: float = Field(..., description="Monthly price in USD.")
    is_metered_billing: bool = Field(False, description="True if billing is metered per action after limit.")
    per_action_cost_usd: Optional[float] = Field(None, description="Cost per action if metered billing is enabled.")
    available_integrations: List[str] = Field([], description="List of integrations available with this plan.")
    priority_support: bool = Field(False, description="True if priority support is included.")
    is_team_plan: bool = Field(False, description="True if this is a team-level plan.")

class PlanResponse(BaseModel):
    id: int
    name: str
    stripe_price_id: Optional[str] = None
    monthly_agent_action_limit: int
    price_usd_per_month: float
    is_metered_billing: bool
    per_action_cost_usd: Optional[float] = None
    available_integrations: List[str]
    priority_support: bool
    is_team_plan: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True 

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    stripe_price_id: Optional[str] = None
    monthly_agent_action_limit: Optional[int] = None
    price_usd_per_month: Optional[float] = None
    is_metered_billing: Optional[bool] = None
    per_action_cost_usd: Optional[float] = None
    available_integrations: Optional[List[str]] = None
    priority_support: Optional[bool] = None
    is_team_plan: Optional[bool] = None