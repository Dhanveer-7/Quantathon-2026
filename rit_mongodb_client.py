"""
═══════════════════════════════════════════════════════════════════════════════
  RIT Quantathan 2026 — MongoDB Data Access Layer
  File: rit_mongodb_client.py
  Team: Schrödinger’s Coders
═══════════════════════════════════════════════════════════════════════════════
"""

import os
from typing import List, Dict, Any, Optional

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "qguard_db"

class RITMongoDBClient:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.connected = False
        
        if PYMONGO_AVAILABLE:
            try:
                # Set a short connection timeout so it fails fast if MongoDB is offline
                self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
                # Ping database to verify connection
                self.client.admin.command('ping')
                self.db = self.client[DB_NAME]
                self.connected = True
                print("[MONGO] ✅ Connected to MongoDB successfully.")
            except (ConnectionFailure, Exception) as e:
                print(f"[MONGO] ⚠ Could not connect to MongoDB: {e}. Falling back to CSV data storage.")
        else:
            print("[MONGO] ⚠ 'pymongo' not installed. Falling back to CSV data storage.")

    def save_transactions(self, transactions: List[Dict[str, Any]]):
        """Insert transaction logs into MongoDB."""
        if not self.connected or self.db is None:
            return False
        try:
            coll = self.db["transactions"]
            # Clear existing logs for fresh demo simulation runs
            coll.delete_many({})
            # Convert float/int fields properly
            for t in transactions:
                t_copy = t.copy()
                if "_id" in t_copy:
                    del t_copy["_id"]
                coll.insert_one(t_copy)
            print(f"[MONGO] ✅ Saved {len(transactions)} transactions to database.")
            return True
        except Exception as e:
            print(f"[MONGO ERROR] Failed to save transactions: {e}")
            return False

    def load_transactions(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch transactions from MongoDB."""
        if not self.connected or self.db is None:
            return None
        try:
            coll = self.db["transactions"]
            txns = list(coll.find({}, {"_id": 0}))
            return txns if len(txns) > 0 else None
        except Exception as e:
            print(f"[MONGO ERROR] Failed to load transactions: {e}")
            return None

    def save_telemetry(self, account_number: str, telemetry: Dict[str, Any]):
        """Save VQC aggregation weights, thresholds, and strategy recommenders."""
        if not self.connected or self.db is None:
            return False
        try:
            coll = self.db["telemetry"]
            # Upsert telemetry configuration
            coll.update_one(
                {"account_number": account_number},
                {"$set": {"account_number": account_number, "telemetry": telemetry}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[MONGO ERROR] Failed to save telemetry for {account_number}: {e}")
            return False

    def get_telemetry(self, account_number: str) -> Optional[Dict[str, Any]]:
        """Retrieve telemetry configurations for a specific account."""
        if not self.connected or self.db is None:
            return None
        try:
            coll = self.db["telemetry"]
            res = coll.find_one({"account_number": account_number})
            return res["telemetry"] if res else None
        except Exception as e:
            print(f"[MONGO ERROR] Failed to fetch telemetry: {e}")
            return None


if __name__ == "__main__":
    # Test client initialization
    db_client = RITMongoDBClient()
    if db_client.connected:
        print("MongoDB integration is ready to go!")
    else:
        print("MongoDB client running in fallback mode.")
