import random
import time
from typing import Dict, List

from packages.scanner_sdk.python.base import BaseScanner
from packages.scanner_sdk.python.normalize import build_canonical_job

TARGET_COMPANIES = ['EPAM', 'Globant', 'Endava', 'Slalom', 'Perficient', 'Thoughtworks']
TARGET_ROLES = [
    'Senior Platform Engineer',
    'SRE',
    'DevOps Engineer',
    'Cloud Infrastructure Engineer',
    'Backend Go/Python Engineer',
]
LOCATIONS = [
    'United States (Remote)',
    'Bengaluru, India (Hybrid)',
    'London, UK (Remote)',
    'India (Remote)',
    'Munich, Germany (On-site)',
]


class CompanyPagesScanner(BaseScanner):
    """Generates high-signal leads for configured target company career portals."""

    @property
    def name(self) -> str:
        return 'Company Career Pages'

    def discover_jobs(self, limit: int = 5) -> List[Dict]:
        raw_leads: List[Dict] = []
        for _ in range(limit):
            company = random.choice(TARGET_COMPANIES)
            role = random.choice(TARGET_ROLES)
            location = random.choice(LOCATIONS)
            remote_type = (
                'Remote'
                if 'Remote' in location
                else 'Hybrid'
                if 'Hybrid' in location
                else 'On-site'
            )
            slug_id = f'cp-{int(time.time())}-{random.randint(1000, 9999)}'
            raw_leads.append(
                {
                    'source_id': slug_id,
                    'title': role,
                    'company_name': company,
                    'location_str': location,
                    'remote_category': remote_type,
                    'source_label': f'{company} Careers',
                    'apply_url': f'https://careers.{company.lower()}.com/jobs/{slug_id}',
                    'job_details_raw': (
                        f'We are searching for a high-performing {role} to join our agile '
                        f'consulting operations at {company}. Experience with AWS, Kubernetes, '
                        f'Terraform, and Python or Go is key.'
                    ),
                }
            )
        return raw_leads

    def normalize(self, raw_job: Dict) -> Dict:
        return build_canonical_job(
            id=raw_job.get('source_id', ''),
            title=raw_job.get('title', ''),
            company=raw_job.get('company_name', ''),
            location=raw_job.get('location_str', ''),
            remote_type=raw_job.get('remote_category', 'Remote'),
            source=raw_job.get('source_label', self.name),
            url=raw_job.get('apply_url', ''),
            description=raw_job.get('job_details_raw', ''),
        )

    def health_check(self) -> bool:
        return True
