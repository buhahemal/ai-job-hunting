import { useCallback, useEffect, useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, Radar, RefreshCw, TrendingUp } from 'lucide-react';
import type { ScanSummary, ScannedJobRecord } from '@ai-job-hunter/database';
import {
  MATCH_SCORE_NEAR_MISS,
  MATCH_SCORE_THRESHOLD,
  SCAN_INSIGHTS_PAGE_SIZE,
} from '@ai-job-hunter/database';
import * as api from '../api/client';
import ScanInsightDetailPanel from './ScanInsightDetailPanel';
import ScanInsightsFilters, {
  scoreBandToRange,
  type ScanInsightsFilterState,
} from './ScanInsightsFilters';

const PAGE_SIZE = SCAN_INSIGHTS_PAGE_SIZE;

export default function ScanInsightsView() {
  const [summary, setSummary] = useState<ScanSummary | null>(null);
  const [items, setItems] = useState<ScannedJobRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [rescanning, setRescanning] = useState(false);
  const [rescanMessage, setRescanMessage] = useState<string | null>(null);
  const [selected, setSelected] = useState<ScannedJobRecord | null>(null);
  const [filters, setFilters] = useState<ScanInsightsFilterState>({
    scoreBand: 'All',
    sourceFilter: 'All',
    roleFilter: 'All',
    seniorityFilter: 'All',
    missingSkillFilter: 'All',
    belowThresholdOnly: false,
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const band = scoreBandToRange(filters.scoreBand);
      const [summaryData, pageData] = await Promise.all([
        api.getScanSummary(),
        api.listScannedJobs({
          page,
          limit: PAGE_SIZE,
          ...band,
          source: filters.sourceFilter !== 'All' ? filters.sourceFilter : undefined,
          role: filters.roleFilter !== 'All' ? filters.roleFilter : undefined,
          missingSkill:
            filters.missingSkillFilter !== 'All' ? filters.missingSkillFilter : undefined,
          belowThresholdOnly: filters.belowThresholdOnly,
        }),
      ]);
      setSummary(summaryData);
      setItems(pageData.items);
      setTotal(pageData.total);
    } catch (error) {
      console.error('Failed to load scan insights', error);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  useEffect(() => {
    setPage(1);
  }, [
    filters.scoreBand,
    filters.sourceFilter,
    filters.roleFilter,
    filters.seniorityFilter,
    filters.missingSkillFilter,
    filters.belowThresholdOnly,
  ]);

  const filteredItems = useMemo(() => {
    if (filters.seniorityFilter === 'All') return items;
    return items.filter((item) => item.seniority === filters.seniorityFilter);
  }, [items, filters.seniorityFilter]);

  const sourceOptions = useMemo(() => {
    const fromSummary = summary?.topSource ? [summary.topSource] : [];
    const fromItems = items.map((item) => item.source).filter(Boolean);
    return [...new Set([...fromItems, ...fromSummary])].sort();
  }, [items, summary]);

  const roleOptions = useMemo(
    () => [...new Set(items.map((item) => item.canonicalRole).filter(Boolean))].sort() as string[],
    [items],
  );

  const missingSkillOptions = useMemo(
    () => (summary?.topMissingSkills ?? []).map((entry) => entry.skill).slice(0, 15),
    [summary],
  );

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const handleRescan = async () => {
    setRescanning(true);
    setRescanMessage(null);
    try {
      const { rescoredCount } = await api.rescanScanInsights();
      setRescanMessage(
        `Rescored ${rescoredCount} scanned job${rescoredCount === 1 ? '' : 's'} with your current profile.`,
      );
      await loadData();
    } catch (error) {
      setRescanMessage(error instanceof Error ? error.message : 'Rescan failed.');
    } finally {
      setRescanning(false);
    }
  };

  const handlePromoted = (dedupeKey: string) => {
    setItems((prev) =>
      prev.map((item) =>
        item.dedupeKey === dedupeKey
          ? { ...item, promotedToJobs: true, promotionType: 'manual' }
          : item,
      ),
    );
    setSelected((prev) =>
      prev?.dedupeKey === dedupeKey
        ? { ...prev, promotedToJobs: true, promotionType: 'manual' }
        : prev,
    );
    void loadData();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">Scan Insights</h2>
          <p className="text-xs text-slate-500 mt-1">
            Every job evaluated by the scanner — including sub-threshold rejects — with match scores
            and verified skill gaps. Separate from promoted Job Leads.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void handleRescan()}
          disabled={rescanning || loading}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-indigo-200 bg-indigo-50 text-indigo-700 text-xs font-semibold hover:bg-indigo-100 disabled:opacity-50 shrink-0"
        >
          <RefreshCw className={`h-4 w-4 ${rescanning ? 'animate-spin' : ''}`} />
          {rescanning ? 'Rescanning…' : 'Rescan with current profile'}
        </button>
      </div>

      {rescanMessage && (
        <div className="text-xs px-3 py-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-600">
          {rescanMessage}
        </div>
      )}

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Radar className="h-4 w-4" />
              <span className="text-[10px] font-bold uppercase">Total Scanned</span>
            </div>
            <div className="text-2xl font-extrabold text-slate-800">{summary.totalScanned}</div>
            {summary.lastRunScanned > 0 && (
              <p className="text-[10px] text-slate-400 mt-1">
                {summary.lastRunScanned} in last run
              </p>
            )}
          </div>

          <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <TrendingUp className="h-4 w-4" />
              <span className="text-[10px] font-bold uppercase">Avg Match</span>
            </div>
            <div className="text-2xl font-extrabold text-slate-800">{summary.averageScore}%</div>
            {summary.topSource && (
              <p className="text-[10px] text-slate-400 mt-1">Top source: {summary.topSource}</p>
            )}
          </div>

          <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
            <div className="text-[10px] font-bold uppercase text-slate-400 mb-1">Promoted</div>
            <div className="text-2xl font-extrabold text-emerald-700">{summary.promotedCount}</div>
            <p className="text-[10px] text-slate-400 mt-1">
              Score &gt; {MATCH_SCORE_THRESHOLD}% → Job Leads
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
            <div className="text-[10px] font-bold uppercase text-slate-400 mb-1">Last Scan</div>
            <div className="text-sm font-bold text-slate-800">
              {summary.lastScanAt
                ? new Date(summary.lastScanAt).toLocaleString([], {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })
                : '—'}
            </div>
          </div>
        </div>
      )}

      {summary && summary.topMissingSkills.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-sm space-y-4">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Top Market Skill Gaps
            </h3>
            <p className="text-[10px] text-slate-500 mt-1">
              Skills demanded by scanned jobs that are not demonstrated in your profile or resume.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {summary.topMissingSkills.map((entry) => (
              <div
                key={entry.skill}
                className="flex items-center justify-between gap-3 bg-slate-50 border border-slate-100 rounded-lg px-3 py-2"
              >
                <div>
                  <div className="text-xs font-bold text-slate-800">{entry.skill}</div>
                  <div className="text-[10px] text-slate-500">
                    Missing in {entry.count} posting{entry.count === 1 ? '' : 's'} • avg{' '}
                    {entry.averageScoreWhenMissing}% when missing
                  </div>
                </div>
                {entry.estimatedBandBoost > 0 && (
                  <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-1 rounded whitespace-nowrap">
                    +{entry.estimatedBandBoost} near {MATCH_SCORE_THRESHOLD}%
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <ScanInsightsFilters
        filters={filters}
        sources={sourceOptions}
        roles={roleOptions}
        missingSkills={missingSkillOptions}
        onChange={(patch) => setFilters((prev) => ({ ...prev, ...patch }))}
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">
        <div className="xl:col-span-2 space-y-4">
          {loading ? (
            <div className="bg-white p-12 text-center rounded-xl border border-slate-100 text-xs text-slate-400">
              Loading scan insights…
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="bg-white p-12 text-center rounded-xl border border-dashed border-slate-200 space-y-3">
              <Radar className="h-10 w-10 text-slate-300 mx-auto" />
              <h4 className="text-sm font-bold text-slate-700">No scanned jobs match filters</h4>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Run a career board scan to populate insights. Jobs below {MATCH_SCORE_THRESHOLD}%
                appear here only.
              </p>
            </div>
          ) : (
            filteredItems.map((insight) => (
              <div
                key={insight.dedupeKey}
                onClick={() => setSelected(insight)}
                className={`bg-white rounded-xl border p-5 hover:shadow-md transition-all cursor-pointer ${
                  selected?.dedupeKey === insight.dedupeKey
                    ? 'border-indigo-500 ring-1 ring-indigo-500/10 shadow-sm'
                    : 'border-slate-100'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide font-mono">
                        {insight.source}
                      </span>
                      {insight.promotedToJobs && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 font-bold uppercase">
                          Promoted
                        </span>
                      )}
                    </div>
                    <h3 className="text-sm font-bold text-slate-800 mt-1">{insight.title}</h3>
                    <p className="text-xs font-semibold text-slate-500 mt-0.5">{insight.company}</p>
                    {insight.canonicalRole && (
                      <span className="inline-block mt-2 text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold uppercase">
                        {insight.canonicalRole}
                      </span>
                    )}
                  </div>
                  <div
                    className={`shrink-0 px-3 py-1.5 rounded-lg text-center ${
                      insight.overallScore >= MATCH_SCORE_THRESHOLD
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                        : insight.overallScore >= MATCH_SCORE_NEAR_MISS
                          ? 'bg-amber-50 text-amber-700 border border-amber-100'
                          : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    <div className="text-[10px] font-bold uppercase tracking-wider leading-none">
                      Match
                    </div>
                    <div className="text-base font-extrabold leading-none mt-1">
                      {insight.overallScore}%
                    </div>
                  </div>
                </div>
                {insight.missingSkills.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {insight.missingSkills.slice(0, 3).map((skill) => (
                      <span
                        key={skill}
                        className="bg-amber-50 border border-amber-100 text-amber-700 text-[10px] px-2 py-0.5 rounded-md font-medium"
                      >
                        −{skill}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}

          {totalPages > 1 && (
            <div className="flex items-center justify-between bg-white rounded-xl border border-slate-100 px-4 py-3">
              <span className="text-xs text-slate-500">
                Page {page} of {totalPages} ({total} scanned)
              </span>
              <div className="flex gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg border border-slate-200 disabled:opacity-40"
                >
                  <ChevronLeft className="h-4 w-4" /> Prev
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg border border-slate-200 disabled:opacity-40"
                >
                  Next <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        <ScanInsightDetailPanel
          insight={selected}
          onClose={() => setSelected(null)}
          onPromoted={handlePromoted}
        />
      </div>

      <p className="mt-6 text-[11px] text-slate-400 text-center">
        Job listings may include data from{' '}
        <a
          href="https://remoteok.com"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-slate-600"
        >
          RemoteOK
        </a>
        . RemoteOK requires attribution when displaying their listings.
      </p>
    </div>
  );
}
