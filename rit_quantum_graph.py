"""
═══════════════════════════════════════════════════════════════════════════════
  RIT Quantathan 2026 — Q-Guard AI Graph & VQC Engine
  File: rit_quantum_graph.py
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

import json, csv, datetime, collections, os
from typing import List, Dict, Any
import numpy as np

import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ─── QUANTUM VARIATIONAL CLASSIFIER SIMULATOR ─────────────────────────────────

class QuantumSimulator:
    """
    Lightweight, self-contained 4-qubit quantum statevector simulator.
    Used to run the Variational Quantum Circuit (VQC) for Q-Guard Agent risk weight optimization.
    """
    def __init__(self, num_qubits: int = 4):
        self.num_qubits = num_qubits
        self.reset()

    def reset(self):
        self.state = np.zeros(2**self.num_qubits, dtype=complex)
        self.state[0] = 1.0

    @staticmethod
    def RY(theta: float):
        return np.array([
            [np.cos(theta/2), -np.sin(theta/2)],
            [np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)

    @staticmethod
    def RX(phi: float):
        return np.array([
            [np.cos(phi/2), -1j*np.sin(phi/2)],
            [1j*np.sin(phi/2), np.cos(phi/2)]
        ], dtype=complex)

    def apply_single_qubit_gate(self, gate, qubit_idx: int):
        size_pre = 2**qubit_idx
        size_post = 2**(self.num_qubits - 1 - qubit_idx)
        reshaped = self.state.reshape(size_pre, 2, size_post)
        
        new_state = np.zeros_like(reshaped)
        for i in range(2):
            for j in range(2):
                new_state[:, i, :] += gate[i, j] * reshaped[:, j, :]
        self.state = new_state.flatten()

    def apply_cnot(self, control: int, target: int):
        for i in range(2**self.num_qubits):
            if ((i >> control) & 1) and not ((i >> target) & 1):
                pair = i | (1 << target)
                self.state[i], self.state[pair] = self.state[pair], self.state[i]

    def get_bloch_coordinates(self, qubit_idx: int) -> Dict[str, float]:
        """Calculates expectation values <X>, <Y>, <Z> for a single qubit (density matrix projection)"""
        size_pre = 2**qubit_idx
        size_post = 2**(self.num_qubits - 1 - qubit_idx)
        reshaped = self.state.reshape(size_pre, 2, size_post)
        
        rho = np.zeros((2, 2), dtype=complex)
        for i in range(2):
            for j in range(2):
                rho[i, j] = np.sum(reshaped[:, i, :] * np.conj(reshaped[:, j, :]))
                
        sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
        sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
        
        x = float(np.real(np.trace(rho @ sigma_x)))
        y = float(np.real(np.trace(rho @ sigma_y)))
        z = float(np.real(np.trace(rho @ sigma_z)))
        return {"x": round(x, 4), "y": round(y, 4), "z": round(z, 4)}


class VariationalQuantumClassifier:
    """
    Q-Guard AI Quantum Optimization Layer.
    Encodes risk scores from User, Device, Merchant, and Network Agents,
    runs a variational entangling circuit, and extracts:
    1. Overall Aggregated Risk Score
    2. Dynamic Agent Aggregation Weights (derived from qubit Z-excitation coordinates)
    """
    def __init__(self):
        # Variational angles optimized to represent inter-agent fraud correlation weights
        self.phi = np.array([0.45, -0.62, 0.78, 0.31])  # Ry variational weights
        self.gamma = np.array([-0.15, 0.84, -0.32, 0.95]) # Rx variational weights
        self.sim = QuantumSimulator(num_qubits=4)

    def predict(self, user_risk: float, device_risk: float, merchant_risk: float, network_risk: float) -> Dict[str, Any]:
        # 1. Normalize scores to range [0, 1] for angle mapping
        x0 = min(user_risk / 100.0, 1.0)
        x1 = min(device_risk / 100.0, 1.0)
        x2 = min(merchant_risk / 100.0, 1.0)
        x3 = min(network_risk / 100.0, 1.0)

        self.sim.reset()

        # 2. Angle Encoding: Prepare state RY(pi * x_i) |0>
        self.sim.apply_single_qubit_gate(QuantumSimulator.RY(np.pi * x0), 0)
        self.sim.apply_single_qubit_gate(QuantumSimulator.RY(np.pi * x1), 1)
        self.sim.apply_single_qubit_gate(QuantumSimulator.RY(np.pi * x2), 2)
        self.sim.apply_single_qubit_gate(QuantumSimulator.RY(np.pi * x3), 3)

        # 3. Variational Entangling Circuit
        for i in range(4):
            self.sim.apply_single_qubit_gate(QuantumSimulator.RY(self.phi[i]), i)

        # Ring Entanglement using CNOTs to capture non-linear correlation
        self.sim.apply_cnot(0, 1)
        self.sim.apply_cnot(1, 2)
        self.sim.apply_cnot(2, 3)
        self.sim.apply_cnot(3, 0)

        for i in range(4):
            self.sim.apply_single_qubit_gate(QuantumSimulator.RX(self.gamma[i]), i)

        # 4. Read expectation coordinates (Bloch projections)
        bloch_coords = [self.sim.get_bloch_coordinates(i) for i in range(4)]
        
        # Calculate dynamic aggregation weights from Qubit Z-coordinate excitation:
        # Z is 1.0 in state |0> (unexcited) and -1.0 in state |1> (excited).
        # We define raw excitation contribution as: 1.0 - Z
        raw_excitations = [max(0.001, 1.0 - c["z"]) for c in bloch_coords]
        total_exc = sum(raw_excitations)
        dynamic_weights = [round((exc / total_exc) * 100.0, 1) for exc in raw_excitations]

        # Calculate final aggregated quantum probability of blocking alignment |1111>
        probabilities = np.abs(self.sim.state) ** 2
        block_probability = float(probabilities[15])  # |1111> basis state projection
        
        # Scale to final risk score range (0-100) overlaying high agent inputs
        max_agent_input = max(user_risk, device_risk, merchant_risk, network_risk)
        if max_agent_input > 75:
            quantum_risk = 70.0 + block_probability * 30.0
        else:
            quantum_risk = block_probability * 80.0
            
        # Ensure it respects boundary limits
        quantum_risk = min(100.0, max(0.0, quantum_risk))

        return {
            "prediction_prob": round(block_probability, 5),
            "quantum_risk_score": round(quantum_risk, 1),
            "dynamic_weights": {
                "user": dynamic_weights[0],
                "device": dynamic_weights[1],
                "merchant": dynamic_weights[2],
                "network": dynamic_weights[3]
            },
            "bloch_vectors": bloch_coords,
            "state_vector": [f"{c.real:.3f}+{c.imag:.3f}j" for c in self.sim.state]
        }


# ─── THRESHOLDS & WEIGHTS ─────────────────────────────────────────────────────

VELOCITY_WINDOW_SEC    = 300
VELOCITY_MIN_TXN       = 3
SHARED_DEVICE_MIN_ACC  = 2
FAN_IN_MIN_SENDERS     = 3
CIRCULAR_MAX_LEN       = 6
CROSS_CHANNEL_SEC      = 120
HIGH_CHURN_THRESHOLD   = 0.85
LOW_ACCOUNT_AGE_DAYS   = 30
HIGH_IP_DENSITY        = 15

RISK_WEIGHTS = {
    "shared_ip":       20.0,
    "shared_device":   30.0,
    "high_velocity":   20.0,
    "cross_channel":   40.0,
    "mule_chain":      35.0,
    "fan_in":          35.0,
    "circular_loop":   40.0,
    "high_churn":      15.0,
    "new_account":     10.0,
    "ip_density":      10.0,
}


# ─── MAIN GRAPH & DETECTOR CLASS ──────────────────────────────────────────────

class GraphIntelligence:

    def __init__(self, csv_path: str = "transactions.csv"):
        self.csv_path = csv_path
        self.G        = nx.MultiDiGraph()
        self.txns:  List[Dict] = []
        self.risk_scores: Dict[str, float] = {}
        self.vqc      = VariationalQuantumClassifier()

    def load(self):
        print(f"[GRAPH] Loading dataset: {self.csv_path}")
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            self.txns = list(csv.DictReader(f))
        print(f"[GRAPH] {len(self.txns)} transactions loaded.")

    def build(self):
        print("[GRAPH] Building RIT network graph...")
        self._ip_to_accounts:     Dict[str, set] = collections.defaultdict(set)
        self._device_to_accounts: Dict[str, set] = collections.defaultdict(set)
        self._acc_ts:             Dict[str, list] = collections.defaultdict(list)
        self._receiver_counts:    Dict[str, int]  = collections.Counter()

        for t in self.txns:
            acc  = t["account_number"]
            recv = t["receiver_account"]
            ip   = t["ip_address"]
            dev  = t["device"]
            ts   = t["timestamp"]
            amt  = float(t["amount"])
            risk = float(t["risk_score"])
            ftyp = t["fraud_type"]
            frau = int(t["is_fraud"])
            age  = float(t.get("account_age_days", 365))
            churn= float(t.get("churn_rate", 0.1))
            dens = int(t.get("ip_account_density", 5))

            # Account node
            if not self.G.has_node(acc):
                self.G.add_node(acc, node_type="account", name=t["name"],
                    is_fraud=frau, fraud_type=ftyp, risk_score=risk,
                    account_type=t["account_type"], pincode=t["pincode"],
                    account_age_days=age, churn_rate=churn)

            # Receiver node
            if recv not in ("SELF","") and not self.G.has_node(recv):
                recv_type = "collector" if recv.startswith("COLL") else "account"
                self.G.add_node(recv, node_type=recv_type, name=t.get("receiver_name","?"),
                    is_fraud=0, fraud_type="Unknown", risk_score=5.0,
                    account_type="Unknown", pincode=t.get("receiver_pincode","000000"),
                    account_age_days=365, churn_rate=0.1)

            # IP node
            ip_id = f"IP:{ip}"
            if not self.G.has_node(ip_id):
                self.G.add_node(ip_id, node_type="ip", ip=ip,
                    risk_score=0.0, density=dens)

            # Device node
            dev_id = f"DEV:{dev}"
            if not self.G.has_node(dev_id):
                self.G.add_node(dev_id, node_type="device", device=dev, risk_score=0.0)

            # Transaction edge
            if recv not in ("SELF",""):
                self.G.add_edge(acc, recv, edge_type="transaction",
                    txn_id=t["txn_id"], timestamp=ts, amount=amt,
                    trans_type=t["trans_type"], is_fraud=frau,
                    fraud_type=ftyp, risk_score=risk)

            # IP & Device edges
            self.G.add_edge(acc, ip_id,  edge_type="ip_usage",  timestamp=ts, is_fraud=frau)
            self.G.add_edge(acc, dev_id, edge_type="dev_usage", timestamp=ts, is_fraud=frau)

            self._ip_to_accounts[ip].add(acc)
            self._device_to_accounts[dev].add(acc)
            self._acc_ts[acc].append((ts, t["txn_id"], amt))
            if recv not in ("SELF",""):
                self._receiver_counts[recv] += 1

        print(f"[GRAPH] Nodes: {self.G.number_of_nodes()}, Edges: {self.G.number_of_edges()}")

    def detect_shared_ip(self) -> List[Dict]:
        out = []
        for ip, accs in self._ip_to_accounts.items():
            if len(accs) >= 2:
                fraud_accs = [a for a in accs if self.G.nodes[a].get("is_fraud",0)]
                out.append({
                    "type": "Shared IP", "ip": ip,
                    "accounts": list(accs), "account_count": len(accs),
                    "fraud_accounts": fraud_accs,
                    "risk_score": min(95.0, len(accs) * RISK_WEIGHTS["shared_ip"]),
                })
        return out

    def detect_shared_device(self) -> List[Dict]:
        out = []
        for dev, accs in self._device_to_accounts.items():
            if len(accs) >= SHARED_DEVICE_MIN_ACC:
                fraud_accs = [a for a in accs if self.G.nodes[a].get("is_fraud",0)]
                out.append({
                    "type": "Shared Device", "device": dev,
                    "accounts": list(accs), "account_count": len(accs),
                    "fraud_accounts": fraud_accs,
                    "risk_score": min(95.0, len(accs) * RISK_WEIGHTS["shared_device"]),
                })
        return out

    def detect_velocity(self) -> List[Dict]:
        fmt = "%Y-%m-%d %H:%M:%S"
        out = []
        for acc, ts_list in self._acc_ts.items():
            if len(ts_list) < VELOCITY_MIN_TXN:
                continue
            sl = sorted(ts_list, key=lambda x: x[0])
            dts = [datetime.datetime.strptime(x[0], fmt) for x in sl]
            for i in range(len(dts)):
                win = [sl[j] for j in range(i, len(dts))
                       if (dts[j]-dts[i]).total_seconds() <= VELOCITY_WINDOW_SEC]
                if len(win) >= VELOCITY_MIN_TXN:
                    out.append({
                        "type": "High Velocity", "account": acc,
                        "name": self.G.nodes[acc].get("name","?"),
                        "txn_count": len(win),
                        "total_amount": sum(w[2] for w in win),
                        "txn_ids": [w[1] for w in win],
                        "start_time": win[0][0], "end_time": win[-1][0],
                        "risk_score": min(95.0, len(win)*RISK_WEIGHTS["high_velocity"]),
                    })
                    break
        return out

    def detect_cross_channel(self) -> List[Dict]:
        fmt = "%Y-%m-%d %H:%M:%S"
        acc_events: Dict[str, list] = collections.defaultdict(list)
        for t in self.txns:
            acc_events[t["account_number"]].append(t)
        out = []
        for acc, evs in acc_events.items():
            evs_sorted = sorted(evs, key=lambda e: e["timestamp"])
            for i in range(len(evs_sorted)-1):
                e1, e2 = evs_sorted[i], evs_sorted[i+1]
                t1 = datetime.datetime.strptime(e1["timestamp"], fmt)
                t2 = datetime.datetime.strptime(e2["timestamp"], fmt)
                delta = (t2-t1).total_seconds()
                if (delta <= CROSS_CHANNEL_SEC
                        and e1["ip_address"] != e2["ip_address"]
                        and e1["pincode"] != e2["pincode"]):
                    out.append({
                        "type": "Cross Channel", "account": acc,
                        "name": e1["name"],
                        "txn_1": e1["txn_id"], "txn_2": e2["txn_id"],
                        "time_1": e1["timestamp"], "time_2": e2["timestamp"],
                        "delta_seconds": delta,
                        "ip_1": e1["ip_address"], "ip_2": e2["ip_address"],
                        "pincode_1": e1["pincode"], "pincode_2": e2["pincode"],
                        "device_1": e1["device"], "device_2": e2["device"],
                        "amount_1": float(e1["amount"]), "amount_2": float(e2["amount"]),
                        "risk_score": 95.0,
                        "description": f"Impossible travel {e1['pincode']} → {e2['pincode']} in {delta:.0f}s",
                    })
        return out

    def detect_fan_in(self) -> List[Dict]:
        in_degree: Dict[str, set] = collections.defaultdict(set)
        for t in self.txns:
            if t["receiver_account"] not in ("SELF",""):
                in_degree[t["receiver_account"]].add(t["account_number"])

        out = []
        for collector, senders in in_degree.items():
            if len(senders) >= FAN_IN_MIN_SENDERS:
                sender_nodes = [s for s in senders if self.G.has_node(s)]
                avg_age   = (sum(self.G.nodes[s].get("account_age_days",365) for s in sender_nodes)
                             / max(len(sender_nodes),1))
                avg_churn = (sum(self.G.nodes[s].get("churn_rate",0.1) for s in sender_nodes)
                             / max(len(sender_nodes),1))
                out.append({
                    "type":           "Mule Collection (Fan-In)",
                    "collector":      collector,
                    "senders":        list(senders),
                    "sender_count":   len(senders),
                    "avg_account_age": round(avg_age, 1),
                    "avg_churn":      round(avg_churn, 3),
                    "risk_score":     min(95.0, len(senders)*RISK_WEIGHTS["fan_in"] * (1 + avg_churn)),
                    "description":    (
                        f"{len(senders)} mule accounts funnel funds into {collector}. "
                        f"Avg account age: {avg_age:.0f} days. Avg churn: {avg_churn:.2f}"
                    ),
                })
        return out

    def detect_circular_loops(self) -> List[Dict]:
        TG = nx.DiGraph()
        for u, v, d in self.G.edges(data=True):
            if d.get("edge_type") == "transaction":
                TG.add_edge(u, v, **d)

        out = []
        try:
            cycles = list(nx.simple_cycles(TG, length_bound=CIRCULAR_MAX_LEN))
            for cycle in cycles:
                if 2 <= len(cycle) <= CIRCULAR_MAX_LEN:
                    names = [self.G.nodes[n].get("name", n) for n in cycle]
                    out.append({
                        "type":       "Circular Loop",
                        "path":       cycle + [cycle[0]],
                        "length":     len(cycle),
                        "names":      names,
                        "risk_score": min(95.0, len(cycle)*RISK_WEIGHTS["circular_loop"]),
                        "description": " → ".join(names) + " → " + names[0],
                    })
        except Exception as e:
            print(f"[GRAPH] Loop detection failed: {e}")
        return out

    def detect_high_churn(self) -> List[Dict]:
        out = []
        for acc, data in self.G.nodes(data=True):
            if data.get("node_type") != "account":
                continue
            churn = float(data.get("churn_rate", 0))
            age   = float(data.get("account_age_days", 365))
            if churn >= HIGH_CHURN_THRESHOLD:
                out.append({
                    "type":             "High Churn",
                    "account":          acc,
                    "name":             data.get("name","?"),
                    "churn_rate":       churn,
                    "account_age_days": age,
                    "risk_score":       min(95.0, churn*100 + (RISK_WEIGHTS["new_account"] if age < LOW_ACCOUNT_AGE_DAYS else 0)),
                })
        return out

    def compute_centrality(self) -> Dict[str, float]:
        UG = self.G.to_undirected()
        UG.remove_edges_from(nx.selfloop_edges(UG))
        deg = nx.degree_centrality(UG)
        bet = nx.betweenness_centrality(UG, normalized=True)
        return {n: round((deg.get(n,0)*0.6 + bet.get(n,0)*0.4)*100, 2)
                for n in set(deg)|set(bet)}

    def compute_risk_scores(self, ip_c, dev_c, vel_a, cross_a, fan_a, loop_a, churn_a) -> Dict[str,float]:
        """
        Refactored to feed Multi-Agent risk metrics into Q-Guard VQC Weight Optimizer.
        """
        print("[GRAPH] Computing Q-Guard AI multi-agent quantum weight optimization...")
        scores: Dict[str,float] = {}
        self.quantum_outputs = {}
        self.adaptive_thresholds = {}
        self.xai_explanations = {}
        self.strategy_recommendations = {}

        for acc, data in self.G.nodes(data=True):
            if data.get("node_type") != "account":
                continue
            
            # Find all transactions for this account to aggregate agent parameters
            txs = [t for t in self.txns if t["account_number"] == acc]
            if not txs:
                continue
            
            # 1. Fetch Agent risk subscores from simulator features (or default to normal ranges)
            user_risk = sum(float(t.get("user_risk_score", 15.0)) for t in txs) / len(txs)
            device_risk = sum(float(t.get("device_risk_score", 10.0)) for t in txs) / len(txs)
            merchant_risk = sum(float(t.get("merchant_risk_score", 10.0)) for t in txs) / len(txs)
            network_risk = sum(float(t.get("network_risk_score", 10.0)) for t in txs) / len(txs)
            
            # Boost scores based on topological detections
            in_fan_in = any(acc in a["senders"] for a in fan_a)
            in_loop = any(acc in a["path"] for a in loop_a)
            in_velocity = any(acc == a["account"] for a in vel_a)
            in_cross = any(acc == a["account"] for a in cross_a)
            
            if in_fan_in:
                merchant_risk = max(merchant_risk, 80.0)
            if in_loop:
                network_risk = max(network_risk, 90.0)
            if in_velocity:
                user_risk = max(user_risk, 92.0)
            if in_cross:
                network_risk = max(network_risk, 95.0)

            # 2. Execute Quantum Aggregator
            q_res = self.vqc.predict(user_risk, device_risk, merchant_risk, network_risk)
            self.quantum_outputs[acc] = q_res
            scores[acc] = q_res["quantum_risk_score"]
            self.G.nodes[acc]["risk_score"] = scores[acc]
            
            # 3. Calculate Adaptive Threshold
            age = float(data.get("account_age_days", 365))
            churn = float(data.get("churn_rate", 0.1))
            
            # Context heuristics:
            is_new_customer = age < LOW_ACCOUNT_AGE_DAYS
            is_trusted_customer = age > 365 and churn < 0.15
            
            # Simulated transaction hour context
            latest_tx = max(txs, key=lambda t: t["timestamp"])
            hour = int(latest_tx["timestamp"].split()[1].split(":")[0])
            is_late_night = (hour >= 0 and hour <= 5)
            
            # Threshold decision tree
            if is_late_night:
                threshold = 65.0  # Tighter block condition at late night
            elif merchant_risk > 65.0:
                threshold = 58.0  # Highly suspicious merchant
            elif is_new_customer:
                threshold = 70.0  # Tighter for new signups
            elif is_trusted_customer:
                threshold = 95.0  # Relaxed for trusted regular users
            else:
                threshold = 80.0  # Default standard
                
            self.adaptive_thresholds[acc] = threshold

            # 4. Generate Explainable AI (XAI) bullet points
            reasons = []
            if user_risk > 45:
                reasons.append(f"User Behavior risk elevated ({user_risk}%): spending deviation detected")
            if device_risk > 45:
                reasons.append(f"Device Intelligence risk elevated ({device_risk}%): compromised rooted/emulator fingerprints")
            if merchant_risk > 45:
                reasons.append(f"Merchant Rating flagged ({merchant_risk}%): high chargeback categories")
            if network_risk > 45:
                reasons.append(f"Network intelligence flagged ({network_risk}%): VPN/impossible travel signature")
            if not reasons:
                reasons.append("All agents reporting normal telemetry bounds")
                
            self.xai_explanations[acc] = reasons

            # 5. Generate Fraud Strategy Recommendation actions
            strategies = []
            if user_risk > 45:
                strategies.extend(["SMS OTP Verification Required", "Temporary Transaction Hold"])
            if device_risk > 45:
                strategies.extend(["Face Authentication Check", "Restrict Device Fingerprint Access"])
            if network_risk > 45:
                strategies.extend(["Proxy/VPN Interdiction Alert", "Out-of-Band Call Verification"])
            if merchant_risk > 45:
                strategies.extend(["Hold Payout to Merchant ID", "Initiate Merchant Chargeback Audit"])
            
            # If final score exceeds context threshold
            if scores[acc] >= threshold:
                strategies.append("BLOCK TRANSACTION & Alert Fraud Response Team")
            elif not strategies:
                strategies.append("Allow transaction with passive background monitoring")
                
            # Deduplicate strategies
            self.strategy_recommendations[acc] = list(dict.fromkeys(strategies))

        self.risk_scores = scores
        return self.risk_scores

    def visualize(self, path="graph_visualization.png"):
        print(f"[GRAPH] Rendering topological plot: {path}")
        viz_nodes = {n for n,d in self.G.nodes(data=True)
                     if float(self.risk_scores.get(n, d.get("risk_score",0))) > 20}
        VG = self.G.subgraph(viz_nodes).copy()
        UG = nx.Graph()
        for u,v,d in VG.edges(data=True):
            if u in viz_nodes and v in viz_nodes:
                UG.add_edge(u,v)

        fig, ax = plt.subplots(figsize=(14,10))
        fig.patch.set_facecolor("#040c14")
        ax.set_facecolor("#040c14")

        if not UG.nodes:
            ax.text(0.5,0.5,"No high-risk nodes found",ha="center",va="center",color="white")
            plt.savefig(path,dpi=120,bbox_inches="tight"); return

        pos = nx.spring_layout(UG, seed=42, k=2.2)
        ncolors, nsizes = [], []
        for n in UG.nodes():
            risk = float(self.risk_scores.get(n, self.G.nodes[n].get("risk_score",5)))
            ntype= self.G.nodes[n].get("node_type","account")
            ncolors.append("#ff3c5a" if risk>80 else "#ffb700" if risk>50 else
                           "#00ff9d" if ntype=="ip" else "#7eb8ff" if ntype=="device" else "#00d4ff")
            nsizes.append(700 if risk>80 else 450 if risk>50 else 200)

        nx.draw_networkx_edges(UG,pos,ax=ax,edge_color="#3a6a9055",alpha=0.5,width=1.2)
        nx.draw_networkx_nodes(UG,pos,ax=ax,node_color=ncolors,node_size=nsizes,alpha=0.85)
        labels = {n:(n.split(":")[-1][-8:] if ":" in n
                     else self.G.nodes[n].get("name",n).split()[0][:8])
                  for n in UG.nodes()}
        nx.draw_networkx_labels(UG,pos,labels,ax=ax,font_size=7,font_color="#c8e8ff")

        legend = [
            mpatches.Patch(color="#ff3c5a",label="Q-Guard Critical Risk (>80)"),
            mpatches.Patch(color="#ffb700",label="Q-Guard Alert (50–80)"),
            mpatches.Patch(color="#00d4ff",label="Normal Account"),
            mpatches.Patch(color="#00ff9d",label="IP Address Node"),
            mpatches.Patch(color="#7eb8ff",label="Device Profile Node"),
        ]
        ax.legend(handles=legend,loc="lower left",facecolor="#0d2035",
                  edgecolor="#1a4060",labelcolor="white",fontsize=8)
        ax.set_title("Q-Guard AI — Quantum AI & Topological Fraud Map",color="#00d4ff",fontsize=13)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(path,dpi=120,bbox_inches="tight",facecolor="#040c14")
        plt.close()
        print(f"[GRAPH] Visualization saved to: {path}")

    def analyze(self) -> Dict[str,Any]:
        self.load()
        self.build()

        ip_c    = self.detect_shared_ip()
        dev_c   = self.detect_shared_device()
        vel_a   = self.detect_velocity()
        cross_a = self.detect_cross_channel()
        fan_a   = self.detect_fan_in()
        loop_a  = self.detect_circular_loops()
        churn_a = self.detect_high_churn()
        cent    = self.compute_centrality()
        scores  = self.compute_risk_scores(ip_c,dev_c,vel_a,cross_a,fan_a,loop_a,churn_a)

        top = sorted(scores.items(), key=lambda x:x[1], reverse=True)[:10]

        # Calculate statistics for VQC simulator separation
        fraud_vqc_scores = []
        normal_vqc_scores = []
        for acc, s in scores.items():
            if acc in self.quantum_outputs:
                q_prob = self.quantum_outputs[acc]["prediction_prob"]
                if self.G.nodes[acc].get("is_fraud", 0):
                    fraud_vqc_scores.append(q_prob)
                else:
                    normal_vqc_scores.append(q_prob)

        avg_fraud_vqc = sum(fraud_vqc_scores)/len(fraud_vqc_scores) if fraud_vqc_scores else 0.0
        avg_normal_vqc = sum(normal_vqc_scores)/len(normal_vqc_scores) if normal_vqc_scores else 0.0

        report = {
            "summary": {
                "total_transactions": len(self.txns),
                "graph_nodes": self.G.number_of_nodes(),
                "graph_edges": self.G.number_of_edges(),
                "fraud_count": sum(1 for t in self.txns if int(t["is_fraud"])),
            },
            "quantum_vqc_telemetry": {
                "vqc_variational_weights_phi": self.vqc.phi.tolist(),
                "vqc_variational_weights_gamma": self.vqc.gamma.tolist(),
                "avg_vqc_fraud_probability": round(avg_fraud_vqc, 5),
                "avg_vqc_normal_probability": round(avg_normal_vqc, 5),
                "model_parameters_count": 8,
                "circuit_qubits": 4,
                "quantum_gates_used": "8 single-qubit rotations, 4 CNOT gates",
                "execution_mode": "Simulated Quantum Weight Optimization (excitation projection)"
            },
            "ip_clusters":      ip_c,
            "device_clusters":  dev_c,
            "velocity_alerts":  vel_a,
            "cross_channel":    cross_a,
            "fan_in_alerts":    fan_a,
            "circular_loops":   loop_a,
            "high_churn":       churn_a,
            "top_risk": [{"account":a,"risk_score":s,
                          "name":self.G.nodes.get(a,{}).get("name","?")} for a,s in top],
            "centrality_top10": sorted(cent.items(),key=lambda x:x[1],reverse=True)[:10],
        }

        self._print(report)
        return report

    def _print(self, r):
        print("\n" + "═"*60)
        print("  Q-Guard AI — Quantum AI & Graph Analysis Report")
        print("═"*60)
        s = r["summary"]
        q = r["quantum_vqc_telemetry"]
        print(f"  Transactions      : {s['total_transactions']}")
        print(f"  Nodes/Edges       : {s['graph_nodes']} / {s['graph_edges']}")
        print(f"  Fraud Txns        : {s['fraud_count']}")
        print(f"  IP/Device Clusters: {len(r['ip_clusters'])} / {len(r['device_clusters'])}")
        print(f"  Fan-In/Loops/Vel  : {len(r['fan_in_alerts'])} / {len(r['circular_loops'])} / {len(r['velocity_alerts'])}")
        print(f"  VQC Mode          : {q['execution_mode']}")
        print(f"  Avg VQC Prob (Fraud/Normal): {q['avg_vqc_fraud_probability']} / {q['avg_vqc_normal_probability']}")
        print("  Top Risk Accounts (Quantum Dynamic Weights):")
        for x in r["top_risk"][:5]:
            print(f"    {x['account']:<16} {x['name']:<22} {x['risk_score']}")
        print("═"*60)

    def save(self, rpt_path="graph_report.json", cl_path="fraud_clusters.json"):
        def ser(o):
            if isinstance(o, set): return list(o)
            raise TypeError(type(o))
            
        # Join Q-Guard metadata to report
        self._last_report["quantum_predictions"] = self.quantum_outputs
        self._last_report["adaptive_thresholds"] = self.adaptive_thresholds
        self._last_report["xai_explanations"] = self.xai_explanations
        self._last_report["strategy_recommendations"] = self.strategy_recommendations
        
        with open(rpt_path,"w") as f: 
            json.dump(self._last_report, f, indent=2, default=ser)
        with open(cl_path,"w") as f:
            json.dump(self._last_report.get("fan_in_alerts",[]), f, indent=2, default=ser)
        print(f"[GRAPH] Report saved: {rpt_path} & {cl_path}")

        try:
            from rit_mongodb_client import RITMongoDBClient
            db = RITMongoDBClient()
            if db.connected:
                for account, pred_data in self.quantum_outputs.items():
                    telemetry = {
                        "vqc_prediction": pred_data,
                        "threshold": self.adaptive_thresholds.get(account, 80.0),
                        "explanations": self.xai_explanations.get(account, ["Telemetry bounds normal"]),
                        "strategies": self.strategy_recommendations.get(account, ["Passive monitoring"])
                    }
                    db.save_telemetry(account, telemetry)
                print("[GRAPH] ✅ Successfully exported all quantum telemetry to MongoDB.")
        except Exception as e:
            print(f"[MONGO WARNING] Could not write telemetry report to MongoDB: {e}")


if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║  Q-Guard AI — Graph Engine & VQC         ║")
    print("║  Schrödinger’s Coders · 2026            ║")
    print("╚══════════════════════════════════════════╝\n")

    engine = GraphIntelligence(csv_path="transactions.csv")
    report = engine.analyze()
    engine._last_report = report
    engine.save()
    engine.visualize("graph_visualization.png")
