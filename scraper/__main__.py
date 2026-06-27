import sys

from scraper.scrapers.scanner_engine import ScannerEngine


def main() -> None:
    try:
        ScannerEngine().run()
    except Exception as exc:
        print(f"Scraper pipeline crashed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
