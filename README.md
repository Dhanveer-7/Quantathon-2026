# Q-Guard AI — Multi-Agent Quantum Fraud Intelligence

[![Live Demo](https://img.shields.io/badge/Demo-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://quantathon-2026.vercel.app)
[![Tech Stack](https://img.shields.io/badge/Stack-Python%20%7C%20FastAPI%20%7C%20MongoDB-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/Dhanveer-7/Quantathon-2026)

Developed by **Team Schrödinger’s Coders** for **Quantathon 2026** (RIT Chennai).
* **Team Members**: Dhinith Pragalyan, Dhanveer M, Venkatesan S, Elamaran B

---

## ⚛️ Overview

**Q-Guard AI** is a state-of-the-art **Multi-Agent Quantum Machine Learning (QML)** framework designed for banks to identify complex, coordinated financial fraud in real-time. By mapping multi-dimensional transaction telemetry (User, Device, Merchant, and Network) to Hilbert space coordinates on a **4-Qubit Variational Quantum Circuit (VQC)**, Q-Guard AI detects non-linear fraud loops, velocity structuring, and mule networks with 90% fewer parameters than classical neural networks.

### Key Innovations:
1. **Multi-Agent Telemetry Ingestion**: Decentralized local agents monitor separate threat sectors.
2. **Quantum Weight Optimization (VQC)**: Computes risk weights dynamically using Bloch Sphere state vector projections.
3. **Adaptive Context Thresholds**: Automatically adjusts blocking limits (from 58% to 95%) based on factors like time of day, merchant category, and device trust.
4. **Self-Explainable AI (XAI)**: Translates quantum state measurements into human-readable compliance logs for regulatory auditing.
5. **Strategic Mitigation Checklists**: Progressive security verification (OTP $\rightarrow$ Face Auth $\rightarrow$ Hold) rather than crude binary blocks.

---

## 🏗️ System Architecture

```mermaid
graph TD
  A[Raw Telemetry Ingestion] --> B[Decentralized Agent Ingestion]
  
  subgraph Ingestion Layer
    B --> B1[User Agent]
    B --> B2[Device Agent]
    B --> B3[Merchant Agent]
    B --> B4[Network Agent]
  end

  B1 & B2 & B3 & B4 --> C[Angle Encoding: Theta = R * Pi]
  C --> D[4-Qubit Variational Quantum Circuit]
  
  subgraph Quantum Optimization Layer (VQC)
    D --> D1[Ry Rotation Gates]
    D1 --> D2[Ring CNOT Entangling Ansatz]
    D2 --> D3[Z-Axis Expectation Measurement]
  end
  
  D3 --> E[Bloch Vector Weighting: W = (1-Z)/2]
  E --> F[Adaptive Context Threshold Engine]
  F --> G[Self-Explainable AI (XAI) Generator]
  F --> H[Strategic Mitigation Checklist]
  
  G & H --> I[(MongoDB Collections)]
  I --> J[FastAPI API Endpoints]
  I --> K[Flask Dashboard Server]
```

---

## 🛠️ Technology Stack

* **Core Backend**: Python 3.10+, FastAPI (High-performance API layer), Flask (Interactive Dashboard).
* **Quantum Simulator & Analytics**: Pennylane / PyTorch (Quantum Circuit Simulation), NetworkX (Topological Graph Modeling), Pandas & NumPy.
* **Database**: MongoDB Community/Atlas (Distributed, indexed transaction and telemetry collections).
* **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), JavaScript (Canvas Bloch Sphere visualizer).
* **Hosting**: Vercel (Static Dashboard), Localhost Tunneling (Live Presentation).

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8+ installed.
* MongoDB installed and running locally on port `27017` (or configured via connection string).

### 1. Clone the Repository
```bash
git clone https://github.com/Dhanveer-7/Quantathon-2026.git
cd Quantathon-2026
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Data Ingestion & Quantum Engine
We validate the system using a processed slice of **3,000 transaction records** from the **Kaggle IEEE-CIS Fraud Detection dataset**:
```bash
# Ingest raw Kaggle tables and export transaction records to MongoDB
python ingest_kaggle_data.py

# Run Quantum Graph Engine to calculate weights, adaptive limits, XAI, and export telemetry
python rit_quantum_graph.py
```

### 4. Start the Application Servers
```bash
# Launch the FastAPI endpoint layer (running on http://127.0.0.1:8000)
python rit_api_layer.py

# Launch the Flask visualization dashboard (running on http://127.0.0.1:5000)
python rit_dashboard.py
```

---

## 📊 Presentation & Media Artifacts

* **Pitch Deck**: [RIT - Quantathan 2026 - PPT.pptx](RIT%20-%20Quantathan%202026%20-%20PPT.pptx) (A complete, 13-slide PowerPoint detailing the technical framework and business value).
* **Product Demonstration Video**: [Project video record .mp4](Project%20video%20record%20.mp4) (Screen recording explaining the interactive dashboard UI).
* **Static Homepage (Vercel-ready)**: [index.html](index.html) (Pre-rendered static version of the dashboard for quick deployments).

---

## 🔒 License
This project was developed exclusively for **Quantathon 2026** by Schrödinger’s Coders. All rights reserved.
