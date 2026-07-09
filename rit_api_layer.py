"""
═══════════════════════════════════════════════════════════════════════════════
  RIT Quantathan 2026 — Q-Guard AI Enhanced REST API Layer
  File: rit_api_layer.py
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

import os, csv, json, uuid, datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import asyncio

try:
    from rit_txn_simulator import TransactionSimulator
    from rit_quantum_graph import GraphIntelligence, VariationalQuantumClassifier
    MODULES = True
except ImportError:
    MODULES = False

app = FastAPI(
    title      = "RIT Quantathan 2026 — Quantum AI Fraud Detection API",
    description= "Real-Time VQC-based Cross-Channel Mule Detection\nTeam: Schrödinger’s Coders",
    version    = "3.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"], allow_credentials=True)

# ─── STATE ────────────────────────────────────────────────────────────────────

_txns:    List[Dict] = []
# Q-Guard AI additions
_report:  Dict       = {}
_alerts:  List[Dict] = []
_clients: List[asyncio.Queue] = []

# ─── MODELS ───────────────────────────────────────────────────────────────────

class TxnIn(BaseModel):
    name:                      str   = Field(..., example="Arjun Sharma")
    account_number:            str   = Field(..., example="SB95822412")
    account_type:              str   = Field("Savings")
    mobile_number:             str   = Field(..., example="9914763202")
    pincode:                   str   = Field(..., example="602117")
    narration:                 str   = Field(..., example="Transfer")
    trans_type:                str   = Field(..., example="UPI Payment")
    amount:                    float = Field(..., gt=0, example=5000.0)
    ip_address:                str   = Field(..., example="103.161.159.227")
    device:                    str   = Field(..., example="iPhone 14")
    receiver_account:          str   = Field("SELF")
    receiver_name:             str   = Field("Unknown")
    receiver_pincode:          str   = Field("000000")
    account_age_days:          float = Field(365.0)
    
    # Q-Guard Agent Parameters (Optional inputs for mock overrides)
    amount_deviation_ratio:    Optional[float] = Field(None, example=1.2)
    daily_limit_fraction:      Optional[float] = Field(None, example=0.05)
    device_trust_score:        Optional[float] = Field(None, example=95.0)
    is_rooted_or_emulator:     Optional[int]   = Field(None, example=0)
    merchant_chargeback_rate:  Optional[float] = Field(None, example=0.005)
    is_vpn_or_proxy:           Optional[int]   = Field(None, example=0)

class QuantumPredictIn(BaseModel):
    user_risk_score:       float = Field(..., ge=0, le=100, example=85.0)
    device_risk_score:     float = Field(..., ge=0, le=100, example=35.0)
    merchant_risk_score:   float = Field(..., ge=0, le=100, example=15.0)
    network_risk_score:    float = Field(..., ge=0, le=100, example=75.0)


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _risk_level(s: float) -> str:
    return "CRITICAL" if s>=90 else "HIGH" if s>=70 else "MEDIUM" if s>=40 else "LOW"

def calculate_risk_summary_matrix() -> List[Dict]:
    if not _txns:
        return []

    mule_txns = [t for t in _txns if int(t.get("is_fraud", 0)) == 1]
    if not mule_txns: return []
    
    # Create simple matrix showing risk profile mapping for Q-Guard
    types = ["Mule Chain", "Shared Device", "High Churn", "Cross Channel", "Circular Loop", "Mule Collection"]
    out = []
    for t in types:
        grp = [x for x in mule_txns if x.get("fraud_type") == t]
        if grp:
            out.append({
                "type": t,
                "count": len(grp),
                "avg_risk": round(sum(float(x["risk_score"]) for x in grp)/len(grp), 1),
                "peak_risk": max(float(x["risk_score"]) for x in grp)
            })
    return out

def _load():
    global _txns, _report, _alerts
    print("[API] Ingesting transaction database...")
    if not os.path.exists("transactions.csv"):
        if MODULES:
            sim = TransactionSimulator()
            sim.run()
            sim.to_csv()
            
    if os.path.exists("transactions.csv"):
        with open("transactions.csv", newline="", encoding="utf-8") as f:
            _txns = list(csv.DictReader(f))
            
    # Load graph engine results
    if os.path.exists("graph_report.json"):
        with open("graph_report.json") as f:
            _report = json.load(f)
            
    # Build alert queue
    _alerts = []
    for t in _txns:
        if int(t.get("is_fraud", 0)) == 1:
            _alerts.append({
                "alert_id": f"ALRT-{t['txn_id']}",
                "severity": "critical" if float(t["risk_score"]) >= 85 else "warning",
                "fraud_type": t["fraud_type"],
                "account": t["account_number"],
                "risk_score": float(t["risk_score"]),
                "timestamp": t["timestamp"]
            })
    # Sort alerts desc
    _alerts.sort(key=lambda x: x["timestamp"], reverse=True)


# ─── LIFECYCLE ────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    _load()
    print(f"[API] ✅ Ready — {len(_txns)} txns, {len(_alerts)} alerts")

# ─── HEALTH ───────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {"status": "online", "system": "RIT Quantathan API", "version": "3.0",
            "transactions": len(_txns), "alerts": len(_alerts),
            "timestamp": datetime.datetime.now().isoformat()}

# ─── TRANSACTIONS ─────────────────────────────────────────────────────────────

@app.get("/transactions", tags=["Transactions"])
async def get_txns(
    fraud_only: bool = Query(False),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    fraud_type: Optional[str] = Query(None),
    min_churn: Optional[float] = Query(None),
):
    data = _txns
    if fraud_only:
        data = [t for t in data if int(t.get("is_fraud", 0)) == 1]
    if fraud_type:
        data = [t for t in data if t.get("fraud_type") == fraud_type]
    if min_churn:
        data = [t for t in data if float(t.get("churn_rate", 0)) >= min_churn]

    return {"total": len(data), "transactions": data[offset:offset+limit]}

@app.get("/transactions/fraud", tags=["Transactions"])
async def get_fraud_txns():
    data = [t for t in _txns if int(t.get("is_fraud", 0)) == 1]
    return {"total": len(data), "transactions": data}

@app.get("/transactions/{txn_id}", tags=["Transactions"])
async def get_txn(txn_id: str):
    t = next((x for x in _txns if x["txn_id"]==txn_id), None)
    if not t: raise HTTPException(404, f"Transaction {txn_id} not found")
    return t

@app.post("/transactions", tags=["Transactions"])
async def add_txn(inp: TxnIn):
    txn_id = str(uuid.uuid4())[:8].upper()
    ts     = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. User Agent scoring
    recent = [t for t in _txns if t["account_number"] == inp.account_number]
    velocity = len(recent)
    amt_dev = inp.amount_deviation_ratio or (1.2 if velocity > 3 else 0.9)
    daily_frac = inp.daily_limit_fraction or min(1.0, inp.amount / 150000.0)
    
    user_risk = 10.0
    if amt_dev > 2.0: user_risk += 35.0
    if daily_frac > 0.8: user_risk += 40.0
    if velocity >= 5: user_risk += 20.0
    user_risk = min(99.0, user_risk)

    # 2. Device Agent scoring
    rooted = inp.is_rooted_or_emulator or (1 if inp.device == "Emulator" else 0)
    trust = inp.device_trust_score or (30.0 if rooted else 95.0)
    
    device_risk = 10.0
    if rooted: device_risk += 70.0
    if trust < 50.0: device_risk += 20.0
    device_risk = min(99.0, device_risk)

    # 3. Merchant Agent scoring
    chargeback = inp.merchant_chargeback_rate or (0.12 if inp.narration == "Hold Category" else 0.005)
    
    merchant_risk = 10.0
    if chargeback > 0.05: merchant_risk += 50.0
    merchant_risk = min(99.0, merchant_risk)

    # 4. Network Agent scoring
    vpn = inp.is_vpn_or_proxy or (1 if "vpn" in inp.ip_address or inp.ip_address.startswith("103.50") else 0)
    
    network_risk = 10.0
    if vpn: network_risk += 60.0
    if inp.pincode == "110001" and velocity > 1: network_risk += 30.0  # Simulated Travel Sequence
    network_risk = min(99.0, network_risk)

    # 5. Quantum Aggregation (VQC Weight Optimizer)
    vqc = VariationalQuantumClassifier()
    q_res = vqc.predict(user_risk, device_risk, merchant_risk, network_risk)
    final_risk = q_res["quantum_risk_score"]

    # 6. Adaptive Threshold Decision
    hour = int(ts.split()[1].split(":")[0])
    is_late_night = (hour >= 0 and hour <= 5)
    
    if is_late_night:
        threshold = 65.0
    elif merchant_risk > 65.0:
        threshold = 58.0
    elif inp.account_age_days < 30:
        threshold = 70.0
    else:
        threshold = 80.0
        
    is_fraud = 1 if final_risk >= threshold else 0
    ftype = "Quantathan Flagged Fraud" if is_fraud else "Normal"
    
    # Generate XAI triggers & action recommendations
    flags = []
    if user_risk > 45: flags.append("User behavior amount deviation")
    if device_risk > 45: flags.append("Device fingerprint integrity compromised")
    if merchant_risk > 45: flags.append("High chargeback merchant profile")
    if network_risk > 45: flags.append("VPN/Proxy impossible travel network signature")
    if not flags: flags.append("Normal telemetry bounds")
    
    strategies = []
    if user_risk > 45: strategies.extend(["SMS OTP Verification Required", "Temporary Transaction Hold"])
    if device_risk > 45: strategies.extend(["Face Authentication Check", "Restrict Device Fingerprint Access"])
    if network_risk > 45: strategies.extend(["Proxy/VPN Interdiction Alert"])
    if is_fraud: strategies.append("BLOCK TRANSACTION & Alert Fraud Response Team")

    new_t = {
        "timestamp": ts, "txn_id": txn_id, "name": inp.name,
        "account_number": inp.account_number, "account_type": inp.account_type,
        "mobile_number": inp.mobile_number, "pincode": inp.pincode,
        "narration": inp.narration, "trans_type": inp.trans_type, "amount": inp.amount,
        "ip_address": inp.ip_address, "device": inp.device,
        "receiver_account": inp.receiver_account, "is_fraud": is_fraud,
        "fraud_type": ftype if is_fraud else "Normal", 
        "risk_score": final_risk,
        "account_age_days": inp.account_age_days,
        "receiver_name": inp.receiver_name, "receiver_pincode": inp.receiver_pincode,
        "velocity_l6h": float(velocity + 1), "churn_rate": 0.15,
        "ip_account_density": 1,
        
        # Q-Guard parameters
        "amount_deviation_ratio": amt_dev,
        "daily_limit_fraction": daily_frac,
        "user_risk_score": user_risk,
        "device_trust_score": trust,
        "is_rooted_or_emulator": rooted,
        "device_risk_score": device_risk,
        "merchant_chargeback_rate": chargeback,
        "merchant_risk_score": merchant_risk,
        "is_vpn_or_proxy": vpn,
        "network_risk_score": network_risk,
    }
    _txns.append(new_t)

    if is_fraud:
        alert = {"alert_id": f"A-NEW-{txn_id}", "severity": "critical" if final_risk >= 85 else "warning",
                 "fraud_type": ftype, "title": f"Q-Guard Alert: {ftype}",
                 "account": inp.account_number, "risk_score": final_risk,
                 "timestamp": ts}
        _alerts.insert(0, alert)
        for q in _clients:
            await q.put(json.dumps(alert))

    return {
        "txn_id": txn_id, 
        "risk_score": final_risk,
        "adaptive_threshold": threshold,
        "risk_level": _risk_level(final_risk), 
        "is_blocked": is_fraud,
        "fraud_type": ftype, 
        "explanations": flags, 
        "recommendations": strategies,
        "quantum_weights": q_res["dynamic_weights"],
        "quantum_vqc": q_res, 
        "transaction": new_t
    }

# ─── QUANTUM SPECIFIC ENDPOINTS ───────────────────────────────────────────────

@app.get("/quantum/state/{account_number}", tags=["Quantum AI"])
async def get_quantum_state(account_number: str):
    """Retrieves computed quantum states & Bloch sphere vectors for an account."""
    if _report and "quantum_predictions" in _report:
        pred = _report["quantum_predictions"].get(account_number)
        if pred: return {"account_number": account_number, "quantum_state": pred}
    
    # Fallback VQC estimation if report not loaded
    acc_txns = [t for t in _txns if t["account_number"]==account_number]
    if not acc_txns: raise HTTPException(404, f"Account {account_number} not found")
    
    user_risk = sum(float(t.get("user_risk_score", 15.0)) for t in acc_txns) / len(acc_txns)
    device_risk = sum(float(t.get("device_risk_score", 10.0)) for t in acc_txns) / len(acc_txns)
    merchant_risk = sum(float(t.get("merchant_risk_score", 10.0)) for t in acc_txns) / len(acc_txns)
    network_risk = sum(float(t.get("network_risk_score", 10.0)) for t in acc_txns) / len(acc_txns)
    
    vqc = VariationalQuantumClassifier()
    q_res = vqc.predict(user_risk, device_risk, merchant_risk, network_risk)
    return {"account_number": account_number, "quantum_state": q_res}

@app.post("/quantum/predict", tags=["Quantum AI"])
async def quantum_predict(inp: QuantumPredictIn):
    """Executes real-time simulated VQC quantum weight aggregation for the 4 Agents."""
    vqc = VariationalQuantumClassifier()
    q_res = vqc.predict(inp.user_risk_score, inp.device_risk_score, inp.merchant_risk_score, inp.network_risk_score)
    return q_res

# ─── ALERTS ───────────────────────────────────────────────────────────────────

@app.get("/alerts", tags=["Alerts"])
async def get_alerts(severity: Optional[str]=None):
    data = _alerts if not severity else [a for a in _alerts if a["severity"]==severity]
    return {"total": len(data), "alerts": data}

@app.get("/alerts/live", tags=["Alerts"])
async def live_alerts(request: Request):
    q: asyncio.Queue = asyncio.Queue()
    _clients.append(q)
    async def gen():
        try:
            for a in _alerts[:5]:
                yield f"data: {json.dumps(a)}\n\n"
            while True:
                msg = await q.get()
                yield f"data: {msg}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            _clients.remove(q)
    return StreamingResponse(gen(), media_type="text/event-stream")

# ─── GRAPH ENGINE INTEGRATION ─────────────────────────────────────────────────

@app.get("/graph/report",  tags=["Graph"])
async def graph_rpt(): return _report if _report else {"error": "Report not loaded"}

@app.get("/graph/fan-in",  tags=["Graph"])
async def graph_fan(): return _report.get("fan_in_alerts", [])

@app.get("/graph/loops",   tags=["Graph"])
async def graph_loops(): return _report.get("circular_loops", [])

@app.get("/graph/churn",   tags=["Graph"])
async def graph_churn(): return _report.get("high_churn", [])

# ─── DETAILED STATS & ANALYTICS ───────────────────────────────────────────────

@app.get("/analytics/velocity", tags=["Analytics"])
async def velocity_anal():
    return _report.get("velocity_alerts", [])

@app.get("/analytics/new-accounts", tags=["Analytics"])
async def new_accounts():
    return [t for t in _txns if float(t.get("account_age_days", 365)) < 30]

@app.get("/analytics/ip-density", tags=["Analytics"])
async def ip_density():
    return _report.get("ip_clusters", [])

# ─── RISK PROFILE FOR INDIVIDUAL ACCOUNT ──────────────────────────────────────

@app.get("/risk/{account_number}", tags=["Risk"])
async def get_risk(account_number: str):
    txs = [t for t in _txns if t["account_number"]==account_number]
    if not txs: raise HTTPException(404, f"Account {account_number} not found")
    
    score = _report.get("quantum_predictions", {}).get(account_number, {}).get("quantum_risk_score", 10.0)
    weights = _report.get("quantum_predictions", {}).get(account_number, {}).get("dynamic_weights", {"user": 25, "device": 25, "merchant": 25, "network": 25})
    reasons = _report.get("xai_explanations", {}).get(account_number, ["Telemetry bounds normal"])
    strategies = _report.get("strategy_recommendations", {}).get(account_number, ["Allow transaction"])
    threshold = _report.get("adaptive_thresholds", {}).get(account_number, 80.0)

    return {
        "account_number": account_number,
        "name": txs[0]["name"],
        "transactions_count": len(txs),
        "aggregated_risk_score": score,
        "adaptive_threshold": threshold,
        "is_blocked": 1 if score >= threshold else 0,
        "risk_level": _risk_level(score),
        "explanations": reasons,
        "recommendations": strategies,
        "quantum_weights": weights,
        "recent_transactions": txs[:10]
    }

# ─── DASHBOARD STATS ──────────────────────────────────────────────────────────

@app.get("/api/dashboard/stats", tags=["Dashboard"])
async def dashboard_stats():
    fraud = [t for t in _txns if int(t.get("is_fraud", 0)) == 1]
    return {
        "total": len(_txns),
        "fraud": len(fraud),
        "blocked": len(set(t["ip_address"] for t in fraud)),
        "max_risk": max((float(t["risk_score"]) for t in _txns), default=0.0),
        "recent_alerts": _alerts[:10]
    }

@app.get("/api/risk_matrix", tags=["Dashboard"])
async def risk_matrix():
    return calculate_risk_summary_matrix()

@app.get("/stats", tags=["Dashboard"])
async def get_dashboard_summary():
    return {
        "total_transactions": len(_txns),
        "fraud_count": sum(1 for t in _txns if int(t.get("is_fraud",0))==1),
        "alerts_count": len(_alerts)
    }

@app.get("/fraud-story", tags=["Dashboard"])
async def get_stories():
    return {
        "stories": [
            {"id":"S1","title":"Mule Fund Relay Chain","fraud_type":"Mule Chain",
             "risk_score":91.0,"ip":"103.161.159.227","device":"iPhone 14",
             "nodes":["SB23451009","SB95822412","SB11094323"],"amounts":[50000,48000,46000]},
            {"id":"S2","title":"Compromised Device Farm","fraud_type":"Shared Device",
             "risk_score":86.0,"ip":"103.221.93.148","device":"Samsung S23",
             "nodes":["SB89254563","SB46913810","SB23756669","SB13999315","SB22575562"],"amounts":[32000,28000,35000,18000,22000]},
            {"id":"S3","title":"Structured IMPS Velocity Evasion","fraud_type":"High Velocity",
             "risk_score":93.5,"ip":"103.50.181.18","device":"Laptop-Chrome",
             "nodes":["SB80943224"],"amounts":[9990,9890,9790,9690,9590,9490,9390,9290]},
            {"id":"S4","title":"Impossible Travel Velocity","fraud_type":"Cross Channel",
             "risk_score":95.0,"ip":"Multiple","device":"Multiple",
             "nodes":["SB23756669"],"amounts":[20000,35000]},
            {"id":"S5","title":"Coordinated Fan-In Mule Collection","fraud_type":"Mule Collection",
             "risk_score":90.0,"ip":"103.50.181.18","device":"OnePlus 11",
             "nodes":["MULE_ACC_0","MULE_ACC_1","MULE_ACC_2","MULE_ACC_3","COLL_ACC_01"],"amounts":[5000,5000,5000,5000]},
            {"id":"S6","title":"Circular Loop Laundering","fraud_type":"Circular Loop",
             "risk_score":93.0,"ip":"192.168.1.1","device":"OnePlus 11",
             "nodes":["ACC_A","ACC_B","ACC_C","ACC_A"],"amounts":[10000,9900,9800]},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print("╔══════════════════════════════════════════╗")
    print("║  Q-Guard AI — API Layer                  ║")
    print("║  Schrödinger’s Coders · 2026            ║")
    print("╚══════════════════════════════════════════╝\n")
    print("[API] Docs running at: http://127.0.0.1:8000/docs\n")
    uvicorn.run("rit_api_layer:app", host="127.0.0.1", port=8000, reload=True)
