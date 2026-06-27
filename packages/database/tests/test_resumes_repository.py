"""Unit tests for resume version repository."""

import unittest
from unittest.mock import MagicMock


class TestResumeRepository(unittest.TestCase):
    def test_next_tailored_version_increments(self):
        from packages.database.python.repositories.resumes import ResumeRepository

        client = MagicMock()
        table = MagicMock()
        client.table.return_value = table
        select = MagicMock()
        table.select.return_value = select
        eq = MagicMock()
        select.eq.return_value = eq
        like = MagicMock()
        eq.like.return_value = like
        like.execute.return_value = MagicMock(
            data=[{'version': 'tailored_v1'}, {'version': 'tailored_v2'}]
        )

        repo = ResumeRepository(client)
        self.assertEqual(repo.next_tailored_version('job-1'), 'tailored_v3')

    def test_ensure_master_snapshot_skips_when_exists(self):
        from packages.database.python.repositories.resumes import ResumeRepository

        client = MagicMock()
        table = MagicMock()
        client.table.return_value = table
        select = MagicMock()
        table.select.return_value = select
        eq = MagicMock()
        select.eq.return_value = eq
        is_null = MagicMock()
        eq.is_.return_value = is_null
        maybe_single = MagicMock()
        is_null.maybe_single.return_value = maybe_single
        maybe_single.execute.return_value = MagicMock(data={'version': 'master', 'id': 'x'})

        repo = ResumeRepository(client)
        row = repo.ensure_master_snapshot()
        self.assertEqual(row['version'], 'master')
        table.insert.assert_not_called()


if __name__ == '__main__':
    unittest.main()
