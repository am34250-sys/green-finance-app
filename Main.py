import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai
import json
import os

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Green Finance AI",
    page_icon="🌱",
    layout="wide"
)

# =====================
# CUSTOM CSS
# =====================
st.markdown("""
<style>
    /* Dark theme */
    .stApp { background-color: #0a0f0a; color: #e2f0e2; }
    
    /* Header */
    .main-header {
        background: #111811;
        padding: 20px 30px;
        border-radius: 12px;
        border: 1px solid #1e2e1e;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* Stat cards */
    .stat-card {
        background: #111811;
        border: 1px solid #1e2e1e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border-top: 3px solid #4ade80;
    }
    
    .stat-card.red { border-top-color: #f87171; }
    .stat-card.yellow { border-top-color: #fbbf24; }
    
    .stat-value {
        font-size: 36px;
        font-weight: 800;
        color: #4ade80;
    }
    
    .stat-label {
        font-size: 12px;
        color: #6b8f6b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Live badge */
    .live-badge {
        background: #111811;
        border: 1px solid #1e2e1e;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        color: #4ade80;
        display: inline-block;
    }
    
    /* AI response */
    .ai-response {
        background: #162016;
        border: 1px solid #1e2e1e;
        border-radius: 12px;
        padding: 16px;
        margin-top: 12px;
        line-height: 1.6;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =====================
# KONFIGURIM
# =====================
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "")
PROJECT_ID = st.secrets.get("PROJECT_ID", "green-finance-ai")
GCP_CREDENTIALS = st.secrets.get("GCP_CREDENTIALS", None)

# =====================
# INICIALIZO CLIENTS
# =====================
@st.cache_resource
def init_clients():
    # BigQuery
    if GCP_CREDENTIALS:
        creds_dict = json.loads(GCP_CREDENTIALS)
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        bq_client = bigquery.Client(project=PROJECT_ID, credentials=credentials)
    else:
        bq_client = bigquery.Client(project=PROJECT_ID)
    
    # Gemini
    genai.configure(api_key=GEMINI_KEY)
    gemini = genai.GenerativeModel("gemini-2.0-flash")
    
    return bq_client, gemini

bq_client, gemini_model = init_clients()

# =====================
# MERR TË DHËNA NGA BIGQUERY
# =====================
@st.cache_data(ttl=60)
def get_latest_data():
    query = """
    SELECT 
        r.symbol, r.name, r.sector,
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

# =====================
# GEMINI ANALYSIS
# =====================
def ask_gemini(question, data):
    company_info = ""
    for d in data[:10]:
        company_info += f"""
- {d['symbol']} ({d['name']}):
  Price: ${d['price']:.2f} | Change: {d['change_percent']:.2f}%
  Risk Score: {d['financial_risk_score']}/100
  Green Score: {d['green_score']}/100
  ESG Rating: {d['esg_rating']}
  Sector: {d['sector']}
"""
    prompt = f"""You are a Green Finance AI Analyst.
Real-time BigQuery data:
{company_info}

Question: {question}

Give a clear analysis with:
1. Direct answer
2. Key insights
3. Recommendations
Keep under 200 words."""

    response = gemini_model.generate_content(prompt)
    return response.text

# =====================
# MAIN APP
# =====================

# Header
st.markdown("""
<div class="main-header">
    <div>
        <h1 style="color:#4ade80; margin:0; font-size:24px;">🌱 Green Finance AI</h1>
        <p style="color:#6b8f6b; margin:0; font-size:12px;">Intelligent S&P 500 Analytics System</p>
    </div>
    <div class="live-badge">● Connected live to BigQuery</div>
</div>
""", unsafe_allow_html=True)

# Merr të dhënat
data = get_latest_data()

if not data:
    st.error("No data found in BigQuery!")
    st.stop()

# =====================
# STATS
# =====================
total = len(data)
high_risk = len([d for d in data if d["financial_risk_score"] >= 60])
low_risk = len([d for d in data if d["financial_risk_score"] <= 20])
avg_green = round(sum(d["green_score"] for d in data) / total, 1)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Total Companies</div>
        <div class="stat-value">{total}</div>
        <div class="stat-label">S&P 500 tracked</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card red">
        <div class="stat-label">High Risk</div>
        <div class="stat-value" style="color:#f87171">{high_risk}</div>
        <div class="stat-label">Risk score ≥ 60</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Low Risk</div>
        <div class="stat-value">{low_risk}</div>
        <div class="stat-label">Risk score ≤ 20</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card yellow">
        <div class="stat-label">Avg Green Score</div>
        <div class="stat-value" style="color:#fbbf24">{avg_green}</div>
        <div class="stat-label">Sustainability index</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# LAYOUT: TABLE + CHAT
# =====================
left_col, right_col = st.columns([3, 2])

with left_col:
    st.markdown("### 📊 Live Company Scores")
    
    import pandas as pd
    df = pd.DataFrame(data)
    df = df[["symbol", "name", "price", "change_percent", 
             "financial_risk_score", "green_score", "esg_rating", "sector"]]
    df.columns = ["Symbol", "Company", "Price ($)", "Change (%)", 
                  "Risk Score", "Green Score", "ESG", "Sector"]
    df["Price ($)"] = df["Price ($)"].apply(lambda x: f"${x:.2f}")
    df["Change (%)"] = df["Change (%)"].apply(lambda x: f"{x:+.2f}%")
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=500
    )

with right_col:
    st.markdown("### 🤖 Green Finance AI Assistant")
    st.markdown(
        "<small style='color:#6b8f6b;'>Powered by Gemini + BigQuery real-time data</small>",
        unsafe_allow_html=True
    )
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I analyze S&P 500 companies using real-time data from BigQuery. Ask me about risks, green scores, or investment recommendations!"}
        ]
    
    # Shfaq mesazhet
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
    
    # Example questions
    st.markdown("**Quick questions:**")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("💰 Best investment?"):
            st.session_state.auto_question = "Which company is the best investment?"
    with col_b:
        if st.button("🌍 Worst ESG?"):
            st.session_state.auto_question = "Which companies have the worst ESG rating?"
    
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("📊 High vs Low risk"):
            st.session_state.auto_question = "Compare high risk vs low risk companies"
    with col_d:
        if st.button("🔴 Avoid which?"):
            st.session_state.auto_question = "Which companies should I avoid?"
    
    # Chat input
    question = st.chat_input("Ask about any company...")
    
    # Auto question nga buttons
    if "auto_question" in st.session_state:
        question = st.session_state.auto_question
        del st.session_state.auto_question
    
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        
        with st.spinner("Gemini is analyzing..."):
            answer = ask_gemini(question, data)
        
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

# Footer
st.markdown("""
<div style="text-align:center; margin-top:20px; color:#6b8f6b; font-size:11px;">
    ● Connected live to BigQuery · green_finance.realtime_scores · Auto-refresh every 60s
</div>
""", unsafe_allow_html=True)
