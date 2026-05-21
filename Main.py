import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai
import pandas as pd
import json
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Green Finance Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: #ffffff !important; }
.block-container { padding: 20px 24px !important; max-width: 100% !important; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }

section[data-testid="stSidebar"] {
    background: #111827 !important;
    min-width: 200px !important;
    max-width: 200px !important;
    border-right: 1px solid #1f2937 !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }
section[data-testid="stSidebar"] * { color: #9ca3af !important; }
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: none !important;
    color: #9ca3af !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    margin: 1px 6px !important;
    width: calc(100% - 12px) !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #1f2937 !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stButton:first-of-type button {
    background: #059669 !important;
    color: #ffffff !important;
}

.live-dot { width:6px;height:6px;background:#22c55e;border-radius:50%;animation:blink 2s infinite;display:inline-block; }
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.live-pill {
    display:inline-flex;align-items:center;gap:5px;
    background:#f0fdf4;border:1px solid #86efac;
    color:#15803d;padding:4px 10px;border-radius:20px;
    font-size:11px;font-weight:600;
}

.kpi {
    background:#ffffff;border:1px solid #f3f4f6;
    border-radius:12px;padding:14px 16px;
    box-shadow:0 1px 3px rgba(0,0,0,0.05);
}
.kpi-top{display:flex;align-items:center;gap:10px;margin-bottom:8px;}
.kpi-ico{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;}
.kpi-ico-g{background:#f0fdf4;} .kpi-ico-r{background:#fef2f2;}
.kpi-ico-b{background:#eff6ff;} .kpi-ico-o{background:#fff7ed;}
.kpi-num{font-size:26px;font-weight:700;line-height:1;}
.kpi-num-g{color:#16a34a;} .kpi-num-r{color:#dc2626;}
.kpi-num-b{color:#2563eb;} .kpi-num-o{color:#d97706;}
.kpi-lbl{font-size:11px;color:#6b7280;font-weight:500;margin-top:1px;}
.kpi-trend{font-size:10px;font-weight:500;margin-top:6px;}
.kpi-trend-up{color:#16a34a;} .kpi-trend-dn{color:#dc2626;}

.card{background:#ffffff;border:1px solid #f3f4f6;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);overflow:hidden;margin-bottom:14px;}
.card-head{padding:12px 16px;border-bottom:1px solid #f9fafb;display:flex;align-items:center;justify-content:space-between;}
.card-title{font-size:13px;font-weight:600;color:#111827;}
.refresh-pill{display:inline-flex;align-items:center;gap:4px;background:#f0fdf4;border:1px solid #86efac;color:#15803d;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:600;}

.ai-card{background:#ffffff;border:1px solid #f3f4f6;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);overflow:hidden;margin-bottom:14px;}
.ai-head{padding:12px 16px;border-bottom:1px solid #f9fafb;display:flex;align-items:center;justify-content:space-between;}
.ai-head-left{display:flex;align-items:center;gap:8px;}
.ai-robot{width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#059669,#10b981);display:flex;align-items:center;justify-content:center;font-size:16px;}
.ai-name{font-size:13px;font-weight:600;color:#111827;}
.ai-sub{font-size:10px;color:#9ca3af;}
.ai-beta{background:linear-gradient(135deg,#059669,#10b981);color:white;padding:2px 7px;border-radius:20px;font-size:9px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;}
.ai-body{padding:12px 16px;}
.ai-msg{background:#f9fafb;border:1px solid #f3f4f6;border-radius:10px;padding:10px 12px;font-size:12px;line-height:1.6;color:#374151;margin-bottom:6px;}
.user-msg{background:linear-gradient(135deg,#059669,#10b981);color:white;border-radius:10px;padding:10px 12px;font-size:12px;margin-bottom:6px;margin-left:15%;line-height:1.5;}

.alert-box{display:flex;gap:10px;background:#f9fafb;border:1px solid #f3f4f6;border-radius:10px;padding:10px;}
.alert-ico{width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;}
.alert-ico-r{background:#fef2f2;} .alert-ico-g{background:#f0fdf4;} .alert-ico-b{background:#eff6ff;}
.alert-title{font-size:11px;font-weight:600;color:#111827;}
.alert-desc{font-size:10px;color:#6b7280;line-height:1.4;margin-top:2px;}
.alert-time{font-size:10px;color:#d1d5db;margin-top:4px;}

.stButton button {
    border-radius:8px !important;font-size:11px !important;font-weight:500 !important;
    border:1px solid #e5e7eb !important;background:#f9fafb !important;
    color:#374151 !important;padding:6px 10px !important;
}
.stButton button:hover{background:#f0fdf4 !important;border-color:#86efac !important;color:#15803d !important;}
</style>
""", unsafe_allow_html=True)

GEMINI_KEY = st.secrets.get("GEMINI_KEY", "")
PROJECT_ID = st.secrets.get("PROJECT_ID", "green-finance-ai")
GCP_CREDENTIALS = st.secrets.get("GCP_CREDENTIALS", None)

@st.cache_resource
def init_clients():
    if GCP_CREDENTIALS:
        creds = service_account.Credentials.from_service_account_info(json.loads(GCP_CREDENTIALS))
        bq = bigquery.Client(project=PROJECT_ID, credentials=creds)
    else:
        bq = bigquery.Client(project=PROJECT_ID)
    genai.configure(api_key=GEMINI_KEY)
    gem = genai.GenerativeModel("gemini-1.5-flash")
    return bq, gem

bq_client, gemini_model = init_clients()

@st.cache_data(ttl=60)
def get_data():
    q = """
    SELECT r.symbol, r.name, r.sector, r.price, r.change_percent,
           r.financial_risk_score, r.green_score, r.esg_rating,
           r.profit_margin, r.beta, r.co2_emission, r.market_cap
    FROM `green-finance-ai.green_finance.realtime_scores` r
    WHERE r.timestamp = (
        SELECT MAX(timestamp) FROM `green-finance-ai.green_finance.realtime_scores` r2
        WHERE r2.symbol = r.symbol
    )
    ORDER BY r.financial_risk_score DESC
    """
    return [dict(row) for row in bq_client.query(q).result()]

def ask_gemini(question, data):
    info = "".join([f"- {d['symbol']} ({d['name']}): Price=${d['price']:.2f}, Risk={d['financial_risk_score']}, Green={d['green_score']}, ESG={d['esg_rating']}\n" for d in data[:12]])
    prompt = f"You are a senior Green Finance AI Analyst.\nData:\n{info}\nQuestion: {question}\nProfessional analysis, max 150 words."
    return gemini_model.generate_content(prompt).text

def sparkline(trend="up", seed=1):
    x = np.linspace(0, 4*np.pi, 20)
    y = np.sin(x + seed) + np.linspace(0, 2 if trend=="up" else -2, 20) * 0.4
    color = "#22c55e" if trend == "up" else "#ef4444"
    fig = go.Figure(go.Scatter(
        x=list(range(20)), y=y.tolist(), mode="lines",
        line=dict(color=color, width=1.5), fill="tozeroy",
        fillcolor=f"rgba({'34,197,94' if trend=='up' else '239,68,68'},0.06)"
    ))
    fig.update_layout(
        margin=dict(t=0,b=0,l=0,r=0), height=40,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False)
    )
    return fig

data = get_data()
df = pd.DataFrame(data)
total = len(data)
high_risk = len([d for d in data if d["financial_risk_score"] >= 60])
low_risk = len([d for d in data if d["financial_risk_score"] <= 20])
avg_green = round(sum(d["green_score"] for d in data) / total, 1) if total else 0

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 12px 12px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#059669,#10b981);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:15px;">🌿</div>
            <div>
                <div style="font-size:12px;font-weight:700;color:#ffffff;">Green Finance</div>
                <div style="font-size:9px;color:#4b5563;">Intelligence System</div>
            </div>
        </div>
        <div style="font-size:9px;color:#374151;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;padding:0 6px;">Navigation</div>
    </div>
    """, unsafe_allow_html=True)

    for item in ["📊 Dashboard", "🏢 Companies", "⚠️ Risk Analytics", "🌱 ESG Scores", "🔔 Alerts", "📋 Reports"]:
        st.button(item, use_container_width=True, key=f"nav_{item}")

    st.markdown("""
    <div style="margin:12px 10px 8px;">
        <div style="background:#1f2937;border-radius:10px;padding:12px;">
            <div style="font-size:9px;color:#6b7280;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;">Market Overview</div>
            <div style="font-size:11px;color:#d1d5db;font-weight:500;">S&P 500</div>
            <div style="font-size:20px;color:#ffffff;font-weight:700;margin:2px 0;">5,309.01</div>
            <div style="font-size:11px;color:#22c55e;font-weight:500;">▲ +0.78% today</div>
            <div style="font-size:9px;color:#4b5563;margin-top:6px;">Last updated: just now</div>
        </div>
    </div>
    <div style="margin:0 10px;">
        <div style="background:#1f2937;border-radius:10px;padding:10px;display:flex;align-items:center;gap:8px;">
            <div style="width:30px;height:30px;background:linear-gradient(135deg,#059669,#10b981);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;">👤</div>
            <div>
                <div style="font-size:11px;color:#ffffff;font-weight:500;">Green Finance</div>
                <div style="font-size:9px;color:#6b7280;">Data Engineer</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# HEADER
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-size:22px;font-weight:700;color:#111827;">Welcome to Green Finance Intelligence! 👋</div>
        <div style="font-size:13px;color:#6b7280;margin-top:2px;">Here's what's happening with your green finance portfolio today.</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;padding-top:6px;">
        <div class="live-pill"><div class="live-dot"></div>Live · {total} companies</div>
    </div>
    """, unsafe_allow_html=True)

# KPI CARDS
k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1,"kpi-ico-g","kpi-num-g","👥",total,"Companies Tracked","kpi-trend-up","↑ Updated live","up",1),
    (k2,"kpi-ico-r","kpi-num-r","⚠️",high_risk,"High Risk Companies","kpi-trend-dn","↓ Risk Score ≥ 60","down",2),
    (k3,"kpi-ico-b","kpi-num-b","✅",low_risk,"Low Risk Companies","kpi-trend-up","↑ Risk Score ≤ 20","up",3),
    (k4,"kpi-ico-o","kpi-num-o","🌱",avg_green,"Avg Green Score","kpi-trend-up","↑ Sustainability","up",4),
]
for col, ic, nc, ico, val, lbl, tc, tt, td, seed in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi">
            <div class="kpi-top">
                <div class="kpi-ico {ic}">{ico}</div>
                <div>
                    <div class="kpi-num {nc}">{val}</div>
                    <div class="kpi-lbl">{lbl}</div>
                </div>
            </div>
            <div class="kpi-trend {tc}">{tt}</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(sparkline(td, seed), use_container_width=True,
                       config={"displayModeBar": False}, key=f"sp_{seed}")

st.markdown("<br>", unsafe_allow_html=True)

# MAIN LAYOUT
left, right = st.columns([13, 9], gap="medium")

with left:
    st.markdown("""
    <div class="card">
        <div class="card-head">
            <div style="display:flex;align-items:center;gap:6px;">
                <div class="live-dot"></div>
                <span class="card-title">Live Company Scores</span>
            </div>
            <div class="refresh-pill"><div class="live-dot"></div>Auto-refresh · 60s</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    def fmt_risk(s):
        if s >= 60: return f"🔴 {s}"
        elif s >= 40: return f"🟡 {s}"
        return f"🟢 {s}"

    def fmt_green(s):
        if s >= 70: return f"🌿 {s}"
        elif s >= 40: return f"🌱 {s}"
        return f"🏭 {s}"

    display_df = pd.DataFrame({
        "Symbol": df["symbol"],
        "Company": df["name"].apply(lambda x: x[:20]+"…" if len(x)>20 else x),
        "Price": df["price"].apply(lambda x: f"${x:.2f}"),
        "Change": df["change_percent"].apply(lambda x: f"+{x:.2f}%" if x>=0 else f"{x:.2f}%"),
        "Risk": df["financial_risk_score"].apply(fmt_risk),
        "Green": df["green_score"].apply(fmt_green),
        "ESG": df["esg_rating"],
        "Sector": df["sector"].apply(lambda x: x[:13]+"…" if len(x)>13 else x),
    })

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=360)

    st.markdown("<br>", unsafe_allow_html=True)

    # ALERTS
    st.markdown("""
    <div class="card">
        <div class="card-head">
            <span class="card-title">🔔 Recent Alerts</span>
            <span style="font-size:11px;color:#059669;font-weight:600;">View all →</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    hr = [d for d in data if d["financial_risk_score"] >= 60]
    lg = [d for d in data if d["green_score"] <= 20]
    bc = max(data, key=lambda x: x["green_score"]) if data else None

    a1, a2, a3 = st.columns(3)
    with a1:
        if hr:
            c = hr[0]
            st.markdown(f"""<div class="alert-box" style="border-left:3px solid #dc2626;">
                <div class="alert-ico alert-ico-r">⚠️</div>
                <div><div class="alert-title">High Risk Alert</div>
                <div class="alert-desc">{c['name']} risk {c['financial_risk_score']}/100</div>
                <div class="alert-time">Just now</div></div></div>""", unsafe_allow_html=True)
    with a2:
        if lg:
            c = lg[0]
            st.markdown(f"""<div class="alert-box" style="border-left:3px solid #f59e0b;">
                <div class="alert-ico" style="background:#fffbeb;width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;">🏭</div>
                <div><div class="alert-title">Low ESG Score</div>
                <div class="alert-desc">{c['name']} score {c['green_score']}/100</div>
                <div class="alert-time">15 min ago</div></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="alert-box" style="border-left:3px solid #22c55e;">
                <div class="alert-ico alert-ico-g">✅</div>
                <div><div class="alert-title">ESG Healthy</div>
                <div class="alert-desc">All stable ESG metrics</div>
                <div class="alert-time">Now</div></div></div>""", unsafe_allow_html=True)
    with a3:
        if bc:
            st.markdown(f"""<div class="alert-box" style="border-left:3px solid #3b82f6;">
                <div class="alert-ico alert-ico-b">🌿</div>
                <div><div class="alert-title">ESG Leader</div>
                <div class="alert-desc">{bc['name']} score {bc['green_score']}/100</div>
                <div class="alert-time">1h ago</div></div></div>""", unsafe_allow_html=True)

with right:
    # AI
    st.markdown("""
    <div class="ai-card">
        <div class="ai-head">
            <div class="ai-head-left">
                <div class="ai-robot">🤖</div>
                <div>
                    <div class="ai-name">AI Assistant</div>
                    <div class="ai-sub">Powered by Gemini + BigQuery</div>
                </div>
            </div>
            <div class="ai-beta">BETA</div>
        </div>
        <div class="ai-body">
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "ai", "content": f"Hello! I analyze <b>{total} S&P 500 companies</b> using real-time ESG and financial risk data from BigQuery. Ask me anything!"}]

    st.markdown(f"""
    <div class="ai-msg">Hello! I analyze <b>{total} S&P 500 companies</b> using real-time data from BigQuery.<br>
    Ask me about: Investment strategy · ESG leaders · Financial risks · Sustainability</div>
    <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:1px;margin:10px 0 6px;">Quick Analysis</div>
    """, unsafe_allow_html=True)

    q1, q2 = st.columns(2)
    with q1:
        if st.button("🏆 Best Investment", use_container_width=True, key="q1"):
            st.session_state.auto_q = "Which company is the best investment combining financial and ESG performance?"
        if st.button("📊 Risk Comparison", use_container_width=True, key="q3"):
            st.session_state.auto_q = "Compare highest and lowest risk companies"
    with q2:
        if st.button("🌍 ESG Leaders", use_container_width=True, key="q2"):
            st.session_state.auto_q = "Which companies are the ESG sustainability leaders?"
        if st.button("⚠️ Watch List", use_container_width=True, key="q4"):
            st.session_state.auto_q = "Which companies should investors watch carefully?"

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    question = st.chat_input("Ask me anything...")
    if "auto_q" in st.session_state:
        question = st.session_state.auto_q
        del st.session_state.auto_q

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Analyzing..."):
            answer = ask_gemini(question, data)
        st.session_state.messages.append({"role": "ai", "content": answer})
        st.rerun()

    for msg in st.session_state.messages[-4:]:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # SECTOR CHART
    st.markdown("""
    <div class="card">
        <div class="card-head">
            <span class="card-title">Sector Breakdown</span>
            <span style="font-size:10px;color:#6b7280;">View all</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sd = df["sector"].value_counts().reset_index()
    sd.columns = ["Sector", "Count"]
    colors = ["#22c55e","#3b82f6","#a855f7","#f59e0b","#ef4444","#06b6d4","#8b5cf6","#f97316"]

    fig2 = go.Figure(go.Pie(
        labels=sd["Sector"], values=sd["Count"],
        hole=0.58, marker_colors=colors[:len(sd)],
        textinfo="percent", textfont_size=10,
    ))
    fig2.update_layout(
        height=220, margin=dict(t=0,b=0,l=0,r=120),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=True,
        legend=dict(font=dict(size=10), orientation="v", x=1.02, y=0.5, xanchor="left"),
        annotations=[dict(text=f"<b>{total}</b><br><span style='font-size:10px'>Total</span>",
                         x=0.38, y=0.5, font_size=12, showarrow=False)]
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

st.markdown("""
<div style="text-align:center;padding:12px;color:#9ca3af;font-size:10px;border-top:1px solid #f3f4f6;margin-top:8px;">
    Green Finance Intelligence · BigQuery · Vertex AI · Gemini · Real-Time S&P 500 ·
    <span style="color:#059669;font-weight:600;">Data Engineer</span>
</div>
""", unsafe_allow_html=True)
