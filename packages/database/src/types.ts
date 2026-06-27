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
export type JobPriority = 'High' | 'Medium' | 'Low';

export interface JobMatchInsights {
  overallScore: number;
  skillMatchScore: number;
  experienceMatchScore: number;
  atsScore: number;
  salaryMatchScore: number;
  companyMatchScore: number;
  locationMatchScore: number;
  remoteMatchScore: number;
  confidenceScore: number;
  matchedSkills: string[];
  missingSkills: string[];
  missingKeywords: string[];
  resumeSuggestions: string[];
  matchExplanation: string;
  scorer?: string;
}

export interface JobMatchScoreRow {
  job_id: string;
  overall_score: number;
  skill_match_score: number;
  experience_match_score: number;
  ats_score: number;
  salary_match_score: number;
  company_match_score: number;
  location_match_score: number;
  remote_match_score: number;
  confidence_score: number;
  matched_skills: string[] | null;
  missing_skills: string[] | null;
  missing_keywords: string[] | null;
  resume_suggestions: string[] | null;
  match_explanation: string | null;
  scorer: string | null;
}

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
  employment_type: string | null;
  required_skills: string[] | null;
  preferred_skills: string[] | null;
  extracted_technologies: string[] | null;
  application_url: string | null;
  source_posted_at: string | null;
  scanned_at: string | null;
  canonical_role: string | null;
  primary_stack: string | null;
  priority: JobPriority | null;
  is_duplicate: boolean | null;
  duplicate_of: string | null;
  match_scorer: string | null;
  job_match_scores?: JobMatchScoreRow | JobMatchScoreRow[] | null;
}

export interface JobRecord {
  id: string;
  externalId?: string;
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
  employmentType?: string;
  requiredSkills?: string[];
  preferredSkills?: string[];
  extractedTechnologies?: string[];
  applicationUrl?: string;
  sourcePostedAt?: string;
  scannedAt?: string;
  canonicalRole?: string;
  primaryStack?: string;
  priority?: JobPriority;
  isDuplicate?: boolean;
  duplicateOf?: string;
  matchScorer?: string;
  matchInsights?: JobMatchInsights;
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
