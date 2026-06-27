import sys
import traceback

from scraper.scanner_engine import ScannerEngine


def main() -> None:
    try:
        ScannerEngine().run()
    except Exception as exc:
        traceback.print_exc()
        print(f'Scraper pipeline crashed: {exc}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
