"""Unit tests for resume publish pipeline (mocked storage)."""

import unittest
from unittest.mock import MagicMock, patch

from packages.resume_engine.python.generator import generate_tailored_resume


class TestPublisher(unittest.TestCase):
    JOB = {
        'id': 'gh-123',
        'title': 'Senior Platform Engineer',
        'company': 'Acme',
        'description': 'Kubernetes AWS Node.js Terraform platform microservices',
        'extractedSkills': ['Kubernetes', 'AWS', 'Node.js'],
    }

    @patch('packages.resume_engine.python.publisher.upload_resume_pdf', return_value='https://example.com/resume.pdf')
    @patch('packages.resume_engine.python.publisher.is_storage_configured', return_value=True)
    @patch('packages.resume_engine.python.publisher.pdflatex_available', return_value=False)
    def test_publish_without_pdflatex_still_versions(self, _avail, _storage, _upload):
        from packages.resume_engine.python.publisher import publish_tailored_resume

        client = MagicMock()
        insert_execute = MagicMock(
            side_effect=[
                MagicMock(data=[{'version': 'master', 'pdf_url': None}]),
                MagicMock(data=[{'version': 'tailored_v1', 'pdf_url': ''}]),
            ]
        )
        insert_chain = MagicMock()
        insert_chain.execute = insert_execute

        master_execute = MagicMock(data=None)
        master_maybe = MagicMock()
        master_maybe.execute.return_value = master_execute
        master_is = MagicMock()
        master_is.maybe_single.return_value = master_maybe
        master_eq = MagicMock()
        master_eq.is_.return_value = master_is
        master_select = MagicMock()
        master_select.eq.return_value = master_eq

        version_execute = MagicMock(data=[])
        version_like = MagicMock()
        version_like.execute.return_value = version_execute
        version_eq = MagicMock()
        version_eq.like.return_value = version_like

        table = MagicMock()
        table.insert.return_value = insert_chain
        table.select.return_value = master_select
        master_select.eq.side_effect = [master_eq, version_eq]
        client.table.return_value = table

        result = generate_tailored_resume(self.JOB)
        published = publish_tailored_resume(
            result,
            job_id='gh-123',
            job=self.JOB,
            client=client,
        )

        self.assertEqual(published.version, 'tailored_v1')
        self.assertFalse(published.pdf_compiled)
        self.assertEqual(table.insert.call_count, 2)
        insert_execute.assert_called()


if __name__ == '__main__':
    unittest.main()
