import type { InterviewRecord, JobRecord, JobRow } from './types.js';

/** Map DB row (snake_case) to app job record (camelCase). */
export function rowToJob(row: JobRow): JobRecord {
  return {
    id: row.id,
    title: row.title,
    company: row.company,
    location: row.location ?? '',
    remoteType: row.remote_type,
    source: row.source,
    url: row.url ?? '',
    description: row.description ?? '',
    postedAt: row.posted_at ?? '',
    status: row.status,
    score: row.score ?? undefined,
    fitExplanation: row.fit_explanation ?? undefined,
    extractedSkills: row.extracted_skills ?? undefined,
    salaryEstimate: row.salary_estimate ?? undefined,
    seniority: row.seniority ?? undefined,
    notes: row.notes ?? undefined,
    tailoredResumeLaTeX: row.tailored_resume_latex ?? undefined,
    tailoredCoverLetter: row.tailored_cover_letter ?? undefined,
    atsScore: row.ats_score ?? undefined,
  };
}

/** Map app job record to DB upsert payload. */
export function jobToRow(job: JobRecord): JobRow {
  return {
    id: job.id,
    source: job.source,
    external_id: job.id,
    title: job.title,
    company: job.company,
    location: job.location || null,
    remote_type: job.remoteType,
    url: job.url || null,
    description: job.description || null,
    posted_at: job.postedAt || null,
    status: job.status,
    score: job.score ?? null,
    fit_explanation: job.fitExplanation ?? null,
    extracted_skills: job.extractedSkills ?? null,
    salary_estimate: job.salaryEstimate ?? null,
    seniority: job.seniority ?? null,
    notes: job.notes ?? null,
    tailored_resume_latex: job.tailoredResumeLaTeX ?? null,
    tailored_cover_letter: job.tailoredCoverLetter ?? null,
    ats_score: job.atsScore ?? null,
  };
}

interface InterviewRow {
  id: string;
  job_id: string;
  role: string;
  company: string;
  interview_date: string;
  interview_type: string;
  notes: string;
  status: InterviewRecord['status'];
}

export function rowToInterview(row: InterviewRow): InterviewRecord {
  return {
    id: row.id,
    jobId: row.job_id,
    role: row.role,
    company: row.company,
    date: row.interview_date,
    type: row.interview_type,
    notes: row.notes,
    status: row.status,
  };
}

export function interviewToRow(interview: InterviewRecord): InterviewRow {
  return {
    id: interview.id,
    job_id: interview.jobId,
    role: interview.role,
    company: interview.company,
    interview_date: interview.date,
    interview_type: interview.type,
    notes: interview.notes,
    status: interview.status,
  };
}
