"""Ensure scanner modules import cleanly on CI Python (3.11, eager annotations)."""

import importlib
import unittest


class TestScannerImports(unittest.TestCase):
    def test_scanner_engine_imports(self):
        module = importlib.import_module('scraper.scanner_engine')
        self.assertTrue(hasattr(module, 'JobStore'))
        self.assertTrue(hasattr(module, 'ScanInsightBuffer'))
        self.assertTrue(hasattr(module, 'ScannerEngine'))

    def test_rescan_engine_imports(self):
        module = importlib.import_module('scraper.rescan_engine')
        self.assertTrue(hasattr(module, 'RescanEngine'))

    def test_scraper_entrypoint_imports(self):
        importlib.import_module('scraper.__main__')


if __name__ == '__main__':
    unittest.main()
