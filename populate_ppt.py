"""
═══════════════════════════════════════════════════════════════════════════════
  RIT Quantathan 2026 — PowerPoint Generator (High-Contrast & Perfect Alignment)
  File: populate_ppt.py
  Team: Schrödinger’s Coders
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
# Configure stdout to support UTF-8 characters in Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

PPT_PATH = "RIT - Quantathan 2026 - PPT.pptx"

def main():
    if not os.path.exists(PPT_PATH):
        print(f"[ERROR] PPT file not found at: {PPT_PATH}")
        return
        
    prs = Presentation(PPT_PATH)
    
    # ─── SLIDE 0: TITLE SLIDE ───
    slide_0 = prs.slides[0]
    
    # Replace slide 0 details by modifying existing text boxes to preserve position
    for shape in slide_0.shapes:
        if not shape.has_text_frame:
            continue
        text = shape.text
        if "Presented by" in text:
            # Main Project Title
            shape.text_frame.clear()
            p = shape.text_frame.paragraphs[0]
            p.text = "Q-GUARD AI"
            p.font.name = 'Rajdhani'
            p.font.size = Pt(40)
            p.font.bold = True
            p.font.color.rgb = RGBColor(10, 45, 80) # High-contrast Dark Blue
            
            p2 = shape.text_frame.add_paragraph()
            p2.text = "Multi-Agent Quantum Fraud Intelligence System"
            p2.font.name = 'Exo 2'
            p2.font.size = Pt(18)
            p2.font.color.rgb = RGBColor(70, 80, 95) # Muted Dark Slate
            p2.space_before = Pt(8)
            
        elif "Name of the Candidate" in text:
            shape.text_frame.clear()
            p = shape.text_frame.paragraphs[0]
            p.text = "Schrödinger’s Coders"
            p.font.name = 'Exo 2'
            p.font.size = Pt(20)
            p.font.bold = True
            p.font.color.rgb = RGBColor(12, 120, 85) # High-contrast Dark Green
            
            p2 = shape.text_frame.add_paragraph()
            p2.text = "Members: Dhinith Pragalyan, Dhanveer M, Venkatesan S, Elamaran B"
            p2.font.name = 'Exo 2'
            p2.font.size = Pt(12)
            p2.font.bold = True
            p2.font.color.rgb = RGBColor(80, 80, 80) # Charcoal
            p2.space_before = Pt(6)
            
        elif "Institution / Organization" in text:
            shape.text_frame.clear()
            p = shape.text_frame.paragraphs[0]
            p.text = "RIT Chennai — Quantathan 2026"
            p.font.name = 'Share Tech Mono'
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = RGBColor(100, 100, 100)

    # ─── CLEAR ALL SLIDES EXCEPT TITLE SLIDE 0 ───
    # Clear any previously appended slides to start fresh
    id_list = prs.slides._sldIdLst
    while len(prs.slides) > 1:
        del id_list[1]

    # ─── DATA FOR CORE PRESENTATION SLIDES ───
    content_layout = prs.slide_layouts[1]
    
    slides_data = [
        {
            "title": "1. PROBLEM STATEMENT (QT-2.8)",
            "bullets": [
                "Classical ML models check transactions in isolation, missing temporal laundering loops.",
                "High False Positive rates annoy regular customers, increasing churn and operational friction.",
                "Regulatory compliance (RBI/Central Bank) requires Explainable AI (XAI) parameters.",
                "Coordinated attacks (Mule Rings, shared device emulators) bypass standard linear limits.",
                "Solution: Q-Guard AI combines Multi-Agent intelligence with a Quantum Optimization layer."
            ]
        },
        {
            "title": "2. Q-GUARD ARCHITECTURE: MULTI-AGENT INGESTION",
            "bullets": [
                "User Behavior Agent: Analyzes daily spending limit fractions and transaction volume.",
                "Device Intelligence Agent: Detects OS versions, emulators, and device trust rating.",
                "Merchant Rating Agent: Assesses merchant category hazard and chargeback rates.",
                "Network Intelligence Agent: Monitors VPN usage, proxy IPs, and impossible travel.",
                "Decentralized Ingestion: Captures separate threat layers simultaneously to prevent bypass."
            ]
        },
        {
            "title": "3. QUANTUM WEIGHT OPTIMIZATION (QML LAYER)",
            "bullets": [
                "State Encoding: Maps the 4 Agent risk variables directly to 4 Qubits (Q0 to Q3).",
                "Entangling Circuit: Employs a Ring CNOT entangler to learn non-linear inter-agent correlations.",
                "Dynamic Weighting: Aggregates risk dynamically based on Qubit Z-coordinate excitation.",
                "Bloch Projections: Agent weights are proportional to excitation (Weight = 1.0 - Z).",
                "Benefit: Captures non-linear threat vectors using 90% fewer parameters than classical NN."
            ]
        },
        {
            "title": "4. ADAPTIVE CONTEXT THRESHOLD ENGINE",
            "bullets": [
                "Static Limits: Traditional systems block at a flat 80% limit, causing high friction.",
                "Adaptive Threshold: Q-Guard shifts limits dynamically based on transaction context.",
                "Late Night Hour Window (12 AM - 5 AM): Threshold drops to 65% (restrictive).",
                "High chargeback Merchant Terminal: Threshold drops to 58% (tighter security).",
                "Trusted Regular Customer: Threshold rises to 95% (minimizes customer friction)."
            ]
        },
        {
            "title": "5. SELF-EXPLAINABLE AI & STRATEGY MITIGATION",
            "bullets": [
                "Self-Explainable AI (XAI): Translates VQC state vectors into natural language warning logs.",
                "Auditable Compliance: Outlines exactly why an agent triggered the transaction block.",
                "Fraud Strategy Advisor: Recommends progressive mitigation checklists instead of binary blocks.",
                "Mitigation Checklist: Request Face Authentication, Require SMS OTP, or Hold payout.",
                "Benefit: Matches regulatory audit frameworks while keeping user friction minimal."
            ]
        },
        {
            "title": "6. SCALABILITY & DATABASE PIPELINE INTEGRATION",
            "bullets": [
                "Kaggle Database: Integrated with 3,000 real-world transaction logs (IEEE-CIS).",
                "MongoDB Integration: Stores transactions and quantum telemetry in indexed collections.",
                "FastAPI REST endpoints: Exposes VQC coordinates, dynamic weights, and strategies.",
                "Vercel Deployment: Standalone HTML visualizer deployed live on cloud static servers.",
                "Result: A scalable, production-grade Quantum-Graph system ready for deployment."
            ]
        }
    ]

    for sd in slides_data:
        # Create slide inheriting template layout
        slide = prs.slides.add_slide(content_layout)
        
        # Set Title
        slide.shapes.title.text = sd["title"]
        # Customize Title Font for visibility
        title_p = slide.shapes.title.text_frame.paragraphs[0]
        title_p.font.name = 'Rajdhani'
        title_p.font.size = Pt(28)
        title_p.font.bold = True
        title_p.font.color.rgb = RGBColor(10, 45, 80) # Dark Blue
        
        # Set Content (Placeholder 1 in slide_layouts[1] represents default bullet textbox)
        content_placeholder = slide.placeholders[1]
        tf = content_placeholder.text_frame
        tf.word_wrap = True
        tf.clear()
        
        for idx, bullet_text in enumerate(sd["bullets"]):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = bullet_text
            p.level = 0
            p.space_after = Pt(14)
            
            # Inherit template styling but ensure high-contrast colors
            for run in p.runs:
                run.font.name = 'Exo 2'
                run.font.size = Pt(15)
                run.font.color.rgb = RGBColor(40, 50, 65) # Charcoal/Dark Slate for maximum legibility

    prs.save(PPT_PATH)
    print(f"[PPT] ✅ Successfully compiled PowerPoint presentation with {len(prs.slides)} slides!")

if __name__ == "__main__":
    main()
