import unittest

from packages.scanner_sdk.python.normalize import build_canonical_job, infer_remote_type, strip_html
from packages.scanner_sdk.python.registry import get_registered_scanners


class TestScannerSdk(unittest.TestCase):
    def test_build_canonical_job(self):
        job = build_canonical_job(
            id='test-1',
            title='Engineer',
            company='Acme',
            location='Remote',
            remote_type='Remote',
            source='Test',
            url='https://example.com',
            description='Build things',
        )
        self.assertEqual(job['id'], 'test-1')
        self.assertEqual(job['status'], 'New')

    def test_strip_html(self):
        self.assertEqual(strip_html('<p>Hello</p>'), 'Hello')

    def test_infer_remote_type(self):
        self.assertEqual(infer_remote_type(True, 'NYC'), 'Remote')
        self.assertEqual(infer_remote_type(None, 'Hybrid NYC'), 'Hybrid')

    def test_registry_returns_scanners(self):
        scanners = get_registered_scanners()
        self.assertGreaterEqual(len(scanners), 3)
        names = {scanner.name for scanner in scanners}
        self.assertIn('Arbeitnow', names)
        self.assertIn('Greenhouse', names)


if __name__ == '__main__':
    unittest.main()
