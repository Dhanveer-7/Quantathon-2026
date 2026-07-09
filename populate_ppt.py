"""
═══════════════════════════════════════════════════════════════════════════════
  RIT Quantathan 2026 — PowerPoint Generator
  File: populate_ppt.py
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

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

PPT_PATH = "RIT - Quantathan 2026 - PPT.pptx"

def main():
    prs = Presentation(PPT_PATH)
    
    # ─── SLIDE 0: TITLE SLIDE MODIFICATIONS ───
    slide_0 = prs.slides[0]
    
    # Find and update placeholders
    for shape in slide_0.shapes:
        if not shape.has_text_frame:
            continue
        text = shape.text
        if "Presented by" in text:
            # Change to project title
            shape.text_frame.text = "Q-GUARD AI\nMulti-Agent Quantum Fraud Intelligence"
            # Set font style
            for paragraph in shape.text_frame.paragraphs:
                paragraph.font.name = 'Rajdhani'
                paragraph.font.size = Pt(36)
                paragraph.font.bold = True
                paragraph.font.color.rgb = RGBColor(0, 212, 255) # Glowing Cyan
        elif "Name of the Candidate" in text:
            shape.text_frame.text = "Team Schrödinger’s Coders\nMembers: Dhinith Pragalyan, Dhanveer M, Venkatesan S, Elamaran B"
            for paragraph in shape.text_frame.paragraphs:
                paragraph.font.name = 'Exo 2'
                paragraph.font.size = Pt(14)
                paragraph.font.bold = True
                paragraph.font.color.rgb = RGBColor(0, 255, 157) # Green
        elif "Institution / Organization" in text:
            shape.text_frame.text = "RIT Chennai — Quantathan 2026"
            for paragraph in shape.text_frame.paragraphs:
                paragraph.font.name = 'Share Tech Mono'
                paragraph.font.size = Pt(14)
                paragraph.font.color.rgb = RGBColor(200, 200, 200)

    # ─── REMOVE SLIDE 1 (TEMPLATE PLACEHOLDER) ───
    # We will remove the placeholder slide 1 and append our structured presentation slides
    # standard python-pptx doesn't have slide.delete(), so we bypass it by clearing its content
    slide_1 = prs.slides[1]
    for shape in list(slide_1.shapes):
        # Remove old shapes to clean slide 1
        sp = shape._element
        sp.getparent().remove(sp)
        
    # Re-use slide 1 as Slide 1: Problem Statement
    # Add title text box
    title_box = slide_1.shapes.add_textbox(Inches(0.75), Inches(0.5), Inches(8.5), Inches(1.0))
    title_tf = title_box.text_frame
    title_p = title_tf.paragraphs[0]
    title_p.text = "1. PROBLEM STATEMENT (QT-2.8)"
    title_p.font.name = 'Rajdhani'
    title_p.font.size = Pt(28)
    title_p.font.bold = True
    title_p.font.color.rgb = RGBColor(0, 212, 255)
    
    # Add content text box
    content_box = slide_1.shapes.add_textbox(Inches(0.75), Inches(1.8), Inches(8.5), Inches(4.5))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    bullets_s1 = [
        "Classical ML models check transactions in isolation, missing temporal loops.",
        "High False Positive rates annoy regular customers, increasing churn and operational friction.",
        "Regulatory compliance (RBI/Central Bank) requires Explainable AI (XAI) parameters.",
        "Coordinated attacks (Mule Rings, shared device farms) bypass linear threshold rules.",
        "Solution: Q-Guard AI combines Multi-Agent intelligence with a Quantum Optimization layer."
    ]
    for b in bullets_s1:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(16)
        p.space_after = Pt(12)
        p.font.color.rgb = RGBColor(220, 240, 255)

    # ─── SLIDE DATA FOR REMAINING SLIDES ───
    # Layout 1 is the standard Title and Content slide layout in pptx templates
    content_layout = prs.slide_layouts[1]
    
    slides_data = [
        {
            "title": "2. Q-GUARD ARCHITECTURE: MULTI-AGENT INGESTION",
            "bullets": [
                "User Behavior Agent: Analyzes daily spending limit fractions and time deviation.",
                "Device Intelligence Agent: Detects OS versions, emulators, and device trust rating.",
                "Merchant Rating Agent: Assesses merchant category hazard and chargeback rates.",
                "Network Intelligence Agent: Monitors VPN usage, proxy IPs, and impossible travel.",
                "Benefit: Decentralized analysis captures separate threat layers simultaneously."
            ]
        },
        {
            "title": "3. QUANTUM WEIGHT OPTIMIZATION (QML LAYER)",
            "bullets": [
                "State Encoding: Maps the 4 Agent risk variables directly to 4 Qubits (Q0 to Q3).",
                "Entangling Circuit: Employs a Ring CNOT entangler to learn inter-agent correlations.",
                "Dynamic Weighting: Aggregates risk dynamically based on Qubit Z-coordinate excitation.",
                "Bloch Projections: Agent weights are proportional to excitation (Weight = 1.0 - Z).",
                "Benefit: Captures non-linear threat vectors using 90% fewer parameters than classical NN."
            ]
        },
        {
            "title": "4. ADAPTIVE CONTEXT THRESHOLD ENGINE",
            "bullets": [
                "Standard Thresholds: Traditional banks use static 80% limits (high friction).",
                "Adaptive Threshold: Q-Guard shifts limits dynamically based on transaction context.",
                "Late Night Hour Window (12 AM - 5 AM): Threshold drops to 65% (restrictive).",
                "High chargeback Merchant Terminal: Threshold drops to 58% (highly secure).",
                "Trusted Regular Customer: Threshold rises to 95% (minimizes customer friction)."
            ]
        },
        {
            "title": "5. SELF-EXPLAINABLE AI & MITIGATION CHECKLISTS",
            "bullets": [
                "Self-Explainable AI (XAI): Translates VQC state vectors into warning logs.",
                "Auditable Compliance: Outlines exactly why an agent triggered the transaction block.",
                "Fraud Strategy Advisor: Recommends progressive mitigation checklists instead of binary blocks.",
                "Mitigation Checklist: Request Face Authentication, Require SMS OTP, or Hold payout.",
                "Benefit: Reduces manual review audit delays and matches regulatory frameworks."
            ]
        },
        {
            "title": "6. SCALABILITY & DATABASE PIPELINE Integration",
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
        slide = prs.slides.add_slide(content_layout)
        slide.shapes.title.text = sd["title"]
        
        # Get or add content text frame
        # Standard layouts have placeholder 1 as content text box
        if len(slide.placeholders) > 1:
            tf = slide.placeholders[1].text_frame
        else:
            tf = slide.shapes.add_textbox(Inches(0.75), Inches(2.0), Inches(8.5), Inches(4.5)).text_frame
            
        tf.word_wrap = True
        tf.clear()
        
        for idx, b in enumerate(sd["bullets"]):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = "• " + b
            p.font.size = Pt(16)
            p.space_after = Pt(12)
            p.font.color.rgb = RGBColor(220, 240, 255)

    # Save
    prs.save(PPT_PATH)
    print(f"[PPT] ✅ Successfully compiled PowerPoint presentation with {len(prs.slides)} slides!")

if __name__ == "__main__":
    main()
