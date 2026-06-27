import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "backend", "data")
DATA_FILE = os.path.join(DATA_DIR, "data.json")
FRONTEND_DIST = os.path.join(REPO_ROOT, "frontend", "dist")
