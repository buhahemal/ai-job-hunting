import os
import sys
import subprocess
import json
from datetime import datetime

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Automatic dynamic bootstrap of python dependencies for seamless container deployment
def bootstrap_packages():
    required = ["flask", "flask-cors", "google-genai", "requests"]
    missing = []
    for pkg in required:
        # Map packages to import names if different
        import_name = "google.genai" if pkg == "google-genai" else pkg.replace("-", "_")
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[Boot] Installing missing dependencies in container: {missing}")
        try:
            # We add --break-system-packages to allow installing packages globally in modern system python versions (PEP 668)
            cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages", *missing]
            subprocess.check_call(cmd)
            print("[Boot] Package installation completed successfully.")
        except Exception as e:
            print(f"[Boot] Primary installation failed: {e}. Trying without --break-system-packages as fallback...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
                print("[Boot] Fallback package installation completed successfully.")
            except Exception as e2:
                print(f"[Boot] CRITICAL: Both installation attempts failed. e1: {e}, e2: {e2}")
                raise RuntimeError(f"Could not bootstrap required dependencies {missing}: {e2}") from e2

bootstrap_packages()

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from apps.api.defaults import DEFAULT_PROFILE, normalize_profile
from apps.api.paths import DATA_FILE, FRONTEND_DIST
from scraper.ai_matcher import AIMatcher
from scraper.scanner_engine import ScannerEngine

app = Flask(__name__)
CORS(app)

DB_FILE = DATA_FILE
PORT = 3000

# Unified Model instances
ai_matcher = AIMatcher()
scanner_engine = ScannerEngine()

DEFAULT_LATEX = DEFAULT_PROFILE["masterResumeLaTeX"]

SAMPLE_JOBS = [
    {
        "id": "job-1000",
        "title": "Senior Platform Engineer",
        "company": "EPAM Systems",
        "location": "US (Remote)",
        "remoteType": "Remote",
        "source": "EPAM Careers",
        "url": "https://careers.epam.com/jobs",
        "description": "EPAM is looking for a Senior Platform Engineer to scale our automated developer enablement cloud stack. In this role, you will lead the architecture of our cloud native landing zones, build Infrastructure as Code modules using Terraform, and deploy critical production services onto Kubernetes (EKS). You will collaborate closely with product development teams to champion modern CI/CD practices and implement proactive observability with Prometheus and Grafana. Key requirements: Strong experience with AWS, extensive knowledge of Terraform, production container orchestration with Kubernetes, and proficiency in scripting languages like Python or Go.",
        "postedAt": datetime.utcnow().isoformat() + "Z",
        "status": "New",
        "score": 94,
        "fitExplanation": "Excellent match! This role seeks AWS, Kubernetes, Terraform, and Python/Go, which are core pillars of your profile. EPAM is also your previous company, signaling a smooth culture fit.",
        "extractedSkills": ["AWS", "Kubernetes", "Terraform", "Prometheus", "Grafana", "Python", "Go"],
        "salaryEstimate": "$140,000 - $175,000",
        "seniority": "Senior"
    },
    {
        "id": "job-1001",
        "title": "Cloud Infrastructure Specialist",
        "company": "Globant",
        "location": "Bengaluru, India (Hybrid)",
        "remoteType": "Hybrid",
        "source": "Globant Job Board",
        "url": "https://jobs.globant.com",
        "description": "Join Globant's Cloud Studio as a Cloud Infrastructure Specialist! We design, build, and support massive multi-tenant platform backbones for world-class clients. You will assist in moving workloads from on-premises datacenters to AWS and GCP, writing Ansible playbooks, maintaining secure networking infrastructure, and managing highly available PostgreSQL databases. High familiarity with Docker, Linux systems administration, security posture benchmarks, and standard CI tooling (Jenkins, GitLab CI) is required.",
        "postedAt": datetime.utcnow().isoformat() + "Z",
        "status": "New",
        "score": 82,
        "fitExplanation": "Strong fit. You possess all requested skills like AWS, Ansible, Docker, and PostgreSQL. Hybrid setting in Bengaluru fits your regional profile.",
        "extractedSkills": ["AWS", "GCP", "Ansible", "PostgreSQL", "Docker", "Jenkins", "GitLab CI"],
        "salaryEstimate": "₹18,00,000 - ₹24,00,000",
        "seniority": "Mid-level"
    }
]

def read_db() -> dict:
    if not os.path.exists(DB_FILE):
        data = {
            "profile": DEFAULT_PROFILE,
            "jobs": SAMPLE_JOBS,
            "interviews": []
        }
        write_db(data)
        return data
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["profile"] = normalize_profile(data.get("profile"))
            return data
    except Exception as e:
        print(f"[Server] Error reading data.json, returning defaults. Error: {e}")
        return {"profile": DEFAULT_PROFILE, "jobs": [], "interviews": []}

def write_db(data: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# --- API Endpoints ---

@app.route("/api/profile", methods=["GET"])
def get_profile():
    db = read_db()
    return jsonify(db.get("profile", {}))

@app.route("/api/profile", methods=["POST"])
def update_profile():
    db = read_db()
    db["profile"] = request.json
    write_db(db)
    return jsonify({"success": True, "profile": db["profile"]})

@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    db = read_db()
    return jsonify({
        "jobs": db.get("jobs", []),
        "interviews": db.get("interviews", [])
    })

@app.route("/api/jobs/<string:job_id>/status", methods=["POST"])
def update_job_status(job_id):
    db = read_db()
    status = request.json.get("status")
    
    jobs = db.get("jobs", [])
    for job in jobs:
        if job.get("id") == job_id:
            job["status"] = status
            write_db(db)
            return jsonify({"success": True, "job": job})
            
    return jsonify({"error": "Job not found"}), 404

@app.route("/api/jobs/<string:job_id>/notes", methods=["POST"])
def update_job_notes(job_id):
    db = read_db()
    notes = request.json.get("notes")
    
    jobs = db.get("jobs", [])
    for job in jobs:
        if job.get("id") == job_id:
            job["notes"] = notes
            write_db(db)
            return jsonify({"success": True, "job": job})
            
    return jsonify({"error": "Job not found"}), 404

@app.route("/api/jobs/add-custom", methods=["POST"])
def add_custom_job():
    db = read_db()
    body = request.json
    
    new_job = {
        "id": f"custom-{int(datetime.utcnow().timestamp() * 1000)}",
        "title": body.get("title", "Software Engineer"),
        "company": body.get("company", "Custom Company"),
        "location": body.get("location", "Remote"),
        "remoteType": body.get("remoteType", "Remote"),
        "source": "Manual Import",
        "url": body.get("url", ""),
        "description": body.get("description", ""),
        "postedAt": datetime.utcnow().isoformat() + "Z",
        "status": "New"
    }

    # Perform instant AI score
    analysis = ai_matcher.score_job(new_job, db.get("profile", {}))
    new_job.update({
        "score": analysis.get("score", 70),
        "extractedSkills": analysis.get("extractedSkills", []),
        "seniority": analysis.get("seniority", "Mid-level"),
        "remoteType": analysis.get("remoteType", new_job["remoteType"]),
        "salaryEstimate": analysis.get("salaryEstimate", "Not Specified"),
        "fitExplanation": analysis.get("fitExplanation", "")
    })

    db.setdefault("jobs", []).insert(0, new_job)
    write_db(db)
    return jsonify({"success": True, "job": new_job})

@app.route("/api/jobs/scan", methods=["POST"])
def scan_jobs():
    try:
        # Executes our clean modular plugin scanner pipeline
        added_jobs = scanner_engine.run(limit_per_source=3)
        return jsonify({
            "success": True, 
            "addedCount": len(added_jobs), 
            "addedJobs": added_jobs
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/jobs/<string:job_id>/tailor", methods=["POST"])
def tailor_resume(job_id):
    db = read_db()
    jobs = db.get("jobs", [])
    
    target_job = None
    for j in jobs:
        if j.get("id") == job_id:
            target_job = j
            break
            
    if not target_job:
        return jsonify({"error": "Job description not found"}), 404

    # Generates custom resume components and cover letter
    latex, cover_letter, ats_score = ai_matcher.tailor_resume_and_cover_letter(
        target_job, db.get("profile", {})
    )

    target_job["tailoredResumeLaTeX"] = latex
    target_job["tailoredCoverLetter"] = cover_letter
    target_job["atsScore"] = ats_score
    target_job["status"] = "Shortlisted"

    write_db(db)
    return jsonify({"success": True, "job": target_job})

@app.route("/api/jobs/<string:job_id>/save-tailored", methods=["POST"])
def save_tailored(job_id):
    db = read_db()
    body = request.json
    
    jobs = db.get("jobs", [])
    for job in jobs:
        if job.get("id") == job_id:
            if "tailoredResumeLaTeX" in body:
                job["tailoredResumeLaTeX"] = body["tailoredResumeLaTeX"]
            if "tailoredCoverLetter" in body:
                job["tailoredCoverLetter"] = body["tailoredCoverLetter"]
            if "atsScore" in body:
                job["atsScore"] = body["atsScore"]
                
            write_db(db)
            return jsonify({"success": True, "job": job})
            
    return jsonify({"error": "Job not found"}), 404

@app.route("/api/interviews", methods=["GET"])
def get_interviews():
    db = read_db()
    return jsonify(db.get("interviews", []))

@app.route("/api/interviews", methods=["POST"])
def add_interview():
    db = read_db()
    body = request.json
    
    new_interview = {
        "id": f"int-{int(datetime.utcnow().timestamp() * 1000)}",
        "jobId": body.get("jobId"),
        "role": body.get("role"),
        "company": body.get("company"),
        "date": body.get("date"),
        "type": body.get("type", "Technical"),
        "notes": body.get("notes", ""),
        "status": "Scheduled"
    }

    db.setdefault("interviews", []).append(new_interview)
    
    # Auto-update corresponding job status to Interviewing
    jobs = db.get("jobs", [])
    for job in jobs:
        if job.get("id") == new_interview["jobId"]:
            job["status"] = "Interviewing"
            break

    write_db(db)
    return jsonify({"success": True, "interview": new_interview})

@app.route("/api/interviews/<string:int_id>/status", methods=["POST"])
def update_interview_status(int_id):
    db = read_db()
    status = request.json.get("status")
    
    interviews = db.get("interviews", [])
    for i in interviews:
        if i.get("id") == int_id:
            i["status"] = status
            
            # Auto update job status if passed/failed
            if status == "Passed":
                for job in db.get("jobs", []):
                    if job.get("id") == i["jobId"]:
                        job["status"] = "Offer"
            elif status == "Failed":
                for job in db.get("jobs", []):
                    if job.get("id") == i["jobId"]:
                        job["status"] = "Rejected"
                        
            write_db(db)
            return jsonify({"success": True, "interview": i})
            
    return jsonify({"error": "Interview not found"}), 404

# --- Serve Single Page Application Static Content ---

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    dist_dir = FRONTEND_DIST
    
    # Fail gracefully if Vite hasn't been compiled yet
    if not os.path.exists(dist_dir):
        return (
            "<h3>Vite production directory 'dist/' was not found.</h3>"
            "<p>Please build the client application by running <code>npm run build</code>, "
            "then refresh this preview.</p>"
        ), 404

    # Route real directory files if found
    file_path = os.path.join(dist_dir, path)
    if path and os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(dist_dir, path)
        
    # SPA route fallback serving the entry index
    return send_from_directory(dist_dir, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
