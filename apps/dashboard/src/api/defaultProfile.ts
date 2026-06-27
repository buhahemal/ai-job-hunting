import type { Profile } from '../types';

const DEFAULT_LATEX = `% Master LaTeX Resume
\\documentclass[11pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage{geometry}
\\geometry{top=1in, bottom=1in, left=1in, right=1in}

\\begin{document}

\\begin{center}
  {\\Huge \\textbf{Amal Singh}} \\\\
  amal.singh@example.com | +91-987-654-3210 | Bengaluru, India \\\\
  github.com/amalsingh | linkedin.com/in/amalsingh
\\end{center}

\\section*{Target Roles}
Senior Platform Engineer, DevOps Engineer, Backend Engineer, SRE

\\section*{Technical Skills}
\\textbf{Cloud & Infrastructure:} AWS, GCP, Kubernetes, Docker \\\\
\\textbf{Automation & IaC:} Terraform, Ansible, GitLab CI, GitHub Actions, Jenkins \\\\
\\textbf{Languages:} Node.js, Go, Python, TypeScript, Shell Scripting

\\end{document}`;

export const DEFAULT_PROFILE: Profile = {
  fullName: 'Amal Singh',
  email: 'amal.singh@example.com',
  phone: '+91-987-654-3210',
  website: 'https://amal.dev',
  github: 'https://github.com/amalsingh',
  linkedin: 'https://linkedin.com/in/amalsingh',
  location: 'Bengaluru, India (Open to Remote / US Relocation)',
  targetRoles: [
    'Senior Platform Engineer',
    'Platform Engineer',
    'DevOps Engineer',
    'Infrastructure Engineer',
    'SRE',
    'Backend Engineer',
  ],
  skills: [
    'AWS',
    'Kubernetes',
    'Docker',
    'Terraform',
    'Ansible',
    'GitHub Actions',
    'GitLab CI',
    'Jenkins',
    'Node.js',
    'Go',
    'Python',
    'TypeScript',
    'Express',
    'Shell Scripting',
    'Prometheus',
    'Grafana',
    'ELK',
    'PostgreSQL',
    'Redis',
    'DynamoDB',
  ],
  experience: [
    {
      role: 'Lead DevOps / Platform Engineer',
      company: 'CloudSolutions Inc.',
      period: '2022 -- Present',
      bullets: [
        'Architected and deployed multi-region AWS containerized workloads on EKS.',
        'Automated deployment pipelines using Terraform and GitHub Actions.',
        'Implemented zero-downtime Blue/Green deployments for microservices.',
      ],
    },
    {
      role: 'Senior Systems Engineer',
      company: 'Global Consulting EPAM',
      period: '2019 -- 2022',
      bullets: [
        'Led migration of legacy applications to serverless and ECS on AWS.',
        'Built monitoring dashboards in Prometheus/Grafana.',
        'Managed PostgreSQL databases with automated scaling and DR.',
      ],
    },
  ],
  education: [
    {
      degree: 'Bachelor of Technology in Computer Science',
      school: 'IIT Delhi',
      period: '2015 -- 2019',
    },
  ],
  projects: [
    {
      title: 'Self-Healing Kubernetes Controller',
      description: 'Custom Go operator for automated pod diagnostics and recovery.',
      tech: ['Go', 'Kubernetes API', 'Docker'],
    },
  ],
  preferences: {
    locations: ['US', 'Remote', 'Europe', 'India'],
    remotePreference: 'Remote',
    companySizes: ['200-10,000', '10,000+'],
    targetCompanies: ['EPAM', 'Globant', 'Endava', 'Slalom', 'Perficient', 'Thoughtworks'],
    skillsKeywords: ['Terraform', 'AWS', 'Kubernetes', 'DevOps', 'Python', 'Go', 'SRE'],
  },
  masterResumeLaTeX: DEFAULT_LATEX,
};

export function normalizeProfile(profile?: Partial<Profile> | null): Profile {
  if (!profile?.fullName) {
    return {
      ...DEFAULT_PROFILE,
      ...profile,
      skills: profile?.skills?.length ? profile.skills : DEFAULT_PROFILE.skills,
      targetRoles: profile?.targetRoles?.length ? profile.targetRoles : DEFAULT_PROFILE.targetRoles,
      experience: profile?.experience?.length ? profile.experience : DEFAULT_PROFILE.experience,
      education: profile?.education?.length ? profile.education : DEFAULT_PROFILE.education,
      projects: profile?.projects?.length ? profile.projects : DEFAULT_PROFILE.projects,
      preferences: {
        ...DEFAULT_PROFILE.preferences,
        ...profile?.preferences,
      },
      masterResumeLaTeX: profile?.masterResumeLaTeX || DEFAULT_PROFILE.masterResumeLaTeX,
    };
  }

  return {
    ...DEFAULT_PROFILE,
    ...profile,
    skills: profile.skills ?? DEFAULT_PROFILE.skills,
    targetRoles: profile.targetRoles ?? DEFAULT_PROFILE.targetRoles,
    experience: profile.experience ?? DEFAULT_PROFILE.experience,
    education: profile.education ?? DEFAULT_PROFILE.education,
    projects: profile.projects ?? DEFAULT_PROFILE.projects,
    preferences: {
      ...DEFAULT_PROFILE.preferences,
      ...profile.preferences,
    },
    masterResumeLaTeX: profile.masterResumeLaTeX ?? DEFAULT_PROFILE.masterResumeLaTeX,
  };
}

export function getProfileInitials(fullName?: string): string {
  if (!fullName?.trim()) return '?';
  return fullName
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}
