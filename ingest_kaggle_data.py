"""
═══════════════════════════════════════════════════════════════════════════════
  RIT Quantathan 2026 — Kaggle Ingestion & Mapping Pipeline
  File: ingest_kaggle_data.py
  Team: Schrödinger’s Coders
═══════════════════════════════════════════════════════════════════════════════
Instructions:
1. Install pandas if not available: pip install pandas
2. Download the IEEE-CIS Fraud Detection dataset from Kaggle:
   https://www.kaggle.com/competitions/ieee-fraud-detection/data
3. Extract 'train_transaction.csv' and 'train_identity.csv' into this directory.
4. Run this script: python ingest_kaggle_data.py
"""

import os
import sys
import datetime
import random
import uuid

# Configure stdout to support UTF-8 characters in Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def ingest_ieee_cis(limit_rows: int = 5000):
    print("╔══════════════════════════════════════════╗")
    print("║  Q-Guard AI — Kaggle Ingestion Pipeline  ║")
    print("║  Schrödinger’s Coders · 2026            ║")
    print("╚══════════════════════════════════════════╝\n")

    if not PANDAS_AVAILABLE:
        print("[ERROR] 'pandas' is not installed. Please run: pip install pandas")
        return

    tx_file = "train_transaction.csv"
    id_file = "train_identity.csv"

    # Check subdirectory ieee-fraud-detection
    if os.path.exists("ieee-fraud-detection/train_transaction.csv"):
        tx_file = "ieee-fraud-detection/train_transaction.csv"
    if os.path.exists("ieee-fraud-detection/train_identity.csv"):
        id_file = "ieee-fraud-detection/train_identity.csv"

    if not os.path.exists(tx_file):
        print(f"[ERROR] Could not find raw Kaggle transaction file: '{tx_file}'")
        print("Please download it from: https://www.kaggle.com/competitions/ieee-fraud-detection/data")
        return

    print(f"[INGEST] Reading transaction dataset (first {limit_rows} rows)...")
    df_tx = pd.read_csv(tx_file, nrows=limit_rows)
    
    if os.path.exists(id_file):
        print("[INGEST] Found identity file. Joining datasets...")
        df_id = pd.read_csv(id_file)
        df = pd.merge(df_tx, df_id, on="TransactionID", how="left")
    else:
        print("[WARNING] 'train_identity.csv' not found. Using transaction features only.")
        df = df_tx
        # Create empty columns to represent identity fields
        for col in ["id_30", "id_31", "DeviceInfo"]:
            df[col] = np.nan

    print(f"[INGEST] Processing and mapping {len(df)} transactions to Q-Guard AI schema...")

    # 1. Base mappings
    processed = pd.DataFrame()
    
    # Generate timestamp starting from June 1st, 2025
    base_date = datetime.datetime(2025, 6, 1, 9, 0, 0)
    # TransactionDT represents seconds delta from a reference
    min_dt = df["TransactionDT"].min()
    processed["timestamp"] = df["TransactionDT"].apply(lambda dt: (base_date + datetime.timedelta(seconds=int(dt - min_dt))).strftime("%Y-%m-%d %H:%M:%S"))
    
    processed["txn_id"] = df["TransactionID"].astype(str)
    
    # Fill Names randomly
    names_pool = [
        "Arjun Sharma","Priya Nair","Karthik Rajan","Meena Pillai","Rahul Gupta",
        "Deepa Krishnan","Suresh Babu","Anitha Reddy","Vijay Kumar","Lakshmi Iyer",
        "Manoj Patel","Rekha Singh","Arun Menon","Sindhu Rao","Balaji Natarajan"
    ]
    processed["name"] = [random.choice(names_pool) for _ in range(len(df))]
    
    # Random account numbers
    processed["account_number"] = df["card1"].apply(lambda c1: f"SB{int(c1):08d}" if not pd.isna(c1) else f"SB{random.randint(10000000, 99999999)}")
    processed["account_type"] = [random.choice(["Savings", "Current", "Salary"]) for _ in range(len(df))]
    processed["mobile_number"] = [f"9{random.randint(100000000, 999999999)}" for _ in range(len(df))]
    
    # Map card2/3 to pincodes
    pincodes_pool = ["602117", "600001", "600040", "110001", "560001", "400001"]
    processed["pincode"] = df["card2"].apply(lambda c2: pincodes_pool[int(c2) % len(pincodes_pool)] if not pd.isna(c2) else random.choice(pincodes_pool))
    
    processed["narration"] = df["ProductCD"].apply(lambda p: f"Purchase Category {p}" if not pd.isna(p) else "General Transfer")
    
    trans_types = ["Online Transfer", "UPI Payment", "Net Banking", "Mobile Banking"]
    processed["trans_type"] = df["ProductCD"].apply(lambda p: "Online Transfer" if p=='W' else "Net Banking" if p=='H' else random.choice(trans_types))
    
    processed["amount"] = df["TransactionAmt"].fillna(100.0).round(2)
    processed["ip_address"] = df["TransactionID"].apply(lambda x: f"103.{random.randint(1,254)}.{random.randint(1,254)}.{x%254}")
    
    # Map DeviceInfo
    processed["device"] = df["DeviceInfo"].fillna("Unknown Device")
    processed["receiver_account"] = [f"COLL{random.randint(10,99)}" for _ in range(len(df))]
    processed["is_fraud"] = df["isFraud"].fillna(0).astype(int)
    processed["fraud_type"] = processed["is_fraud"].apply(lambda f: "Kaggle Verified Fraud" if f == 1 else "Normal")
    
    # Fill defaults
    processed["account_age_days"] = [round(random.uniform(30, 700), 0) for _ in range(len(df))]
    processed["receiver_name"] = [random.choice(["Priya Sharma","Anjali Gupta","Karan Malhotra"]) for _ in range(len(df))]
    processed["receiver_pincode"] = processed["pincode"]
    processed["velocity_l6h"] = [float(random.randint(1, 3)) for _ in range(len(df))]
    processed["churn_rate"] = [round(random.uniform(0.10, 0.40), 3) for _ in range(len(df))]
    processed["ip_account_density"] = [random.randint(1, 2) for _ in range(len(df))]

    # ─── AGENT 1: User Behavior Intelligence ───
    # spending deviation based on TransactionAmt compared to normal mean
    amt_mean = processed["amount"].mean()
    processed["amount_deviation_ratio"] = (processed["amount"] / amt_mean).round(2)
    processed["daily_limit_fraction"] = (processed["amount"] / 150000.0).round(3)
    
    # Calculate User Risk (high deviation or daily limit fraction boosts risk)
    processed["user_risk_score"] = processed.apply(
        lambda r: min(99.0, round((r["amount_deviation_ratio"] * 15.0) + (r["daily_limit_fraction"] * 40.0) + random.uniform(5, 15), 1)),
        axis=1
    )

    # ─── AGENT 2: Device Intelligence ───
    # If device info represents rooted indicators or desktop/emulators
    def get_device_metrics(device_str):
        device_str = str(device_str).lower()
        if "unknown" in device_str:
            return 70.0, 0, 20.0
        elif any(kw in device_str for kw in ["windows", "mac", "linux"]):
            return 85.0, 0, 15.0
        elif any(kw in device_str for kw in ["ios", "iphone", "samsung", "oneplus"]):
            return 90.0, 0, 10.0
        else: # Rooted/emulator indicator heuristic
            return 30.0, 1, 80.0
            
    dev_metrics = processed["device"].apply(get_device_metrics)
    processed["device_trust_score"] = [m[0] for m in dev_metrics]
    processed["is_rooted_or_emulator"] = [m[1] for m in dev_metrics]
    processed["device_risk_score"] = [m[2] for m in dev_metrics]

    # ─── AGENT 3: Merchant Rating Intelligence ───
    # Heuristics based on card type or ProductCD
    processed["merchant_chargeback_rate"] = df["ProductCD"].apply(lambda p: 0.125 if p in ['C', 'S'] else 0.005).round(4)
    processed["merchant_risk_score"] = processed["merchant_chargeback_rate"].apply(lambda r: round(r * 400.0 + random.uniform(5, 15), 1))

    # ─── AGENT 4: Network Intelligence ───
    # Proxy/VPN flag based on mapping card3/card5
    processed["is_vpn_or_proxy"] = df["card3"].apply(lambda c3: 1 if c3 > 150 else 0)
    processed["network_risk_score"] = processed["is_vpn_or_proxy"].apply(lambda v: round(80.0 + random.uniform(0, 15), 1) if v == 1 else round(random.uniform(5, 25), 1))

    # Calculate overall risk score as base average
    processed["risk_score"] = processed.apply(
        lambda r: round((r["user_risk_score"] + r["device_risk_score"] + r["merchant_risk_score"] + r["network_risk_score"])/4.0, 1),
        axis=1
    )

    # Save to CSV
    output_file = "transactions.csv"
    processed.to_csv(output_file, index=False)
    print(f"\n[INGEST] Successfully merged and mapped {len(processed)} rows into '{output_file}'!")
    print(f"[INGEST] Fraud Cases Mapped: {len(processed[processed['is_fraud'] == 1])}")
    print("[INGEST] Ready for Q-Guard AI Quantum optimization processing.")

    # Save to MongoDB dynamically
    try:
        from rit_mongodb_client import RITMongoDBClient
        db = RITMongoDBClient()
        if db.connected:
            db.save_transactions(processed.to_dict('records'))
    except Exception as e:
        print(f"[MONGO WARNING] Could not push Kaggle dataset to MongoDB: {e}")


if __name__ == "__main__":
    # Ingest 3000 transactions from raw Kaggle tables
    ingest_ieee_cis(limit_rows=3000)
