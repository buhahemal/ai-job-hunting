import json
import os
import tempfile
import unittest
from unittest.mock import patch

from packages.scanner_sdk.python.ats_seeds import apply_ats_seed_environment


class TestAtsSeeds(unittest.TestCase):
    def test_enabled_seed_loader_merges_without_overwriting_user_tokens(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as handle:
            json.dump({'greenhouse': ['stripe', 'hashicorp'], 'lever': ['netlify']}, handle)
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
                    'existing,stripe,hashicorp',
                )
                self.assertEqual(os.environ['LEVER_COMPANY_SITES'], 'netlify')


if __name__ == '__main__':
    unittest.main()
