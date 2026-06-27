"""Single source of truth for platform policy constants.

Update tunable values here only. Mirror changes in ``packages/database/src/constants.ts``.
Scanner env vars (see ``.env.example``) override these defaults at runtime.
"""

# --- Match scoring & promotion ---
MATCH_SCORE_THRESHOLD = 90
MATCH_SCORE_NEAR_MISS_BAND = 10
MATCH_SCORE_NEAR_MISS = MATCH_SCORE_THRESHOLD - MATCH_SCORE_NEAR_MISS_BAND

# Enrichment gates (promotion reliability)
SKILL_MATCH_CONFIDENCE_MIN = 60
LOW_CONFIDENCE_OVERALL_CAP = 70
FULL_MATCH_SKILL_SCORE_FLOOR = 80

# --- Scanner pipeline ---
SCANNER_MIN_JOBS_PER_RUN = 3
SCANNER_LIMIT_PER_SOURCE = 15
SCANNER_MAX_PASSES = 0
SCANNER_LIMIT_STEP = 50
SCANNER_MAX_LIMIT_PER_SOURCE = 2000
SCANNER_MAX_EVALUATIONS = 3000
SCANNER_SCAN_INSIGHT_BATCH_SIZE = 10

# --- Dashboard / API ---
SCAN_INSIGHTS_PAGE_SIZE = 25
SCAN_INSIGHTS_LIST_MAX = 100
PROFILE_ID = 'default'
