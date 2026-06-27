export interface Profile {
  fullName: string;
  email: string;
  phone: string;
  website: string;
  github: string;
  linkedin: string;
  location: string;
  targetRoles: string[];
  skills: string[];
  experience: {
    role: string;
    company: string;
    period: string;
    bullets: string[];
  }[];
  education: {
    degree: string;
    school: string;
    period: string;
  }[];
  projects: {
    title: string;
    description: string;
    tech: string[];
  }[];
  preferences: {
    locations: string[];
    remotePreference: 'Remote' | 'Hybrid' | 'On-site' | 'Any';
    companySizes: string[];
    targetCompanies: string[];
    skillsKeywords: string[];
  };
  masterResumeLaTeX: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  remoteType: 'Remote' | 'Hybrid' | 'On-site';
  source: string;
  url: string;
  description: string;
  postedAt: string;
  status:
    | 'New'
    | 'Shortlisted'
    | 'Applied'
    | 'Interviewing'
    | 'Offer'
    | 'Rejected'
    | 'Accepted'
    | 'Ignored';
  notes?: string;
  score?: number;
  fitExplanation?: string;
  extractedSkills?: string[];
  salaryEstimate?: string;
  seniority?: string;
  tailoredResumeLaTeX?: string;
  tailoredCoverLetter?: string;
  atsScore?: number;
}

export interface Interview {
  id: string;
  jobId: string;
  role: string;
  company: string;
  date: string;
  type: string;
  notes: string;
  status: 'Scheduled' | 'Completed' | 'Cancelled' | 'Passed' | 'Failed';
}
