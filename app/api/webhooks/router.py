import base64
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db_dep
from app.models.rbac.user import User
from app.models.subscription import Subscription
from app.models.webhook_event import WebhookEvent

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def _safe_json_loads(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def _verify_fastspring_signature(
    secret: str, body: bytes, signature_header: Optional[str]
) -> bool:
    if not secret:
        return True

    if not signature_header:
        return False

    sig = signature_header.strip()
    if "=" in sig and sig.lower().startswith("sha256"):
        sig = sig.split("=", 1)[1].strip()

    digest = hmac.new(secret.encode("utf-8"), body or b"", hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    try:
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False


def _parse_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        ts = float(value)
        if ts > 10_000_000_000:
            ts = ts / 1000.0
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

    return None


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


def _find_first_email(obj: Any) -> Optional[str]:
    if obj is None:
        return None
    if isinstance(obj, str):
        m = EMAIL_RE.search(obj)
        return m.group(0).lower() if m else None
    if isinstance(obj, dict):
        for k in ("email", "customerEmail", "buyerEmail"):
            v = obj.get(k)
            if isinstance(v, str) and EMAIL_RE.fullmatch(v.strip()):
                return v.strip().lower()
        for v in obj.values():
            got = _find_first_email(v)
            if got:
                return got
    if isinstance(obj, list):
        for v in obj:
            got = _find_first_email(v)
            if got:
                return got
    return None


def _extract_event_items(payload: Any) -> List[Dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [p for p in payload if isinstance(p, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("events"), list):
            return [e for e in payload.get("events") if isinstance(e, dict)]
        return [payload]
    return []


def _extract_subscription_id(event: Dict[str, Any]) -> Optional[str]:
    data = event.get("data") if isinstance(event.get("data"), dict) else event
    for k in ("subscription", "subscriptionId", "subscription_id", "subscriptionid"):
        v = data.get(k) if isinstance(data, dict) else None
        if v is not None:
            return str(v)
    # sometimes id is the subscription id for subscription.* webhooks
    if event.get("id") is not None:
        return str(event.get("id"))
    return None


def _extract_period_end(event: Dict[str, Any]) -> Optional[datetime]:
    data = event.get("data") if isinstance(event.get("data"), dict) else event
    if not isinstance(data, dict):
        return None
    for k in (
        "nextChargeDate",
        "nextCharge",
        "nextPaymentDate",
        "currentPeriodEnd",
        "current_period_end",
        "periodEnd",
        "end",
    ):
        dt = _parse_dt(data.get(k))
        if dt:
            return dt
    return None


def _guess_plan_code(event: Dict[str, Any]) -> Optional[str]:
    allowed = {"basic_monthly", "basic_yearly", "pro_monthly", "pro_yearly"}
    blob = json.dumps(event, ensure_ascii=False).lower()
    tier = None
    if "pro" in blob:
        tier = "pro"
    elif "basic" in blob:
        tier = "basic"
    if not tier:
        return None
    cadence = "yearly" if any(x in blob for x in ("year", "annual")) else "monthly"
    plan_code = f"{tier}_{cadence}"
    return plan_code if plan_code in allowed else None


def _apply_subscription_update(
    *,
    db: Session,
    user: User,
    provider_subscription_id: Optional[str],
    event_type: str,
    event: Dict[str, Any],
):
    sub = None

    if provider_subscription_id:
        sub = (
            db.query(Subscription)
            .filter(
                Subscription.provider == "fastspring",
                Subscription.provider_subscription_id == provider_subscription_id,
            )
            .first()
        )

    if not sub:
        sub = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == int(user.id),
                Subscription.provider == "fastspring",
            )
            .first()
        )

    plan_code = _guess_plan_code(event)

    if not sub:
        if not plan_code:
            return False
        sub = Subscription(
            user_id=int(user.id), provider="fastspring", plan_code=plan_code
        )
        db.add(sub)

    if provider_subscription_id:
        sub.provider_subscription_id = provider_subscription_id

    if plan_code:
        sub.plan_code = plan_code

    et = str(event_type or "").lower()
    if et == "subscription.activated":
        sub.status = "active"
        sub.cancel_at_period_end = False
        if sub.current_period_start is None:
            sub.current_period_start = datetime.now(timezone.utc)
    elif et == "subscription.canceled":
        sub.status = sub.status or "active"
        sub.cancel_at_period_end = True
    elif et == "subscription.uncanceled":
        sub.cancel_at_period_end = False
        if not sub.status:
            sub.status = "active"
    elif et == "subscription.deactivated":
        sub.status = "canceled"
        sub.cancel_at_period_end = True

    period_end = _extract_period_end(event)
    if period_end:
        sub.current_period_end = period_end

    return True


@router.post("/fastspring", status_code=202)
async def fastspring_webhook(request: Request, db: Session = Depends(get_db_dep)):
    body = await request.body()
    payload = _safe_json_loads(body)

    secret = str(getattr(settings, "FASTSPRING_WEBHOOK_SECRET", "") or "")
    sig = request.headers.get("X-FS-Signature")
    if not _verify_fastspring_signature(secret, body, sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature"
        )

    evt = WebhookEvent(provider="fastspring")
    evt.payload_json = body.decode("utf-8", errors="replace") if body else "{}"
    evt.headers_json = json.dumps(dict(request.headers), ensure_ascii=False)
    db.add(evt)
    db.commit()
    db.refresh(evt)

    if not body:
        evt.processed = False
        evt.error = "Empty webhook body"
        db.commit()
        return {"status": "accepted"}

    try:
        items = _extract_event_items(payload)
        if not items:
            evt.error = "Unable to parse webhook payload"
            evt.processed = False
            db.commit()
            return {"status": "accepted"}

        processed_any = False
        for event in items:
            event_type = str(event.get("type") or event.get("eventType") or "")
            if not event_type:
                event_type = (
                    str(payload.get("type") or "") if isinstance(payload, dict) else ""
                )

            email = _find_first_email(event)
            if not email:
                continue

            user = db.query(User).filter(User.email.ilike(email)).first()
            if not user:
                continue

            provider_subscription_id = _extract_subscription_id(event)
            updated = _apply_subscription_update(
                db=db,
                user=user,
                provider_subscription_id=provider_subscription_id,
                event_type=event_type,
                event=event,
            )
            if updated:
                processed_any = True

        if processed_any:
            evt.processed = True
            evt.error = None
        else:
            evt.processed = False
            evt.error = "No subscription update applied (missing user/email or unknown plan mapping)"

        first = items[0]
        if first.get("id") is not None:
            evt.event_id = str(first.get("id"))
        if first.get("type") is not None:
            evt.event_type = str(first.get("type"))

        db.commit()
    except Exception as e:
        evt.processed = False
        evt.error = str(e)
        db.commit()

    return {"status": "accepted"}
