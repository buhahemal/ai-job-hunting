import { Filter, Search } from 'lucide-react';

export interface JobFilterState {
  searchQuery: string;
  statusFilter: string;
  scoreFilter: string;
  remoteFilter: string;
  seniorityFilter: string;
  sourceFilter: string;
  roleFilter: string;
  priorityFilter: string;
  hideDuplicates: boolean;
}

interface JobFiltersProps {
  filters: JobFilterState;
  sources: string[];
  roles: string[];
  onChange: (patch: Partial<JobFilterState>) => void;
}

export default function JobFilters({ filters, sources, roles, onChange }: JobFiltersProps) {
  return (
    <div className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex flex-wrap gap-4 items-center justify-between">
      <div className="flex-1 min-w-[240px] relative">
        <Search className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
        <input
          type="text"
          placeholder="Search roles, companies, skills, stack..."
          value={filters.searchQuery}
          onChange={(e) => onChange({ searchQuery: e.target.value })}
          className="w-full bg-slate-50 pl-9 pr-4 py-2 rounded-lg text-xs border border-slate-200/80 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
        />
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5">
          <Filter className="h-3.5 w-3.5 text-slate-400" />
          <span className="text-[11px] font-bold text-slate-500 uppercase">Filters:</span>
        </div>

        <select
          value={filters.statusFilter}
          onChange={(e) => onChange({ statusFilter: e.target.value })}
          className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs"
        >
          <option value="All">All Statuses</option>
          <option value="New">New</option>
          <option value="Shortlisted">Shortlisted</option>
          <option value="Applied">Applied</option>
          <option value="Interviewing">Interviewing</option>
          <option value="Offer">Offer</option>
          <option value="Rejected">Rejected</option>
        </select>

        <select
          value={filters.scoreFilter}
          onChange={(e) => onChange({ scoreFilter: e.target.value })}
          className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs"
        >
          <option value="All">All Match Levels</option>
          <option value="Excellent">Excellent (&gt;85%)</option>
          <option value="Good">Good (70-85%)</option>
          <option value="Fair">Fair (&lt;70%)</option>
        </select>

        <select
          value={filters.remoteFilter}
          onChange={(e) => onChange({ remoteFilter: e.target.value })}
          className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs"
        >
          <option value="All">All Remote</option>
          <option value="Remote">Remote</option>
          <option value="Hybrid">Hybrid</option>
          <option value="On-site">On-site</option>
        </select>

        <select
          value={filters.seniorityFilter}
          onChange={(e) => onChange({ seniorityFilter: e.target.value })}
          className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs"
        >
          <option value="All">All Seniority</option>
          <option value="Senior">Senior</option>
          <option value="Mid-level">Mid-level</option>
          <option value="Junior">Junior</option>
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
          value={filters.priorityFilter}
          onChange={(e) => onChange({ priorityFilter: e.target.value })}
          className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs"
        >
          <option value="All">All Priority</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>

        <label className="flex items-center gap-1.5 text-[11px] text-slate-600">
          <input
            type="checkbox"
            checked={filters.hideDuplicates}
            onChange={(e) => onChange({ hideDuplicates: e.target.checked })}
            className="rounded border-slate-300"
          />
          Hide duplicates
        </label>
      </div>
    </div>
  );
}

export function filterJobs<
  T extends {
    title: string;
    company: string;
    status: string;
    score?: number;
    remoteType?: string;
    seniority?: string;
    source?: string;
    canonicalRole?: string;
    priority?: string;
    isDuplicate?: boolean;
    extractedSkills?: string[];
    primaryStack?: string;
    extractedTechnologies?: string[];
  },
>(jobs: T[], filters: JobFilterState): T[] {
  return jobs.filter((job) => {
    const haystack = [
      job.title,
      job.company,
      job.primaryStack,
      ...(job.extractedSkills ?? []),
      ...(job.extractedTechnologies ?? []),
    ]
      .join(' ')
      .toLowerCase();

    const matchesSearch =
      !filters.searchQuery ||
      haystack.includes(filters.searchQuery.toLowerCase()) ||
      job.title.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
      job.company.toLowerCase().includes(filters.searchQuery.toLowerCase());

    const matchesStatus = filters.statusFilter === 'All' || job.status === filters.statusFilter;

    let matchesScore = true;
    if (filters.scoreFilter === 'Excellent') matchesScore = (job.score || 0) >= 85;
    else if (filters.scoreFilter === 'Good')
      matchesScore = (job.score || 0) >= 70 && (job.score || 0) < 85;
    else if (filters.scoreFilter === 'Fair') matchesScore = (job.score || 0) < 70;

    const matchesRemote = filters.remoteFilter === 'All' || job.remoteType === filters.remoteFilter;
    const matchesSeniority =
      filters.seniorityFilter === 'All' || job.seniority === filters.seniorityFilter;
    const matchesSource = filters.sourceFilter === 'All' || job.source === filters.sourceFilter;
    const matchesRole = filters.roleFilter === 'All' || job.canonicalRole === filters.roleFilter;
    const matchesPriority =
      filters.priorityFilter === 'All' || job.priority === filters.priorityFilter;
    const matchesDuplicate = !filters.hideDuplicates || !job.isDuplicate;

    return (
      matchesSearch &&
      matchesStatus &&
      matchesScore &&
      matchesRemote &&
      matchesSeniority &&
      matchesSource &&
      matchesRole &&
      matchesPriority &&
      matchesDuplicate
    );
  });
}
