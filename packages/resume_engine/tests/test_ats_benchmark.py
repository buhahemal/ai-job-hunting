"""ATS improvement benchmark — tailored resume must beat master by >= 25 points."""

import unittest

from packages.resume_engine.python.ats import estimate_ats_score
from packages.resume_engine.python.master import load_master_resume
from packages.resume_engine.python.tailor import tailor_resume_json

ATS_IMPROVEMENT_MIN_RATIO = 0.25

OBSERVABILITY_JOB = {
    'title': 'Staff SRE Platform Engineer',
    'company': 'Datadog',
    'description': (
        'Prometheus Grafana OpenTelemetry Kafka Helm ArgoCD Istio Spinnaker Tekton '
        'Crossplane Vault Consul Nomad Pulumi Temporal Airflow Flink Spark Druid ClickHouse '
        'service mesh canary deployments blue-green observability SRE incident response '
        'on-call distributed tracing eBPF Cilium reliability engineering chaos engineering '
        'capacity planning autoscaling multi-region failover splunk elk logstash fluentd vector '
        'Thanos Loki Mimir Cortex Tempo Pyroscope VictoriaMetrics'
    ),
    'extractedSkills': [
        'Prometheus',
        'Grafana',
        'OpenTelemetry',
        'Kafka',
        'Helm',
        'ArgoCD',
        'Istio',
        'Spinnaker',
        'Vault',
        'Nomad',
        'Temporal',
        'Airflow',
    ],
    'requiredSkills': ['Prometheus', 'Kafka', 'OpenTelemetry', 'Vault', 'Temporal'],
    'preferredSkills': ['Grafana', 'Helm', 'Istio', 'Spinnaker', 'Airflow'],
}


class TestAtsBenchmark(unittest.TestCase):
    def test_tailored_resume_improves_ats_by_at_least_25_points(self):
        master = load_master_resume()
        master_score = estimate_ats_score(master, OBSERVABILITY_JOB)
        tailored = tailor_resume_json(master, OBSERVABILITY_JOB)
        tailored_score = estimate_ats_score(tailored, OBSERVABILITY_JOB)

        improvement = tailored_score - master_score
        improvement_ratio = improvement / max(master_score, 1)
        self.assertLess(
            master_score,
            80,
            f'Master baseline should be below 80 for benchmark job (got {master_score})',
        )
        self.assertGreaterEqual(
            improvement_ratio,
            ATS_IMPROVEMENT_MIN_RATIO,
            f'Expected >= {ATS_IMPROVEMENT_MIN_RATIO:.0%} ATS improvement, got '
            f'{improvement_ratio:.0%} (+{improvement} points, '
            f'master={master_score}, tailored={tailored_score})',
        )


if __name__ == '__main__':
    unittest.main()
