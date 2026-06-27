import os
import json
import time
from typing import Dict, List, Tuple
from google import genai
from google.genai import types

class AIMatcher:
    """
    AI Processing & Matching Engine using Gemini 3.5 Flash.
    Optimizes candidate-job fit analysis, ATS compatibility scoring,
    and LaTeX resume tailoring.
    """

    def __init__(self):
        self._client = None
        self._init_checked = False

    def get_client(self) -> genai.Client:
        """Lazy initialization of the official Google GenAI Client."""
        if not self._client and not self._init_checked:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key and api_key != "MY_GEMINI_API_KEY":
                try:
                    self._client = genai.Client(api_key=api_key)
                    print("[AIMatcher] Successfully loaded official Google GenAI client.")
                except Exception as e:
                    print(f"[AIMatcher] Error initializing GenAI client: {e}")
            else:
                print("[AIMatcher] No valid GEMINI_API_KEY environment variable found. Falling back to heuristic matching.")
            self._init_checked = True
        return self._client

    def calculate_heuristic_score(self, job: Dict, profile: Dict) -> Dict:
        """
        Calculates a highly deterministic skill-matching Jaccard-like score.
        Serves as a reliable, zero-cost offline fallback.
        """
        score = 50  # Baseline
        matched_skills = []
        
        job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        skills = profile.get("skills", [])
        
        for skill in skills:
            if skill.lower() in job_text:
                matched_skills.append(skill)
                
        # Skill overlap ratio weight (30%)
        skill_ratio = len(matched_skills) / max(1, len(skills))
        score += int(skill_ratio * 30)

        # Remote type match weight (15%)
        remote_preference = profile.get("preferences", {}).get("remotePreference", "Any")
        job_remote = job.get("remoteType", "Hybrid")
        
        if job_remote == "Remote" and remote_preference in ["Remote", "Any"]:
            score += 15
        elif job_remote == "Hybrid" and remote_preference in ["Hybrid", "Any"]:
            score += 10

        # Preferred company match weight (10%)
        target_companies = profile.get("preferences", {}).get("targetCompanies", [])
        job_company = job.get("company", "").lower()
        if any(tc.lower() in job_company for tc in target_companies):
            score += 10

        score = min(100, max(0, score))

        explanation = (
            f"Heuristic alignment score of {score}% based on matching {len(matched_skills)} "
            f"primary skills: {', '.join(matched_skills[:5])}."
        )
        if job_remote == "Remote":
            explanation += " Fully remote role matches work preferences."

        return {
            "score": score,
            "extractedSkills": matched_skills,
            "fitExplanation": explanation,
            "salaryEstimate": "Not Specified",
            "seniority": "Senior" if "senior" in job.get("title", "").lower() else "Mid-level"
        }

    def score_job(self, job: Dict, profile: Dict) -> Dict:
        """
        Scores a job description against the candidate's profile.
        Uses structured schemas to ensure valid JSON return parsing.
        """
        client = self.get_client()
        if not client:
            return self.calculate_heuristic_score(job, profile)

        prompt = f"""You are an expert AI Technical Recruiter. Analyze the following job description against the candidate's professional profile.

CANDIDATE PROFILE:
{json.dumps(profile, indent=2)}

JOB DETAILS:
Title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location')}
Description: {job.get('description')}

Assess skills matching, salary parameters, remote preference alignment, and candidate fit.
"""

        # Enforce exact JSON response schema
        schema = {
            "type": "OBJECT",
            "properties": {
                "score": {"type": "INTEGER"},
                "extractedSkills": {"type": "ARRAY", "items": {"type": "STRING"}},
                "seniority": {"type": "STRING"},
                "remoteType": {"type": "STRING"},
                "salaryEstimate": {"type": "STRING"},
                "fitExplanation": {"type": "STRING"}
            },
            "required": ["score", "extractedSkills", "seniority", "remoteType", "salaryEstimate", "fitExplanation"]
        }

        # Dynamic retry with exponential backoff
        delay = 1.0
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                    )
                )
                parsed = json.loads(response.text)
                return parsed
            except Exception as e:
                print(f"[AIMatcher] Gemini error (attempt {attempt + 1}): {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2

        # Fallback to heuristic score on failure
        return self.calculate_heuristic_score(job, profile)

    def tailor_resume_and_cover_letter(self, job: Dict, profile: Dict) -> Tuple[str, str, int]:
        """
        Generates customized LaTeX resume and plaintext cover letter for target jobs.
        Computes dynamic ATS score comparing result against job specs.
        """
        client = self.get_client()
        master_latex = profile.get("masterResumeLaTeX", "")
        
        if not client:
            # Safe Fallback Generator
            tailored_latex = master_latex.replace(
                "\\section*{Target Roles}",
                f"\\section*{{Target Roles - Tailored for {job.get('title')} at {job.get('company')}}}"
            )
            cover_letter = f"""Dear Hiring Team at {job.get('company')},

I am writing to express my strong interest in the {job.get('title')} position. With my background in DevOps, Platform engineering, and AWS systems, I am confident I am a great fit.

I look forward to discussing how my experience can add value to the engineering operations at {job.get('company')}.

Sincerely,
{profile.get('fullName', 'Hemal Buha')}"""
            return tailored_latex, cover_letter, 75

        # 1. Tailor LaTeX
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
        
        # 2. Cover Letter
        cover_letter_prompt = f"""Write a highly compelling, professional 3-paragraph cover letter for:
Candidate Name: {profile.get('fullName')}
Target Role: {job.get('title')}
Company: {job.get('company')}
Job Description: {job.get('description')}

Do not include any placeholders like [Company Name]. Write real text. Keep it professional.
"""

        try:
            # Run parallel or sequential completions
            resume_res = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=resume_prompt
            )
            latex_out = resume_res.text or ""
            # Strip markdown elements
            latex_out = latex_out.replace("```latex", "").replace("```", "").strip()

            cover_res = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=cover_letter_prompt
            )
            cover_out = cover_res.text or ""

            # 3. Compute ATS Score
            ats_prompt = f"""Compare this tailored resume with the job description.
Estimate an ATS match score (integer between 0 and 100).

RESUME:
{latex_out}

JOB DESCRIPTION:
{job.get('description')}
"""
            ats_schema = {
                "type": "OBJECT",
                "properties": {
                    "atsScore": {"type": "INTEGER"}
                },
                "required": ["atsScore"]
            }
            
            ats_res = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=ats_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ats_schema
                )
            )
            ats_score = json.loads(ats_res.text).get("atsScore", 85)

            return latex_out, cover_out, ats_score
            
        except Exception as e:
            print(f"[AIMatcher] Error generating tailored files: {e}")
            return master_latex, "Fallback cover letter", 70
