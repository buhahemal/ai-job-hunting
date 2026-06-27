"""Shared default profile and database seed values."""

DEFAULT_LATEX = r"""% Master LaTeX Resume
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{top=1in, bottom=1in, left=1in, right=1in}

\begin{document}

\begin{center}
  {\Huge \textbf{Amal Singh}} \\
  amal.singh@example.com | +91-987-654-3210 | Bengaluru, India \\
  github.com/amalsingh | linkedin.com/in/amalsingh
\end{center}

\section*{Target Roles}
Senior Platform Engineer, DevOps Engineer, Backend Engineer, SRE

\section*{Technical Skills}
\textbf{Cloud & Infrastructure:} AWS (VPC, EC2, ECS, RDS, S3), GCP, Kubernetes, Docker \\
\textbf{Automation & IaC:} Terraform, Ansible, GitLab CI, GitHub Actions, Jenkins \\
\textbf{Languages & Frameworks:} Node.js, Go, Python, TypeScript, Express, Shell Scripting \\
\textbf{Observability & Databases:} Prometheus, Grafana, ELK, PostgreSQL, Redis, DynamoDB

\section*{Professional Experience}
\textbf{Lead DevOps / Platform Engineer} | CloudSolutions Inc. \hfill 2022 -- Present \\
\begin{itemize}
  \item Architected and deployed multi-region AWS containerized workloads on EKS, achieving 99.99\% infrastructure availability.
  \item Automated standard developer environment setups and deployment pipelines using Terraform and custom GitHub Actions.
  \item Implemented zero-downtime Blue/Green deployments for microservices, reducing release failure rates by 45\%.
\end{itemize}

\textbf{Senior Systems Engineer} | Global Consulting EPAM \hfill 2019 -- 2022 \\
\begin{itemize}
  \item Led migration of 15 legacy server-based monolithic applications to serverless and ECS container structures on AWS.
  \item Built dynamic monitoring and alerting dashboards in Prometheus/Grafana, resulting in 30\% faster MTTR.
  \item Managed PostgreSQL databases, implementing automated scaling, replication, and disaster recovery strategies.
\end{itemize}

\section*{Education}
\textbf{Bachelor of Technology in Computer Science} | IIT Delhi \hfill 2015 -- 2019

\end{document}"""

DEFAULT_PROFILE = {
    "fullName": "Amal Singh",
    "email": "amal.singh@example.com",
    "phone": "+91-987-654-3210",
    "website": "https://amal.dev",
    "github": "https://github.com/amalsingh",
    "linkedin": "https://linkedin.com/in/amalsingh",
    "location": "Bengaluru, India (Open to Remote / US Relocation)",
    "targetRoles": [
        "Senior Platform Engineer",
        "Platform Engineer",
        "DevOps Engineer",
        "Infrastructure Engineer",
        "SRE",
        "Backend Engineer",
    ],
    "skills": [
        "AWS",
        "Kubernetes",
        "Docker",
        "Terraform",
        "Ansible",
        "GitHub Actions",
        "GitLab CI",
        "Jenkins",
        "Node.js",
        "Go",
        "Python",
        "TypeScript",
        "Express",
        "Shell Scripting",
        "Prometheus",
        "Grafana",
        "ELK",
        "PostgreSQL",
        "Redis",
        "DynamoDB",
    ],
    "experience": [
        {
            "role": "Lead DevOps / Platform Engineer",
            "company": "CloudSolutions Inc.",
            "period": "2022 -- Present",
            "bullets": [
                "Architected and deployed multi-region AWS containerized workloads on EKS, achieving 99.99% infrastructure availability.",
                "Automated standard developer environment setups and deployment pipelines using Terraform and custom GitHub Actions.",
                "Implemented zero-downtime Blue/Green deployments for microservices, reducing release failure rates by 45%.",
            ],
        },
        {
            "role": "Senior Systems Engineer",
            "company": "Global Consulting EPAM",
            "period": "2019 -- 2022",
            "bullets": [
                "Led migration of 15 legacy server-based monolithic applications to serverless and ECS container structures on AWS.",
                "Built dynamic monitoring and alerting dashboards in Prometheus/Grafana, resulting in 30% faster MTTR.",
                "Managed PostgreSQL databases, implementing automated scaling, replication, and disaster recovery strategies.",
            ],
        },
    ],
    "education": [
        {
            "degree": "Bachelor of Technology in Computer Science",
            "school": "IIT Delhi",
            "period": "2015 -- 2019",
        }
    ],
    "projects": [
        {
            "title": "Self-Healing Kubernetes Controller",
            "description": "Designed a lightweight Custom Operator in Go that watches pod restarts and performs automated diagnostic memory dumps and service recycles.",
            "tech": ["Go", "Kubernetes API", "Docker"],
        },
        {
            "title": "Multi-Cloud Cost Management Dashboard",
            "description": "Developed a secure serverless pipeline using AWS Lambda and Node.js that crawls cost telemetry from AWS and GCP, highlighting unused resources.",
            "tech": ["Node.js", "AWS Lambda", "Terraform", "React"],
        },
    ],
    "preferences": {
        "locations": ["US", "Remote", "Europe", "India"],
        "remotePreference": "Remote",
        "companySizes": ["200-10,000", "10,000+"],
        "targetCompanies": [
            "EPAM",
            "Globant",
            "Endava",
            "Slalom",
            "Perficient",
            "Thoughtworks",
            "SoftServe",
            "Nagarro",
            "Valtech",
            "Cprime",
        ],
        "skillsKeywords": [
            "Terraform",
            "AWS",
            "Kubernetes",
            "DevOps",
            "Python",
            "Go",
            "TypeScript",
            "SRE",
            "CI/CD",
        ],
    },
    "masterResumeLaTeX": DEFAULT_LATEX,
}


def normalize_profile(profile: dict | None) -> dict:
    if not profile or not profile.get("fullName"):
        return {**DEFAULT_PROFILE, **(profile or {})}
    return {**DEFAULT_PROFILE, **profile}
