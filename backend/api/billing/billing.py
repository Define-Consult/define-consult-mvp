"""
Billing API endpoints for Define Consult
Implements Stripe integration for subscription management
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import Annotated, Optional, List
import logging
import stripe
import os
from datetime import datetime

from db.database import get_db
from dependencies import get_current_user_id
from models.models import User, Plan
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

router = APIRouter(prefix="/billing", tags=["Billing"])


# --- Pydantic Models ---


class PlanResponse(BaseModel):
    id: str
    name: str
    price_usd_per_month: float
    monthly_agent_action_limit: int
    stripe_price_id: str
    is_metered_billing: bool
    per_action_cost_usd: Optional[float] = None
    available_integrations: List[str]
    priority_support: bool
    is_team_plan: bool


class UsageResponse(BaseModel):
    current_plan: str
    agent_actions_used: int
    agent_actions_limit: int
    billing_period_start: str
    billing_period_end: str
    estimated_cost: float


class CheckoutSessionRequest(BaseModel):
    plan_id: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


# --- Endpoints ---


@router.get("/plans", response_model=List[PlanResponse])
async def get_available_plans(db: Annotated[Session, Depends(get_db)]):
    """
    Get all available billing plans
    """
    try:
        plans = db.query(Plan).filter(Plan.is_active == True).all()

        return [
            PlanResponse(
                id=plan.id,
                name=plan.name,
                price_usd_per_month=plan.price_usd_per_month,
                monthly_agent_action_limit=plan.monthly_agent_action_limit,
                stripe_price_id=plan.stripe_price_id,
                is_metered_billing=plan.is_metered_billing,
                per_action_cost_usd=plan.per_action_cost_usd,
                available_integrations=plan.available_integrations or [],
                priority_support=plan.priority_support,
                is_team_plan=plan.is_team_plan,
            )
            for plan in plans
        ]

    except Exception as e:
        logger.error(f"Error getting billing plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve billing plans")


@router.get("/usage", response_model=UsageResponse)
async def get_current_usage(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Get current user's billing usage information
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's current plan
        plan = db.query(Plan).filter(Plan.id == user.current_plan_id).first()
        plan_name = plan.name if plan else "Free"

        # Get usage stats from user's record
        usage_stats = user.usage_stats or {}
        agent_actions_used = usage_stats.get("total_agent_actions_this_month", 0)
        agent_actions_limit = (
            plan.monthly_agent_action_limit if plan else 25
        )  # Free plan limit

        return UsageResponse(
            current_plan=plan_name,
            agent_actions_used=agent_actions_used,
            agent_actions_limit=agent_actions_limit,
            billing_period_start="2024-12-01T00:00:00Z",  # This would be calculated from subscription
            billing_period_end="2024-12-31T23:59:59Z",
            estimated_cost=plan.price_usd_per_month if plan else 0.0,
        )

    except Exception as e:
        logger.error(f"Error getting usage information: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve usage information"
        )


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Create a Stripe checkout session for plan upgrade
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        plan = db.query(Plan).filter(Plan.id == request.plan_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        # Create or get Stripe customer
        customer_id = user.billing_customer_id
        if not customer_id:
            customer = stripe.Customer.create(
                email=user.email, name=user.name, metadata={"user_id": user.id}
            )
            customer_id = customer.id
            user.billing_customer_id = customer_id
            db.commit()

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                "user_id": user.id,
                "plan_id": plan.id,
            },
        )

        return CheckoutSessionResponse(
            checkout_url=session.url,
            session_id=session.id,
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.get("/manage-subscription")
async def manage_subscription(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Redirect to Stripe Customer Portal for subscription management
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.billing_customer_id:
            raise HTTPException(status_code=404, detail="No billing account found")

        # Create Customer Portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=user.billing_customer_id,
            return_url="https://your-domain.com/billing",  # Update with actual domain
        )

        return {"portal_url": portal_session.url}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating portal session: {e}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portal session")


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhooks for subscription events
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        if not STRIPE_WEBHOOK_SECRET:
            logger.warning("Stripe webhook secret not configured")
            raise HTTPException(status_code=400, detail="Webhook not configured")

        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )

        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            # Handle successful subscription creation
            logger.info(f"Checkout session completed: {session['id']}")

        elif event["type"] == "customer.subscription.created":
            subscription = event["data"]["object"]
            # Handle new subscription
            logger.info(f"Subscription created: {subscription['id']}")

        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            # Handle subscription changes
            logger.info(f"Subscription updated: {subscription['id']}")

        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            # Handle subscription cancellation
            logger.info(f"Subscription canceled: {subscription['id']}")

        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            # Handle successful payment
            logger.info(f"Payment succeeded: {invoice['id']}")

        elif event["type"] == "invoice.payment_failed":
            invoice = event["data"]["object"]
            # Handle failed payment
            logger.warning(f"Payment failed: {invoice['id']}")

        else:
            logger.info(f"Unhandled event type: {event['type']}")

        return {"status": "success"}

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Stripe signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


# --- Test Endpoints (No Auth Required) ---


@router.get("/test/plans", response_model=List[PlanResponse])
async def get_test_plans():
    """
    Get test billing plans (no auth required for development)
    """
    return [
        PlanResponse(
            id="free",
            name="Free",
            price_usd_per_month=0.0,
            monthly_agent_action_limit=25,
            stripe_price_id="price_test_free",
            is_metered_billing=False,
            available_integrations=["slack"],
            priority_support=False,
            is_team_plan=False,
        ),
        PlanResponse(
            id="pro",
            name="Pro",
            price_usd_per_month=74.99,
            monthly_agent_action_limit=500,
            stripe_price_id="price_test_pro",
            is_metered_billing=False,
            available_integrations=["slack", "zoom", "notion"],
            priority_support=True,
            is_team_plan=False,
        ),
        PlanResponse(
            id="team",
            name="Team",
            price_usd_per_month=349.99,
            monthly_agent_action_limit=5000,
            stripe_price_id="price_test_team",
            is_metered_billing=False,
            available_integrations=["slack", "zoom", "notion", "jira", "zendesk"],
            priority_support=True,
            is_team_plan=True,
        ),
    ]


@router.get("/test/usage", response_model=UsageResponse)
async def get_test_usage():
    """
    Get test usage information (no auth required for development)
    """
    return UsageResponse(
        current_plan="Pro",
        agent_actions_used=235,
        agent_actions_limit=500,
        billing_period_start="2024-12-01T00:00:00Z",
        billing_period_end="2024-12-31T23:59:59Z",
        estimated_cost=74.0,
    )
