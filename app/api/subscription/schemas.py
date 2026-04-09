from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SubscriptionMeResponse(BaseModel):
    effective_plan: str
    plan_code: Optional[str] = None
    status: Optional[str] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None

    model_config = {"from_attributes": True}
