"""Job Hunt AI Engine implementing the complete modern job hunt stack.

Synthesizes the best frameworks from:
1. Vaibhav Sisinty's Complete AI Job Hunt Stack (Gemini ATS Optimizer, Value Cover Letter, NotebookLM Interview Prep).
2. Mayank Joshi's Claude Job Skill (12+ platform scoring, complete application package bundling, multi-platform search).
3. Vaibhav Sisinty x Raj Shamani (Proof-of-Work pitch, 3-sentence direct founder/hiring manager LinkedIn outreach).
"""
from __future__ import annotations

import io
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from lib._env import load_env
from lib.frontierpilot_integrator import ARYAN_PROFILE, FrontierPilotIntegrator
DossierIntegrator = FrontierPilotIntegrator

load_env()
ROOT = Path(__file__).resolve().parents[1]


class JobHunterEngine:
    _MODELS = ["gemini-4-hydrogen", "gemini-3.5-flash-lite"]

    def __init__(self):
        load_env()
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.integrator = DossierIntegrator()
        self.output_dir = ROOT / "testing" / "application_bundles"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _call_gemini_json(self, prompt: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a prompt against Google Gemini expecting structured JSON with model cascade."""
        if not self.gemini_key:
            return fallback

        for model in self._MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.25, "responseMimeType": "application/json"}
            }
            try:
                r = requests.post(url, json=payload, timeout=6)
                if r.status_code == 200:
                    data = r.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text)
            except Exception as e:
                print(f"Gemini call fallback ({model}): {e}")
        return fallback

    def _call_gemini_text(self, prompt: str, fallback: str) -> str:
        """Execute a prompt against Google Gemini expecting formatted markdown/prose with model cascade."""
        if not self.gemini_key:
            return fallback

        for model in self._MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3}
            }
            try:
                r = requests.post(url, json=payload, timeout=6)
                if r.status_code == 200:
                    data = r.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                print(f"Gemini text fallback ({model}): {e}")
        return fallback

    # =========================================================================
    # 1. Vaibhav Sisinty Framework: Gemini ATS Keyword & Resume Optimizer
    # =========================================================================

    def generate_ats_resume(self, opp: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-scoring ATS resume tailored to specific role without hallucinating."""
        title = opp.get("title", "AI Engineer")
        org = opp.get("organization", "Company")
        match_reason = opp.get("match_reason", "")
        summary_rec = opp.get("executive_summary", "")

        prompt = f"""You are an elite technical recruiter and ATS optimization specialist following Vaibhav Sisinty's AI Job Hunt Stack.

CANDIDATE VERIFIED PROFILE:
{json.dumps(ARYAN_PROFILE, indent=2)}

TARGET OPPORTUNITY:
Role: {title}
Company: {org}
Context: {match_reason}
Recommendation: {summary_rec}

Generate an ATS-optimized, high-conversion resume tailored strictly for this role.
Rules:
1. Extract the top 10 mandatory ATS technical keywords for this role.
2. Weave those keywords naturally into Aryan's verified experiences (Handshake, McKinsey, Research Publication, Harvard CS50x).
3. Absolutely NO lying or fake experiences. Use metric-driven action verbs (Evaluated, Benchmarked, Engineered, Optimized).
4. Return a JSON object with:
   - "ats_keywords": list of 8-12 keywords targeted.
   - "professional_summary": 3-line executive summary directly targeted to {org}.
   - "tailored_markdown": Full markdown formatted resume ready for ATS scanning.
"""
        fallback_md = f"""# Aryan Sharma
**Email:** {ARYAN_PROFILE['contact']['email']} | **LinkedIn:** {ARYAN_PROFILE['contact']['linkedin']} | **GitHub:** {ARYAN_PROFILE['contact']['github']}

## Professional Summary
AI/ML & Distributed Systems Engineer specializing in LLM evaluation, adversarial prompt security, and scalable systems. Proven track record evaluating complex model outputs for alignment and safety at Handshake and authoring published research on prompt injection vulnerability. Eager to contribute high-rigor engineering to {org} as {title}.

## Core Technical Skills
- **Languages:** Python, C, SQL, TypeScript, Bash
- **AI & Systems:** PyTorch, LLM Evaluation, RAG Guardrails, Prompt Security, Hugging Face, Linux Internals
- **Tools & Infrastructure:** Docker, Git/GitHub Actions, PostgreSQL, REST APIs, FastAPI

## Experience
**AI Evaluation Specialist (Remote Freelance)** | Handshake (San Francisco, CA)
*Jul 2026 – Present*
- Executed systematic evaluation of large language models for reasoning accuracy, semantic coherence, and safety alignment.
- Benchmarked failure modes, hallucinations, and jailbreak vectors across multi-turn conversational agents.

**Forward Program Participant** | McKinsey & Company
*Sep 2026 – Present*
- Mastered structured problem-solving, digital toolkits, and executive technical communication.

## Research & Publications
**Investigating Prompt Vulnerability and Injection in Large Language Models**
- Investigated adversarial attack surfaces, automated defense guardrails, and jailbreak boundaries in production LLM pipelines.

## Education
**Bachelor of Technology in Computer Science (AI & ML)** | IILM University, Greater Noida (*2026 – 2030*)
**CS50x: Introduction to Computer Science** | Harvard University (*2026*)
"""
        fallback = {
            "ats_keywords": ["LLM Evaluation", "Prompt Security", "Python", "PyTorch", "Model Alignment", "Systems", "Linux"],
            "professional_summary": f"AI/ML & Distributed Systems Engineer with published research on prompt security, evaluating models at Handshake and scaling high-rigor solutions for {org}.",
            "tailored_markdown": fallback_md
        }

        res = self._call_gemini_json(prompt, fallback)
        if "tailored_markdown" not in res:
            res["tailored_markdown"] = fallback_md
        return res

    # =========================================================================
    # 2. Vaibhav Sisinty Framework: Problem-Solver Cover Letter (<300 Words)
    # =========================================================================

    def generate_value_cover_letter(self, opp: Dict[str, Any]) -> str:
        """Generate a concise, problem-solving cover letter focused on company value."""
        title = opp.get("title", "AI Engineer")
        org = opp.get("organization", "Company")

        prompt = f"""You are Aryan Sharma writing a value-first, problem-solving cover letter to {org} for the role of {title}.
Follow Vaibhav Sisinty's proven cover letter structure:
- Paragraph 1 (The Hook): Demonstrate genuine understanding of {org}'s engineering mission and why this specific role excites you.
- Paragraph 2 (The Proof): Connect 2 of your verified achievements (Handshake AI evaluation, LLM prompt security publication, or Harvard CS50x) directly to their requirements.
- Paragraph 3 (The Ask): Professional call to action offering a brief conversation.
- Rules: Strictly under 280 words. NO corporate buzzwords (no 'passionate', 'delve', 'leverage', 'in today's fast-paced world'). Direct, technical, and confident.

Candidate details:
{json.dumps(ARYAN_PROFILE, indent=2)}
"""
        fallback = (
            f"Dear Hiring Team at {org},\n\n"
            f"I have been closely following {org}'s engineering work and mission. When I saw the opening for the {title}, "
            f"the technical challenges resonated directly with the systems and evaluation work I focus on.\n\n"
            f"At Handshake, I evaluate large language model outputs for reasoning accuracy, semantic coherence, and alignment boundaries. "
            f"Additionally, my research publication on prompt injection and adversarial vulnerabilities analyzed production defense guardrails for "
            f"generative pipelines. Combined with a strong foundation in Python, Linux internals, and C from Harvard CS50x, I build systems with "
            f"both research rigor and practical reliability.\n\n"
            f"I would welcome the opportunity to discuss how my systems and AI evaluation background can support {org}'s upcoming milestones.\n\n"
            f"Best regards,\n"
            f"Aryan Sharma\n"
            f"aryanaryan.9956@icloud.com | linkedin.com/in/aryan-sharma-engineer"
        )
        return self._call_gemini_text(prompt, fallback)

    # =========================================================================
    # 3. Vaibhav Sisinty x Raj Shamani: Direct Recruiter & Founder LinkedIn Outreach
    # =========================================================================

    def generate_recruiter_outreach_dm(self, opp: Dict[str, Any]) -> Dict[str, str]:
        """Generate high-converting 3-sentence direct LinkedIn messages for hiring managers."""
        title = opp.get("title", "AI Engineer")
        org = opp.get("organization", "Company")

        prompt = f"""Generate a high-converting 3-sentence cold LinkedIn direct message for Aryan Sharma to send to an engineering manager or founder at {org} for the {title} role.
Follow Vaibhav Sisinty's direct outreach rule:
- Sentence 1: Specific observation or respect for their team's technical release or product.
- Sentence 2: Crisp proof-of-work showing how Aryan's AI evaluation/prompt security work solves their exact problem.
- Sentence 3: Low-friction call to action (e.g. 'Happy to share a 1-page tactical plan or repo link if you are exploring this.').

Keep it under 70 words total. No fluff.
"""
        fallback_3lines = (
            f"Hi [Name], loved {org}'s recent work scaling your systems and model reliability. "
            f"I specialize in LLM evaluation and prompt security research, recently publishing on adversarial attack surfaces while benchmarking models at Handshake. "
            f"I’d love to share a brief 1-page tactical architecture breakdown on how this applies to {org}'s {title} roadmap if helpful."
        )
        dm_text = self._call_gemini_text(prompt, fallback_3lines)

        return {
            "linkedin_dm_3_sentences": dm_text,
            "cold_email_subject": f"Aryan Sharma <> {org} | {title} & Systems Reliability",
            "proof_of_work_hook": f"Architecture breakdown for {org}'s AI pipeline."
        }

    # =========================================================================
    # 4. Vaibhav Sisinty Strategy: 1-Page Proof-of-Work (PoW) Tactical Plan
    # =========================================================================

    def generate_proof_of_work_plan(self, opp: Dict[str, Any]) -> str:
        """Generate a 1-page tactical plan solving a real engineering problem for the company."""
        title = opp.get("title", "AI Systems Contributor")
        org = opp.get("organization", "Company")

        prompt = f"""Generate a 1-page Tactical Proof-of-Work Plan from Aryan Sharma for {org} for the role of {title}.
Structure:
1. Executive Summary: The technical challenge {org} faces in scaling this role.
2. Proposed 90-Day Implementation Architecture:
   - Days 1-30: Evaluation baseline, security audit, benchmarking suite.
   - Days 31-60: Automated guardrails, CI/CD pipeline integration, latency optimization.
   - Days 61-90: Scaling, production monitoring, documentation.
3. Candidate Synergy: How Aryan's background (LLM Prompt Injection research, Handshake evaluation, Python/Linux systems) guarantees rapid execution.

Format as clean, professional Markdown. Under 400 words.
"""
        fallback = f"""# Tactical Engineering Proposal: {org} — {title}
**Prepared by:** Aryan Sharma | AI/ML & Distributed Systems Engineer

## 1. Challenge Overview
Modern production pipelines at {org} require both high throughput and bulletproof semantic reliability. As models scale, automated evaluation, adversarial prompt resistance, and low-latency validation become critical engineering bottlenecks.

## 2. 90-Day Technical Roadmap
- **Phase 1 (Days 1–30): Baseline Benchmark & Guardrail Audit**
  - Establish programmatic evaluation harness for model accuracy and semantic drift.
  - Implement automated regression testing for adversarial prompts and jailbreak boundaries.
- **Phase 2 (Days 31–60): Pipeline Optimization & Tooling**
  - Deploy lightweight asynchronous middleware in Python/FastAPI for sub-50ms security checks.
  - Integrate continuous evaluation into GitHub Actions CI/CD.
- **Phase 3 (Days 61–90): Production Hardening & Documentation**
  - Stress-test system under peak load and publish reproducibility benchmarks.
  - Establish self-healing monitoring alerts for edge-case failures.

## 3. Immediate Value Add
With published research in LLM prompt vulnerabilities and practical experience benchmarking reasoning models at Handshake, I eliminate ramp-up time and deliver production-grade results from Day 1.
"""
        return self._call_gemini_text(prompt, fallback)

    # =========================================================================
    # 5. Vaibhav Sisinty Framework: NotebookLM & Gemini Interview Prep Guide
    # =========================================================================

    def generate_interview_prep_guide(self, opp: Dict[str, Any]) -> Dict[str, Any]:
        """Generate targeted technical & behavioral interview questions tailored to the company."""
        title = opp.get("title", "AI Engineer")
        org = opp.get("organization", "Company")

        prompt = f"""You are an elite principal engineer and interview coach following Vaibhav Sisinty's NotebookLM interview prep framework.
Prepare an interview mastery guide for Aryan Sharma interviewing for {title} at {org}.

Candidate Background:
{json.dumps(ARYAN_PROFILE, indent=2)}

Return a JSON object containing:
1. "company_tech_stack_summary": 2 sentences explaining {org}'s engineering focus.
2. "technical_questions": list of 4 deep-dive questions (covering algorithms, systems design, and AI/ML evaluation) with bulleted "Ideal Answer Key".
3. "system_design_challenge": 1 realistic architecture problem {org} might ask.
4. "behavioral_star_scenarios": list of 2 behavioral questions with suggested STAR framing from Aryan's background.
"""
        fallback = {
            "company_tech_stack_summary": f"{org} operates high-performance distributed infrastructure, emphasizing rigorous model evaluation, low latency, and robust reliability.",
            "technical_questions": [
                {
                    "question": "How do you detect and mitigate indirect prompt injection in an LLM pipeline with external tool access?",
                    "answer_key": "Isolate system instructions from untrusted data using semantic delimiters, implement AST-level tool argument validation, and benchmark against known jailbreak callsets."
                },
                {
                    "question": "Walk me through how you benchmark hallucination and factual consistency at scale.",
                    "answer_key": "Combine programmatic assertion testing (exact-match, regex), embedding similarity against ground truth, and calibrated LLM-as-judge with strict temperature=0."
                },
                {
                    "question": "How do you optimize memory and I/O when processing large vector datasets in Python?",
                    "answer_key": "Use memory-mapped files (numpy.memmap), batch vector embeddings to prevent OOM, and leverage SIMD-accelerated libraries like FAISS or USearch."
                },
                {
                    "question": "Explain how Linux virtual memory management protects processes and handles page faults.",
                    "answer_key": "Page tables map virtual to physical addresses; copy-on-write prevents redundant memory duplication during fork(); page faults trigger demand paging from swap or disk."
                }
            ],
            "system_design_challenge": f"Design an automated, low-latency LLM evaluation gateway capable of evaluating 10,000 prompt-response pairs per second for {org}.",
            "behavioral_star_scenarios": [
                {
                    "question": "Tell me about a time you discovered an unexpected edge-case failure in a complex system.",
                    "star_framework": "S: Benchmarking models at Handshake. T: Evaluate semantic reasoning under stress. A: Constructed adversarial edge cases that broke standard guardrails. R: Documented failure pattern and authored research publication on prompt vulnerability."
                }
            ]
        }

        return self._call_gemini_json(prompt, fallback)

    # =========================================================================
    # 6. Word Document (.docx) Export & Application Bundle (ZIP)
    # =========================================================================

    def _markdown_to_docx(self, markdown_text: str, file_path: Path, title: str) -> None:
        """Convert structured markdown into a clean, ATS-compliant Word document."""
        doc = docx.Document()
        
        # Set normal margins (1 inch)
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        for line in markdown_text.splitlines():
            line = line.strip()
            if not line:
                continue

            if line.startswith("# "):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(line[2:].strip())
                run.bold = True
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(15, 23, 42)
            elif line.startswith("## "):
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(line[3:].strip())
                run.bold = True
                run.font.size = Pt(13)
                run.font.color.rgb = RGBColor(30, 41, 59)
            elif line.startswith("- ") or line.startswith("* "):
                p = doc.add_paragraph(style="List Bullet")
                p.paragraph_format.space_after = Pt(2)
                # Parse bold spans
                text = line[2:].strip()
                self._add_markdown_runs(p, text)
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(4)
                self._add_markdown_runs(p, line)

        doc.save(str(file_path))

    def _add_markdown_runs(self, paragraph: Any, text: str) -> None:
        """Helper to add bold/italic runs from basic markdown."""
        parts = re.split(r"(\*\*.*?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                r = paragraph.add_run(part[2:-2])
                r.bold = True
            else:
                paragraph.add_run(part)

    def create_complete_application_bundle(self, opp: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and package the complete application stack into a downloadable ZIP."""
        opp_id = opp.get("id", "role")
        org = opp.get("organization", "Company").replace(" ", "_").replace("/", "_")
        role_slug = opp.get("title", "Role").replace(" ", "_").replace("/", "_")[:30]

        bundle_folder = self.output_dir / f"{org}_{opp_id}"
        bundle_folder.mkdir(parents=True, exist_ok=True)

        # 1. ATS Resume
        ats_res = self.generate_ats_resume(opp)
        resume_md = ats_res.get("tailored_markdown", "")
        resume_md_path = bundle_folder / f"Aryan_Sharma_Resume_{org}.md"
        resume_md_path.write_text(resume_md, encoding="utf-8")

        resume_docx_path = bundle_folder / f"Aryan_Sharma_Resume_{org}.docx"
        self._markdown_to_docx(resume_md, resume_docx_path, f"Resume: {opp.get('organization')}")

        # 2. Value-First Cover Letter
        cover_letter_text = self.generate_value_cover_letter(opp)
        cover_md_path = bundle_folder / f"Aryan_Sharma_CoverLetter_{org}.md"
        cover_md_path.write_text(cover_letter_text, encoding="utf-8")

        cover_docx_path = bundle_folder / f"Aryan_Sharma_CoverLetter_{org}.docx"
        self._markdown_to_docx(cover_letter_text, cover_docx_path, f"Cover Letter: {opp.get('organization')}")

        # 3. 3-Sentence Recruiter DM
        outreach_data = self.generate_recruiter_outreach_dm(opp)
        dm_path = bundle_folder / "Recruiter_LinkedIn_Outreach_DM.txt"
        dm_content = (
            f"=== 3-SENTENCE LINKEDIN DIRECT MESSAGE FOR {opp.get('organization').upper()} ===\n\n"
            f"{outreach_data['linkedin_dm_3_sentences']}\n\n"
            f"Subject line (if email): {outreach_data['cold_email_subject']}\n"
        )
        dm_path.write_text(dm_content, encoding="utf-8")

        # 4. 1-Page Proof-of-Work Tactical Plan
        pow_plan = self.generate_proof_of_work_plan(opp)
        pow_path = bundle_folder / f"Proof_of_Work_Tactical_Plan_{org}.md"
        pow_path.write_text(pow_plan, encoding="utf-8")

        # 5. NotebookLM Interview Prep Guide
        interview_data = self.generate_interview_prep_guide(opp)
        interview_path = bundle_folder / f"NotebookLM_Interview_Prep_{org}.json"
        interview_path.write_text(json.dumps(interview_data, indent=2), encoding="utf-8")

        # 6. Bundle all into a clean ZIP archive
        zip_filename = f"Aryan_Sharma_{org}_Application_Package.zip"
        zip_path = self.output_dir / zip_filename

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for item in bundle_folder.iterdir():
                zipf.write(item, arcname=item.name)

        return {
            "success": True,
            "organization": opp.get("organization"),
            "role": opp.get("title"),
            "zip_path": str(zip_path),
            "zip_filename": zip_filename,
            "ats_keywords": ats_res.get("ats_keywords", []),
            "recruiter_dm": outreach_data["linkedin_dm_3_sentences"],
            "bundle_files": [f.name for f in bundle_folder.iterdir()]
        }
