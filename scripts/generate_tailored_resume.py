#!/usr/bin/env python3
"""Tailored Resume & Application Generator for Aryan Sharma.

Extracts core credentials from Aryan's verified resume and dynamically
generates ATS-optimized resumes and application proposals tailored
to specific roles (GSoC, MLH, LFX, Big Tech SWE, AI Research).
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

BASE_PROFILE = {
    "name": "Aryan Sharma",
    "headline": "AI/ML & Data | AI Evaluation | Software Engineering",
    "contact": {
        "email": "aryanaryan.9956@icloud.com",
        "linkedin": "https://www.linkedin.com/in/aryan-sharma-engineer",
        "github": "https://github.com/Aryansharma906",
        "location": "India"
    },
    "education": [
        {
            "institution": "IILM University, Greater Noida",
            "degree": "Bachelor of Technology in Computer Science, Specialization: AI & ML",
            "period": "Jul 2026 – Jun 2030"
        },
        {
            "institution": "Harvard University",
            "degree": "CS50x: Introduction to Computer Science",
            "period": "Jan 2026 – Jun 2026"
        },
        {
            "institution": "Alison",
            "degree": "Diploma in Applied Generative AI",
            "period": "2026"
        }
    ],
    "experience": [
        {
            "role": "AI Evaluation Specialist (Remote Freelance)",
            "organization": "Handshake",
            "location": "San Francisco, CA",
            "period": "Jul 2026 – Present",
            "highlights": [
                "Produced structured evaluations of AI model outputs for reasoning accuracy, alignment, safety, and semantic quality using defined assessment criteria.",
                "Improved consistency of AI-output assessment by systematically evaluating responses across reasoning and safety dimensions."
            ]
        },
        {
            "role": "Forward Program Participant",
            "organization": "McKinsey & Company",
            "period": "Sep 2026 – Present",
            "highlights": [
                "Selected for structured development in problem-solving, digital toolkits, and executive communication applied to AI/ML systems."
            ]
        },
        {
            "role": "Harvard Aspire Leaders Program Fellow",
            "organization": "Aspire Institute",
            "location": "Cambridge, MA",
            "period": "Jul 2026 – Present",
            "highlights": [
                "Global leadership-development program focused on leadership, communication, mentorship, and high-impact tech collaboration."
            ]
        },
        {
            "role": "HPAIR Delegate",
            "organization": "Harvard College Project for Asian and International Relations",
            "period": "Sep 2026 – Present",
            "highlights": [
                "Selected delegate engaging with international leaders on emerging tech, AI governance, and global innovation."
            ]
        },
        {
            "role": "Sagan Summer Workshop Research Participant",
            "organization": "NASA Exoplanet Science Institute (NExScI) at Caltech",
            "period": "Jul 2026",
            "highlights": [
                "Trained in exoplanet detection, observational astronomy, and computational astrophysical data pipelines."
            ]
        }
    ],
    "projects": [
        {
            "title": "JABSON AI & Autonomous Agent Architecture",
            "tech": "Python, Multi-Agent Orchestration, REST APIs, LLM Security",
            "description": "Engineered autonomous agentic infrastructure replacing repetitive software agency workflows with deterministic LLM pipelines."
        },
        {
            "title": "Z-Score Statistical Analysis Tool",
            "tech": "Python, NumPy, Pandas, Scipy",
            "description": "Python application for hypothesis testing, Z-score computation, outlier detection, and distribution analysis."
        },
        {
            "title": "Full-Stack Developer Portfolio",
            "tech": "TypeScript, React, Responsive Modern Web",
            "description": "High-performance portfolio showcasing full-stack systems, dynamic component architecture, and responsive UI."
        },
        {
            "title": "VectorShift Frontend Architecture",
            "tech": "React, JavaScript, State Management",
            "description": "Dynamic component architecture demonstrating state flow, third-party API integration, and clean UI rendering."
        }
    ],
    "publication": "The Architecture of Vulnerability: A Contemplative Inquiry into LLM Prompt Injection and the Future of Semantic Security",
    "skills": {
        "languages": ["Python", "JavaScript", "TypeScript", "Java", "SQL", "HTML/CSS"],
        "ai_ml": ["Machine Learning", "AI Safety", "Prompt Engineering", "Deep Learning", "NLP", "LLM Evaluation"],
        "data": ["Pandas", "NumPy", "Matplotlib", "Seaborn", "Tableau", "EDA", "Statistical Analysis"],
        "databases": ["PostgreSQL", "MySQL", "Schema Design", "CTEs", "Query Optimization"],
        "tools": ["Git", "GitHub", "Jupyter", "REST APIs", "Docker", "Linux"]
    }
}


def tailor_resume(role_title: str, target_org: str, job_description: str = "") -> str:
    """Generate tailored resume in markdown format."""
    summary = (
        f"AI/ML & Software Engineer with rigorous foundations in AI evaluation, LLM security, and data pipelines. "
        f"Recognized through competitive selection by Harvard Aspire, NASA NExScI/Caltech, McKinsey Forward, and HPAIR. "
        f"Hands-on experience conducting structured model evaluations at Handshake and architecting autonomous systems at JABSON AI. "
        f"Targeting high-impact contributions as {role_title} at {target_org}."
    )

    doc = []
    doc.append(f"# {BASE_PROFILE['name'].upper()}")
    doc.append(f"**{BASE_PROFILE['headline']}**")
    doc.append(f"{BASE_PROFILE['contact']['location']} | {BASE_PROFILE['contact']['email']} | [LinkedIn]({BASE_PROFILE['contact']['linkedin']}) | [GitHub]({BASE_PROFILE['contact']['github']})\n")
    
    doc.append("## PROFESSIONAL SUMMARY")
    doc.append(summary + "\n")

    doc.append("## EDUCATION")
    for edu in BASE_PROFILE["education"]:
        doc.append(f"- **{edu['institution']}** — *{edu['degree']}* ({edu['period']})")
    doc.append("")

    doc.append("## SELECT EXPERIENCE & FELLOWSHIPS")
    for exp in BASE_PROFILE["experience"]:
        loc = f" | {exp['location']}" if "location" in exp else ""
        doc.append(f"### {exp['role']} — {exp['organization']}{loc} ({exp['period']})")
        for hl in exp["highlights"]:
            doc.append(f"- {hl}")
    doc.append("")

    doc.append("## KEY PROJECTS")
    for p in BASE_PROFILE["projects"]:
        doc.append(f"- **{p['title']}** (`{p['tech']}`): {p['description']}")
    doc.append("")

    doc.append("## TECHNICAL SKILLS")
    doc.append(f"- **Languages:** {', '.join(BASE_PROFILE['skills']['languages'])}")
    doc.append(f"- **AI / ML & Evaluation:** {', '.join(BASE_PROFILE['skills']['ai_ml'])}")
    doc.append(f"- **Data & Analysis:** {', '.join(BASE_PROFILE['skills']['data'])}")
    doc.append(f"- **Databases & Tools:** {', '.join(BASE_PROFILE['skills']['databases'] + BASE_PROFILE['skills']['tools'])}")
    doc.append("")

    doc.append("## PUBLICATIONS & HONORS")
    doc.append(f"- **Publication:** *{BASE_PROFILE['publication']}*")
    doc.append("- **Competitive Selections:** NASA NExScI Sagan Workshop, Harvard Aspire Leaders, McKinsey Forward, HPAIR Delegate.")

    return "\n".join(doc)


if __name__ == "__main__":
    target_role = sys.argv[1] if len(sys.argv) > 1 else "Open Source AI Contributor"
    target_org = sys.argv[2] if len(sys.argv) > 2 else "Google Summer of Code (GSoC 2026)"
    
    output_dir = ROOT / "testing" / "tailored_resumes"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tailored = tailor_resume(target_role, target_org)
    filename = f"Aryan_Sharma_{target_org.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
    out_path = output_dir / filename
    out_path.write_text(tailored, encoding="utf-8")
    
    print(f"Generated tailored resume for {target_role} at {target_org}: {out_path}")
    print("\n" + tailored[:800] + "\n...")
