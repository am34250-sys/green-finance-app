import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Green Finance Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================
# CSS — match the mockup
# =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; box-sizing: border-box; }
.stApp { background: #f5f6f8; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
.block-container { padding: 22px 28px !important; max-width: 100% !important; }

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: #0f1729 !important;
    min-width: 250px !important;
    max-width: 250px !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div { padding-top: 14px; }
section[data-testid="stSidebar"] * { color: #a8b2c7 !important; }

.brand {
    display:flex; align-items:center; gap:10px;
    padding: 10px 14px 22px 14px;
}
.brand-logo {
    width:38px; height:38px; border-radius:10px;
    background: linear-gradient(135deg,#10b981,#059669);
    display:flex; align-items:center; justify-content:center;
    font-size:20px;
}
.brand-text { line-height:1.15; }
.brand-text .t1 { color:#fff !important; font-weight:700; font-size:14px; }
.brand-text .t2 { color:#fff !important; font-weight:700; font-size:14px; }

/* sidebar buttons as nav items */
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: none !important;
    color: #a8b2c7 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    margin: 2px 8px !important;
    width: calc(100% - 16px) !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #1a2235 !important;
    color: #fff !important;
}
section[data-testid="stSidebar"] .stButton button[kind="primary"],
section[data-testid="stSidebar"] .nav-active button {
    background: #10b981 !important;
    color: #fff !important;
}

.side-user {
    margin: 18px 12px 10px 12px;
    padding: 12px;
    background:#1a2235;
    border-radius:12px;
    display:flex; align-items:center; gap:10px;
}
.side-user .av {
    width:36px;height:36px;border-radius:50%;
    background:linear-gradient(135deg,#10b981,#059669);
    display:flex;align-items:center;justify-content:center;
    color:#fff !important; font-weight:700; font-size:13px;
}
.side-user .nm { color:#fff !important; font-weight:600; font-size:13px; }
.side-user .rl { color:#7c879b !important; font-size:11px; }

.side-market {
    margin: 10px 12px;
    padding: 14px;
    background:#1a2235;
    border-radius:12px;
}
.side-market .lbl { font-size:11px; color:#7c879b !important; text-transform:uppercase; letter-spacing:.5px; }
.side-market .sp { font-size:12px; color:#a8b2c7 !important; margin-top:4px; }
.side-market .val { color:#fff !important; font-size:22px; font-weight:700; margin-top:6px; }
.side-market .chg { color:#10b981 !important; font-size:12px; font-weight:600; margin-top:2px; }
.side-market .upd { color:#5b6478 !important; font-size:10px; margin-top:10px; }

/* ---------- HEADER ---------- */
.page-title { font-size: 22px; font-weight: 700; color:#0f1729; margin:0; }
.page-sub { font-size: 13px; color:#6b7280; margin-top:4px; }
.search-bar {
    background:#fff; border:1px solid #e5e7eb; border-radius:10px;
    padding:9px 14px; font-size:12.5px; color:#9ca3af;
    display:flex; align-items:center; gap:8px;
}
.live-pill {
    background:#ecfdf5; color:#059669; border:1px solid #a7f3d0;
    padding:6px 12px; border-radius:999px;
    font-size:11.5px; font-weight:600;
    display:inline-flex; align-items:center; gap:6px;
}
.live-dot { width:7px;height:7px;background:#10b981;border-radius:50%; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ---------- KPI CARDS ---------- */
.kpi {
    background:#fff; border:1px solid #eef0f4; border-radius:14px;
    padding:18px 18px 14px 18px;
    box-shadow:0 1px 2px rgba(16,24,40,.04);
}
.kpi-top { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.kpi-ico {
    width:36px;height:36px;border-radius:9px;
    display:flex;align-items:center;justify-content:center;font-size:17px;
}
.kpi-ico.g { background:#ecfdf5; }
.kpi-ico.r { background:#fef2f2; }
.kpi-ico.b { background:#eff6ff; }
.kpi-ico.y { background:#fefce8; }
.kpi-label { font-size:12px; color:#6b7280; font-weight:500; }
.kpi-value { font-size:30px; font-weight:700; color:#0f1729; line-height:1.1; }
.kpi-foot { display:flex; align-items:center; justify-content:space-between; margin-top:8px; }
.kpi-trend { font-size:11.5px; font-weight:500; }
.t-up { color:#059669; } .t-dn { color:#dc2626; }

/* ---------- SECTION CARD ---------- */
.card {
    background:#fff; border:1px solid #eef0f4; border-radius:14px;
    box-shadow:0 1px 2px rgba(16,24,40,.04);
    padding:18px 20px; margin-bottom:18px;
}
.card-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.card-title { font-size:14.5px; font-weight:600; color:#0f1729; display:flex; align-items:center; gap:8px; }
.green-dot { width:8px;height:8px;border-radius:50%; background:#10b981; }
.card-meta { font-size:12px; color:#6b7280; }
.link-btn { font-size:12px; color:#059669; font-weight:600; cursor:pointer; }

/* table */
[data-testid="stDataFrame"] { border:none !important; }

/* ---------- AI CARD ---------- */
.ai-card {
    background:#fff; border:1px solid #eef0f4; border-radius:14px;
    padding:18px; margin-bottom:18px;
    box-shadow:0 1px 2px rgba(16,24,40,.04);
}
.ai-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
.ai-title { font-size:14px; font-weight:700; color:#0f1729; }
.ai-beta { background:#ecfdf5; color:#059669; font-size:9.5px; font-weight:700;
    padding:2px 7px; border-radius:6px; letter-spacing:.5px; }
.ai-sub { font-size:11.5px; color:#6b7280; margin-bottom:14px; }
.ai-bubble {
    background:#f9fafb; border:1px solid #f1f3f6; border-radius:12px;
    padding:12px 14px; font-size:12.5px; color:#374151; line-height:1.6;
    margin-bottom:12px;
}
.ai-robot {
    width:64px; height:64px; border-radius:14px;
    background:linear-gradient(135deg,#10b981,#059669);
    display:flex;align-items:center;justify-content:center;
    font-size:34px; margin-left:auto; margin-bottom:10px;
}

/* quick analysis buttons */
.qa-title { font-size:13px; font-weight:600; color:#0f1729; margin: 6px 0 10px; }
div[data-testid="column"] .stButton > button {
    background:#fff !important;
    border:1px solid #e5e7eb !important;
    color:#374151 !important;
    border-radius:10px !important;
    font-size:12px !important;
    font-weight:500 !important;
    padding: 10px !important;
}
div[data-testid="column"] .stButton > button:hover {
    background:#ecfdf5 !important;
    border-color:#a7f3d0 !important;
    color:#059669 !important;
}

/* alerts */
.alert {
    background:#fafbfc; border:1px solid #eef0f4; border-radius:12px;
    padding:14px; display:flex; gap:12px; align-items:flex-start;
}
.alert .ic { font-size:18px; }
.alert .ttl { font-size:12.5px; font-weight:600; color:#0f1729; }
.alert .ds { font-size:11.5px; color:#6b7280; margin-top:2px; line-height:1.5; }
.alert .tm { font-size:10.5px; color:#9ca3af; margin-top:6px; }

/* chat msgs */
.msg-a { background:#f9fafb; border:1px solid #f1f3f6; border-radius:12px;
    padding:10px 14px; font-size:12.5px; color:#374151; margin:6px 0; line-height:1.6; }
.msg-u { background:linear-gradient(135deg,#10b981,#059669); color:#fff;
    border-radius:12px; padding:10px 14px; font-size:12.5px;
    margin:6px 0 6px 18%; line-height:1.5; }
</style>
""", unsafe_allow_html=True)

# =====================
# CONFIG
# =====================
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "")
PROJECT_ID = st.secrets.get("PROJECT_ID", "green-finance-ai")
GCP_CREDENTIALS = st.secrets.get("GCP_CREDENTIALS", None)

@st.cache_resource
def init_clients():
    if GCP_CREDENTIALS:
        creds_dict = json.loads(GCP_CREDENTIALS)
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        bq = bigquery.Client(project=PROJECT_ID, credentials=credentials)
    else:
        bq = bigquery.Client(project=PROJECT_ID)
    genai.configure(api_key=GEMINI_KEY)
    gem = genai.GenerativeModel("gemini-1.5-flash")
    return bq, gem

bq_client, gemini_model = init_clients()

# =====================
# DATA
# =====================
@st.cache_data(ttl=60)
def get_data():
    query = """
    SELECT r.symbol, r.name, r.sector,
           r.price, r.change_percent,
           r.financial_risk_score, r.green_score,
           r.esg_rating, r.profit_margin,
           r.beta, r.co2_emission, r.market_cap
    FROM `green-finance-ai.green_finance.realtime_scores` r
    WHERE r.timestamp = (
        SELECT MAX(timestamp)
        FROM `green-finance-ai.green_finance.realtime_scores` r2
        WHERE r2.symbol = r.symbol
    )
    ORDER BY r.financial_risk_score DESC
    """
    rows = list(bq_client.query(query).result())
    return [dict(row) for row in rows]

def ask_gemini(question, data):
    info = ""
    for d in data[:12]:
        info += (f"- {d['symbol']} ({d['name']}): Price=${d['price']:.2f}, "
                 f"Change={d['change_percent']:+.2f}%, Risk={d['financial_risk_score']}, "
                 f"Green={d['green_score']}, ESG={d['esg_rating']}, Sector={d['sector']}\n")
    prompt = f"""You are a senior Green Finance AI Analyst.
Real-time S&P 500 BigQuery data:
{info}
Question: {question}
Professional analysis: direct answer, key insights, recommendations. Max 180 words."""
    return gemini_model.generate_content(prompt).text

data = get_data()
df = pd.DataFrame(data)
total = len(data)
high_risk = len([d for d in data if d["financial_risk_score"] >= 60])
low_risk  = len([d for d in data if d["financial_risk_score"] <= 20])
avg_green = round(sum(d["green_score"] for d in data) / total, 1) if total else 0

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-logo">🌿</div>
        <div class="brand-text">
            <div class="t1">Green Finance</div>
            <div class="t2">Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    nav = [
        ("📊  Dashboard",      "dashboard"),
        ("🏢  Companies",      "companies"),
        ("📈  Risk Analytics", "risk"),
        ("🌱  ESG Scores",     "esg"),
        ("⭐  Watchlist",      "watchlist"),
        ("🔔  Alerts",         "alerts"),
        ("📋  Reports",        "reports"),
        ("⚙️  Settings",       "settings"),
    ]
    for label, key in nav:
        is_active = st.session_state.page == key
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="side-user">
        <div class="av">AK</div>
        <div>
            <div class="nm">Arben K.</div>
            <div class="rl">Senior Solution Developer</div>
        </div>
    </div>
    <div class="side-market">
        <div class="lbl">Market Overview</div>
        <div class="sp">S&amp;P 500</div>
        <div class="val">5,309.01</div>
        <div class="chg">▲ +0.78%</div>
        <div class="upd">Last updated: just now</div>
    </div>
    """, unsafe_allow_html=True)

# =====================
# HEADER
# =====================
hc1, hc2, hc3 = st.columns([5, 3, 2])
with hc1:
    st.markdown(f"""
        <h1 class="page-title">Welcome back, Arben! 👋</h1>
        <div class="page-sub">Here's what's happening with your green finance portfolio today.</div>
    """, unsafe_allow_html=True)
with hc2:
    st.markdown('<div class="search-bar">🔍 &nbsp; Search companies, sectors...</div>', unsafe_allow_html=True)
with hc3:
    st.markdown(f"""
        <div style="text-align:right;">
            <span class="live-pill"><span class="live-dot"></span> Live · {total} companies</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# =====================
# KPI CARDS with sparklines
# =====================
def sparkline(values, color):
    fig = go.Figure(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=f"rgba{(*tuple(int(color.lstrip('#')[i:i+2],16) for i in (0,2,4)), 0.12)}",
    ))
    fig.update_layout(
        height=50, margin=dict(t=0,b=0,l=0,r=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor="white", plot_bgcolor="white", showlegend=False,
    )
    return fig

import random
random.seed(1)
def trend(up=True, n=12):
    base = [random.uniform(0.4, 1.0) for _ in range(n)]
    return sorted(base) if up else sorted(base, reverse=True)

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "👥", "b", "Companies Tracked", total,     "↑ 3 new this week",   "t-up", "#3b82f6", trend(True)),
    (k2, "⚠️", "r", "High Risk Companies", high_risk, "↓ -1 from yesterday", "t-dn", "#ef4444", trend(False)),
    (k3, "🛡️", "g", "Low Risk Companies",  low_risk,  "↑ 2 from yesterday",  "t-up", "#10b981", trend(True)),
    (k4, "🌱", "y", "Avg Green Score",     avg_green, "↑ 4.3 vs last week",  "t-up", "#f59e0b", trend(True)),
]
for col, ico, cls, label, value, trend_txt, trend_cls, color, series in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi">
            <div class="kpi-top">
                <div class="kpi-ico {cls}">{ico}</div>
                <div class="kpi-label">{label}</div>
            </div>
            <div class="kpi-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)
        # overlay sparkline + trend
        sc1, sc2 = st.columns([1,1])
        with sc1:
            st.markdown(f"<div class='kpi-trend {trend_cls}' style='margin-top:-10px;padding-left:6px;'>{trend_txt}</div>", unsafe_allow_html=True)
        with sc2:
            st.plotly_chart(sparkline(series, color), use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# =====================
# MAIN LAYOUT
# =====================
left, right = st.columns([7, 3], gap="large")

with left:
    # LIVE COMPANY SCORES
    st.markdown("""
    <div class="card">
        <div class="card-head">
            <div class="card-title"><span class="green-dot"></span> Live Company Scores</div>
            <div style="display:flex; align-items:center; gap:14px;">
                <span class="card-meta">● Auto-refresh: 60s</span>
                <span class="link-btn">View all</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    def fmt_risk(s):
        if s >= 60: return f"🔴 {s}"
        if s >= 40: return f"🟡 {s}"
        return f"🟢 {s}"
    def fmt_green(s):
        if s >= 70: return f"🌿 {s}"
        if s >= 40: return f"🌱 {s}"
        return f"🏭 {s}"

    display_df = pd.DataFrame({
        "Symbol":  df["symbol"],
        "Company": df["name"].apply(lambda x: x[:24]+"..." if len(x)>24 else x),
        "Price":   df["price"].apply(lambda x: f"${x:.2f}"),
        "Change":  df["change_percent"].apply(lambda x: f"+{x:.2f}%" if x>=0 else f"{x:.2f}%"),
        "Risk Score":  df["financial_risk_score"].apply(fmt_risk),
        "Green Score": df["green_score"].apply(fmt_green),
        "ESG":    df["esg_rating"],
        "Sector": df["sector"].apply(lambda x: x[:16]+"..." if len(x)>16 else x),
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=460)
    st.markdown("<div style='text-align:center;margin-top:8px;'><span class='link-btn'>View more companies ⌄</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # RECENT ALERTS
    st.markdown("""
    <div class="card">
        <div class="card-head">
            <div class="card-title">🔔 Recent Alerts</div>
            <span class="link-btn">View all alerts →</span>
        </div>
    """, unsafe_allow_html=True)

    high_risk_companies = [d for d in data if d["financial_risk_score"] >= 60]
    low_green_companies = [d for d in data if d["green_score"] <= 20]
    best_company = max(data, key=lambda x: x["green_score"]) if data else None

    a1, a2, a3 = st.columns(3)
    with a1:
        if high_risk_companies:
            c = high_risk_companies[0]
            st.markdown(f"""<div class="alert"><div class="ic">⚠️</div><div>
                <div class="ttl">High risk alert</div>
                <div class="ds">{c['name']} ({c['symbol']}) risk increased to {c['financial_risk_score']}</div>
                <div class="tm">2 m ago</div></div></div>""", unsafe_allow_html=True)
    with a2:
        if best_company:
            st.markdown(f"""<div class="alert"><div class="ic">🌱</div><div>
                <div class="ttl">ESG improvement</div>
                <div class="ds">{best_company['name']} ({best_company['symbol']}) improved ESG score</div>
                <div class="tm">15 m ago</div></div></div>""", unsafe_allow_html=True)
    with a3:
        st.markdown("""<div class="alert"><div class="ic">🔵</div><div>
            <div class="ttl">New company added</div>
            <div class="ds">NVIDIA Corporation added to tracking</div>
            <div class="tm">1 h ago</div></div></div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =====================
# RIGHT COLUMN
# =====================
with right:
    # AI ASSISTANT
    st.markdown(f"""
    <div class="ai-card">
        <div class="ai-head">
            <div>
                <div class="ai-title">AI Assistant <span class="ai-beta">BETA</span></div>
                <div class="ai-sub">Powered by real-time BigQuery data</div>
            </div>
            <div class="ai-robot">🤖</div>
        </div>
        <div class="ai-bubble">
            Hello! I analyze S&amp;P 500 companies using real-time data from BigQuery.
            Ask me about risks, green scores, or investment recommendations!
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    question = st.chat_input("Ask me anything...")

    # QUICK ANALYSIS
    st.markdown('<div class="qa-title">Quick Analysis</div>', unsafe_allow_html=True)
    q1, q2 = st.columns(2)
    with q1:
        if st.button("🏆  Best Investment", use_container_width=True, key="qa1"):
            st.session_state.auto_q = "Which company is the best investment combining financial and ESG performance?"
        if st.button("📊  Risk Comparison", use_container_width=True, key="qa3"):
            st.session_state.auto_q = "Compare highest and lowest risk companies"
    with q2:
        if st.button("🌿  ESG Leaders", use_container_width=True, key="qa2"):
            st.session_state.auto_q = "Show ESG sustainability leaders"
        if st.button("⚠️  Companies to Watch", use_container_width=True, key="qa4"):
            st.session_state.auto_q = "Which companies should investors watch carefully?"

    if "auto_q" in st.session_state:
        question = st.session_state.auto_q
        del st.session_state.auto_q

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Analyzing..."):
            answer = ask_gemini(question, data)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    for msg in st.session_state.messages[-4:]:
        cls = "msg-u" if msg["role"] == "user" else "msg-a"
        st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

    # SECTOR BREAKDOWN
    st.markdown("""
    <div class="card" style="margin-top:18px;">
        <div class="card-head">
            <div class="card-title">Sector Breakdown</div>
            <span class="link-btn">View all</span>
        </div>
    """, unsafe_allow_html=True)

    sector_counts = df["sector"].value_counts().reset_index()
    sector_counts.columns = ["Sector", "Count"]

    palette = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ef4444", "#06b6d4", "#ec4899"]
    fig = px.pie(
        sector_counts, values="Count", names="Sector",
        hole=0.68, color_discrete_sequence=palette,
    )
    fig.update_traces(textinfo="none", marker=dict(line=dict(color="#fff", width=3)))
    fig.update_layout(
        height=260, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=True,
        legend=dict(orientation="v", x=1.05, y=0.5, font=dict(size=11)),
        annotations=[dict(text=f"<b>{total}</b><br><span style='font-size:10px;color:#6b7280'>Total</span>",
                          x=0.5, y=0.5, font_size=20, showarrow=False)],
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
