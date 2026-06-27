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
DASHBOARD_DIST = os.path.join(REPO_ROOT, "apps", "dashboard", "dist")
