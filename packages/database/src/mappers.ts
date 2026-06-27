import type {
  InterviewRecord,
  JobMatchInsights,
  JobMatchScoreRow,
  JobRecord,
  JobRow,
  ScanSummary,
  ScanSummaryMissingSkill,
  ScanSummaryRow,
  ScannedJobRecord,
  ScannedJobRow,
} from './types.js';

function rowToMatchInsights(
  row: JobMatchScoreRow | null | undefined,
): JobMatchInsights | undefined {
  if (!row) return undefined;
  return {
    overallScore: row.overall_score ?? 0,
    skillMatchScore: row.skill_match_score ?? 0,
    experienceMatchScore: row.experience_match_score ?? 0,
    atsScore: row.ats_score ?? 0,
    salaryMatchScore: row.salary_match_score ?? 0,
    companyMatchScore: row.company_match_score ?? 0,
    locationMatchScore: row.location_match_score ?? 0,
    remoteMatchScore: row.remote_match_score ?? 0,
    confidenceScore: row.confidence_score ?? 0,
    matchedSkills: row.matched_skills ?? [],
    missingSkills: row.missing_skills ?? [],
    missingKeywords: row.missing_keywords ?? [],
    resumeSuggestions: row.resume_suggestions ?? [],
    matchExplanation: row.match_explanation ?? '',
    scorer: row.scorer ?? undefined,
  };
}

function resolveMatchRow(row: JobRow): JobMatchScoreRow | undefined {
  const payload = row.job_match_scores;
  if (!payload) return undefined;
  if (Array.isArray(payload)) return payload[0];
  return payload;
}

/** Map DB row (snake_case) to app job record (camelCase). */
export function rowToJob(row: JobRow): JobRecord {
  const insights = rowToMatchInsights(resolveMatchRow(row));
  return {
    id: row.id,
    externalId: row.external_id,
    title: row.title,
    company: row.company,
    location: row.location ?? '',
    remoteType: row.remote_type,
    source: row.source,
    url: row.url ?? '',
    description: row.description ?? '',
    postedAt: row.posted_at ?? '',
    status: row.status,
    score: row.score ?? insights?.overallScore,
    fitExplanation: row.fit_explanation ?? insights?.matchExplanation,
    extractedSkills: row.extracted_skills ?? undefined,
    salaryEstimate: row.salary_estimate ?? undefined,
    seniority: row.seniority ?? undefined,
    notes: row.notes ?? undefined,
    tailoredResumeLaTeX: row.tailored_resume_latex ?? undefined,
    tailoredCoverLetter: row.tailored_cover_letter ?? undefined,
    atsScore: row.ats_score ?? insights?.atsScore,
    employmentType: row.employment_type ?? undefined,
    requiredSkills: row.required_skills ?? undefined,
    preferredSkills: row.preferred_skills ?? undefined,
    extractedTechnologies: row.extracted_technologies ?? undefined,
    applicationUrl: row.application_url ?? row.url ?? '',
    sourcePostedAt: row.source_posted_at ?? undefined,
    scannedAt: row.scanned_at ?? undefined,
    canonicalRole: row.canonical_role ?? undefined,
    primaryStack: row.primary_stack ?? undefined,
    priority: row.priority ?? undefined,
    isDuplicate: row.is_duplicate ?? false,
    duplicateOf: row.duplicate_of ?? undefined,
    matchScorer: row.match_scorer ?? insights?.scorer,
    matchInsights: insights,
  };
}

/** Map app job record to DB upsert payload. */
export function jobToRow(job: JobRecord): JobRow {
  const insights = job.matchInsights;
  return {
    id: job.id,
    source: job.source,
    external_id: job.externalId ?? job.id,
    title: job.title,
    company: job.company,
    location: job.location || null,
    remote_type: job.remoteType,
    url: job.url || null,
    description: job.description || null,
    posted_at: job.postedAt || null,
    status: job.status,
    score: job.score ?? insights?.overallScore ?? null,
    fit_explanation: job.fitExplanation ?? insights?.matchExplanation ?? null,
    extracted_skills: job.extractedSkills ?? null,
    salary_estimate: job.salaryEstimate ?? null,
    seniority: job.seniority ?? null,
    notes: job.notes ?? null,
    tailored_resume_latex: job.tailoredResumeLaTeX ?? null,
    tailored_cover_letter: job.tailoredCoverLetter ?? null,
    ats_score: job.atsScore ?? insights?.atsScore ?? null,
    employment_type: job.employmentType ?? null,
    required_skills: job.requiredSkills ?? null,
    preferred_skills: job.preferredSkills ?? null,
    extracted_technologies: job.extractedTechnologies ?? null,
    application_url: job.applicationUrl ?? job.url ?? null,
    source_posted_at: job.sourcePostedAt ?? null,
    scanned_at: job.scannedAt ?? null,
    canonical_role: job.canonicalRole ?? null,
    primary_stack: job.primaryStack ?? null,
    priority: job.priority ?? null,
    is_duplicate: job.isDuplicate ?? false,
    duplicate_of: job.duplicateOf ?? null,
    match_scorer: job.matchScorer ?? insights?.scorer ?? null,
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

/** Map scanned_jobs DB row to app insight record. */
export function rowToScannedJob(row: ScannedJobRow): ScannedJobRecord {
  const overall = row.overall_score ?? row.score ?? 0;
  return {
    dedupeKey: row.dedupe_key,
    jobId: row.job_id ?? undefined,
    source: row.source ?? '',
    title: row.title ?? '',
    company: row.company ?? '',
    location: row.location ?? '',
    remoteType: row.remote_type ?? 'Remote',
    canonicalRole: row.canonical_role ?? undefined,
    primaryStack: row.primary_stack ?? undefined,
    seniority: row.seniority ?? undefined,
    employmentType: row.employment_type ?? undefined,
    applicationUrl: row.application_url ?? '',
    requiredSkills: row.required_skills ?? [],
    preferredSkills: row.preferred_skills ?? [],
    extractedTechnologies: row.extracted_technologies ?? [],
    overallScore: overall,
    skillMatchScore: row.skill_match_score ?? undefined,
    experienceMatchScore: row.experience_match_score ?? undefined,
    atsScore: row.ats_score ?? undefined,
    matchedSkills: row.matched_skills ?? [],
    missingSkills: row.missing_skills ?? [],
    missingKeywords: row.missing_keywords ?? [],
    matchExplanation: row.match_explanation ?? '',
    scorer: row.scorer ?? undefined,
    promotedToJobs: row.promoted_to_jobs ?? false,
    scanRunId: row.scan_run_id ?? undefined,
    scannedAt: row.scanned_at ?? '',
  };
}

function aggregateMissingSkills(
  rows: ScanSummaryRow[],
  threshold: number,
): ScanSummaryMissingSkill[] {
  const counts = new Map<string, number>();
  const scoreSum = new Map<string, number>();
  const bandBoost = new Map<string, number>();

  for (const row of rows) {
    const overall = row.overall_score ?? row.score ?? 0;
    for (const skill of row.missing_skills ?? []) {
      counts.set(skill, (counts.get(skill) ?? 0) + 1);
      scoreSum.set(skill, (scoreSum.get(skill) ?? 0) + overall);
      if (overall >= threshold - 10 && overall <= threshold) {
        bandBoost.set(skill, (bandBoost.get(skill) ?? 0) + 1);
      }
    }
  }

  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([skill, count]) => ({
      skill,
      count,
      averageScoreWhenMissing: Math.round((scoreSum.get(skill) ?? 0) / count),
      estimatedBandBoost: bandBoost.get(skill) ?? 0,
    }));
}

/** Build scan summary aggregates from scanned job rows. */
export function buildScanSummary(rows: ScanSummaryRow[], threshold = 75): ScanSummary {
  if (!rows.length) {
    return {
      totalScanned: 0,
      promotedCount: 0,
      averageScore: 0,
      topSource: null,
      lastScanAt: null,
      lastRunScanned: 0,
      topMissingSkills: [],
    };
  }

  const sourceCounts = new Map<string, number>();
  let promotedCount = 0;
  let scoreTotal = 0;
  let lastScanAt: string | null = null;
  let latestRunId: string | null = null;

  for (const row of rows) {
    const overall = row.overall_score ?? row.score ?? 0;
    scoreTotal += overall;
    if (row.promoted_to_jobs) promotedCount += 1;
    if (row.source) {
      sourceCounts.set(row.source, (sourceCounts.get(row.source) ?? 0) + 1);
    }
    if (row.scanned_at && (!lastScanAt || row.scanned_at > lastScanAt)) {
      lastScanAt = row.scanned_at;
      latestRunId = row.scan_run_id ?? null;
    }
  }

  const topSource = [...sourceCounts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? null;
  const lastRunScanned = latestRunId
    ? rows.filter((row) => row.scan_run_id === latestRunId).length
    : 0;

  return {
    totalScanned: rows.length,
    promotedCount,
    averageScore: Math.round(scoreTotal / rows.length),
    topSource,
    lastScanAt,
    lastRunScanned,
    topMissingSkills: aggregateMissingSkills(rows, threshold),
  };
}
