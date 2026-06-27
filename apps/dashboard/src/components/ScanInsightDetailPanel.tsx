import { useState } from 'react';
import { ArrowUpRight, Search, Sparkles, X } from 'lucide-react';
import type { ScannedJobRecord } from '@ai-job-hunter/database';
import * as api from '../api/client';

interface ScanInsightDetailPanelProps {
  insight: ScannedJobRecord | null;
  onClose: () => void;
  onPromoted?: (dedupeKey: string) => void;
}

function ScoreBar({ label, value }: { label: string; value?: number }) {
  if (value === undefined) return null;
  return (
    <div>
      <div className="flex justify-between text-[10px] text-slate-500 mb-1">
        <span>{label}</span>
        <span className="font-bold">{value}%</span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-500 rounded-full"
          style={{ width: `${Math.min(100, value)}%` }}
        />
      </div>
    </div>
  );
}

function ChipList({
  title,
  items,
  tone,
}: {
  title: string;
  items?: string[];
  tone: 'good' | 'warn' | 'neutral';
}) {
  if (!items?.length) return null;
  const styles =
    tone === 'good'
      ? 'bg-emerald-50 border-emerald-100 text-emerald-700'
      : tone === 'warn'
        ? 'bg-amber-50 border-amber-100 text-amber-700'
        : 'bg-slate-50 border-slate-200 text-slate-600';
  return (
    <div className="space-y-2">
      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">{title}</h4>
      <div className="flex flex-wrap gap-1.5">
        {items.map((item) => (
          <span
            key={item}
            className={`text-[10px] px-2 py-0.5 rounded-md border font-medium ${styles}`}
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function ScanInsightDetailPanel({
  insight,
  onClose,
  onPromoted,
}: ScanInsightDetailPanelProps) {
  const [promoting, setPromoting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [promoteMessage, setPromoteMessage] = useState<string | null>(null);

  if (!insight) {
    return (
      <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm sticky top-6">
        <div className="text-center py-12 text-slate-400 space-y-3">
          <Search className="h-8 w-8 text-slate-300 mx-auto" />
          <p className="text-xs">
            Select a scanned job to view match breakdown, missing skills, and posting link.
          </p>
        </div>
      </div>
    );
  }

  const handlePromote = async () => {
    setPromoting(true);
    setPromoteMessage(null);
    try {
      await api.promoteScannedJob(insight.dedupeKey);
      setShowConfirm(false);
      setPromoteMessage('Added to Job Leads. Open the Job Leads tab to apply or tailor.');
      onPromoted?.(insight.dedupeKey);
    } catch (error) {
      setPromoteMessage(error instanceof Error ? error.message : 'Promotion failed.');
    } finally {
      setPromoting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm sticky top-6 space-y-6 max-h-[calc(100vh-8rem)] overflow-auto">
      <div className="flex justify-between items-start gap-3 border-b border-slate-50 pb-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] font-mono font-bold uppercase text-slate-400">
              {insight.source}
            </span>
            {insight.canonicalRole && (
              <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold uppercase">
                {insight.canonicalRole}
              </span>
            )}
            {insight.promotedToJobs && (
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-bold uppercase">
                Promoted to Leads
              </span>
            )}
          </div>
          <h3 className="text-base font-bold text-slate-800 mt-1">{insight.title}</h3>
          <p className="text-xs font-semibold text-slate-500 mt-0.5">
            {insight.company} • {insight.location} • {insight.remoteType}
          </p>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1 rounded-lg">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="flex items-center justify-between">
        <div
          className={`px-4 py-2 rounded-lg text-center ${
            insight.overallScore >= 75
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
              : insight.overallScore >= 65
                ? 'bg-amber-50 text-amber-700 border border-amber-100'
                : 'bg-slate-100 text-slate-600'
          }`}
        >
          <div className="text-[10px] font-bold uppercase tracking-wider">Overall Match</div>
          <div className="text-2xl font-extrabold">{insight.overallScore}%</div>
        </div>
        <div className="text-right space-y-1">
          {insight.scannedAt && (
            <p className="text-[10px] text-slate-400 font-mono">
              Scanned {new Date(insight.scannedAt).toLocaleString()}
            </p>
          )}
          {insight.rescoredAt && (
            <p className="text-[10px] text-indigo-500 font-mono">
              Rescored {new Date(insight.rescoredAt).toLocaleString()}
            </p>
          )}
        </div>
      </div>

      <div className="space-y-3">
        <ScoreBar label="Skill Match" value={insight.skillMatchScore} />
        <ScoreBar label="Experience Match" value={insight.experienceMatchScore} />
        <ScoreBar label="ATS Readiness" value={insight.atsScore} />
        {insight.skillMatchConfidence !== undefined && (
          <ScoreBar label="Match Confidence" value={insight.skillMatchConfidence} />
        )}
      </div>

      {insight.matchExplanation && (
        <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
          <h4 className="text-[10px] font-bold text-slate-400 uppercase mb-1">Match Summary</h4>
          <p className="text-xs text-slate-600 leading-relaxed">{insight.matchExplanation}</p>
        </div>
      )}

      <ChipList title="Matched Skills" items={insight.matchedSkills} tone="good" />
      <ChipList
        title="Missing Skills (job requirements)"
        items={insight.missingSkills}
        tone="warn"
      />
      <ChipList title="Missing Keywords" items={insight.missingKeywords} tone="neutral" />

      {!insight.promotedToJobs && (
        <div className="space-y-2">
          {showConfirm ? (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 space-y-3">
              <p className="text-xs text-amber-900">
                Add to your apply/tailor pipeline regardless of auto score?
              </p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => void handlePromote()}
                  disabled={promoting}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs py-2 rounded-lg font-semibold disabled:opacity-50"
                >
                  {promoting ? 'Promoting…' : 'Confirm promote'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowConfirm(false)}
                  className="px-3 text-xs py-2 rounded-lg border border-slate-200 text-slate-600"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setShowConfirm(true)}
              className="flex items-center justify-center gap-2 w-full border border-emerald-200 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs py-2.5 rounded-lg font-semibold transition-colors"
            >
              <Sparkles className="h-4 w-4" />
              Promote to Job Leads
            </button>
          )}
        </div>
      )}

      {promoteMessage && (
        <p className="text-[10px] text-slate-600 bg-slate-50 border border-slate-100 rounded-lg px-3 py-2">
          {promoteMessage}
        </p>
      )}

      {insight.applicationUrl && (
        <a
          href={insight.applicationUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs py-2.5 rounded-lg font-semibold transition-colors"
        >
          View Job Posting
          <ArrowUpRight className="h-4 w-4" />
        </a>
      )}
    </div>
  );
}
