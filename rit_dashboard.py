"""
═══════════════════════════════════════════════════════════════════════════════
  RIT Quantathan 2026 — Flask UI Monolith Server
  File: rit_dashboard.py
  Team: Schrödinger’s Coders
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
# Configure stdout to support UTF-8 characters in Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os, csv, json, datetime
from typing import List, Dict, Any
from flask import Flask, render_template_string, jsonify, request

# ─── AI INTEGRATION (MONOLITH APPROACH) ───────────────────────────────────────
try:
    from rit_quantum_chatbot import RITQuantumChatbot
    bot = RITQuantumChatbot()
    AI_ENABLED = True
except Exception as e:
    print(f"[WARNING] Could not load RITQuantumChatbot: {e}")
    bot = None
    AI_ENABLED = False

app  = Flask(__name__)
app.config["SECRET_KEY"] = "rit-quantathan-hackathon-2026"
CSV_PATH  = "transactions.csv"
TEMPLATE_PATH = "rit_quantum_dashboard_standalone.html"

# ─── DATA ─────────────────────────────────────────────────────────────────────

def _load() -> List[Dict]:
    # Try fetching from MongoDB first
    try:
        from rit_mongodb_client import RITMongoDBClient
        db = RITMongoDBClient()
        if db.connected:
            mongo_txns = db.load_transactions()
            if mongo_txns:
                for r in mongo_txns:
                    r["amount"]             = float(r["amount"])
                    r["risk_score"]         = float(r["risk_score"])
                    r["is_fraud"]           = int(r["is_fraud"])
                    r["account_age_days"]   = float(r.get("account_age_days", 365))
                    r["velocity_l6h"]       = float(r.get("velocity_l6h", 1))
                    r["churn_rate"]         = float(r.get("churn_rate", 0.1))
                    r["ip_account_density"] = int(r.get("ip_account_density", 5))
                    r["user_risk_score"]    = float(r.get("user_risk_score", 15.0))
                    r["device_risk_score"]  = float(r.get("device_risk_score", 10.0))
                    r["merchant_risk_score"]= float(r.get("merchant_risk_score", 10.0))
                    r["network_risk_score"] = float(r.get("network_risk_score", 10.0))
                return mongo_txns
    except Exception as e:
        print(f"[MONGO WARNING] Could not load data from MongoDB: {e}. Falling back to CSV.")

    # Fallback to CSV file
    if not os.path.exists(CSV_PATH): return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["amount"]             = float(r["amount"])
        r["risk_score"]         = float(r["risk_score"])
        r["is_fraud"]           = int(r["is_fraud"])
        r["account_age_days"]   = float(r.get("account_age_days", 365))
        r["velocity_l6h"]       = float(r.get("velocity_l6h", 1))
        r["churn_rate"]         = float(r.get("churn_rate", 0.1))
        r["ip_account_density"] = int(r.get("ip_account_density", 5))
        
        # New Q-Guard Agents fields
        r["user_risk_score"]    = float(r.get("user_risk_score", 15.0))
        r["device_risk_score"]  = float(r.get("device_risk_score", 10.0))
        r["merchant_risk_score"]= float(r.get("merchant_risk_score", 10.0))
        r["network_risk_score"] = float(r.get("network_risk_score", 10.0))
    return rows

def _chat(msg: str) -> str:
    if not AI_ENABLED or bot is None:
        return "[SYSTEM] Quantum Chatbot offline. Ensure 'openai' is installed and OPENROUTER_API_KEY is configured."
    try:
        return bot.chat(msg)
    except Exception as e:
        return f"[ERROR] Quantum AI chat failed: {str(e)}"

# Mapping fraud categories to dashboard badges
BADGE = {
    "Normal":                    "b-N",
    "Mule Chain":                "b-MC",
    "Shared Device":             "b-SD",
    "High Velocity":             "b-HV",
    "Cross Channel":             "b-CC",
    "Mule Collection":           "b-MX",
    "Circular Loop":             "b-CL",
    "Quantathan Flagged Fraud":  "b-MC",
    "Kaggle Verified Fraud":     "b-SD",
}

FT_COLORS = {
    "Mule Chain":                "#ffb700",
    "Shared Device":             "#c864ff",
    "High Velocity":             "#ff3c5a",
    "Cross Channel":             "#00d4ff",
    "Mule Collection":           "#ff6a00",
    "Circular Loop":             "#ff00ff",
    "Quantathan Flagged Fraud":  "#ff3c5a",
    "Kaggle Verified Fraud":     "#c864ff",
}

ALERTS_STATIC = [
    {"title":"[CRITICAL] VQC Trigger: 8 Mules → COLL_ACC_01 (Fan-In)","meta":"2025-07-02 10:00–10:07 · IP: 103.50.181.18 · age: 5d","risk":90},
    {"title":"[CRITICAL] VQC Trigger: Alpha→Beta→Gamma→Alpha (Circular Loop)","meta":"2025-07-02 15:00–15:10 · IP: 192.168.1.1 · age: 5d","risk":93},
    {"title":"[CRITICAL] Geolocation Anomaly: Saranya Venkat (Impossible Travel)","meta":"2025-06-10 11:05 · Chennai RIT Branch + Delhi ATM 45s apart","risk":95},
    {"title":"[HIGH] VQC Prediction: Senthil Kumar IMPS structuring","meta":"2025-06-09 16:00 · velocity_l6h peaks at 9 (HVEL)","risk":93},
    {"title":"[HIGH] Network Anomaly: Arjun→Priya→Karthik (Mule Chain)","meta":"2025-06-05 14:00 · IP: 103.161.159.227 · iPhone 14","risk":91},
    {"title":"[WARN] Shared Hardware: Samsung S23 · 5 Accounts","meta":"2025-06-07 10:30–38 · ip_account_density: 14","risk":86},
]

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
    else:
        return f"<h3>Error: {TEMPLATE_PATH} not found. Run simulation first.</h3>"

    txns = _load()
    fraud = [t for t in txns if t["is_fraud"]==1]
    
    # Calculate statistics
    ft_counts: dict = {}
    for t in fraud:
        ft_counts[t["fraud_type"]] = ft_counts.get(t["fraud_type"],0)+1
    total = max(len(fraud),1)
    
    fraud_types = [
        {"name":ft,"count":cnt,"pct":round(cnt/total*100),
         "color":FT_COLORS.get(ft,"#00d4ff")}
        for ft,cnt in ft_counts.items()
    ]
    
    # Read Q-Guard telemetry metadata
    xai = {}
    strategies = {}
    thresholds = {}
    weights = {}
    
    quantum_metadata = {
        "vqc_variational_weights_phi": [0.45, -0.62, 0.78, 0.31],
        "vqc_variational_weights_gamma": [-0.15, 0.84, -0.32, 0.95],
        "avg_vqc_fraud_probability": 0.842,
        "avg_vqc_normal_probability": 0.041,
        "circuit_qubits": 4,
        "quantum_gates_used": "8 single-qubit rotations, 4 CNOT gates",
        "execution_mode": "Simulated Quantum Weight Optimization (excitation projection)"
    }
    
    if os.path.exists("graph_report.json"):
        try:
            with open("graph_report.json", "r") as f:
                rpt = json.load(f)
                if "quantum_vqc_telemetry" in rpt:
                    quantum_metadata = rpt["quantum_vqc_telemetry"]
                xai = rpt.get("xai_explanations", {})
                strategies = rpt.get("strategy_recommendations", {})
                thresholds = rpt.get("adaptive_thresholds", {})
                weights = rpt.get("quantum_predictions", {})
        except Exception as e:
            print(f"[WARNING] Could not parse graph_report.json: {e}")

    for t in txns:
        acc = t["account_number"]
        t["badge"] = BADGE.get(t.get("fraud_type","Normal"), "b-N")
        t["threshold"] = thresholds.get(acc, 80.0)
        t["explanation"] = " | ".join(xai.get(acc, ["Telemetry bounds normal"]))
        t["strategy"] = " | ".join(strategies.get(acc, ["Passive monitoring"]))
        t["weights"] = json.dumps(weights.get(acc, {}).get("dynamic_weights", {"user": 25, "device": 25, "merchant": 25, "network": 25}))

    blocked_ips_count = len(set(t["ip_address"] for t in fraud))
    mule_names = ['Mule0','Mule1','Mule2','Mule3','Mule4','Mule5','Mule6','Mule7']
    vel_vals    = ['₹9,990\nvel:2','₹9,890\nvel:3','₹9,790\nvel:4','₹9,690\nvel:5',
                   '₹9,590\nvel:6','₹9,490\nvel:7','₹9,390\nvel:8','₹9,290\nvel:9 [!]']
    
    return render_template_string(html_content,
        stats={"total":len(txns),"fraud":len(fraud),
               "max_risk":max((t["risk_score"] for t in fraud),default=0.0),
               "blocked": blocked_ips_count},
        alerts=ALERTS_STATIC,
        fraud_types=fraud_types,
        transactions=txns,
        mule_names=mule_names,
        vel_vals=vel_vals,
        quantum=quantum_metadata
    )

@app.route("/api/status")
def api_status():
    return jsonify({"api": True, "chat": AI_ENABLED, "quantum": True})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    return jsonify({"response": _chat(data.get("message",""))})

@app.route("/api/transactions")
def api_txns():
    fraud_only = request.args.get("fraud_only","false").lower()=="true"
    txns = _load()
    if fraud_only: txns=[t for t in txns if t["is_fraud"]]
    return jsonify(txns)

@app.route("/api/stats")
def api_stats():
    txns=_load(); fraud=[t for t in txns if t["is_fraud"]]
    return jsonify({"total":len(txns),"fraud":len(fraud),
                    "max_risk":max((t["risk_score"] for t in fraud),default=0.0)})


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║  RIT Quantathan — UI Command Terminal    ║")
    print("║  Schrödinger’s Coders · 2026            ║")
    print("╚══════════════════════════════════════════╝\n")
    print("[DASH] Dashboard running at: http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
