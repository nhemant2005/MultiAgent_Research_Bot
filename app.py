import streamlit as st
from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain, reviser_chain
from src.rate_limiter import consume_request, get_status, DAILY_LIMIT
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Research Bot",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── Global ─────────────────────────────────── */
    [data-testid="stAppViewContainer"] {
        background: #0e1117;
    }
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }

    /* ── Hero card ───────────────────────────────── */
    .hero {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f2744 60%, #0e1117 100%);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 44px 40px;
        text-align: center;
        margin-bottom: 28px;
    }
    .hero h1 { font-size: 2.4rem; font-weight: 800; color: #f1f5f9; margin: 0 0 8px 0; }
    .hero p  { font-size: 1.05rem; color: #94a3b8; margin: 0; }

    /* ── Sidebar step cards ──────────────────────── */
    .step-card {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        background: #1f2937;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .step-icon {
        font-size: 1.2rem;
        line-height: 1;
        padding-top: 2px;
    }
    .step-title { font-weight: 600; color: #e2e8f0; font-size: 0.88rem; }
    .step-desc  { color: #6b7280; font-size: 0.78rem; margin-top: 2px; }

    /* ── Pill badges ─────────────────────────────── */
    .pill {
        display: inline-block;
        background: #1e3a5f;
        color: #60a5fa;
        border-radius: 999px;
        padding: 3px 11px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 3px 3px 3px 0;
        border: 1px solid #2563eb44;
    }

    /* ── Result section headers ──────────────────── */
    .result-header {
        font-size: 1rem;
        font-weight: 700;
        color: #e2e8f0;
        padding: 10px 0 6px 0;
        border-bottom: 2px solid #1e3a5f;
        margin-bottom: 14px;
        letter-spacing: 0.01em;
    }

    /* ── Topic chip shown above results ─────────── */
    .topic-chip {
        display: inline-block;
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 6px 16px;
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 18px;
    }
    .topic-chip strong { color: #e2e8f0; }

    /* ── Hide Streamlit footer/menu ──────────────── */
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 Research Bot")
    st.markdown("<hr style='border-color:#1f2937;margin:8px 0 16px 0'>", unsafe_allow_html=True)

    st.markdown("**How it works**")
    steps = [
        ("🔍", "Search Agent",  "Queries Tavily for recent, reliable sources"),
        ("📄", "Reader Agent",  "Picks the best URL and scrapes its content"),
        ("✍️",  "Writer Chain",  "Drafts a structured, in-depth report"),
        ("🏆", "Critic Chain",  "Scores the report and suggests improvements"),
        ("🔄", "Reviser Chain", "Rewrites the report based on critic feedback"),
    ]
    for icon, title, desc in steps:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-icon">{icon}</div>
            <div>
                <div class="step-title">{title}</div>
                <div class="step-desc">{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1f2937;margin:16px 0 10px 0'>", unsafe_allow_html=True)
    st.markdown("**Stack**")
    st.markdown("""
    <div>
        <span class="pill">DeepSeek V4 Flash</span>
        <span class="pill">Tavily Search</span>
        <span class="pill">LangChain</span>
        <span class="pill">LangGraph</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1f2937;margin:16px 0 10px 0'>", unsafe_allow_html=True)
    _used, _limit = get_status()
    st.markdown("**Daily Usage**")
    st.progress(_used / _limit, text=f"{_used} / {_limit} requests used today")
    if _used >= _limit:
        st.error("Daily limit reached. Resets at midnight UTC.", icon="🚫")

    st.markdown("")
    st.info("Thinking mode is disabled so agents work correctly with multi-turn tool calls.", icon="ℹ️")

# ── Session state ──────────────────────────────────────────────────────────
if "results"    not in st.session_state: st.session_state.results    = None
if "last_topic" not in st.session_state: st.session_state.last_topic = ""

# ── Hero ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🔬 MultiAgent Research Bot</h1>
    <p>Enter any topic — get a fully researched, written, and peer-reviewed report in minutes.</p>
</div>""", unsafe_allow_html=True)

# ── Input row ──────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([6, 1])
with col_in:
    topic = st.text_input(
        "topic",
        placeholder="e.g. the rise of agentic AI systems in 2026",
        label_visibility="collapsed",
    )
with col_btn:
    _used_now, _ = get_status()
    _limit_reached = _used_now >= DAILY_LIMIT
    run = st.button(
        "🚀 Research",
        type="primary",
        disabled=not topic.strip() or _limit_reached,
        use_container_width=True,
        help="Daily request limit reached. Please try again tomorrow." if _limit_reached else None,
    )

if st.session_state.last_topic:
    with st.chat_message("user"):
        st.markdown(st.session_state.last_topic)

# ── Pipeline ───────────────────────────────────────────────────────────────
if run:
    _allowed, _count, _daily_limit = consume_request()
    if not _allowed:
        st.error(f"Daily limit of {_daily_limit} requests reached. Please try again tomorrow.")
        st.stop()

    st.session_state.results    = None
    st.session_state.last_topic = topic
    state = {}

    with st.status("🔍 Step 1 — Searching the web...", expanded=True) as s:
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        state["search_results"] = search_result["messages"][-1].content
        s.update(label="✅ Step 1 — Search complete", state="complete", expanded=False)

    with st.status("📄 Step 2 — Scraping top sources...", expanded=True) as s:
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:800]}"
            )]
        })
        state["scraped_content"] = reader_result["messages"][-1].content
        s.update(label="✅ Step 2 — Scraping complete", state="complete", expanded=False)

    with st.status("✍️ Step 3 — Writing report...", expanded=True) as s:
        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
        s.update(label="✅ Step 3 — Report drafted", state="complete", expanded=False)

    with st.status("🏆 Step 4 — Reviewing report...", expanded=True) as s:
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        s.update(label="✅ Step 4 — Review complete", state="complete", expanded=False)

    with st.status("🔄 Step 5 — Revising based on feedback...", expanded=True) as s:
        state["revised_report"] = reviser_chain.invoke({
            "topic": topic,
            "report": state["report"],
            "feedback": state["feedback"],
        })
        s.update(label="✅ Step 5 — Revision complete", state="complete", expanded=False)

    st.session_state.results = state
    st.success("Research complete! Your report is ready below.", icon="✅")

# ── Results ────────────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="result-header">📄 Final Report (Revised)</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(results["revised_report"])

    with col2:
        st.markdown('<div class="result-header">🏆 Critic Feedback</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(results["feedback"])

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("✍️ Original Draft (before revision)"):
        st.markdown(results["report"])
    with st.expander("🔍 Raw Search Results"):
        st.code(results["search_results"], language=None)
    with st.expander("🌐 Scraped Content"):
        st.code(results["scraped_content"], language=None)
