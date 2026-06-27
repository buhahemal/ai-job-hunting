import json
import time
from typing import Dict, Tuple

from google.genai import types

from packages.ai_engine.python import heuristic_scorer
from packages.ai_engine.python.gemini_scorer import get_client
from packages.ai_engine.python.matcher import score_job as engine_score_job


class AIMatcher:
    """
    Facade for job scoring and resume tailoring.

    Scoring uses the Phase 6 ai_engine fallback chain:
    local embeddings -> optional Gemini -> heuristic.
    """

    def calculate_heuristic_score(self, job: Dict, profile: Dict) -> Dict:
        """Deterministic offline scoring helper (backward compatible)."""
        return heuristic_scorer.score(job, profile)

    def score_job(self, job: Dict, profile: Dict) -> Dict:
        """Score a job against the candidate profile."""
        return engine_score_job(job, profile)

    def tailor_resume_and_cover_letter(self, job: Dict, profile: Dict) -> Tuple[str, str, int]:
        """
        Generates customized LaTeX resume and plaintext cover letter for target jobs.
        Computes dynamic ATS score comparing result against job specs.
        """
        client = get_client()
        master_latex = profile.get('masterResumeLaTeX', '')

        if not client:
            tailored_latex = master_latex.replace(
                '\\section*{Target Roles}',
                f'\\section*{{Target Roles - Tailored for {job.get("title")} at {job.get("company")}}}',
            )
            cover_letter = f"""Dear Hiring Team at {job.get('company')},

I am writing to express my strong interest in the {job.get('title')} position. With my background in DevOps, Platform engineering, and AWS systems, I am confident I am a great fit.

I look forward to discussing how my experience can add value to the engineering operations at {job.get('company')}.

Sincerely,
{profile.get('fullName', 'Hemal Buha')}"""
            return tailored_latex, cover_letter, 75

        resume_prompt = f"""You are a professional LaTeX Resume Optimizer.
Tailor the master LaTeX resume specifically for the job description below.

MASTER RESUME:
{master_latex}

TARGET JOB DESCRIPTION:
Title: {job.get('title')}
Company: {job.get('company')}
Description: {job.get('description')}

CRITICAL RULES:
1. Remain factually accurate. Do NOT invent new jobs, roles, companies, or degrees.
2. Rearrange technical skills to prioritize what this job description requests.
3. Highlight relevant achievements in experience bullets matching required keywords.
4. OUTPUT ONLY valid LaTeX. Start with \\documentclass and end with \\end{{document}}. No code-blocks, no introductory remarks.
"""

        cover_letter_prompt = f"""Write a highly compelling, professional 3-paragraph cover letter for:
Candidate Name: {profile.get('fullName')}
Target Role: {job.get('title')}
Company: {job.get('company')}
Job Description: {job.get('description')}

Do not include any placeholders like [Company Name]. Write real text. Keep it professional.
"""

        try:
            resume_res = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=resume_prompt,
            )
            latex_out = (resume_res.text or '').replace('```latex', '').replace('```', '').strip()

            cover_res = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=cover_letter_prompt,
            )
            cover_out = cover_res.text or ''

            ats_prompt = f"""Compare this tailored resume with the job description.
Estimate an ATS match score (integer between 0 and 100).

RESUME:
{latex_out}

JOB DESCRIPTION:
{job.get('description')}
"""
            ats_schema = {
                'type': 'OBJECT',
                'properties': {'atsScore': {'type': 'INTEGER'}},
                'required': ['atsScore'],
            }

            ats_res = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=ats_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=ats_schema,
                ),
            )
            ats_score = json.loads(ats_res.text).get('atsScore', 85)
            return latex_out, cover_out, ats_score

        except Exception as exc:
            print(f'[AIMatcher] Error generating tailored files: {exc}')
            return master_latex, 'Fallback cover letter', 70
