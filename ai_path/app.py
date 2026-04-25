import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from ai_path.pipeline import build_graph
from ai_path.models.schemas import PipelineState
from ai_path.utils.subscription import (
    get_user_id, get_current_tier, set_tier,
    get_usage, record_generation,
    get_history, TIERS, estimate_monthly_cost,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AIFetchPathly — Research-Driven Learning Paths",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 AIFetchPathly")
st.caption(
    "Searches the web for real tutorials, summarises them, "
    "then builds your personalised learning path — grounded in what actually exists."
)

# ── Init session ───────────────────────────────────────────────────────────────
user_id = get_user_id(st.session_state)
current_tier = get_current_tier(user_id)

# ── Preference definitions ───────────────────────────────────────────────────────
LEARNING_DEPTH_OPTIONS = ["quick", "standard", "deep"]
CONTENT_TYPE_OPTIONS = ["video", "article", "mixed"]
RESOURCE_COUNT_OPTIONS = ["compact", "standard", "rich"]
PRACTICAL_RATIO_OPTIONS = ["theory_first", "balanced", "practice_first"]

PREFERENCE_LABELS = {
    "learning_depth": {
        "quick": "⚡ Quick intro",
        "standard": "📚 Standard path",
        "deep": "🧠 Deep dive",
    },
    "content_type": {
        "video": "🎬 Video-focused",
        "article": "📝 Article-focused",
        "mixed": "⚖️ Mixed",
    },
    "resource_count": {
        "compact": "5 resources (concise)",
        "standard": "10 resources (balanced)",
        "rich": "15 resources (comprehensive)",
    },
    "practical_ratio": {
        "theory_first": "🧠 Theory → Practice",
        "balanced": "⚖️ Theory & Practice balance",
        "practice_first": "🛠️ Practice → Theory",
    },
}

# Free/Basic tiers are locked to standard options only
LOCKED_TIERS = {"free", "basic"}


# ── Sidebar: subscription UI ───────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    st.info(
        "Add a `.env` file with:\n"
        "- `OPENAI_API_KEY`\n"
        "- `TAVILY_API_KEY` **or** `SERPER_API_KEY`\n"
        "- `SEARCH_PROVIDER` = `tavily` or `serper`\n"
        "- `LLM_PROVIDER` = `openai` (default) or `minimax`"
    )
    st.divider()

    # ── Tier selector ──────────────────────────────────────────────────────────
    st.markdown("### 📦 Subscription Tier")
    tier_key = st.selectbox(
        "Select your plan",
        options=list(TIERS.keys()),
        index=list(TIERS.keys()).index(current_tier),
        format_func=lambda t: f"{TIERS[t]['label']} — {TIERS[t]['price']} ({TIERS[t]['limit']} gen/mo)",
    )
    if tier_key != current_tier:
        set_tier(user_id, tier_key)
        st.rerun()

    # ── Usage meter ────────────────────────────────────────────────────────────
    used, limit, tier = get_usage(user_id)
    if limit == float("inf"):
        remaining = "∞"
        pct = 100.0
    else:
        remaining = limit - used
        pct = (used / limit) * 100 if limit > 0 else 0

    st.markdown(f"**This month:** {used} / {limit if limit != float('inf') else '∞'} generations used")
    st.progress(min(pct / 100, 1.0), text=f"{remaining} remaining" if remaining != "∞" else "unlimited")

    if remaining == 0:
        st.warning("⚠️ Monthly limit reached. Upgrade your plan to continue.")
    elif remaining != "∞" and remaining <= 2:
        st.info(f"⚡ Only {remaining} generation{'s' if remaining > 1 else ''} left this month.")

    # ── Cost estimate ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 💰 Cost Estimate")
    cost_per_gen = estimate_monthly_cost(1)
    st.caption(f"~${cost_per_gen:.2f} API cost per generation\n(GPT-4o-mini, Brave Search)")

    # ── History ───────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📜 Generation History")
    history = get_history(user_id)
    if history:
        for item in history[:5]:
            prefs = item.get("preferences", {})
            pref_str = ""
            if prefs:
                depth = prefs.get("learning_depth", "standard")
                ratio = prefs.get("practical_ratio", "balanced")
                pref_str = f" ({PREFERENCE_LABELS['learning_depth'][depth]} · {PREFERENCE_LABELS['practical_ratio'][ratio]})"
            st.caption(f"**{item['topic']}** ({item['level']}){pref_str}\n{item['generated_at'][:10]}")
    else:
        st.caption("No generations yet this month.")

    st.divider()
    st.markdown("**Pipeline stages**")
    st.markdown(
        "1. 🔎 Generate search queries\n"
        "2. 🌐 Search the web\n"
        "3. 📥 Fetch & extract pages\n"
        "4. 🧠 Summarise each resource\n"
        "5. 🗂️ Organise into sections\n"
        "6. ✍️ Write your learning path"
    )

# ── Main input ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input(
        "What do you want to learn?",
        placeholder="e.g. FastAPI, Kubernetes, Machine Learning with PyTorch",
    )
with col2:
    level = st.selectbox("Your level", ["beginner", "intermediate", "advanced"])

# ── Learning path preferences ─────────────────────────────────────────────────
st.markdown("### 🎯 Learning Path Preferences")
if current_tier in LOCKED_TIERS:
    st.info(f"💡 **Free/Basic plan** — locked to standard preferences. Upgrade to Pro to unlock all options.")

pref_cols = st.columns(2)

with pref_cols[0]:
    # Learning depth — locked for free/basic
    if current_tier in LOCKED_TIERS:
        learning_depth = "standard"
        st.selectbox(
            "Learning depth",
            options=["standard"],
            format_func=lambda x: PREFERENCE_LABELS["learning_depth"][x],
            disabled=True,
        )
        st.caption("🔒 *Upgrade to Pro for Quick intro & Deep dive*")
    else:
        learning_depth = st.selectbox(
            "Learning depth",
            options=LEARNING_DEPTH_OPTIONS,
            index=LEARNING_DEPTH_OPTIONS.index("standard"),
            format_func=lambda x: PREFERENCE_LABELS["learning_depth"][x],
        )

    # Content type — locked for free/basic
    if current_tier in LOCKED_TIERS:
        content_type = "mixed"
        st.selectbox(
            "Content type",
            options=["mixed"],
            format_func=lambda x: PREFERENCE_LABELS["content_type"][x],
            disabled=True,
        )
        st.caption("🔒 *Upgrade to Pro for Video & Article focus*")
    else:
        content_type = st.selectbox(
            "Content type",
            options=CONTENT_TYPE_OPTIONS,
            index=CONTENT_TYPE_OPTIONS.index("mixed"),
            format_func=lambda x: PREFERENCE_LABELS["content_type"][x],
        )

with pref_cols[1]:
    # Resource count — locked for free/basic
    if current_tier in LOCKED_TIERS:
        resource_count = "standard"
        st.selectbox(
            "Resource count",
            options=["standard"],
            format_func=lambda x: PREFERENCE_LABELS["resource_count"][x],
            disabled=True,
        )
        st.caption("🔒 *Upgrade to Pro for compact & rich*")
    else:
        resource_count = st.selectbox(
            "Resource count",
            options=RESOURCE_COUNT_OPTIONS,
            index=RESOURCE_COUNT_OPTIONS.index("standard"),
            format_func=lambda x: PREFERENCE_LABELS["resource_count"][x],
        )

    # Practical ratio — locked for free/basic
    if current_tier in LOCKED_TIERS:
        practical_ratio = "balanced"
        st.selectbox(
            "Theory/Practice balance",
            options=["balanced"],
            format_func=lambda x: PREFERENCE_LABELS["practical_ratio"][x],
            disabled=True,
        )
        st.caption("🔒 *Upgrade to Pro for Theory-first & Practice-first*")
    else:
        practical_ratio = st.selectbox(
            "Theory/Practice balance",
            options=PRACTICAL_RATIO_OPTIONS,
            index=PRACTICAL_RATIO_OPTIONS.index("balanced"),
            format_func=lambda x: PREFERENCE_LABELS["practical_ratio"][x],
        )

# ── Check before running ───────────────────────────────────────────────────────
used, limit, _ = get_usage(user_id)
at_limit = (limit != float("inf")) and (used >= limit)

if at_limit:
    run_btn = st.button("🚀 Build My Learning Path", type="primary", disabled=True)
    st.error("❌ Monthly generation limit reached. Please upgrade your plan above.")
else:
    run_btn = st.button("🚀 Build My Learning Path", type="primary", disabled=not topic)

# ── Stage labels ───────────────────────────────────────────────────────────────
STAGE_LABELS = {
    "search":    "🌐 Searching the web for resources...",
    "fetch":     "📥 Fetching & extracting page content...",
    "summarize": "🧠 Summarising each resource with AI...",
    "organize":  "🗂️  Organising resources into a learning path...",
    "report":    "✍️  Writing your personalised learning path...",
    "done":      "✅ Done!",
    "error":     "❌ An error occurred.",
}

# ── Run pipeline ───────────────────────────────────────────────────────────────
if run_btn and topic:
    progress_ph = st.empty()
    metrics_ph  = st.empty()
    report_ph   = st.empty()

    progress_ph.info("🔎 Generating search queries...")

    def run_pipeline(topic: str, level: str, learning_depth: str, content_type: str, resource_count: str, practical_ratio: str) -> dict:
        import asyncio
        graph = build_graph()
        initial: PipelineState = {
            "topic": topic,
            "level": level,
            "learning_depth": learning_depth,
            "content_type": content_type,
            "resource_count": resource_count,
            "practical_ratio": practical_ratio,
            "current_stage": "search",
        }
        result: dict = {}
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def _stream():
                async for event in graph.astream_events(initial, version="v2"):
                    if event["event"] == "on_chain_end":
                        output = event.get("data", {}).get("output", {})
                        if isinstance(output, dict):
                            stage = output.get("current_stage", "")
                            if stage:
                                result["_stage"] = stage
                            if "queries" in output:
                                result["_n_queries"] = len(output["queries"])
                            if "search_results" in output:
                                result["_n_results"] = len(output["search_results"])
                            if "fetched_pages" in output:
                                result["_n_pages"] = len(output["fetched_pages"])
                            if "summaries" in output:
                                result["_n_summaries"] = len(output["summaries"])
                            if output.get("final_report"):
                                result["_report"] = output["final_report"]
                            if output.get("error"):
                                result["_error"] = output["error"]
            loop.run_until_complete(_stream())
        finally:
            loop.close()
        return result

    import time
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_pipeline, topic, level, learning_depth, content_type, resource_count, practical_ratio)
        while not future.done():
            time.sleep(1.5)

    result = future.result()

    # ── Display results ────────────────────────────────────────────────────────
    if result.get("_error"):
        progress_ph.error(f"❌ {result['_error']}")
    elif result.get("_report"):
        stage = result.get("_stage", "done")
        progress_ph.success("✅ Your learning path is ready!")

        # Record generation (deduct from quota) — include preferences
        record_generation(
            user_id, topic, level, result["_report"],
            preferences={
                "learning_depth": learning_depth,
                "content_type": content_type,
                "resource_count": resource_count,
                "practical_ratio": practical_ratio,
            }
        )

        # Metrics row
        cols = metrics_ph.columns(4)
        cols[0].metric("Search Queries", result.get("_n_queries", "—"))
        cols[1].metric("Web Results", result.get("_n_results", "—"))
        cols[2].metric("Pages Fetched", result.get("_n_pages", "—"))
        cols[3].metric("Resources Summarised", result.get("_n_summaries", "—"))

        report_ph.markdown(result["_report"])

        # Refresh usage display
        st.rerun()
    else:
        stage = result.get("_stage", "unknown")
        label = STAGE_LABELS.get(stage, stage)
        progress_ph.warning(f"⚠️ Pipeline stopped at: {label}")
