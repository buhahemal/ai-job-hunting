import json
import os
import tempfile
import unittest
from unittest.mock import patch

from packages.scanner_sdk.python.ats_seeds import (
    DEFAULT_SEED_PATH,
    apply_ats_seed_environment,
)

# Validated 2026-07-19 against boards-api.greenhouse.io (see design spec).
EXPECTED_GREENHOUSE_MNC = [
    'twilio',
    'gitlab',
    'okta',
    'elastic',
    'newrelic',
    'datadog',
    'coinbase',
    'mongodb',
    'rubrik',
    'sumologic',
    'cloudflare',
    'stripe',
    'cockroachlabs',
    'samsara',
    'airbnb',
    'dropbox',
    'reddit',
    'pinterest',
    'affirm',
    'grafanalabs',
]


class TestAtsSeeds(unittest.TestCase):
    def test_default_seed_file_has_validated_mnc_greenhouse_boards(self):
        payload = json.loads(DEFAULT_SEED_PATH.read_text(encoding='utf-8'))
        greenhouse = payload.get('greenhouse', [])
        self.assertGreaterEqual(len(greenhouse), 20)
        self.assertEqual(len(greenhouse), len(set(greenhouse)))
        self.assertIn('stripe', greenhouse)
        self.assertIn('openai', greenhouse)
        self.assertIn('cloudflare', greenhouse)

    def test_enabled_seed_loader_merges_without_overwriting_user_tokens(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as handle:
            json.dump({'greenhouse': ['stripe', 'exampleco'], 'lever': ['netlify']}, handle)
            handle.flush()
            with patch.dict(
                os.environ,
                {
                    'ATS_DISCOVERY_ENABLED': 'true',
                    'GREENHOUSE_BOARD_TOKENS': 'existing',
                },
                clear=True,
            ):
                apply_ats_seed_environment(handle.name)
                self.assertEqual(
                    os.environ['GREENHOUSE_BOARD_TOKENS'],
                    'existing,stripe,exampleco',
                )
                self.assertEqual(os.environ['LEVER_COMPANY_SITES'], 'netlify')

    def test_default_seeds_merge_into_empty_env(self):
        with patch.dict(
            os.environ,
            {'ATS_DISCOVERY_ENABLED': 'true'},
            clear=True,
        ):
            apply_ats_seed_environment()
            tokens = [
                t.strip()
                for t in os.environ.get('GREENHOUSE_BOARD_TOKENS', '').split(',')
                if t.strip()
            ]
            self.assertGreaterEqual(len(tokens), 20)
            self.assertIn('twilio', tokens)
            self.assertIn('gitlab', tokens)


if __name__ == '__main__':
    unittest.main()
