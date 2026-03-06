from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import re
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db_dep
from app.core.config import settings
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionMeResponse

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


def _is_active(sub: Subscription) -> bool:
    if not sub:
        return False

    status = str(sub.status or "").lower()
    if status not in {"active", "trial", "trialing"}:
        return False

    if sub.current_period_end is None:
        return True

    now = datetime.now(timezone.utc)
    end = sub.current_period_end
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    return end > now


def _effective_plan(plan_code: str) -> str:
    code = str(plan_code or "").strip().lower()
    if code.startswith("pro"):
        return "Pro"
    if code.startswith("basic"):
        return "Basic"
    return "Free"


class DevSeedSubscriptionRequest(BaseModel):
    plan_code: str


@router.get("/me", response_model=SubscriptionMeResponse)
def get_my_subscription(db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == int(current_user.id))
        .order_by(Subscription.id.desc())
        .first()
    )

    if not sub or not _is_active(sub):
        return SubscriptionMeResponse(effective_plan="Free")

    return SubscriptionMeResponse(
        effective_plan=_effective_plan(sub.plan_code),
        plan_code=sub.plan_code,
        status=sub.status,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=bool(sub.cancel_at_period_end),
    )


@router.post("/dev/seed", response_model=SubscriptionMeResponse)
def dev_seed_my_subscription(
    payload: DevSeedSubscriptionRequest,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    # Dev guard: allow only when running with the default dev SECRET_KEY, or for superusers.
    if settings.SECRET_KEY != "dev-secret-change-me" and not bool(getattr(current_user, "is_superuser", False)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dev endpoint is disabled")

    plan_code_raw = str(payload.plan_code or "").strip().lower()
    plan_code = re.sub(r"[^a-z0-9]+", "_", plan_code_raw).strip("_")
    allowed = {"basic_monthly", "basic_yearly", "pro_monthly", "pro_yearly"}
    if plan_code not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid plan_code. Allowed: {', '.join(sorted(allowed))}")

    now = datetime.now(timezone.utc)
    duration_days = 365 if plan_code.endswith("yearly") else 30
    period_end = now + timedelta(days=duration_days)

    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == int(current_user.id), Subscription.provider == "fastspring")
        .first()
    )

    if not sub:
        sub = Subscription(user_id=int(current_user.id), provider="fastspring")
        db.add(sub)

    sub.provider_subscription_id = f"dev_{int(current_user.id)}"
    sub.plan_code = plan_code
    sub.status = "active"
    sub.current_period_start = now
    sub.current_period_end = period_end
    sub.cancel_at_period_end = False

    db.commit()
    db.refresh(sub)

    return SubscriptionMeResponse(
        effective_plan=_effective_plan(sub.plan_code),
        plan_code=sub.plan_code,
        status=sub.status,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=bool(sub.cancel_at_period_end),
    )
