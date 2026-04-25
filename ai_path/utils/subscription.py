"""
Subscription & usage tracking for AIFetchPathly.

Simple JSON-file based storage. Tracks generations per user per month.
No auth required — uses a session UUID stored in session_state.

Tiers:
  free      — 3 generations / month (locked to standard preferences)
  basic     — 20 generations / month ($5, locked to standard preferences)
  pro       — 100 generations / month ($15, all preferences unlocked)
  unlimited — unlimited ($49, all preferences unlocked)
"""

from __future__ import annotations
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Tier definitions ────────────────────────────────────────────────────────────

TIERS: dict[str, dict] = {
    "free":      {"limit": 3,   "label": "Free",      "price": "$0/mo"},
    "basic":     {"limit": 20,  "label": "Basic",     "price": "$5/mo"},
    "pro":       {"limit": 100, "label": "Pro",       "price": "$15/mo"},
    "unlimited": {"limit": float("inf"), "label": "Unlimited", "price": "$49/mo"},
}

DEFAULT_TIER = "free"
USAGE_FILE = Path(__file__).parent.parent / ".usage_data.json"


# ── User ID ────────────────────────────────────────────────────────────────────

def get_user_id(session_state) -> str:
    """Get or create a persistent user ID from session_state."""
    if "user_id" not in session_state:
        session_state["user_id"] = str(uuid.uuid4())
    return session_state["user_id"]


# ── Persistence ─────────────────────────────────────────────────────────────────

def _load() -> dict[str, dict]:
    """Load all user records from JSON file."""
    if not USAGE_FILE.exists():
        return {}
    try:
        with open(USAGE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save(data: dict[str, dict]) -> None:
    """Write all user records to JSON file."""
    try:
        with open(USAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass


# ── Core API ───────────────────────────────────────────────────────────────────

def get_current_tier(user_id: str) -> str:
    """Return the user's current tier (default: free)."""
    data = _load()
    record = data.get(user_id, {})
    return record.get("tier", DEFAULT_TIER)


def set_tier(user_id: str, tier: str) -> None:
    """Upgrade/downgrade the user's tier."""
    if tier not in TIERS:
        tier = DEFAULT_TIER
    data = _load()
    if user_id not in data:
        data[user_id] = {"tier": tier, "generations": [], "month": ""}
    else:
        data[user_id]["tier"] = tier
    _save(data)


def get_usage(user_id: str) -> tuple[int, int, str]:
    """
    Return (used, limit, tier) for the current calendar month.
    Resets counter when month changes.
    """
    data = _load()
    record = data.get(user_id, {})
    tier = record.get("tier", DEFAULT_TIER)
    limit = TIERS[tier]["limit"]

    current_month = datetime.now().strftime("%Y-%m")
    stored_month = record.get("month", "")

    # Monthly reset
    if stored_month != current_month:
        used = 0
    else:
        used = len(record.get("generations", []))

    return used, limit, tier


def can_generate(user_id: str) -> bool:
    """Return True if the user has remaining generations this month."""
    used, limit, _ = get_usage(user_id)
    return used < limit


def record_generation(
    user_id: str,
    topic: str,
    level: str,
    report: str,
    preferences: Optional[dict] = None,
) -> None:
    """Record one successful generation for the user."""
    data = _load()
    current_month = datetime.now().strftime("%Y-%m")

    if user_id not in data:
        data[user_id] = {"tier": DEFAULT_TIER, "generations": [], "month": ""}

    record = data[user_id]

    # Reset if new month
    if record.get("month", "") != current_month:
        record["generations"] = []
        record["month"] = current_month

    record["generations"].append({
        "topic": topic,
        "level": level,
        "generated_at": datetime.now().isoformat(),
        "report_preview": report[:200] if report else "",
        "preferences": preferences or {},
    })

    _save(data)


def get_history(user_id: str) -> list[dict]:
    """Return the user's generation history for current month."""
    data = _load()
    record = data.get(user_id, {})
    current_month = datetime.now().strftime("%Y-%m")

    if record.get("month", "") != current_month:
        return []

    return list(reversed(record.get("generations", [])))


# ── Cost helpers ────────────────────────────────────────────────────────────────

def estimate_cost_per_generation() -> float:
    """Estimated LLM cost per learning path generation (USD)."""
    return 0.035  # GPT-4o-mini based estimate


def estimate_monthly_cost(generations: int) -> float:
    """Estimated API cost for N generations."""
    return round(generations * estimate_cost_per_generation(), 2)
