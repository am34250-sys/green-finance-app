import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai
import pandas as pd
import json

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Green Finance Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================
# CUSTOM CSS - Senior Level UI
# =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', sans-serif; }
code, .mono { font-family: 'JetBrains Mono', monospace !important; }

/* Reset & Base */
.stApp {
    background: #f8f9fa;
    color: #1a1a2e;
}

/* Hide streamlit chrome */
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ===== TOP NAV ===== */
.topnav {
    background: #ffffff;
    border-bottom: 1px solid #e8ecf0;
    padding: 0 40px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.nav-logo {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #00875a, #00c278);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.nav-title {
    font-size: 17px;
    font-weight: 700;
    color: #1a1a2e;
    letter-spacing: -0.3px;
}

.nav-subtitle {
    font-size: 11px;
    color: #8492a6;
    font-weight: 400;
}

.nav-right {
    display: flex;
    align-items: center;
    gap: 16px;
}

.live-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    background: #f0faf5;
    border: 1px solid #b7ebcf;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    color: #00875a;
}

.live-dot {
    width: 7px;
    height: 7px;
    background: #00c278;
    border-radius: 50%;
    animation: blink 2s infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.bq-pill {
    background: #f5f7ff;
    border: 1px solid #d0d9ff;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 11px;
    color: #4361ee;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
}

/* ===== MAIN CONTENT ===== */
.main-content {
    padding: 32px 40px;
}

/* ===== SECTION HEADER ===== */
.section-header {
    margin-bottom: 24px;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #1a1a2e;
    letter-spacing: -0.5px;
    margin: 0 0 4px 0;
}

.section-sub {
    font-size: 13px;
    color: #8492a6;
    margin: 0;
}

/* ===== KPI CARDS ===== */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}

.kpi-card {
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 14px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s;
}

.kpi-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00875a, #00c278);
    border-radius: 0 0 14px 14px;
}

.kpi-card.danger::after {
    background: linear-gradient(90deg, #e63946, #ff6b6b);
}

.kpi-card.warning::after {
    background: linear-gradient(90deg, #f4a261, #ffb347);
}

.kpi-card.info::after {
    background: linear-gradient(90deg, #4361ee, #7b8cde);
}

.kpi-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin-bottom: 16px;
    background: #f0faf5;
}

.kpi-card.danger .kpi-icon { background: #fff5f5; }
.kpi-card.warning .kpi-icon { background: #fff8f0; }
.kpi-card.info .kpi-icon { background: #f5f7ff; }

.kpi-value {
    font-size: 36px;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1;
    letter-spacing: -1px;
    margin-bottom: 6px;
}

.kpi-card.danger .kpi-value { color: #e63946; }
.kpi-card.warning .kpi-value { color: #f4a261; }
.kpi-card.info .kpi-value { color: #4361ee; }

.kpi-label {
    font-size: 13px;
    color: #8492a6;
    font-weight: 500;
}

/* ===== DATA TABLE ===== */
.table-card {
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 24px;
}

.table-header {
    padding: 20px 24px;
    border-bottom: 1px solid #f0f2f5;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.table-title {
    font-size: 15px;
    font-weight: 600;
    color: #1a1a2e;
}

.table-badge {
    background: #f0faf5;
    color: #00875a;
    border: 1px solid #b7ebcf;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
}

/* Risk badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.badge-high { background: #fff0f0; color: #e63946; border: 1px solid #ffd0d0; }
.badge-mid { background: #fff8f0; color: #f4a261; border: 1px solid #ffd9b0; }
.badge-low { background: #f0faf5; color: #00875a; border: 1px solid #b7ebcf; }

/* ===== AI CHAT ===== */
.chat-card {
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 14px;
    overflow: hidden;
    height: 100%;
}

.chat-header {
    padding: 20px 24px;
    border-bottom: 1px solid #f0f2f5;
    background: linear-gradient(135deg, #00875a08, #4361ee08);
}

.chat-title {
    font-size: 15px;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 2px;
}

.chat-sub {
    font-size: 11px;
    color: #8492a6;
}

.chat-body {
    padding: 20px 24px;
}

/* Quick buttons */
.quick-btn {
    background: #f8f9fa;
    border: 1px solid #e8ecf0;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    color: #4a5568;
    cursor: pointer;
    transition: all 0.15s;
    width: 100%;
    text-align: left;
    margin-bottom: 6px;
    font-family: 'Inter', sans-serif;
}

.quick-btn:hover {
    background: #f0faf5;
    border-color: #b7ebcf;
    color: #00875a;
}

/* AI message */
.ai-msg {
    background: #f8f9fa;
    border: 1px solid #e8ecf0;
    border-radius: 12px;
    padding: 16px;
    font-size: 13px;
    line-height: 1.7;
    color: #2d3748;
    margin-top: 12px;
}

.ai-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #00875a, #00c278);
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}

/* User message */
.user-msg {
    background: linear-gradient(135deg, #4361ee, #7b8cde);
    color: white;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 13px;
    margin-top: 12px;
    margin-left: 20%;
}

/* ===== FOOTER ===== */
.footer {
    text-align: center;
    padding: 20px;
    color: #b0bac9;
    font-size: 11px;
    border-top: 1px solid #e8ecf0;
    background: #ffffff;
    margin-top: 32px;
}

/* Streamlit overrides */
div[data-testid="stDataFrame"] {
    border-radius: 0 !important;
}

div[data-testid="column"] {
    padding: 0 8px !important;
}

.stChatInput > div {
    border-radius: 10px !important;
    border-color: #e8ecf0 !important;
}

.stChatMessage {
    background: transparent !important;
    padding: 0 !important;
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
    ORDER BY r.financial_risk_score DESC, r.green_score ASC
    """
    rows = list(bq_client.query(query).result())
    return [dict(row) for row in rows]

def ask_gemini(question, data):
    info = ""
    for d in data[:12]:
        info += f"- {d['symbol']} ({d['name']}): Price=${d['price']:.2f}, Change={d['change_percent']:+.2f}%, Risk={d['financial_risk_score']}, Green={d['green_score']}, ESG={d['esg_rating']}, Sector={d['sector']}\n"
    prompt = f"""You are a senior Green Finance AI Analyst at a top investment firm.
Real-time S&P 500 data from BigQuery:
{info}

Question: {question}

Provide a professional analysis:
- Direct, data-driven answer
- Key financial and ESG insights  
- Specific actionable recommendations
- Flag any risks

Be concise and professional. Max 180 words."""
    return gemini_model.generate_content(prompt).text

# =====================
# LOAD DATA
# =====================
data = get_data()
total = len(data)
high_risk = len([d for d in data if d["financial_risk_score"] >= 60])
low_risk = len([d for d in data if d["financial_risk_score"] <= 20])
avg_green = round(sum(d["green_score"] for d in data) / total, 1) if total else 0

# =====================
# TOP NAV
# =====================
st.markdown(f"""
<div class="topnav">
    <div class="nav-brand">
        <div class="nav-logo">🌿</div>
        <div>
            <div class="nav-title">Green Finance Intelligence</div>
            <div class="nav-subtitle">Real-Time S&P 500 ESG & Risk Analytics</div>
        </div>
    </div>
    <div class="nav-right">
        <div class="bq-pill">BigQuery · realtime_scores</div>
        <div class="live-pill">
            <div class="live-dot"></div>
            Live · {total} companies
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================
# MAIN CONTENT
# =====================
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Section header
st.markdown("""
<div class="section-header">
    <p class="section-title">Portfolio Overview</p>
    <p class="section-sub">Real-time financial risk and ESG sustainability scores — updated every 60 seconds from BigQuery</p>
</div>
""", unsafe_allow_html=True)

# KPI Cards
st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-icon">📊</div>
        <div class="kpi-value">{total}</div>
        <div class="kpi-label">Companies Tracked</div>
    </div>
    <div class="kpi-card danger">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-value">{high_risk}</div>
        <div class="kpi-label">High Risk Companies</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">✅</div>
        <div class="kpi-value">{low_risk}</div>
        <div class="kpi-label">Low Risk Companies</div>
    </div>
    <div class="kpi-card warning">
        <div class="kpi-icon">🌱</div>
        <div class="kpi-value">{avg_green}</div>
        <div class="kpi-label">Avg Green Score</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================
# TABLE + CHAT
# =====================
table_col, chat_col = st.columns([6, 4])

with table_col:
    st.markdown(f"""
    <div class="table-header" style="background:#fff;border:1px solid #e8ecf0;border-radius:14px 14px 0 0;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;">
        <span class="table-title">📈 Live Company Scores</span>
        <span class="table-badge">Auto-refresh 60s</span>
    </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame(data)
    
    def format_risk(score):
        if score >= 60:
            return f"🔴 {score}"
        elif score >= 40:
            return f"🟡 {score}"
        else:
            return f"🟢 {score}"

    def format_green(score):
        if score >= 70:
            return f"🌿 {score}"
        elif score >= 40:
            return f"🌱 {score}"
        else:
            return f"🏭 {score}"

    def format_change(val):
        return f"+{val:.2f}%" if val >= 0 else f"{val:.2f}%"

    display_df = pd.DataFrame({
        "Symbol": df["symbol"],
        "Company": df["name"].apply(lambda x: x[:22] + "..." if len(x) > 22 else x),
        "Price": df["price"].apply(lambda x: f"${x:.2f}"),
        "Change": df["change_percent"].apply(format_change),
        "Risk Score": df["financial_risk_score"].apply(format_risk),
        "Green Score": df["green_score"].apply(format_green),
        "ESG": df["esg_rating"],
        "Sector": df["sector"].apply(lambda x: x[:16] + "..." if len(x) > 16 else x),
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=520,
    )

with chat_col:
    st.markdown("""
    <div class="chat-header" style="background:linear-gradient(135deg,#f0faf520,#f5f7ff20);border:1px solid #e8ecf0;border-radius:14px 14px 0 0;padding:16px 20px;">
        <div class="chat-title">🤖 Green Finance AI Assistant</div>
        <div class="chat-sub">Gemini · Powered by real-time BigQuery data</div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Green Finance AI analyst. I have real-time access to S&P 500 financial risk and ESG data via BigQuery. Ask me anything about company performance, sustainability, or investment recommendations."}
        ]

    # Mesazhet
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state.messages[-6:]:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-msg"><span class="ai-tag">🌿 Green Finance AI</span><br>{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick questions
    st.markdown('<p style="font-size:12px;font-weight:600;color:#8492a6;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Quick Analysis</p>', unsafe_allow_html=True)

    q1, q2 = st.columns(2)
    with q1:
        if st.button("💰 Best investment", use_container_width=True):
            st.session_state.auto_q = "Which company is the best investment combining financial and ESG performance?"
        if st.button("📊 Risk comparison", use_container_width=True):
            st.session_state.auto_q = "Compare the highest and lowest risk companies in detail"
    with q2:
        if st.button("🌍 ESG leaders", use_container_width=True):
            st.session_state.auto_q = "Which companies are the ESG sustainability leaders?"
        if st.button("⚠️ Avoid these", use_container_width=True):
            st.session_state.auto_q = "Which companies should investors avoid and why?"

    # Chat input
    question = st.chat_input("Ask about any company or portfolio strategy...")

    if "auto_q" in st.session_state:
        question = st.session_state.auto_q
        del st.session_state.auto_q

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Analyzing..."):
            answer = ask_gemini(question, data)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    Green Finance Intelligence System · BigQuery · Vertex AI · Gemini · Real-Time S&P 500 Analytics
</div>
""", unsafe_allow_html=True)
