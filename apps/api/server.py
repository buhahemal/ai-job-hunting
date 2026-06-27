import os
import sys
import subprocess
from datetime import datetime

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Automatic dynamic bootstrap of python dependencies for seamless container deployment
def bootstrap_packages():
    required = ["flask", "flask-cors", "requests"]
    missing = []
    for pkg in required:
        import_name = pkg.replace("-", "_")
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
from apps.api.paths import FRONTEND_DIST
from scraper.ai_matcher import AIMatcher
from scraper.scanner_engine import ScannerEngine, create_job_store
from scraper.rescan_engine import RescanEngine
from packages.database.python.client import create_service_client, is_supabase_configured
from packages.database.python.repositories.jobs import JobRepository

app = Flask(__name__)
CORS(app)

PORT = 3000

ai_matcher = AIMatcher()
scanner_engine = ScannerEngine()
_repository: JobRepository | None = None


def get_repository() -> JobRepository:
    """Return Supabase repository or raise when data store is not configured."""
    global _repository
    if _repository is None:
        if not is_supabase_configured():
            raise RuntimeError(
                'Data not found. Configure Supabase with SUPABASE_URL and SUPABASE_SERVICE_KEY.'
            )
        _repository = JobRepository(create_service_client())
    return _repository


@app.errorhandler(RuntimeError)
def handle_runtime_error(error):
    return jsonify({"error": str(error)}), 503


@app.errorhandler(ValueError)
def handle_value_error(error):
    message = str(error)
    status = 404 if 'not found' in message.lower() else 400
    return jsonify({"error": message}), status


# --- API Endpoints ---

@app.route("/api/profile", methods=["GET"])
def get_profile():
    return jsonify(get_repository().get_profile())

@app.route("/api/profile", methods=["POST"])
def update_profile():
    profile = request.json
    get_repository().save_profile(profile)
    return jsonify({"success": True, "profile": profile})

@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    repo = get_repository()
    return jsonify({
        "jobs": repo.list_jobs(),
        "interviews": repo.list_interviews()
    })

@app.route("/api/jobs/<string:job_id>/status", methods=["POST"])
def update_job_status(job_id):
    status = request.json.get("status")
    job = get_repository().update_job_status(job_id, status)
    return jsonify({"success": True, "job": job})

@app.route("/api/jobs/<string:job_id>/notes", methods=["POST"])
def update_job_notes(job_id):
    notes = request.json.get("notes")
    job = get_repository().update_job_notes(job_id, notes)
    return jsonify({"success": True, "job": job})

@app.route("/api/jobs/add-custom", methods=["POST"])
def add_custom_job():
    body = request.json
    repo = get_repository()

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

    enriched = ai_matcher.enrich_job(new_job, repo.get_profile(), existing_jobs=repo.list_jobs())
    repo.upsert_jobs([enriched])
    return jsonify({"success": True, "job": enriched})

@app.route("/api/jobs/scan", methods=["POST"])
def scan_jobs():
    try:
        added_jobs = scanner_engine.run()
        return jsonify({
            "success": True,
            "addedCount": len(added_jobs),
            "addedJobs": added_jobs
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/scan-insights/rescan", methods=["POST"])
def rescan_scan_insights():
    """Re-score all stored scan insights against the current profile."""
    try:
        store = create_job_store()
        engine = RescanEngine(store)
        rescored_count = engine.run()
        return jsonify({"success": True, "rescoredCount": rescored_count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/scan-insights/<path:dedupe_key>/promote", methods=["POST"])
def promote_scanned_job(dedupe_key):
    """Manually promote a scanned job into Job Leads."""
    try:
        store = create_job_store()
        if hasattr(store, "promote_scanned_job_to_lead"):
            job = store.promote_scanned_job_to_lead(dedupe_key)
        else:
            return jsonify({"error": "Promotion is not supported for this store backend."}), 501
        return jsonify({"success": True, "job": job})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/jobs/<string:job_id>/tailor", methods=["POST"])
def tailor_resume(job_id):
    repo = get_repository()
    target_job = repo.get_job(job_id)
    if not target_job:
        return jsonify({"error": "Job description not found"}), 404

    profile = repo.get_profile()
    published = None
    try:
        from packages.resume_engine.python.generator import generate_tailored_resume
        from packages.resume_engine.python.publisher import publish_tailored_resume

        result = generate_tailored_resume(target_job)
        published = publish_tailored_resume(
            result,
            job_id=job_id,
            job=target_job,
            client=repo._client,
        )
        latex = result.latex
        cover_letter = result.cover_letter
        ats_score = result.ats_score
    except Exception as exc:
        print(f"[Server] Resume engine error, using matcher fallback: {exc}")
        latex, cover_letter, ats_score = ai_matcher.tailor_resume_and_cover_letter(
            target_job, profile
        )

    updated = repo.update_job_tailored(
        job_id,
        tailored_resume_latex=latex,
        tailored_cover_letter=cover_letter,
        ats_score=ats_score,
        status="Shortlisted",
    )
    payload = {"success": True, "job": updated}
    if published:
        payload["resume"] = {
            "version": published.version,
            "pdfUrl": published.pdf_url,
            "pdfCompiled": published.pdf_compiled,
        }
    return jsonify(payload)


@app.route("/api/jobs/<string:job_id>/resumes", methods=["GET"])
def list_job_resumes(job_id):
    from packages.database.python.repositories.resumes import ResumeRepository

    repo = get_repository()
    if not repo.get_job(job_id):
        return jsonify({"error": "Job not found"}), 404
    resume_repo = ResumeRepository(repo._client)
    rows = resume_repo.list_for_job(job_id)
    return jsonify(
        {
            "items": [
                {
                    "version": row.get("version"),
                    "pdfUrl": row.get("pdf_url"),
                    "atsScore": row.get("ats_score"),
                    "createdAt": row.get("created_at"),
                }
                for row in rows
            ]
        }
    )

@app.route("/api/jobs/<string:job_id>/save-tailored", methods=["POST"])
def save_tailored(job_id):
    body = request.json
    updated = get_repository().update_job_tailored(
        job_id,
        tailored_resume_latex=body.get("tailoredResumeLaTeX", ""),
        tailored_cover_letter=body.get("tailoredCoverLetter", ""),
        ats_score=body.get("atsScore"),
    )
    return jsonify({"success": True, "job": updated})

@app.route("/api/interviews", methods=["GET"])
def get_interviews():
    return jsonify(get_repository().list_interviews())

@app.route("/api/interviews", methods=["POST"])
def add_interview():
    body = request.json
    repo = get_repository()

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

    repo.add_interview(new_interview)

    if new_interview["jobId"]:
        try:
            repo.update_job_status(new_interview["jobId"], "Interviewing")
        except ValueError:
            pass

    return jsonify({"success": True, "interview": new_interview})

@app.route("/api/interviews/<string:int_id>/status", methods=["POST"])
def update_interview_status(int_id):
    status = request.json.get("status")
    repo = get_repository()
    interview = repo.update_interview_status(int_id, status)

    if status == "Passed":
        try:
            repo.update_job_status(interview["jobId"], "Offer")
        except ValueError:
            pass
    elif status == "Failed":
        try:
            repo.update_job_status(interview["jobId"], "Rejected")
        except ValueError:
            pass

    return jsonify({"success": True, "interview": interview})

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
