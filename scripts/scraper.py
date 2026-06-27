import sys
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
