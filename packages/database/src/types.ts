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
  skillMatchConfidence?: number;
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

export interface ScannedJobRow {
  dedupe_key: string;
  job_id: string | null;
  source: string | null;
  score: number | null;
  scanned_at: string;
  title: string | null;
  company: string | null;
  location: string | null;
  remote_type: RemoteType | null;
  canonical_role: string | null;
  primary_stack: string | null;
  seniority: string | null;
  employment_type: string | null;
  application_url: string | null;
  required_skills: string[] | null;
  preferred_skills: string[] | null;
  extracted_technologies: string[] | null;
  overall_score: number | null;
  skill_match_score: number | null;
  experience_match_score: number | null;
  ats_score: number | null;
  matched_skills: string[] | null;
  missing_skills: string[] | null;
  missing_keywords: string[] | null;
  match_explanation: string | null;
  scorer: string | null;
  promoted_to_jobs: boolean;
  scan_run_id: string | null;
  promotion_type?: string | null;
  profile_hash?: string | null;
  skill_match_confidence?: number | null;
  rescored_at?: string | null;
}

export interface ScannedJobRecord {
  dedupeKey: string;
  jobId?: string;
  source: string;
  title: string;
  company: string;
  location: string;
  remoteType: RemoteType;
  canonicalRole?: string;
  primaryStack?: string;
  seniority?: string;
  employmentType?: string;
  applicationUrl: string;
  requiredSkills: string[];
  preferredSkills: string[];
  extractedTechnologies: string[];
  overallScore: number;
  skillMatchScore?: number;
  experienceMatchScore?: number;
  atsScore?: number;
  matchedSkills: string[];
  missingSkills: string[];
  missingKeywords: string[];
  matchExplanation: string;
  scorer?: string;
  promotedToJobs: boolean;
  scanRunId?: string;
  promotionType?: string;
  profileHash?: string;
  skillMatchConfidence?: number;
  rescoredAt?: string;
  scannedAt: string;
}

export interface ScanSummaryRow {
  overall_score?: number | null;
  score?: number | null;
  source?: string | null;
  scanned_at?: string;
  promoted_to_jobs?: boolean;
  missing_skills?: string[] | null;
  scan_run_id?: string | null;
}

export interface ScanSummaryMissingSkill {
  skill: string;
  count: number;
  averageScoreWhenMissing: number;
  estimatedBandBoost: number;
}

export interface ScanSummary {
  totalScanned: number;
  promotedCount: number;
  averageScore: number;
  topSource: string | null;
  lastScanAt: string | null;
  lastRunScanned: number;
  topMissingSkills: ScanSummaryMissingSkill[];
}

export interface ScannedJobsPage {
  items: ScannedJobRecord[];
  page: number;
  limit: number;
  total: number;
}

export interface ListScannedJobsParams {
  page?: number;
  limit?: number;
  minScore?: number;
  maxScore?: number;
  source?: string;
  role?: string;
  missingSkill?: string;
  belowThresholdOnly?: boolean;
  threshold?: number;
}
