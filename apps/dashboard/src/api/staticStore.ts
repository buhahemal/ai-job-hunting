import type { Job, Profile } from '../types';

export function heuristicScore(
  job: Partial<Job>,
  profile: Profile,
): Pick<Job, 'score' | 'extractedSkills' | 'fitExplanation' | 'salaryEstimate' | 'seniority'> {
  let score = 50;
  const matchedSkills: string[] = [];
  const jobText = `${job.title ?? ''} ${job.description ?? ''}`.toLowerCase();

  for (const skill of profile.skills ?? []) {
    if (jobText.includes(skill.toLowerCase())) {
      matchedSkills.push(skill);
    }
  }

  score += Math.round((matchedSkills.length / Math.max(1, (profile.skills ?? []).length)) * 30);

  const remotePreference = profile.preferences?.remotePreference ?? 'Any';
  const jobRemote = job.remoteType ?? 'Hybrid';

  if (jobRemote === 'Remote' && ['Remote', 'Any'].includes(remotePreference)) {
    score += 15;
  } else if (jobRemote === 'Hybrid' && ['Hybrid', 'Any'].includes(remotePreference)) {
    score += 10;
  }

  const company = (job.company ?? '').toLowerCase();
  if (
    (profile.preferences?.targetCompanies ?? []).some((target) =>
      company.includes(target.toLowerCase()),
    )
  ) {
    score += 10;
  }

  score = Math.min(100, Math.max(0, score));

  return {
    score,
    extractedSkills: matchedSkills,
    fitExplanation: `Heuristic alignment score of ${score}% based on matching ${matchedSkills.length} primary skills.`,
    salaryEstimate: 'Not Specified',
    seniority: (job.title ?? '').toLowerCase().includes('senior') ? 'Senior' : 'Mid-level',
  };
}

export function tailorFallback(
  job: Job,
  profile: Profile,
): Pick<Job, 'tailoredResumeLaTeX' | 'tailoredCoverLetter' | 'atsScore' | 'status'> {
  const masterLatex = profile.masterResumeLaTeX ?? '';
  const tailoredLatex = masterLatex.replace(
    '\\section*{Target Roles}',
    `\\section*{Target Roles - Tailored for ${job.title} at ${job.company}}`,
  );
  const coverLetter = `Dear Hiring Team at ${job.company},

I am writing to express my strong interest in the ${job.title} position. With my background in DevOps, platform engineering, and AWS systems, I am confident I am a strong fit.

Sincerely,
${profile.fullName ?? 'Candidate'}`;

  return {
    tailoredResumeLaTeX: tailoredLatex,
    tailoredCoverLetter: coverLetter,
    atsScore: 75,
    status: 'Shortlisted',
  };
}
