import { Filter } from 'lucide-react';

export interface ScanInsightsFilterState {
  scoreBand: string;
  sourceFilter: string;
  roleFilter: string;
  seniorityFilter: string;
  missingSkillFilter: string;
  belowThresholdOnly: boolean;
}

interface ScanInsightsFiltersProps {
  filters: ScanInsightsFilterState;
  sources: string[];
  roles: string[];
  missingSkills: string[];
  onChange: (patch: Partial<ScanInsightsFilterState>) => void;
}

export default function ScanInsightsFilters({
  filters,
  sources,
  roles,
  missingSkills,
  onChange,
}: ScanInsightsFiltersProps) {
  return (
    <div className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex flex-wrap gap-4 items-center">
      <div className="flex items-center gap-1.5">
        <Filter className="h-3.5 w-3.5 text-slate-400" />
        <span className="text-[11px] font-bold text-slate-500 uppercase">Filters:</span>
      </div>

      <select
        value={filters.scoreBand}
        onChange={(e) => onChange({ scoreBand: e.target.value })}
        className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs"
      >
        <option value="All">All Score Bands</option>
        <option value="0-50">0–50%</option>
        <option value="50-65">50–65%</option>
        <option value="65-75">65–75%</option>
        <option value="75+">75%+</option>
      </select>

      <select
        value={filters.sourceFilter}
        onChange={(e) => onChange({ sourceFilter: e.target.value })}
        className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs"
      >
        <option value="All">All Sources</option>
        {sources.map((source) => (
          <option key={source} value={source}>
            {source}
          </option>
        ))}
      </select>

      <select
        value={filters.roleFilter}
        onChange={(e) => onChange({ roleFilter: e.target.value })}
        className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs"
      >
        <option value="All">All Roles</option>
        {roles.map((role) => (
          <option key={role} value={role}>
            {role}
          </option>
        ))}
      </select>

      <select
        value={filters.seniorityFilter}
        onChange={(e) => onChange({ seniorityFilter: e.target.value })}
        className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs"
      >
        <option value="All">All Seniority</option>
        <option value="Junior">Junior</option>
        <option value="Mid-level">Mid-level</option>
        <option value="Senior">Senior</option>
        <option value="Staff">Staff</option>
      </select>

      <select
        value={filters.missingSkillFilter}
        onChange={(e) => onChange({ missingSkillFilter: e.target.value })}
        className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs min-w-[140px]"
      >
        <option value="All">Any Missing Skill</option>
        {missingSkills.map((skill) => (
          <option key={skill} value={skill}>
            Missing: {skill}
          </option>
        ))}
      </select>

      <label className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer">
        <input
          type="checkbox"
          checked={filters.belowThresholdOnly}
          onChange={(e) => onChange({ belowThresholdOnly: e.target.checked })}
          className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
        />
        Below 75% only
      </label>
    </div>
  );
}

export function scoreBandToRange(band: string): { minScore?: number; maxScore?: number } {
  switch (band) {
    case '0-50':
      return { minScore: 0, maxScore: 50 };
    case '50-65':
      return { minScore: 50, maxScore: 65 };
    case '65-75':
      return { minScore: 65, maxScore: 75 };
    case '75+':
      return { minScore: 75 };
    default:
      return {};
  }
}
