import { useMemo, useRef, useState, type ReactNode } from 'react';
import { AlertCircle, ChevronDown, ChevronUp, Save, Upload } from 'lucide-react';
import {
  getProfileCompletenessIssues,
  type ProfileRecord,
  type RemoteType,
} from '@ai-job-hunter/database';
import TagListEditor from './TagListEditor';

const REMOTE_OPTIONS: Array<ProfileRecord['preferences']['remotePreference']> = [
  'Any',
  'Remote',
  'Hybrid',
  'On-site',
];

const inputClass =
  'w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none';
const labelClass = 'text-[10px] font-bold text-slate-600 dark:text-slate-400 uppercase';

interface ProfileViewProps {
  profile: ProfileRecord;
  saving: boolean;
  onChange: (profile: ProfileRecord) => void;
  onSave: (options?: { rescan?: boolean }) => Promise<void>;
  onImport: (payload: Partial<ProfileRecord>) => Promise<void>;
}

function SectionCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm space-y-4">
      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
        {title}
      </h3>
      {children}
    </div>
  );
}

export default function ProfileView({
  profile,
  saving,
  onChange,
  onSave,
  onImport,
}: ProfileViewProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [rescanOnSave, setRescanOnSave] = useState(true);
  const completenessIssues = useMemo(() => getProfileCompletenessIssues(profile), [profile]);

  const updatePreferences = (patch: Partial<ProfileRecord['preferences']>) => {
    onChange({
      ...profile,
      preferences: { ...profile.preferences, ...patch },
    });
  };

  const updateMatchSettings = (patch: Partial<ProfileRecord['matchSettings']>) => {
    onChange({
      ...profile,
      matchSettings: { ...profile.matchSettings, ...patch },
    });
  };

  const handleImportFile = async (file: File) => {
    const text = await file.text();
    const parsed = JSON.parse(text) as Partial<ProfileRecord>;
    await onImport(parsed);
  };

  return (
    <form
      className="space-y-6 max-w-4xl"
      onSubmit={(event) => {
        event.preventDefault();
        void onSave({ rescan: rescanOnSave });
      }}
    >
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          Profile & Match Settings
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Your profile drives job matching and resume generation. Import JSON, edit fields, then
          save to regenerate your master resume.
        </p>
      </div>

      {completenessIssues.length > 0 ? (
        <div className="rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/50 p-4 space-y-2">
          <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 text-xs font-semibold">
            <AlertCircle className="h-4 w-4" />
            Complete your profile for better matches and tailoring
          </div>
          <ul className="text-[11px] text-amber-900 dark:text-amber-200 list-disc pl-5 space-y-1">
            {completenessIssues.map((issue) => (
              <li key={issue.field}>{issue.message}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <SectionCard title="Import Resume / Profile JSON">
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Upload a structured JSON file (`profile.json` or `master.json` format). You can edit every
          field after import.
        </p>
        <div className="flex flex-wrap gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) void handleImportFile(file).catch(console.error);
              event.target.value = '';
            }}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-4 py-2 rounded-lg font-semibold"
          >
            <Upload className="h-4 w-4" />
            Import JSON
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Personal Information">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(
            [
              ['fullName', 'Full Name'],
              ['email', 'Email'],
              ['phone', 'Phone'],
              ['location', 'Location'],
              ['website', 'Website'],
              ['github', 'GitHub'],
              ['linkedin', 'LinkedIn'],
            ] as const
          ).map(([field, label]) => (
            <div key={field} className="space-y-1">
              <label className={labelClass}>{label}</label>
              <input
                type={field === 'email' ? 'email' : 'text'}
                value={profile[field]}
                required={field === 'fullName' || field === 'email'}
                onChange={(event) => onChange({ ...profile, [field]: event.target.value })}
                className={inputClass}
              />
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Professional Summary">
        <textarea
          value={profile.summary}
          onChange={(event) => onChange({ ...profile, summary: event.target.value })}
          rows={4}
          placeholder="Senior engineer with experience in..."
          className={inputClass}
        />
      </SectionCard>

      <SectionCard title="Target Roles">
        <TagListEditor
          label="Roles you are targeting"
          description="Used for experience matching during scans."
          items={profile.targetRoles}
          placeholder="Senior Backend Engineer"
          onChange={(targetRoles) => onChange({ ...profile, targetRoles })}
        />
      </SectionCard>

      <SectionCard title="Skills">
        <TagListEditor
          label="Core skills inventory"
          description="Primary skill list used for matching and gap analysis."
          items={profile.skills}
          placeholder="Node.js, AWS, Kubernetes"
          onChange={(skills) => onChange({ ...profile, skills })}
        />
      </SectionCard>

      <SectionCard title="Work Experience">
        <div className="space-y-4">
          {profile.experience.map((entry, index) => (
            <div
              key={`exp-${index}`}
              className="border border-slate-100 dark:border-slate-800 rounded-lg p-4 space-y-3"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {(
                  [
                    ['role', 'Role'],
                    ['company', 'Company'],
                    ['period', 'Period'],
                    ['techStack', 'Tech Stack'],
                  ] as const
                ).map(([field, label]) => (
                  <div key={field} className="space-y-1">
                    <label className={labelClass}>{label}</label>
                    <input
                      value={entry[field] ?? ''}
                      onChange={(event) => {
                        const experience = [...profile.experience];
                        experience[index] = { ...entry, [field]: event.target.value };
                        onChange({ ...profile, experience });
                      }}
                      className={inputClass}
                    />
                  </div>
                ))}
              </div>
              <TagListEditor
                label="Bullets"
                items={entry.bullets.map((bullet) =>
                  typeof bullet === 'string'
                    ? bullet
                    : `${bullet.title}: ${bullet.body}`.replace(/^: /, ''),
                )}
                placeholder="Achievement bullet"
                onChange={(bullets) => {
                  const experience = [...profile.experience];
                  experience[index] = { ...entry, bullets };
                  onChange({ ...profile, experience });
                }}
              />
              <button
                type="button"
                className="text-[10px] text-red-600 dark:text-red-400 font-semibold"
                onClick={() =>
                  onChange({
                    ...profile,
                    experience: profile.experience.filter((_, itemIndex) => itemIndex !== index),
                  })
                }
              >
                Remove experience
              </button>
            </div>
          ))}
          <button
            type="button"
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400"
            onClick={() =>
              onChange({
                ...profile,
                experience: [
                  ...profile.experience,
                  { role: '', company: '', period: '', bullets: [] },
                ],
              })
            }
          >
            + Add experience
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Education">
        <div className="space-y-4">
          {profile.education.map((entry, index) => (
            <div key={`edu-${index}`} className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {(
                [
                  ['degree', 'Degree'],
                  ['school', 'School'],
                  ['period', 'Period'],
                  ['location', 'Location'],
                ] as const
              ).map(([field, label]) => (
                <div key={field} className="space-y-1">
                  <label className={labelClass}>{label}</label>
                  <input
                    value={entry[field] ?? ''}
                    onChange={(event) => {
                      const education = [...profile.education];
                      education[index] = { ...entry, [field]: event.target.value };
                      onChange({ ...profile, education });
                    }}
                    className={inputClass}
                  />
                </div>
              ))}
            </div>
          ))}
          <button
            type="button"
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400"
            onClick={() =>
              onChange({
                ...profile,
                education: [...profile.education, { degree: '', school: '', period: '' }],
              })
            }
          >
            + Add education
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Projects">
        <div className="space-y-4">
          {profile.projects.map((entry, index) => (
            <div
              key={`proj-${index}`}
              className="border border-slate-100 dark:border-slate-800 rounded-lg p-4 space-y-3"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className={labelClass}>Title</label>
                  <input
                    value={entry.title}
                    onChange={(event) => {
                      const projects = [...profile.projects];
                      projects[index] = { ...entry, title: event.target.value };
                      onChange({ ...profile, projects });
                    }}
                    className={inputClass}
                  />
                </div>
                <div className="space-y-1 md:col-span-2">
                  <label className={labelClass}>Description</label>
                  <textarea
                    value={entry.description}
                    onChange={(event) => {
                      const projects = [...profile.projects];
                      projects[index] = { ...entry, description: event.target.value };
                      onChange({ ...profile, projects });
                    }}
                    rows={3}
                    className={inputClass}
                  />
                </div>
              </div>
              <TagListEditor
                label="Technologies"
                items={entry.tech}
                placeholder="Node.js"
                onChange={(tech) => {
                  const projects = [...profile.projects];
                  projects[index] = { ...entry, tech };
                  onChange({ ...profile, projects });
                }}
              />
            </div>
          ))}
          <button
            type="button"
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400"
            onClick={() =>
              onChange({
                ...profile,
                projects: [...profile.projects, { title: '', description: '', tech: [] }],
              })
            }
          >
            + Add project
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Match Preferences">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className={labelClass}>Remote Preference</label>
            <select
              value={profile.preferences.remotePreference}
              onChange={(event) =>
                updatePreferences({
                  remotePreference: event.target.value as RemoteType | 'Any',
                })
              }
              className={inputClass}
            >
              {REMOTE_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        </div>
        <TagListEditor
          label="Preferred locations"
          items={profile.preferences.locations}
          placeholder="Remote, India, US"
          onChange={(locations) => updatePreferences({ locations })}
        />
        <TagListEditor
          label="Target companies"
          items={profile.preferences.targetCompanies}
          placeholder="Stripe, Atlassian"
          onChange={(targetCompanies) => updatePreferences({ targetCompanies })}
        />
        <TagListEditor
          label="Company sizes"
          items={profile.preferences.companySizes}
          placeholder="50-200, 200-10,000"
          onChange={(companySizes) => updatePreferences({ companySizes })}
        />
        <TagListEditor
          label="Skill keywords for matching"
          description="Extra keywords used for gap analysis and skill corpus."
          items={profile.preferences.skillsKeywords}
          placeholder="Microservices, CI/CD"
          onChange={(skillsKeywords) => updatePreferences({ skillsKeywords })}
        />
        <TagListEditor
          label="Excluded companies"
          description="Jobs from these companies are filtered before scoring."
          items={profile.preferences.companyBlacklist}
          placeholder="Crossover, Example Corp"
          onChange={(companyBlacklist) => updatePreferences({ companyBlacklist })}
        />
        <TagListEditor
          label="Excluded job titles"
          items={profile.preferences.titleBlacklist}
          placeholder="Intern, Sales Engineer"
          onChange={(titleBlacklist) => updatePreferences({ titleBlacklist })}
        />
        <TagListEditor
          label="Excluded locations"
          items={profile.preferences.locationBlacklist}
          placeholder="US only, On-site"
          onChange={(locationBlacklist) => updatePreferences({ locationBlacklist })}
        />
        <TagListEditor
          label="Experience levels"
          items={profile.preferences.experienceLevels}
          placeholder="Senior, Lead, Staff"
          onChange={(experienceLevels) => updatePreferences({ experienceLevels })}
        />
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={profile.preferences.applyOncePerCompany}
            onChange={(event) => updatePreferences({ applyOncePerCompany: event.target.checked })}
          />
          Show only one active lead per company
        </label>
      </SectionCard>

      <SectionCard title="Advanced Match Settings">
        <button
          type="button"
          className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-400"
          onClick={() => setShowAdvanced((value) => !value)}
        >
          {showAdvanced ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          {showAdvanced ? 'Hide advanced settings' : 'Show advanced settings'}
        </button>
        {showAdvanced ? (
          <div className="space-y-4 pt-2">
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <label className={labelClass}>Minimum match score for promotion</label>
                <span className="font-bold text-indigo-600 dark:text-indigo-400">
                  {profile.matchSettings.minMatchScore}%
                </span>
              </div>
              <input
                type="range"
                min={70}
                max={95}
                value={profile.matchSettings.minMatchScore}
                onChange={(event) =>
                  updateMatchSettings({ minMatchScore: Number(event.target.value) })
                }
                className="w-full"
              />
              <p className="text-[10px] text-slate-500 dark:text-slate-400">
                Jobs must score above this threshold to promote into Job Leads. Scanner reads this
                value from your saved profile.
              </p>
            </div>
            <label className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
              <input
                type="checkbox"
                checked={rescanOnSave}
                onChange={(event) => setRescanOnSave(event.target.checked)}
              />
              Re-score Scan Insights after saving match settings
            </label>
          </div>
        ) : null}
      </SectionCard>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={saving}
          className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-6 py-2.5 rounded-lg font-bold shadow-sm transition-colors flex items-center gap-2"
        >
          <Save className="h-4 w-4" />
          {saving ? 'Saving…' : 'Save Profile & Settings'}
        </button>
      </div>
    </form>
  );
}
