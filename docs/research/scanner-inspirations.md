# Scanner Inspiration Review

All external ideas pass four gates before adoption: license compatibility, ₹0 operation,
public/official data access, and measurable improvement to match quality.

| Project                                                                  | License / status   | Adopted                                                                         | Rejected / deferred                                           |
| ------------------------------------------------------------------------ | ------------------ | ------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| [Harsh-C7/JobScraper](https://github.com/Harsh-C7/JobScraper)            | MIT                | Remotive, Hacker News, explainable worldwide-remote phrases, ATS seed discovery | LinkedIn/Indeed/Glassdoor scraping; Twitter search dorking    |
| [AIHawk](https://github.com/feder-cr/jobs_applier_ai_agent_aihawk)       | AGPL-3.0, archived | Preference semantics: blacklists, experience levels, one lead per company       | Source code reuse, Selenium auto-apply, paid LLM integrations |
| [awesome-remote-job](https://github.com/lukasz-madon/awesome-remote-job) | Curated list       | Reviewed remote-company names as optional ATS board seeds                       | Treating a curated list as verified live jobs                 |
| ResumeLM / ResumeCraftr patterns                                         | Mixed              | Matched and missing ATS keyword feedback                                        | Paid model dependency or factual resume rewriting             |
| JobSync patterns                                                         | Open source        | Application-stage summary in the tracker                                        | Separate data store                                           |

## Product boundary

AI Job Hunter is a human-in-the-loop discovery, matching, tailoring, and tracking system.
It does not bulk-submit applications. New repositories should extend official APIs, RSS,
public ATS feeds, explainable matching, or dashboard usability without violating platform
terms.
