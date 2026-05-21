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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: #f8fafc !important; }
.block-container { padding: 24px 28px !important; max-width: 100% !important; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }

section[data-testid="stSidebar"] {
    background: #0f172a !important;
    min-width: 200px !important; max-width: 200px !important;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important; border: none !important;
    color: #94a3b8 !important; font-size: 13px !important;
    text-align: left !important; padding: 9px 14px !important;
    border-radius: 8px !important; width: 100% !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #1e293b !important; color: #f1f5f9 !important;
}
section[data-testid="stSidebar"] .stButton:first-of-type button {
    background: #059669 !important; color: white !important;
}

.dot{width:6px;height:6px;background:#22c55e;border-radius:50%;animation:b 2s infinite;display:inline-block;}
@keyframes b{0%,100%{opacity:1}50%{opacity:0.2}}
.pill{display:inline-flex;align-items:center;gap:5px;background:#f0fdf4;border:1px solid #bbf7d0;color:#15803d;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;}

.kpi{background:white;border-radius:14px;padding:20px 22px;border:1px solid #e2e8f0;}
.kpi-ico{width:40px;height:40px;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:12px;}
.kpi-val{font-size:36px;font-weight:700;line-height:1;}
.kpi-lbl{font-size:13px;color:#64748b;margin-top:4px;}
.kpi-trend{font-size:11px;margin-top:10px;font-weight:500;}
.up{color:#059669;} .dn{color:#dc2626;}

.card{background:white;border-radius:14px;border:1px solid #e2e8f0;overflow:hidden;margin-bottom:16px;}
.ch{padding:14px 18px;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;justify-content:space-between;}
.ct{font-size:14px;font-weight:600;color:#0f172a;}
.rpill{background:#f0fdf4;border:1px solid #bbf7d0;color:#15803d;padding:3px 9px;border-radius:20px;font-size:10px;font-weight:600;display:inline-flex;align-items:center;gap:4px;}

.ai-box{background:white;border-radius:14px;border:1px solid #e2e8f0;overflow:hidden;margin-bottom:16px;}
.ai-h{padding:14px 18px;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;justify-content:space-between;}
.ai-ico{width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#059669,#10b981);display:flex;align-items:center;justify-content:center;font-size:16px;}
.ai-n{font-size:13px;font-weight:600;color:#0f172a;}
.ai-s{font-size:10px;color:#94a3b8;}
.beta{background:#059669;color:white;padding:2px 7px;border-radius:20px;font-size:9px;font-weight:700;text-transform:uppercase;}
.ai-b{padding:14px 18px;}
.amsg{background:#f8fafc;border:1px solid #f1f5f9;border-radius:10px;padding:10px 12px;font-size:12px;line-height:1.6;color:#334155;margin-bottom:6px;}
.umsg{background:linear-gradient(135deg,#059669,#10b981);color:white;border-radius:10px;padding:10px 12px;font-size:12px;margin-bottom:6px;margin-left:20%;line-height:1.5;}

.alrt{display:flex;gap:10px;background:#f8fafc;border:1px solid #f1f5f9;border-radius:10px;padding:10px;}
.aico{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;}
.at{font-size:11px;font-weight:600;color:#0f172a;}
.ad{font-size:10px;color:#64748b;line-height:1.4;margin-top:2px;}
.atm{font-size:9px;color:#cbd5e1;margin-top:4px;}

.stButton button{border-radius:8px !important;font-size:11px !important;font-weight:500 !important;border:1px solid #e2e8f0 !important;background:#f8fafc !important;color:#334155 !important;padding:6px 10px !important;}
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
    return bq, genai.GenerativeModel("gemini-1.5-flash")

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

def ask_gemini(q, data):
    info = "".join([f"- {d['symbol']} ({d['name']}): Price=${d['price']:.2f}, Risk={d['financial_risk_score']}, Green={d['green_score']}, ESG={d['esg_rating']}\n" for d in data[:12]])
    return gemini_model.generate_content(f"Senior Green Finance AI Analyst.\nData:\n{info}\nQuestion: {q}\nMax 150 words.").text

def make_spark(trend="up", seed=1, h=55):
    x = np.linspace(0, 4*np.pi, 24)
    y = np.sin(x + seed) + np.linspace(0, 1.5 if trend=="up" else -1.5, 24) * 0.5
    color = "#22c55e" if trend == "up" else "#ef4444"
    fill = "rgba(34,197,94,0.08)" if trend == "up" else "rgba(239,68,68,0.08)"
    fig = go.Figure(go.Scatter(x=list(range(24)), y=y.tolist(), mode="lines",
        line=dict(color=color, width=2), fill="tozeroy", fillcolor=fill))
    fig.update_layout(margin=dict(t=0,b=0,l=0,r=0), height=h,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False))
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
    <div style="padding:18px 12px 12px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px;">
            <div style="width:30px;height:30px;background:linear-gradient(135deg,#059669,#10b981);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;">🌿</div>
            <div>
                <div style="font-size:12px;font-weight:700;color:white;">Green Finance</div>
                <div style="font-size:9px;color:#475569;">Intelligence</div>
            </div>
        </div>
        <div style="font-size:9px;color:#334155;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">Navigation</div>
    </div>
    """, unsafe_allow_html=True)

    for item in ["📊 Dashboard","🏢 Companies","⚠️ Risk Analytics","🌱 ESG Scores","🔔 Alerts","📋 Reports"]:
        st.button(item, use_container_width=True, key=f"n_{item}")

    st.markdown("""
    <div style="margin:16px 10px 8px;">
        <div style="background:#1e293b;border-radius:10px;padding:12px;">
            <div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Market Overview</div>
            <div style="font-size:11px;color:#cbd5e1;">S&P 500</div>
            <div style="font-size:20px;color:white;font-weight:700;margin:2px 0;">5,309.01</div>
            <div style="font-size:11px;color:#22c55e;">▲ +0.78% today</div>
            <div style="font-size:9px;color:#334155;margin-top:6px;">Last updated: just now</div>
        </div>
        <div style="background:#1e293b;border-radius:10px;padding:10px;margin-top:8px;display:flex;align-items:center;gap:8px;">
            <div style="width:28px;height:28px;background:linear-gradient(135deg,#059669,#10b981);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;">👤</div>
            <div>
                <div style="font-size:11px;color:white;font-weight:500;">Green Finance</div>
                <div style="font-size:9px;color:#475569;">Data Engineer</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# HEADER
h1, h2 = st.columns([3,1])
with h1:
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-size:21px;font-weight:700;color:#0f172a;">Welcome to Green Finance Intelligence! 👋</div>
        <div style="font-size:12px;color:#64748b;margin-top:2px;">Here's what's happening with your green finance portfolio today.</div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;padding-top:4px;">
        <div class="pill"><div class="dot"></div>Live · {total} companies</div>
    </div>""", unsafe_allow_html=True)

# KPI CARDS — numra të mëdhenj + sparkline poshtë brenda card
k1,k2,k3,k4 = st.columns(4)

kpi_cfg = [
    (k1,"#f0fdf4","👥",total,"#059669","Companies Tracked","up","↑ Updated live from BigQuery","up",1),
    (k2,"#fef2f2","⚠️",high_risk,"#dc2626","High Risk Companies","dn","↓ Risk Score ≥ 60","down",2),
    (k3,"#eff6ff","✅",low_risk,"#2563eb","Low Risk Companies","up","↑ Risk Score ≤ 20","up",3),
    (k4,"#fff7ed","🌱",avg_green,"#d97706","Avg Green Score","up","↑ Sustainability Index","up",4),
]

for col, bg, ico, val, color, lbl, tc, tt, td, seed in kpi_cfg:
    with col:
        st.markdown(f"""
        <div class="kpi">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;">
                <div>
                    <div class="kpi-ico" style="background:{bg};">{ico}</div>
                    <div class="kpi-val" style="color:{color};">{val}</div>
                    <div class="kpi-lbl">{lbl}</div>
                    <div class="kpi-trend {'up' if tc=='up' else 'dn'}">{tt}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Sparkline direkt pas card — pa hapësirë bosh
        st.plotly_chart(make_spark(td, seed, 45), use_container_width=True,
                       config={"displayModeBar":False}, key=f"sp_{seed}")

st.markdown("<br>", unsafe_allow_html=True)

# LAYOUT
L, R = st.columns([13,9], gap="medium")

with L:
    st.markdown("""<div class="card"><div class="ch">
        <div style="display:flex;align-items:center;gap:6px;"><div class="dot"></div><span class="ct">Live Company Scores</span></div>
        <div class="rpill"><div class="dot"></div>Auto-refresh · 60s</div>
    </div></div>""", unsafe_allow_html=True)

    def fr(s): return f"🔴 {s}" if s>=60 else (f"🟡 {s}" if s>=40 else f"🟢 {s}")
    def fg(s): return f"🌿 {s}" if s>=70 else (f"🌱 {s}" if s>=40 else f"🏭 {s}")

    ddf = pd.DataFrame({
        "Symbol": df["symbol"],
        "Company": df["name"].apply(lambda x: x[:20]+"…" if len(x)>20 else x),
        "Price": df["price"].apply(lambda x: f"${x:.2f}"),
        "Change": df["change_percent"].apply(lambda x: f"+{x:.2f}%" if x>=0 else f"{x:.2f}%"),
        "Risk": df["financial_risk_score"].apply(fr),
        "Green": df["green_score"].apply(fg),
        "ESG": df["esg_rating"],
        "Sector": df["sector"].apply(lambda x: x[:13]+"…" if len(x)>13 else x),
    })
    st.dataframe(ddf, use_container_width=True, hide_index=True, height=420)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div class="card"><div class="ch">
        <span class="ct">🔔 Recent Alerts</span>
        <span style="font-size:11px;color:#059669;font-weight:600;">View all →</span>
    </div></div>""", unsafe_allow_html=True)

    hr2=[d for d in data if d["financial_risk_score"]>=60]
    lg2=[d for d in data if d["green_score"]<=20]
    bc2=max(data,key=lambda x:x["green_score"]) if data else None

    a1,a2,a3 = st.columns(3)
    with a1:
        if hr2:
            c=hr2[0]
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #dc2626;">
                <div class="aico" style="background:#fef2f2;">⚠️</div>
                <div><div class="at">High Risk Alert</div>
                <div class="ad">{c['name']} risk {c['financial_risk_score']}/100</div>
                <div class="atm">Just now</div></div></div>""", unsafe_allow_html=True)
    with a2:
        if lg2:
            c=lg2[0]
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #f59e0b;">
                <div class="aico" style="background:#fffbeb;">🏭</div>
                <div><div class="at">Low ESG Score</div>
                <div class="ad">{c['name']} {c['green_score']}/100</div>
                <div class="atm">15 min ago</div></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="alrt" style="border-left:3px solid #22c55e;">
                <div class="aico" style="background:#f0fdf4;">✅</div>
                <div><div class="at">ESG Healthy</div>
                <div class="ad">All stable</div>
                <div class="atm">Now</div></div></div>""", unsafe_allow_html=True)
    with a3:
        if bc2:
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #3b82f6;">
                <div class="aico" style="background:#eff6ff;">🌿</div>
                <div><div class="at">ESG Leader</div>
                <div class="ad">{bc2['name']} {bc2['green_score']}/100</div>
                <div class="atm">1h ago</div></div></div>""", unsafe_allow_html=True)

with R:
    st.markdown("""<div class="ai-box"><div class="ai-h">
        <div style="display:flex;align-items:center;gap:8px;">
            <div class="ai-ico">🤖</div>
            <div><div class="ai-n">AI Assistant</div><div class="ai-s">Gemini + BigQuery</div></div>
        </div>
        <div class="beta">BETA</div>
    </div><div class="ai-b">""", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages=[{"role":"ai","content":f"Hello! I analyze <b>{total} S&P 500 companies</b> using real-time ESG and financial risk data. Ask me anything!"}]

    st.markdown(f"""<div class="amsg">Hello! I analyze <b>{total} S&P 500 companies</b> using real-time data from BigQuery.<br>
    Ask me: Investment strategy · ESG leaders · Financial risks</div>
    <div style="font-size:10px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin:10px 0 6px;">Quick Analysis</div>
    """, unsafe_allow_html=True)

    qa,qb=st.columns(2)
    with qa:
        if st.button("🏆 Best Investment",use_container_width=True,key="q1"):
            st.session_state.auto_q="Which company is the best investment combining financial and ESG performance?"
        if st.button("📊 Risk Comparison",use_container_width=True,key="q3"):
            st.session_state.auto_q="Compare highest and lowest risk companies"
    with qb:
        if st.button("🌍 ESG Leaders",use_container_width=True,key="q2"):
            st.session_state.auto_q="Which companies are the ESG sustainability leaders?"
        if st.button("⚠️ Watch List",use_container_width=True,key="q4"):
            st.session_state.auto_q="Which companies should investors watch carefully?"

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    question=st.chat_input("Ask me anything...")
    if "auto_q" in st.session_state:
        question=st.session_state.auto_q
        del st.session_state.auto_q
    if question:
        st.session_state.messages.append({"role":"user","content":question})
        with st.spinner("Analyzing..."):
            answer=ask_gemini(question,data)
        st.session_state.messages.append({"role":"ai","content":answer})
        st.rerun()

    for msg in st.session_state.messages[-4:]:
        cls="umsg" if msg["role"]=="user" else "amsg"
        st.markdown(f'<div class="{cls}">{msg["content"]}</div>',unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""<div class="card"><div class="ch">
        <span class="ct">Sector Breakdown</span>
        <span style="font-size:10px;color:#64748b;">View all</span>
    </div></div>""", unsafe_allow_html=True)

    sd=df["sector"].value_counts().reset_index()
    sd.columns=["Sector","Count"]
    colors=["#22c55e","#3b82f6","#a855f7","#f59e0b","#ef4444","#06b6d4","#8b5cf6","#f97316"]
    fig=go.Figure(go.Pie(labels=sd["Sector"],values=sd["Count"],hole=0.6,
        marker_colors=colors[:len(sd)],textinfo="percent",textfont_size=10))
    fig.update_layout(height=200,margin=dict(t=0,b=0,l=0,r=100),
        paper_bgcolor="white",plot_bgcolor="white",showlegend=True,
        legend=dict(font=dict(size=10),orientation="v",x=1.02,y=0.5,xanchor="left"),
        annotations=[dict(text=f"<b>{total}</b><br>Total",x=0.38,y=0.5,font_size=12,showarrow=False)])
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

st.markdown("""
<div style="text-align:center;padding:12px;color:#94a3b8;font-size:10px;border-top:1px solid #f1f5f9;margin-top:8px;">
    Green Finance Intelligence · BigQuery · Vertex AI · Gemini · Real-Time S&P 500 ·
    <span style="color:#059669;font-weight:600;">Data Engineer</span>
</div>""", unsafe_allow_html=True)
