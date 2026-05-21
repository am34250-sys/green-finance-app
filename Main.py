import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
from google import genai
from google.genai import types
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

.amsg{background:#f8fafc;border:1px solid #f1f5f9;border-radius:10px;padding:9px 11px;font-size:11px;line-height:1.6;color:#334155;margin-bottom:6px;}
.umsg{background:linear-gradient(135deg,#059669,#10b981);color:white;border-radius:10px;padding:9px 11px;font-size:11px;margin-bottom:6px;margin-left:10%;line-height:1.5;}

.alrt{display:flex;gap:8px;background:#f8fafc;border:1px solid #f1f5f9;border-radius:8px;padding:7px;margin-bottom:4px;}
.aico{width:22px;height:22px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:10px;flex-shrink:0;}
.at{font-size:10px;font-weight:600;color:#0f172a;} .ad{font-size:9px;color:#64748b;} .atm{font-size:8px;color:#cbd5e1;margin-top:1px;}

.stTextInput input {
    background: #059669 !important; color: white !important;
    border-radius: 25px !important; border: none !important;
    padding: 9px 16px !important; font-size: 12px !important;
}
.stTextInput input::placeholder { color: rgba(255,255,255,0.8) !important; }
.stTextInput input:focus { box-shadow: none !important; }
.stTextInput label { display: none !important; }

.stButton button{border-radius:25px !important;font-size:12px !important;font-weight:500 !important;border:1px solid #e2e8f0 !important;background:white !important;color:#334155 !important;padding:8px 14px !important;text-align:left !important;}
.stButton button:hover{background:#f0fdf4 !important;border-color:#86efac !important;color:#059669 !important;}
div[data-testid="column"]{padding:0 3px !important;}

.ctable{width:100%;border-collapse:collapse;font-size:12px;}
.ctable th{font-size:10px;font-weight:600;color:#94a3b8;text-transform:uppercase;padding:7px 10px;border-bottom:1px solid #f1f5f9;text-align:left;letter-spacing:.04em;}
.ctable td{padding:8px 10px;border-bottom:1px solid #f8fafc;color:#334155;vertical-align:middle;}
.ctable tr:hover td{background:#f8fafc;}
.sym{font-weight:700;color:#0f172a;font-size:12px;}
.chg-up{color:#16a34a;font-weight:600;}
.chg-dn{color:#dc2626;font-weight:600;}
.risk-red{background:#fef2f2;color:#dc2626;padding:2px 7px;border-radius:20px;font-weight:600;font-size:11px;}
.risk-yel{background:#fffbeb;color:#d97706;padding:2px 7px;border-radius:20px;font-weight:600;font-size:11px;}
.risk-grn{background:#f0fdf4;color:#16a34a;padding:2px 7px;border-radius:20px;font-weight:600;font-size:11px;}
.esg-a{color:#16a34a;font-weight:600;} .esg-b{color:#2563eb;font-weight:600;} .esg-c{color:#dc2626;font-weight:600;}
.sec-cell{display:flex;align-items:center;gap:5px;color:#64748b;font-size:11px;}
</style>
""", unsafe_allow_html=True)

GEMINI_KEY = st.secrets.get("GEMINI_KEY", "")
PROJECT_ID = st.secrets.get("PROJECT_ID", "green-finance-ai")
GCP_CREDENTIALS = st.secrets.get("GCP_CREDENTIALS", None)

@st.cache_resource
def init_clients():
    try:
        if GCP_CREDENTIALS:
            creds_info = json.loads(GCP_CREDENTIALS) if isinstance(GCP_CREDENTIALS, str) else GCP_CREDENTIALS
            creds = service_account.Credentials.from_service_account_info(creds_info)
            bq = bigquery.Client(project=PROJECT_ID, credentials=creds)
        else:
            st.error("GCP_CREDENTIALS mungon ne Streamlit Secrets.")
            st.stop()
    except Exception as e:
        st.error(f"BigQuery lidhja deshtoi: {e}")
        st.stop()
    try:
        if not GEMINI_KEY:
            st.error("GEMINI_KEY mungon ne Streamlit Secrets.")
            st.stop()
        gemini_client = genai.Client(api_key=GEMINI_KEY)
    except Exception as e:
        st.error(f"Gemini inicializimi deshtoi: {e}")
        st.stop()
    return bq, gemini_client

bq_client, gemini_client = init_clients()

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

def ask_gemini(question, data_str):
    cache_key = f"ai_{hash(question + data_str[:50])}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    try:
        prompt = (
            "You are a Green Finance AI Analyst. "
            "Answer in maximum 100 words. "
            f"Company data:\n{data_str}\n"
            f"Question: {question}"
        )
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        result = response.text
        st.session_state[cache_key] = result
        return result
    except Exception as e:
        err = str(e)
        if "429" in err:
            return "Quota e API u tejkalua. Provo perseri pas 1 minute."
        return f"Gabim: {err[:200]}"

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

def trend_spark(trend="up", seed=1):
    pts, w, h = 10, 70, 20
    xs = [i * w / (pts-1) for i in range(pts)]
    ys_raw = [math.sin(i*0.9 + seed*0.6)*0.4 + (i/pts*1.2 if trend=="up" else -i/pts*1.2 if trend=="down" else math.sin(i*0.4)*0.2) for i in range(pts)]
    mn, mx = min(ys_raw), max(ys_raw)
    ys = [h-2-(y-mn)/(mx-mn+0.001)*(h-4) for y in ys_raw]
    color = "#22c55e" if trend=="up" else ("#ef4444" if trend=="down" else "#94a3b8")
    ps = " ".join(f"{x:.1f},{y:.1f}" for x,y in zip(xs,ys))
    return f'<svg viewBox="0 0 {w} {h}" style="width:70px;height:20px;display:inline-block;vertical-align:middle;"><polyline points="{ps}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

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

SECTOR_ICONS = {
    "Technology": "💻", "Chemicals": "🧪", "Utilities": "⚡",
    "Health Care": "❤️", "Semiconductors": "🔬", "Building": "🏗️",
    "Insurance": "🛡️", "Media": "📺", "Automobiles": "🚗",
    "Real Estate": "🏢", "Biotechnology": "🧬", "Energy": "⚡",
    "Industrial": "⚙️", "Industrial Con...": "⚙️", "Retail": "🛒",
    "Finance": "💰", "Life Sciences": "🔭", "Consumer": "🛍️",
}

def build_table_rows(rows):
    html = ""
    for i, d in enumerate(rows):
        chg = d["change_percent"]
        chg_cls = "chg-up" if chg >= 0 else "chg-dn"
        chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        risk = d["financial_risk_score"]
        if risk >= 60:
            risk_html = f'<span class="risk-red">● {risk}</span>'
            tr = "down"
        elif risk >= 40:
            risk_html = f'<span class="risk-yel">● {risk}</span>'
            tr = "neutral"
        else:
            risk_html = f'<span class="risk-grn">● {risk}</span>'
            tr = "up"
        gs = d["green_score"]
        green_ico = "🌿" if gs >= 70 else ("🌱" if gs >= 40 else "🏭")
        esg = d["esg_rating"]
        esg_cls = "esg-a" if esg and esg.startswith("A") else ("esg-b" if esg and esg.startswith("B") else "esg-c")
        sec = d["sector"]
        sec_ico = SECTOR_ICONS.get(sec, "📊")
        sec_short = sec[:14]+"…" if len(sec)>14 else sec
        spark = trend_spark(tr, seed=i+1)
        html += f"""<tr>
            <td><span class="sym">{d['symbol']}</span></td>
            <td style="color:#475569">{d['name'][:22]}{"…" if len(d['name'])>22 else ""}</td>
            <td style="font-weight:600">${d['price']:.2f}</td>
            <td class="{chg_cls}">{chg_str}</td>
            <td>{risk_html}</td>
            <td>{green_ico} {gs}</td>
            <td class="{esg_cls}">{esg}</td>
            <td><div class="sec-cell">{sec_ico} {sec_short}</div></td>
            <td>{spark}</td>
        </tr>"""
    return html

@st.dialog("All Alerts", width="large")
def show_all_alerts(hr2, lg2, data):
    st.markdown("#### High Risk Companies")
    if hr2:
        for d in hr2:
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #dc2626;">
                <div class="aico" style="background:#fef2f2;">⚠️</div>
                <div><div class="at">{d['name']}</div>
                <div class="ad">{d['symbol']} · Risk {d['financial_risk_score']}/100 · {d['sector']}</div>
                </div></div>""", unsafe_allow_html=True)
    else:
        st.info("Asnje kompani me risk te larte.")
    st.markdown("#### Low ESG Companies")
    if lg2:
        for d in lg2:
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #f59e0b;">
                <div class="aico" style="background:#fffbeb;">🏭</div>
                <div><div class="at">{d['name']}</div>
                <div class="ad">{d['symbol']} · Green {d['green_score']}/100 · ESG {d['esg_rating']}</div>
                </div></div>""", unsafe_allow_html=True)
    else:
        st.info("Asnje kompani me ESG te ulet.")
    st.markdown("#### Top 5 ESG Leaders")
    for d in sorted(data, key=lambda x: x["green_score"], reverse=True)[:5]:
        st.markdown(f"""<div class="alrt" style="border-left:3px solid #3b82f6;">
            <div class="aico" style="background:#eff6ff;">🌿</div>
            <div><div class="at">{d['name']}</div>
            <div class="ad">{d['symbol']} · Green {d['green_score']}/100 · ESG {d['esg_rating']}</div>
            </div></div>""", unsafe_allow_html=True)

@st.dialog("All Companies", width="large")
def show_all_companies(data):
    rows_html = build_table_rows(data)
    st.markdown(f"""
    <table class="ctable">
      <thead><tr>
        <th>Symbol</th><th>Company</th><th>Price</th><th>Change</th>
        <th>Risk Score</th><th>Green Score</th><th>ESG</th><th>Sector</th><th>Trend</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

data = get_data()
df = pd.DataFrame(data)
total = len(data)
high_risk = len([d for d in data if d["financial_risk_score"] >= 60])
low_risk = len([d for d in data if d["financial_risk_score"] <= 20])
avg_green = round(sum(d["green_score"] for d in data) / total, 1) if total else 0

h1, h2 = st.columns([3,1])
with h1:
    st.markdown("""<div style="margin-bottom:10px;">
        <div style="font-size:18px;font-weight:700;color:#0f172a;">Welcome to Green Finance Intelligence! 👋</div>
        <div style="font-size:11px;color:#64748b;margin-top:1px;">Here's what's happening with your green finance portfolio today.</div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown(f"""<div style="display:flex;justify-content:flex-end;padding-top:3px;">
        <div class="pill"><div class="dot"></div>Live · {total} companies</div>
    </div>""", unsafe_allow_html=True)

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

L, R = st.columns([14, 9], gap="medium")

with L:
    hc1, hc2, hc3 = st.columns([6, 3, 2])
    with hc1:
        st.markdown("""<div style="display:flex;align-items:center;gap:5px;padding:4px 0;">
            <div class="dot"></div><span class="ct">Live Company Scores</span>
        </div>""", unsafe_allow_html=True)
    with hc2:
        st.markdown("""<div style="padding:4px 0;">
            <div class="rpill"><div class="dot"></div>Auto-refresh · 60s</div>
        </div>""", unsafe_allow_html=True)
    with hc3:
        if st.button("View all →", key="view_all_companies", use_container_width=True):
            show_all_companies(data)

    rows_html = build_table_rows(data[:10])
    st.markdown(f"""
    <div style="background:white;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;">
    <table class="ctable">
      <thead><tr>
        <th>Symbol</th><th>Company</th><th>Price</th><th>Change</th>
        <th>Risk Score</th><th>Green Score</th><th>ESG</th><th>Sector</th><th>Trend</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    sc, ac = st.columns([1,1], gap="small")
    with sc:
        st.markdown("""<div style="padding:4px 0 2px;"><span class="ct">Sector Breakdown</span></div>""", unsafe_allow_html=True)
        sd = df["sector"].value_counts().reset_index()
        sd.columns = ["Sector","Count"]
        colors = ["#22c55e","#3b82f6","#a855f7","#f59e0b","#ef4444","#06b6d4","#8b5cf6","#f97316"]
        fig = go.Figure(go.Pie(labels=sd["Sector"], values=sd["Count"], hole=0.6,
            marker_colors=colors[:len(sd)], textinfo="percent", textfont_size=8))
        fig.update_layout(height=220, margin=dict(t=0,b=0,l=0,r=110),
            paper_bgcolor="white", plot_bgcolor="white", showlegend=True,
            legend=dict(font=dict(size=11), orientation="v", x=1.02, y=0.5, xanchor="left"),
            annotations=[dict(text=f"<b>{total}</b><br><span style='font-size:10px'>Total</span>", x=0.35, y=0.5, font_size=13, showarrow=False)])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with ac:
        hr2 = [d for d in data if d["financial_risk_score"] >= 60]
        lg2 = [d for d in data if d["green_score"] <= 20]
        bc2 = max(data, key=lambda x: x["green_score"]) if data else None

        a1, a2 = st.columns([3, 1])
        with a1:
            st.markdown("""<div style="padding:4px 0 6px;"><span class="ct">🔔 Recent Alerts</span></div>""", unsafe_allow_html=True)
        with a2:
            if st.button("View all →", key="view_all_btn", use_container_width=True):
                show_all_alerts(hr2, lg2, data)

        if hr2:
            c = hr2[0]
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #dc2626;">
                <div class="aico" style="background:#fef2f2;">⚠️</div>
                <div><div class="at">High Risk — {c['name'][:18]}</div>
                <div class="ad">{c['symbol']} · Risk {c['financial_risk_score']}/100 · {c['sector'][:14]}</div>
                <div class="atm">Just now</div></div></div>""", unsafe_allow_html=True)
        if lg2:
            c = lg2[0]
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #f59e0b;">
                <div class="aico" style="background:#fffbeb;">🏭</div>
                <div><div class="at">Low ESG — {c['name'][:18]}</div>
                <div class="ad">{c['symbol']} · Green {c['green_score']}/100 · ESG {c['esg_rating']}</div>
                <div class="atm">15m ago</div></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="alrt" style="border-left:3px solid #22c55e;">
                <div class="aico" style="background:#f0fdf4;">✅</div>
                <div><div class="at">ESG Scores Healthy</div>
                <div class="ad">All tracked companies have stable ESG metrics</div>
                <div class="atm">Updated now</div></div></div>""", unsafe_allow_html=True)
        if bc2:
            st.markdown(f"""<div class="alrt" style="border-left:3px solid #3b82f6;">
                <div class="aico" style="background:#eff6ff;">🌿</div>
                <div><div class="at">ESG Leader — {bc2['name'][:18]}</div>
                <div class="ad">{bc2['symbol']} · Green {bc2['green_score']}/100 · ESG {bc2['esg_rating']}</div>
                <div class="atm">1h ago</div></div></div>""", unsafe_allow_html=True)

with R:
    st.markdown(f"""<div style="background:white;border-radius:14px;border:1px solid #e2e8f0;padding:16px 16px 12px 16px;margin-bottom:6px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:14px;font-weight:700;color:#0f172a;">Green Finance AI Assistant</span>
                    <span style="background:#059669;color:white;padding:2px 7px;border-radius:20px;font-size:8px;font-weight:700;text-transform:uppercase;">BETA</span>
                </div>
                <div style="font-size:10px;color:#94a3b8;margin-top:1px;">Powered by real-time BigQuery data</div>
            </div>
            <div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#059669,#10b981);display:flex;align-items:center;justify-content:center;font-size:18px;">🤖</div>
        </div>
        <div style="background:#f8fafc;border:1px solid #f1f5f9;border-radius:10px;padding:10px 12px;font-size:12px;line-height:1.6;color:#334155;">
            Hello! I analyze <b>{total} S&P 500 companies</b> using real-time data from BigQuery. Ask me about risks, green scores, or investment recommendations!
        </div>
    </div>""", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**Quick Analysis**")
        qa, qb = st.columns(2, gap="small")
        with qa:
            if st.button("🏆  Best Investment", use_container_width=True, key="q1"):
                st.session_state.auto_q = "Which company is the best investment combining financial and ESG performance?"
            if st.button("📊  Risk Comparison", use_container_width=True, key="q3"):
                st.session_state.auto_q = "Compare highest and lowest risk companies"
        with qb:
            if st.button("🌍  ESG Leaders", use_container_width=True, key="q2"):
                st.session_state.auto_q = "Which companies are the ESG sustainability leaders?"
            if st.button("⚠️  Companies to Watch", use_container_width=True, key="q4"):
                st.session_state.auto_q = "Which companies should investors watch carefully?"

    ci, cb = st.columns([5,1])
    with ci:
        user_input = st.text_input("chat_input_label", placeholder="Ask me anything...",
                                   label_visibility="collapsed", key="chat_input")
    with cb:
        send = st.button("➤", use_container_width=True, key="send_btn")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    question = None
    if send and user_input:
        question = user_input
    elif "auto_q" in st.session_state:
        question = st.session_state.auto_q
        del st.session_state.auto_q

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Analyzing..."):
            info = "".join([
                f"- {d['symbol']} ({d['name']}): Risk={d['financial_risk_score']}, "
                f"Green={d['green_score']}, ESG={d['esg_rating']}\n"
                for d in data[:10]
            ])
            answer = ask_gemini(question, info)
        st.session_state.messages.append({"role": "ai", "content": answer})
        st.rerun()

    for msg in st.session_state.messages[-6:]:
        cls = "umsg" if msg["role"] == "user" else "amsg"
        st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown("""<div style="text-align:center;padding:6px;color:#94a3b8;font-size:9px;border-top:1px solid #f1f5f9;margin-top:6px;">
    Green Finance Intelligence · BigQuery · Vertex AI · Gemini · Real-Time S&P 500 ·
    <span style="color:#059669;font-weight:600;">Data Engineer</span>
</div>""", unsafe_allow_html=True)
