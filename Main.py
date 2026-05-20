import os
import json
from flask import Flask, render_template, request, jsonify
from google.cloud import bigquery
import google.generativeai as genai
import finnhub

app = Flask(__name__)

# =====================
# KONFIGURIM
# =====================
FINNHUB_KEY = os.environ.get("FINNHUB_KEY", "")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "")
PROJECT_ID = os.environ.get("PROJECT_ID", "green-finance-ai")

# Inicializo clients
bq_client = bigquery.Client(project=PROJECT_ID)
genai.configure(api_key=GEMINI_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")
finnhub_client = finnhub.Client(api_key=FINNHUB_KEY)

# =====================
# MERR TË DHËNA NGA BIGQUERY
# =====================
def get_latest_data():
    query = """
    SELECT 
        r.symbol,
        r.name,
        r.sector,
        r.price,
        r.change_percent,
        r.financial_risk_score,
        r.green_score,
        r.esg_rating,
        r.profit_margin,
        r.beta,
        r.co2_emission,
        r.market_cap,
        r.timestamp
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
# LLOGARIT STATS
# =====================
def get_stats(data):
    if not data:
        return {}
    
    total = len(data)
    high_risk = len([d for d in data if d["financial_risk_score"] >= 60])
    low_risk = len([d for d in data if d["financial_risk_score"] <= 20])
    avg_green = round(sum(d["green_score"] for d in data) / total, 1)
    
    return {
        "total_companies": total,
        "high_risk": high_risk,
        "low_risk": low_risk,
        "avg_green_score": avg_green
    }

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
You have real-time data from BigQuery for S&P 500 companies.

Company Data:
{company_info}

User Question: {question}

Provide a clear, concise analysis with:
1. Direct answer
2. Key insights from the data
3. Specific recommendations
Keep it under 200 words."""

    response = gemini_model.generate_content(prompt)
    return response.text

# =====================
# ROUTES
# =====================
@app.route("/")
def index():
    data = get_latest_data()
    stats = get_stats(data)
    return render_template("index.html", data=data, stats=stats)

@app.route("/api/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    data = get_latest_data()
    answer = ask_gemini(question, data)
    return jsonify({"answer": answer})

@app.route("/api/refresh")
def refresh():
    data = get_latest_data()
    stats = get_stats(data)
    return jsonify({"data": data, "stats": stats})

if __name__ == "__main__":
    app.run(debug=True, port=8080)