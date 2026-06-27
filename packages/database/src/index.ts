export { createBrowserClient, readSupabaseEnvFromImportMeta } from './client.js';
export { normalizeStoredProfile } from './profile.js';
export {
  buildScanSummary,
  filterVerifiedGaps,
  jobToRow,
  matchInsightsToRow,
  normalizeSkillToken,
  rowToInterview,
  rowToJob,
  rowToScannedJob,
  scannedJobRowToJob,
  interviewToRow,
} from './mappers.js';
export { DashboardRepository } from './repository.js';
export type {
  InterviewRecord,
  InterviewRecord as Interview,
  JobRecord,
  JobRecord as Job,
  JobRow,
  JobStatus,
  ListScannedJobsParams,
  ProfileRecord,
  ProfileRecord as Profile,
  RemoteType,
  ScanSummary,
  ScanSummaryMissingSkill,
  ScanSummaryRow,
  ScannedJobRecord,
  ScannedJobRow,
  ScannedJobsPage,
} from './types.js';
