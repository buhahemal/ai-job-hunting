"""Re-exports centralized paths for the API module."""

from packages.config.python.paths import DASHBOARD_DIST, DATA_DIR, DATA_FILE, REPO_ROOT

__all__ = ['DASHBOARD_DIST', 'DATA_DIR', 'DATA_FILE', 'REPO_ROOT']

# Legacy alias used by server static file serving
FRONTEND_DIST = DASHBOARD_DIST
