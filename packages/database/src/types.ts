export type JobStatus =
  | 'New'
  | 'Shortlisted'
  | 'Applied'
  | 'Interviewing'
  | 'Offer'
  | 'Rejected'
  | 'Accepted'
  | 'Ignored';

export type RemoteType = 'Remote' | 'Hybrid' | 'On-site';

export interface JobRow {
  id: string;
  source: string;
  external_id: string;
  title: string;
  company: string;
  location: string | null;
  remote_type: RemoteType;
  url: string | null;
  description: string | null;
  posted_at: string | null;
  status: JobStatus;
  score: number | null;
  fit_explanation: string | null;
  extracted_skills: string[] | null;
  salary_estimate: string | null;
  seniority: string | null;
  notes: string | null;
  tailored_resume_latex: string | null;
  tailored_cover_letter: string | null;
  ats_score: number | null;
}

export interface JobRecord {
  id: string;
  title: string;
  company: string;
  location: string;
  remoteType: RemoteType;
  source: string;
  url: string;
  description: string;
  postedAt: string;
  status: JobStatus;
  score?: number;
  fitExplanation?: string;
  extractedSkills?: string[];
  salaryEstimate?: string;
  seniority?: string;
  notes?: string;
  tailoredResumeLaTeX?: string;
  tailoredCoverLetter?: string;
  atsScore?: number;
}

export interface InterviewRecord {
  id: string;
  jobId: string;
  role: string;
  company: string;
  date: string;
  type: string;
  notes: string;
  status: 'Scheduled' | 'Completed' | 'Cancelled' | 'Passed' | 'Failed';
}

export interface ProfileRecord {
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
    remotePreference: RemoteType | 'Any';
    companySizes: string[];
    targetCompanies: string[];
    skillsKeywords: string[];
  };
  masterResumeLaTeX: string;
}
