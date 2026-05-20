import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Green Finance Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# CSS
# =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

.stApp { background: #f0f2f5; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
.block-container { padding: 24px 32px !important; max-width: 100% !important; }

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: #1a1f2e !important;
    min-width: 240px !important;
    max-width: 240px !important;
}

section[data-testid="stSidebar"] * {
    color: #c8d0e0 !important;
}

/* ===== KPI CARDS ===== */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #eaecf0;
    position: relative;
    overflow: hidden;
    margin-bottom: 4px;
}

.kpi-icon-wrap {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-bottom: 14px;
}

.kpi-green .kpi-icon-wrap { background: #e8f9f2; }
.kpi-red .kpi-icon-wrap { background: #fff0f0; }
.kpi-blue .kpi-icon-wrap { background: #eff4ff; }
.kpi-orange .kpi-icon-wrap { background: #fff7ed; }

.kpi-value {
    font-size: 34px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
    color: #111827;
}

.kpi-green .kpi-value { color: #059669; }
.kpi-red .kpi-value { color: #dc2626; }
.kpi-blue .kpi-value { color: #2563eb; }
.kpi-orange .kpi-value { color: #d97706; }

.kpi-label {
    font-size: 13px;
    color: #6b7280;
    font-weight: 500;
}

.kpi-trend {
    font-size: 11px;
    margin-top: 8px;
    font-weight: 500;
}

.trend-up { color: #059669; }
.trend-down { color: #dc2626; }

/* ===== SECTION CARDS ===== */
.section-card {
    background: white;
    border-radius: 16px;
    padding: 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #eaecf0;
    overflow: hidden;
    margin-bottom: 20px;
}

.section-card-header {
    padding: 18px 24px;
    border-bottom: 1px solid #f3f4f6;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.section-card-title {
    font-size: 15px;
    font-weight: 600;
    color: #111827;
    display: flex;
    align-items: center;
    gap: 8px;
}

.live-badge {
    background: #e8f9f2;
    color: #059669;
    border: 1px solid #a7f3d0;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}

.live-dot {
    width: 6px;
    height: 6px;
    background: #059669;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ===== ALERT CARDS ===== */
.alert-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    padding: 20px 24px;
}

.alert-item {
    background: #f9fafb;
    border: 1px solid #f3f4f6;
    border-radius: 12px;
    padding: 16px;
}

.alert-icon {
    font-size: 20px;
    margin-bottom: 8px;
}

.alert-title {
    font-size: 13px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 4px;
}

.alert-desc {
    font-size: 12px;
    color: #6b7280;
    line-height: 1.5;
}

.alert-time {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 8px;
}

/* ===== AI CHAT ===== */
.ai-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 24px;
    border-bottom: 1px solid #f3f4f6;
}

.ai-title {
    font-size: 15px;
    font-weight: 600;
    color: #111827;
}

.ai-badge {
    background: linear-gradient(135deg, #059669, #10b981);
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.ai-msg {
    background: #f9fafb;
    border: 1px solid #f3f4f6;
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 13px;
    line-height: 1.7;
    color: #374151;
    margin: 4px 0;
}

.user-msg {
    background: linear-gradient(135deg, #059669, #10b981);
    color: white;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 13px;
    margin: 4px 0;
    margin-left: 15%;
    line-height: 1.6;
}

.quick-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    padding: 16px 24px;
}

/* Streamlit overrides */
div[data-testid="stDataFrame"] table {
    font-size: 13px !important;
}

.stButton button {
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    border: 1px solid #e5e7eb !important;
    background: #f9fafb !important;
    color: #374151 !important;
    transition: all 0.15s !important;
}

.stButton button:hover {
    background: #e8f9f2 !important;
    border-color: #a7f3d0 !important;
    color: #059669 !important;
}
</style>
""", unsafe_allow_html=True)

# =====================
# KONFIGURIM
# =====================
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "")
PROJECT_ID = st.secrets.get("PROJECT_ID", "green-finance-ai")
GCP_CREDENTIALS = st.secrets.get("GCP_CREDENTIALS", None)

# =====================
# INIT CLIENTS
# =====================
@st.cache_resource
def init_clients():
    if GCP_CREDENTIALS:
        creds_dict = json.loads(GCP_CREDENTIALS)
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        bq = bigquery.Client(project=PROJECT_ID, credentials=credentials)
    else:
        bq = bigquery.Client(project=PROJECT_ID)
    genai.configure(api_key=GEMINI_KEY)
    gem = genai.GenerativeModel("gemini-2.0-flash")
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
        info += f"- {d['symbol']} ({d['name']}): Price=${d['price']:.2f}, Change={d['change_percent']:+.2f}%, Risk={d['financial_risk_score']}, Green={d['green_score']}, ESG={d['esg_rating']}, Sector={d['sector']}\n"
    prompt = f"""You are a senior Green Finance AI Analyst.
Real-time S&P 500 BigQuery data:
{info}

Question: {question}

Professional analysis with:
- Direct data-driven answer
- Key financial & ESG insights
- Specific recommendations
Max 180 words."""
    return gemini_model.generate_content(prompt).text

# =====================
# LOAD DATA
# =====================
data = get_data()
df = pd.DataFrame(data)
total = len(data)
high_risk = len([d for d in data if d["financial_risk_score"] >= 60])
low_risk = len([d for d in data if d["financial_risk_score"] <= 20])
avg_green = round(sum(d["green_score"] for d in data) / total, 1) if total else 0

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 0 24px 0;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <div style="width:36px;height:36px;background:linear-gradient(135deg,#059669,#10b981);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">🌿</div>
            <div>
                <div style="font-size:14px;font-weight:700;color:white;">Green Finance</div>
                <div style="font-size:10px;color:#6b7280;">Intelligence System</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:10px;color:#4b5563;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Navigation</div>
    </div>
    """, unsafe_allow_html=True)

    pages = {
        "📊 Dashboard": "dashboard",
        "🏢 Companies": "companies",
        "⚠️ Risk Analytics": "risk",
        "🌱 ESG Scores": "esg",
        "🔔 Alerts": "alerts",
        "📋 Reports": "reports",
    }

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    for label, key in pages.items():
        active = st.session_state.page == key
        btn_style = "background:#059669;color:white;" if active else ""
        if st.button(label, use_container_width=True, key=f"nav_{key}"):
            st.session_state.page = key

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Market overview
    st.markdown("""
    <div style="background:#242938;border-radius:12px;padding:16px;margin-top:auto;">
        <div style="font-size:11px;color:#6b7280;margin-bottom:8px;">Market Overview</div>
        <div style="font-size:13px;color:white;font-weight:600;">S&P 500</div>
        <div style="font-size:22px;color:#10b981;font-weight:700;">5,309.01</div>
        <div style="font-size:12px;color:#10b981;">▲ +0.78% today</div>
        <div style="font-size:10px;color:#4b5563;margin-top:6px;">Last updated: just now</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # User info
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:12px;background:#242938;border-radius:12px;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#059669,#10b981);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;">👤</div>
        <div>
            <div style="font-size:13px;color:white;font-weight:500;">Green Finance</div>
            <div style="font-size:11px;color:#6b7280;">Data Engineer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================
# MAIN CONTENT
# =====================

# Top header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:26px;font-weight:700;color:#111827;margin:0 0 4px 0;">
            Welcome to Green Finance Intelligence! 👋
        </h1>
        <p style="color:#6b7280;font-size:14px;margin:0;">
            Here's what's happening with your green finance portfolio today.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;align-items:center;gap:12px;margin-top:8px;">
        <div class="live-badge">
            <div class="live-dot"></div>
            Live · {total} companies
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================
# KPI CARDS
# =====================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <div class="kpi-icon-wrap">👥</div>
        <div class="kpi-value">{total}</div>
        <div class="kpi-label">Companies Tracked</div>
        <div class="kpi-trend trend-up">↑ Updated live from BigQuery</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card kpi-red">
        <div class="kpi-icon-wrap">⚠️</div>
        <div class="kpi-value">{high_risk}</div>
        <div class="kpi-label">High Risk Companies</div>
        <div class="kpi-trend trend-down">Risk Score ≥ 60</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div class="kpi-icon-wrap">✅</div>
        <div class="kpi-value">{low_risk}</div>
        <div class="kpi-label">Low Risk Companies</div>
        <div class="kpi-trend trend-up">↑ Risk Score ≤ 20</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card kpi-orange">
        <div class="kpi-icon-wrap">🌱</div>
        <div class="kpi-value">{avg_green}</div>
        <div class="kpi-label">Avg Green Score</div>
        <div class="kpi-trend trend-up">↑ Sustainability Index</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# TABLE + CHART + CHAT
# =====================
left, right = st.columns([6, 4])

with left:
    # Table header
    st.markdown("""
    <div class="section-card-header" style="background:white;border:1px solid #eaecf0;border-radius:16px 16px 0 0;">
        <span class="section-card-title">📈 Live Company Scores</span>
        <span class="live-badge"><div class="live-dot"></div> Auto-refresh · 60s</span>
    </div>
    """, unsafe_allow_html=True)

    def fmt_risk(s):
        if s >= 60: return f"🔴 {s}"
        elif s >= 40: return f"🟡 {s}"
        else: return f"🟢 {s}"

    def fmt_green(s):
        if s >= 70: return f"🌿 {s}"
        elif s >= 40: return f"🌱 {s}"
        else: return f"🏭 {s}"

    display_df = pd.DataFrame({
        "Symbol": df["symbol"],
        "Company": df["name"].apply(lambda x: x[:20]+"..." if len(x)>20 else x),
        "Price": df["price"].apply(lambda x: f"${x:.2f}"),
        "Change": df["change_percent"].apply(lambda x: f"+{x:.2f}%" if x>=0 else f"{x:.2f}%"),
        "Risk": df["financial_risk_score"].apply(fmt_risk),
        "Green": df["green_score"].apply(fmt_green),
        "ESG": df["esg_rating"],
        "Sector": df["sector"].apply(lambda x: x[:14]+"..." if len(x)>14 else x),
    })

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=420)

    # Sector pie chart
    st.markdown("<br>", unsafe_allow_html=True)
    sector_counts = df["sector"].value_counts().reset_index()
    sector_counts.columns = ["Sector", "Count"]

    fig = px.pie(
        sector_counts,
        values="Count",
        names="Sector",
        title="Sector Breakdown",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.5
    )
    fig.update_layout(
        height=300,
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter", size=12),
        legend=dict(font=dict(size=11)),
        title_font=dict(size=15, color="#111827")
    )
    fig.update_traces(textposition="inside", textinfo="percent")
    st.plotly_chart(fig, use_container_width=True)

with right:
    # AI Chat
    st.markdown("""
    <div style="background:white;border:1px solid #eaecf0;border-radius:16px 16px 0 0;padding:18px 24px;display:flex;align-items:center;justify-content:space-between;">
        <div>
            <span style="font-size:15px;font-weight:600;color:#111827;">🤖 AI Assistant</span>
        </div>
        <span class="ai-badge">BETA</span>
    </div>
    <div style="background:white;border:1px solid #eaecf0;border-left:1px solid #eaecf0;border-right:1px solid #eaecf0;padding:6px 16px;">
        <span style="font-size:11px;color:#9ca3af;">Powered by real-time BigQuery data</span>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hello! I analyze {total} S&P 500 companies using real-time data from BigQuery. Ask me about risks, green scores, or investment recommendations!"}
        ]

    # Mesazhet
    with st.container():
        for msg in st.session_state.messages[-6:]:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick buttons
    st.markdown('<p style="font-size:12px;font-weight:600;color:#6b7280;margin-bottom:8px;">Quick Analysis</p>', unsafe_allow_html=True)
    q1, q2 = st.columns(2)
    with q1:
        if st.button("🏆 Best Investment", use_container_width=True):
            st.session_state.auto_q = "Which company is the best investment combining financial and ESG performance?"
        if st.button("📊 Risk Comparison", use_container_width=True):
            st.session_state.auto_q = "Compare the highest and lowest risk companies"
    with q2:
        if st.button("🌍 ESG Leaders", use_container_width=True):
            st.session_state.auto_q = "Which companies are the ESG sustainability leaders?"
        if st.button("⚠️ Companies to Watch", use_container_width=True):
            st.session_state.auto_q = "Which companies should investors watch carefully?"

    question = st.chat_input("Ask me anything...")

    if "auto_q" in st.session_state:
        question = st.session_state.auto_q
        del st.session_state.auto_q

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Analyzing..."):
            answer = ask_gemini(question, data)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

# =====================
# ALERTS
# =====================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="section-card-header" style="background:white;border:1px solid #eaecf0;border-radius:16px 16px 0 0;">
    <span class="section-card-title">🔔 Recent Alerts</span>
    <span style="font-size:12px;color:#059669;font-weight:500;cursor:pointer;">View all alerts →</span>
</div>
""", unsafe_allow_html=True)

# Gjeneroi alerts automatikisht nga të dhënat
high_risk_companies = [d for d in data if d["financial_risk_score"] >= 60]
low_green_companies = [d for d in data if d["green_score"] <= 20]
best_company = max(data, key=lambda x: x["green_score"]) if data else None

a1, a2, a3 = st.columns(3)
with a1:
    if high_risk_companies:
        c = high_risk_companies[0]
        st.markdown(f"""
        <div class="alert-item" style="border-left:3px solid #dc2626;">
            <div class="alert-icon">⚠️</div>
            <div class="alert-title">High Risk Alert</div>
            <div class="alert-desc">{c['name']} ({c['symbol']}) risk score is {c['financial_risk_score']}/100</div>
            <div class="alert-time">Just now</div>
        </div>""", unsafe_allow_html=True)

with a2:
    if low_green_companies:
        c = low_green_companies[0]
        st.markdown(f"""
        <div class="alert-item" style="border-left:3px solid #f4a261;">
            <div class="alert-icon">🏭</div>
            <div class="alert-title">Low ESG Score</div>
            <div class="alert-desc">{c['name']} ({c['symbol']}) green score is only {c['green_score']}/100</div>
            <div class="alert-time">15 min ago</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-item" style="border-left:3px solid #10b981;">
            <div class="alert-icon">✅</div>
            <div class="alert-title">All ESG Scores Healthy</div>
            <div class="alert-desc">All tracked companies have acceptable ESG scores</div>
            <div class="alert-time">Just now</div>
        </div>""", unsafe_allow_html=True)

with a3:
    if best_company:
        st.markdown(f"""
        <div class="alert-item" style="border-left:3px solid #2563eb;">
            <div class="alert-icon">🌿</div>
            <div class="alert-title">ESG Leader</div>
            <div class="alert-desc">{best_company['name']} leads with green score {best_company['green_score']}/100</div>
            <div class="alert-time">1 hr ago</div>
        </div>""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;padding:20px;color:#9ca3af;font-size:11px;margin-top:24px;border-top:1px solid #e5e7eb;">
    Green Finance Intelligence · BigQuery · Vertex AI · Gemini · Real-Time S&P 500 · 
    <span style="color:#059669;">Data Engineer</span>
</div>
""", unsafe_allow_html=True)
