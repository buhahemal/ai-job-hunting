import { useState } from 'react';
import { Filter, Search, SlidersHorizontal, X, RotateCcw } from 'lucide-react';

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

export const DEFAULT_JOB_FILTERS: JobFilterState = {
  searchQuery: '',
  statusFilter: 'All',
  scoreFilter: 'All',
  remoteFilter: 'All',
  seniorityFilter: 'All',
  sourceFilter: 'All',
  roleFilter: 'All',
  priorityFilter: 'All',
  hideDuplicates: false,
};

interface JobFiltersProps {
  filters: JobFilterState;
  sources: string[];
  roles: string[];
  onChange: (patch: Partial<JobFilterState>) => void;
}

export default function JobFilters({ filters, sources, roles, onChange }: JobFiltersProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const activeFilterCount = [
    filters.statusFilter !== 'All',
    filters.scoreFilter !== 'All',
    filters.remoteFilter !== 'All',
    filters.seniorityFilter !== 'All',
    filters.sourceFilter !== 'All',
    filters.roleFilter !== 'All',
    filters.priorityFilter !== 'All',
    filters.hideDuplicates,
  ].filter(Boolean).length;

  const handleReset = () => {
    onChange(DEFAULT_JOB_FILTERS);
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-3 md:p-4 rounded-xl border border-slate-200/80 dark:border-slate-700 shadow-sm space-y-3">
      {/* Search Input & Mobile Filter Toggle Header */}
      <div className="flex items-center gap-2.5">
        <div className="flex-1 relative">
          <Search className="h-4 w-4 text-slate-400 dark:text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search roles, companies, skills, tech stack..."
            value={filters.searchQuery}
            onChange={(e) => onChange({ searchQuery: e.target.value })}
            className="w-full bg-slate-50/80 dark:bg-slate-800 pl-9 pr-8 py-2 rounded-lg text-xs md:text-sm border border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 focus:outline-none transition-all"
          />
          {filters.searchQuery && (
            <button
              onClick={() => onChange({ searchQuery: '' })}
              className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-400"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Mobile Toggle Button */}
        <button
          type="button"
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden flex items-center gap-1.5 px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg transition-colors border border-slate-200 dark:border-slate-700"
        >
          <SlidersHorizontal className="h-3.5 w-3.5" />
          <span>Filters</span>
          {activeFilterCount > 0 && (
            <span className="bg-indigo-600 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">
              {activeFilterCount}
            </span>
          )}
        </button>

        {/* Desktop Reset Button */}
        {(activeFilterCount > 0 || filters.searchQuery) && (
          <button
            type="button"
            onClick={handleReset}
            className="hidden md:flex items-center gap-1 text-[11px] font-semibold text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors px-2 py-1.5 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800"
          >
            <RotateCcw className="h-3 w-3" />
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Filter Dropdowns Grid (Always visible on desktop md+, collapsible on mobile) */}
      <div
        className={`${
          mobileOpen ? 'block' : 'hidden'
        } md:flex flex-wrap items-center gap-2.5 pt-2 md:pt-0 border-t md:border-0 border-slate-100 dark:border-slate-800 animate-slide-up`}
      >
        <div className="hidden md:flex items-center gap-1.5 text-slate-400 dark:text-slate-500 pr-1">
          <Filter className="h-3.5 w-3.5" />
          <span className="text-[10px] font-bold uppercase tracking-wider">Filter by:</span>
        </div>

        <select
          value={filters.statusFilter}
          onChange={(e) => onChange({ statusFilter: e.target.value })}
          className="w-full md:w-auto bg-slate-50/90 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:ring-1 focus:ring-indigo-500 focus:outline-none"
        >
          <option value="All">Status: All Active Leads</option>
          <option value="New">Status: New</option>
          <option value="Shortlisted">Status: Shortlisted</option>
          <option value="Applied">Status: Applied</option>
          <option value="Interviewing">Status: Interviewing</option>
          <option value="Offer">Status: Offer</option>
          <option value="Rejected">Status: Rejected</option>
          <option value="Ignored">Status: Ignored</option>
        </select>

        <select
          value={filters.scoreFilter}
          onChange={(e) => onChange({ scoreFilter: e.target.value })}
          className="w-full md:w-auto bg-slate-50/90 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:ring-1 focus:ring-indigo-500 focus:outline-none"
        >
          <option value="All">Match: All Levels</option>
          <option value="Excellent">Match: Excellent (&gt;85%)</option>
          <option value="Good">Match: Good (70-85%)</option>
          <option value="Fair">Match: Fair (&lt;70%)</option>
        </select>

        <select
          value={filters.remoteFilter}
          onChange={(e) => onChange({ remoteFilter: e.target.value })}
          className="w-full md:w-auto bg-slate-50/90 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:ring-1 focus:ring-indigo-500 focus:outline-none"
        >
          <option value="All">Location: All Remote</option>
          <option value="Remote">Remote</option>
          <option value="Hybrid">Hybrid</option>
          <option value="On-site">On-site</option>
        </select>

        <select
          value={filters.seniorityFilter}
          onChange={(e) => onChange({ seniorityFilter: e.target.value })}
          className="w-full md:w-auto bg-slate-50/90 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:ring-1 focus:ring-indigo-500 focus:outline-none"
        >
          <option value="All">Seniority: All Level</option>
          <option value="Senior">Senior</option>
          <option value="Mid-level">Mid-level</option>
          <option value="Junior">Junior</option>
        </select>

        <select
          value={filters.sourceFilter}
          onChange={(e) => onChange({ sourceFilter: e.target.value })}
          className="w-full md:w-auto bg-slate-50/90 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:ring-1 focus:ring-indigo-500 focus:outline-none"
        >
          <option value="All">Source: All Platforms</option>
          {sources.map((source) => (
            <option key={source} value={source}>
              {source}
            </option>
          ))}
        </select>

        <select
          value={filters.roleFilter}
          onChange={(e) => onChange({ roleFilter: e.target.value })}
          className="w-full md:w-auto bg-slate-50/90 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:ring-1 focus:ring-indigo-500 focus:outline-none"
        >
          <option value="All">Role: All Canonical Roles</option>
          {roles.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </select>

        <select
          value={filters.priorityFilter}
          onChange={(e) => onChange({ priorityFilter: e.target.value })}
          className="w-full md:w-auto bg-slate-50/90 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:ring-1 focus:ring-indigo-500 focus:outline-none"
        >
          <option value="All">Priority: All</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>

        <label className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-600 dark:text-slate-400 cursor-pointer pt-1 md:pt-0 select-none">
          <input
            type="checkbox"
            checked={filters.hideDuplicates}
            onChange={(e) => onChange({ hideDuplicates: e.target.checked })}
            className="rounded border-slate-300 dark:border-slate-600 text-indigo-600 focus:ring-indigo-500"
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

    const matchesStatus =
      filters.statusFilter === 'All'
        ? job.status !== 'Ignored' && job.status !== 'Rejected'
        : job.status === filters.statusFilter;

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
