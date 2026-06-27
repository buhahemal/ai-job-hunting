import os
import sys

# Allow `python3 scripts/scraper.py` from the repo root (CI and local runs).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.scrapers.scanner_engine import ScannerEngine

def main():
    try:
        engine = ScannerEngine()
        engine.run()
    except Exception as e:
        print(f"Scraper Pipeline crashed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
