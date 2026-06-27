/**
 * Single source of truth for platform policy constants.
 *
 * Update tunable values here only. Mirror changes in `packages/database/python/constants.py`.
 * Scanner env vars (see `.env.example`) override these defaults at runtime.
 */

// --- Match scoring & promotion ---
export const MATCH_SCORE_THRESHOLD = 90;
export const MATCH_SCORE_NEAR_MISS_BAND = 10;
export const MATCH_SCORE_NEAR_MISS = MATCH_SCORE_THRESHOLD - MATCH_SCORE_NEAR_MISS_BAND;

// Enrichment gates (promotion reliability)
export const SKILL_MATCH_CONFIDENCE_MIN = 60;
export const LOW_CONFIDENCE_OVERALL_CAP = 70;
export const FULL_MATCH_SKILL_SCORE_FLOOR = 80;

// --- Scanner pipeline ---
export const SCANNER_MIN_JOBS_PER_RUN = 3;
export const SCANNER_LIMIT_PER_SOURCE = 15;
export const SCANNER_MAX_PASSES = 0;
export const SCANNER_LIMIT_STEP = 50;
export const SCANNER_MAX_LIMIT_PER_SOURCE = 2000;
export const SCANNER_MAX_EVALUATIONS = 3000;
export const SCANNER_SCAN_INSIGHT_BATCH_SIZE = 10;

// --- Dashboard / API ---
export const SCAN_INSIGHTS_PAGE_SIZE = 25;
export const SCAN_INSIGHTS_LIST_MAX = 100;
export const PROFILE_ID = 'default';
