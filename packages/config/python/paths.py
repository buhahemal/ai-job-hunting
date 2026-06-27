"""Centralized repository path resolution for Python modules."""

from __future__ import annotations

import os

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

DATA_DIR = os.path.join(REPO_ROOT, "apps", "api", "data")
DATA_FILE = os.path.join(DATA_DIR, "data.json")
PROFILE_JSON = os.path.join(DATA_DIR, "profile.json")
MASTER_RESUME_TEX = os.path.join(DATA_DIR, "master-resume.tex")
MASTER_RESUME_PDF = os.path.join(DATA_DIR, "HemalBuha-Resume.pdf")
RESUME_DIR = os.path.join(DATA_DIR, "resume")
MASTER_RESUME_JSON = os.path.join(RESUME_DIR, "master.json")
RESUME_TEMPLATE_TEX = os.path.join(RESUME_DIR, "template.tex")
RESUME_GENERATED_DIR = os.path.join(RESUME_DIR, "generated")
DASHBOARD_DIST = os.path.join(REPO_ROOT, "apps", "dashboard", "dist")
