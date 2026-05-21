import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai
import pandas as pd
import json
import plotly.graph_objects as go
import math

st.set_page_config(page_title="Green Finance Intelligence", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: #f8fafc !important; }
.block-container { padding: 12px 16px !important; max-width: 100% !important; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
[data-testid="collapsedControl"] { display: none; }

.dot{width:5px;height:5px;background:#22c55e;border-radius:50%;animation:bl 2s infinite;display:inline-block;}
@keyframes bl{0%,100%{opacity:1}50%{opacity:0.2}}
.pill{display:inline-flex;align-items:center;gap:4px;background:#f0fdf4;border:1px solid #bbf7d0;color:#15803d;padding:3px 8px;border-radius:20px;font-size:10px;font-weight:600;}

.card{background:white;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;margin-bottom:8px;}
.ch{padding:8px 12px;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;justify-content:space-between;}
.ct{font-size:12px;font-weight:600;color:#0f172a;}
.rpill{background:#f0fdf4;border:1px solid #bbf7d0;color:#15803d;padding:2px 6px;border-radius:20px;font-size:9px;font-weight:600;display:inline-flex;align-items:center;gap:3px;}

.ai-box{background:white;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;margin-bottom:8px;}
.ai-h{padding:8px 12px;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;justify-content:space-between;}
.ai-ico{width:26px;height:26px;border-radius:7px;background:linear-gradient(135deg,#059669,#10b981);display:flex;align-items:center;justify-content:center;font-size:12px;}
.ai-n{font-size:12px;font-weight:600;color:#0f172a;} .ai-s{font-size:9px;color:#94a3b8;}
.beta{background:#059669;color:white;padding:1px 6px;border-radius:20px;font-size:8px;font-weight:700;text-transform:uppercase;}
.ai-b{padding:8px 12px;}
.amsg{background:#f8fafc;border:1px solid #f1f5f9;border-radius:8px;padding:8px 10px;font-size:11px;line-height:1.5;color:#334155;margin-bottom:5px;}
.umsg{background:linear-gradient(135deg,#059669,#10b981);color:white;border-radius:8px;padding:8px 10px;font-size:11px;margin-bottom:5px;margin-left:10%;line-height:1.5;}

.alrt{display:flex;gap:8px;background:#f8fafc;border:1px solid #f1f5f9;border-radius:8px;padding:7px;}
.aico{width:22px;height:22px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:10px;flex-shrink:0;}
.at{font-size:10px;font-weight:600;color:#0f172a;} .ad{font-size:9px;color:#64748b;line-height:1.3;} .atm{font-size:8px;color:#cbd5e1;margin-top:2px;}

div[data-testid="column"]{padding:0 3px !important;}
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
    return gemini_model.generate_content(f"Senior Green Finance AI Analyst.\nData:\n{info}\nQuestion: {q}\nMax 120 words.").text

def svg_spark(trend="up", seed=1):
    pts, w, h = 24, 300, 28
    xs = [i * w / (pts-1) for i in range(pts)]
    ys_raw = [math.sin(i*0.6 + seed*0.5)*0.6 + (i/pts*2.0 if trend=="up" else -i/pts*2.0) for i in range(pts)]
    mn, mx = min(ys_raw), max(ys_raw)
    ys = [h-2-(y-mn)/(mx-mn+0.001)*(h-4) for y in ys_raw]
    color = "#22c55e" if trend=="up" else "#ef4444"
    fill = "rgba(34,197,94,0.07)" if trend=="up" else "rgba(239,68,68,0.07)"
    ps = " ".join(f"{x:.1f},{y:.1f}" for x,y in zip(xs,ys))
    fp = f"0,{h} "+ps+f" {w},{h}"
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:28px;display:block;"><polygon points="{fp}" fill="{fill}"/><polyline points="{ps}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def kpi(ico, ico_bg, lbl, val, val_color, trend_txt, trend_color, td, seed):
    return f"""<div style="background:white;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;">
  <div style="padding:10px 12px 6px;">
    <div style="display:flex;align-items:center;gap:5px;margin-bottom:5px;">
      <div style="width:24px;height:24px;background:{ico_bg};border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;">{ico}</div>
      <span style="font-size:12px;color:#64748b;font-weight:500;">{lbl}</span>
    </div>
    <div style="display:flex;align-items:baseline;gap:6px;">
      <span style="font-size:28px;font-weight:700;color:{val_color};line-height:1;">{val}</span>
      <span style="font-size:10px;font-weight:500;color:{trend_color};">{trend_txt}</span>
    </div>
  </div>
  {svg_spark(td, seed)}
</div>"""

data = get_data()
df = pd.DataFrame(data)
total = len(data)
high_risk = len([d for d in data if d["financial_risk_score"] >= 60])
low_risk = len([d for d in data if d["financial_risk_score"] <= 20])
avg_green = round(sum(d["green_score"] for d in data) / total, 1) if total else 0

# HEADER
h1, h2 = st.columns([3,1])
with h1:
    st.markdown("""<div style="margin-bottom:10px;">
        <div style="font-size:17px;font-weight:700;color:#0f172a;">Welcome to Green Finance Intelligence! 👋</div>
        <div style="font-size:11px;color:#64748b;margin-top:1px;">Here's what's happening with your green finance portfolio today.</div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown(f"""<div style="display:flex;justify-content:flex-end;padding-top:3px;">
        <div class="pill"><div class="dot"></div>Live · {total} companies</div>
    </div>""", unsafe_allow_html=True)

# KPI
k1,k2,k3,k4 = st.columns(4)
with k1:
    st.markdown(kpi("👥","#f0fdf4","Companies Tracked",total,"#059669","↑ Updated live","#059669","up",1), unsafe_allow_html=True)
with k2:
    st.markdown(kpi("⚠️","#fef2f2","High Risk",high_risk,"#dc2626","↓ Risk ≥ 60","#dc2626","down",2), unsafe_allow_html=True)
with k3:
    st.markdown(kpi("✅","#eff6ff","Low Risk",low_risk,"#2563eb","↑ Risk ≤ 20","#059669","up",3), unsafe_allow_html=True)
with k4:
    st.markdown(kpi("🌱","#fff7ed","Avg Green Score",avg_green,"#d97706","↑ Sustainability","#059669","up",4), unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# MAIN LAYOUT
L, R = st.columns([14,9], gap="medium")

with L:
    # TABLE
    st.markdown("""<div class="card"><div class="ch">
        <div style="display:flex;align-items:center;gap:5px;"><div class="dot"></div><span class="ct">Live Company Scores</span></div>
        <div class="rpill"><div class="dot"></div>Auto-refresh · 60s</div>
    </div></div>""", unsafe_allow_html=True)

    def fr(s): return f"🔴 {s}" if s>=60 else (f"🟡 {s}" if s>=40 else f"🟢 {s}")
    def fg(s): return f"🌿 {s}" if s>=70 else (f"🌱 {s}" if s>=40 else f"🏭 {s}")

    ddf = pd.DataFrame({
        "Symbol": df["symbol"],
        "Company": df["name"].apply(lambda x: x[:18]+"…" if len(x)>18 else x),
        "Price": df["price"].apply(lambda x: f"${x:.2f}"),
        "Change": df["change_percent"].apply(lambda x: f"+{x:.2f}%" if x>=0 else f"{x:.2f}%"),
        "Risk": df["financial_risk_score"].apply(fr),
        "Green": df["green_score"].apply(fg),
        "ESG": df["esg_rating"],
        "Sector": df["sector"].apply(lambda x: x[:12]+"…" if len(x)>12 else x),
    })
    st.dataframe(ddf, use_container_width=True, hide_index=True, height=320)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # SECTOR + ALERTS side by side
    sc, ac = st.columns([1,1], gap="small")

    with sc:
        st.markdown("""<div class="card"><div class="ch">
            <span class="ct">Sector Breakdown</span>
        </div></div>""", unsafe_allow_html=True)
        sd = df["sector"].value_counts().reset_index()
        sd.columns = ["Sector","Count"]
        colors = ["#22c55e","#3b82f6","#a855f7","#f59e0b","#ef4444","#06b6d4","#8b5cf6","#f97316"]
        fig = go.Figure(go.Pie(labels=sd["Sector"], values=sd["Count"], hole=0.6,
            marker_colors=colors[:len(sd)], textinfo="percent", textfont_size=8))
        fig.update_layout(height=200, margin=dict(t=0,b=0,l=0,r=100),
            paper_bgcolor="white", plot_bgcolor="white", showlegend=True,
            legend=dict(font=dict(size=9), orientation="v", x=1.02, y=0.5, xanchor="left"),
            annotations=[dict(text=f"<b>{total}</b>", x=0.35, y=0.5, font_size=14, showarrow=False)])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with ac:
        st.markdown("""<div class="card"><div class="ch">
            <span class="ct">🔔 Alerts</span>
            <span style="font-size:9px;color:#059669;font-weight:600;">View all →</span>
        </div></div>""", unsafe_allow_html=True)

        hr2=[d for d in data if d["financial_risk_score"]>=60]
        lg2=[d for d in data if d["green_score"]<=20]
        bc2=max(data,key=lambda x:x["green_score"]) if data else None

        if hr2:
            c=hr2[0]
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #dc2626;margin-bottom:4px;">
                <div class="aico" style="background:#fef2f2;">⚠️</div>
                <div><div class="at">High Risk — {c['symbol']}</div>
                <div class="ad">Score {c['financial_risk_score']}/100</div>
                <div class="atm">Just now</div></div></div>""", unsafe_allow_html=True)
        if lg2:
            c=lg2[0]
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #f59e0b;margin-bottom:4px;">
                <div class="aico" style="background:#fffbeb;">🏭</div>
                <div><div class="at">Low ESG — {c['symbol']}</div>
                <div class="ad">Score {c['green_score']}/100</div>
                <div class="atm">15m ago</div></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="alrt" style="border-left:3px solid #22c55e;margin-bottom:4px;">
                <div class="aico" style="background:#f0fdf4;">✅</div>
                <div><div class="at">ESG Healthy</div>
                <div class="ad">All stable</div>
                <div class="atm">Now</div></div></div>""", unsafe_allow_html=True)
        if bc2:
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #3b82f6;">
                <div class="aico" style="background:#eff6ff;">🌿</div>
                <div><div class="at">ESG Leader — {bc2['symbol']}</div>
                <div class="ad">Score {bc2['green_score']}/100</div>
                <div class="atm">1h ago</div></div></div>""", unsafe_allow_html=True)

with R:
    # AI
    st.markdown("""<div class="ai-box"><div class="ai-h">
        <div style="display:flex;align-items:center;gap:7px;">
            <div class="ai-ico">🤖</div>
            <div><div class="ai-n">AI Assistant</div><div class="ai-s">Gemini + BigQuery</div></div>
        </div>
        <div class="beta">BETA</div>
    </div><div class="ai-b">""", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages=[{"role":"ai","content":f"Hello! I analyze <b>{total} S&P 500 companies</b> using real-time ESG and financial risk data. Ask me anything!"}]

    st.markdown(f"""<div class="amsg">I analyze <b>{total} S&P 500 companies</b> via BigQuery.<br>
    Ask: investment strategy · ESG leaders · financial risks</div>""", unsafe_allow_html=True)

    question = st.chat_input("Ask me anything...")

    st.markdown('<div style="font-size:10px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin:8px 0 5px;">Quick Analysis</div>', unsafe_allow_html=True)

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

    if "auto_q" in st.session_state:
        question=st.session_state.auto_q
        del st.session_state.auto_q

    if question:
        st.session_state.messages.append({"role":"user","content":question})
        with st.spinner("Analyzing..."):
            answer=ask_gemini(question,data)
        st.session_state.messages.append({"role":"ai","content":answer})
        st.rerun()

    for msg in st.session_state.messages[-6:]:
        cls="umsg" if msg["role"]=="user" else "amsg"
        st.markdown(f'<div class="{cls}">{msg["content"]}</div>',unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("""<div style="text-align:center;padding:6px;color:#94a3b8;font-size:9px;border-top:1px solid #f1f5f9;margin-top:4px;">
    Green Finance Intelligence · BigQuery · Vertex AI · Gemini · Real-Time S&P 500 ·
    <span style="color:#059669;font-weight:600;">Data Engineer</span>
</div>""", unsafe_allow_html=True)
