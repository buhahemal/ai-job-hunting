import { useState } from 'react';
import { ArrowUpRight, Clock, History, Sparkles, X } from 'lucide-react';
import { Job } from '../types';

interface JobDetailPanelProps {
  job: Job | null;
  onClose: () => void;
  onSaveNotes: (jobId: string, notes: string) => void;
  onUpdateStatus?: (jobId: string, status: Job['status'], note?: string) => void;
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

export default function JobDetailPanel({
  job,
  onClose,
  onSaveNotes,
  onUpdateStatus,
}: JobDetailPanelProps) {
  const [selectedStatus, setSelectedStatus] = useState<Job['status'] | ''>('');
  const [statusNote, setStatusNote] = useState('');
  const [updating, setUpdating] = useState(false);

  if (!job) {
    return (
      <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm sticky top-6">
        <div className="text-center py-12 text-slate-400 space-y-3">
          <Sparkles className="h-8 w-8 text-slate-300 mx-auto" />
          <p className="text-xs">
            Select a job to view enriched metadata, score breakdown, missing skills, and history.
          </p>
        </div>
      </div>
    );
  }

  const insights = job.matchInsights;
  const currentStatus = job.status;

  const handleStatusSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newStatus = selectedStatus || currentStatus;
    if (!onUpdateStatus) return;
    setUpdating(true);
    try {
      await onUpdateStatus(job.id, newStatus, statusNote.trim() || undefined);
      setStatusNote('');
      setSelectedStatus('');
    } finally {
      setUpdating(false);
    }
  };

  const createdDate = job.createdAt || job.scannedAt || job.postedAt;
  const updatedDate = job.updatedAt || job.scannedAt || job.createdAt;

  return (
    <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm sticky top-6 space-y-6 max-h-[calc(100vh-8rem)] overflow-auto">
      <div className="flex justify-between items-start gap-3 border-b border-slate-50 pb-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] font-mono font-bold uppercase text-slate-400">
              {job.source}
            </span>
            {job.canonicalRole && (
              <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold uppercase">
                {job.canonicalRole}
              </span>
            )}
            {job.priority && (
              <span
                className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                  job.priority === 'High'
                    ? 'bg-emerald-50 text-emerald-700'
                    : job.priority === 'Medium'
                      ? 'bg-amber-50 text-amber-700'
                      : 'bg-slate-100 text-slate-600'
                }`}
              >
                {job.priority} Priority
              </span>
            )}
          </div>
          <h3 className="text-base font-bold text-slate-800 mt-1">{job.title}</h3>
          <p className="text-xs font-semibold text-slate-500 mt-0.5">
            {job.company} • {job.location} • {job.remoteType}
          </p>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1 rounded-lg">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Metadata Grid */}
      <div className="grid grid-cols-2 gap-3 text-[11px]">
        <div className="bg-slate-50 rounded-lg p-3">
          <div className="text-slate-400 uppercase font-bold text-[10px]">Stack</div>
          <div className="font-semibold text-slate-700 mt-1">
            {job.primaryStack || 'Generalist'}
          </div>
        </div>
        <div className="bg-slate-50 rounded-lg p-3">
          <div className="text-slate-400 uppercase font-bold text-[10px]">Seniority</div>
          <div className="font-semibold text-slate-700 mt-1">{job.seniority || 'Unknown'}</div>
        </div>
        <div className="bg-slate-50 rounded-lg p-3">
          <div className="text-slate-400 uppercase font-bold text-[10px] flex items-center gap-1">
            <Clock className="h-3 w-3 text-slate-400" />
            Created / Scanned
          </div>
          <div className="font-semibold text-slate-700 mt-1">
            {createdDate ? new Date(createdDate).toLocaleString() : '—'}
          </div>
        </div>
        <div className="bg-slate-50 rounded-lg p-3">
          <div className="text-slate-400 uppercase font-bold text-[10px] flex items-center gap-1">
            <Clock className="h-3 w-3 text-indigo-400" />
            Last Modified
          </div>
          <div className="font-semibold text-slate-700 mt-1">
            {updatedDate ? new Date(updatedDate).toLocaleString() : 'Just now'}
          </div>
        </div>
      </div>

      {/* Update Status & Reason Form */}
      {onUpdateStatus && (
        <form
          onSubmit={handleStatusSubmit}
          className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3"
        >
          <div className="flex items-center justify-between">
            <label className="text-[10px] font-bold text-slate-600 uppercase tracking-wide">
              Update Status & Add Reason Note
            </label>
            <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-indigo-50 text-indigo-700">
              Current: {currentStatus}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <select
              value={selectedStatus || currentStatus}
              onChange={(e) => setSelectedStatus(e.target.value as Job['status'])}
              className="bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-semibold focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="New">New Lead</option>
              <option value="Shortlisted">Shortlisted</option>
              <option value="Applied">Applied</option>
              <option value="Interviewing">Interviewing</option>
              <option value="Offer">Offer</option>
              <option value="Rejected">Rejected</option>
              <option value="Ignored">Ignored</option>
            </select>

            <button
              type="submit"
              disabled={updating}
              className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold py-1.5 px-3 rounded-lg transition-colors disabled:opacity-50"
            >
              {updating ? 'Updating…' : 'Save Status & Note'}
            </button>
          </div>

          <input
            type="text"
            placeholder="Optional reason note (e.g. Relocation required, Applied on portal, Referral set)..."
            value={statusNote}
            onChange={(e) => setStatusNote(e.target.value)}
            className="w-full bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </form>
      )}

      {/* Action History / Change Log */}
      {job.actionHistory && job.actionHistory.length > 0 && (
        <div className="space-y-3 border-t border-slate-100 pt-4">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700 uppercase tracking-wide">
            <History className="h-4 w-4 text-indigo-500" />
            <span>Action History & Notes Timeline</span>
          </div>
          <div className="space-y-2 max-h-48 overflow-auto pr-1">
            {job.actionHistory.map((entry, idx) => (
              <div
                key={idx}
                className="bg-slate-50 border border-slate-100 rounded-lg p-2.5 text-xs space-y-1"
              >
                <div className="flex items-center justify-between text-[10px] text-slate-400">
                  <span className="font-bold text-slate-600">{entry.action}</span>
                  <span>{new Date(entry.timestamp).toLocaleString()}</span>
                </div>
                {entry.note && (
                  <p className="text-xs text-slate-700 bg-white border border-slate-100 p-2 rounded italic">
                    "{entry.note}"
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-gradient-to-br from-indigo-50 to-sky-50/50 rounded-xl border border-indigo-100/30 p-4.5 space-y-4">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-800 uppercase tracking-wide">
            <Sparkles className="h-4 w-4 text-indigo-500" />
            <span>Match Analysis</span>
          </div>
          {job.matchScorer && (
            <span className="text-[10px] uppercase font-bold text-indigo-600 bg-white/70 px-2 py-0.5 rounded">
              {job.matchScorer}
            </span>
          )}
        </div>

        {insights && (
          <div className="grid gap-2.5">
            <ScoreBar label="Overall" value={insights.overallScore} />
            <ScoreBar label="Skills" value={insights.skillMatchScore} />
            <ScoreBar label="Experience" value={insights.experienceMatchScore} />
            <ScoreBar label="ATS" value={insights.atsScore} />
            <ScoreBar label="Remote Fit" value={insights.remoteMatchScore} />
            <ScoreBar label="Company Fit" value={insights.companyMatchScore} />
            <ScoreBar label="Location Fit" value={insights.locationMatchScore} />
            <ScoreBar label="Confidence" value={insights.confidenceScore} />
          </div>
        )}

        <p className="text-xs text-slate-700 leading-relaxed font-medium">
          {insights?.matchExplanation || job.fitExplanation || 'No match explanation available.'}
        </p>
      </div>

      <ChipList
        title="Matched Skills"
        items={insights?.matchedSkills || job.extractedSkills}
        tone="good"
      />
      <ChipList title="Missing Skills" items={insights?.missingSkills} tone="warn" />
      <ChipList title="Missing Keywords" items={insights?.missingKeywords} tone="warn" />
      <ChipList title="Technologies" items={job.extractedTechnologies} tone="neutral" />
      <ChipList title="Required Skills" items={job.requiredSkills} tone="neutral" />

      {insights?.resumeSuggestions?.length ? (
        <div className="space-y-2">
          <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
            Resume Suggestions
          </h4>
          <ul className="space-y-2">
            {insights.resumeSuggestions.map((item) => (
              <li
                key={item}
                className="text-xs text-slate-600 bg-slate-50 border border-slate-100 rounded-lg p-2.5"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="space-y-2.5">
        {(job.applicationUrl || job.url) && (
          <a
            href={job.applicationUrl || job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full bg-white border border-slate-200 text-slate-700 text-xs py-2.5 rounded-lg font-semibold uppercase flex items-center justify-center gap-1 hover:bg-slate-50"
          >
            Apply / View Posting
            <ArrowUpRight className="h-4 w-4" />
          </a>
        )}
      </div>

      <div className="space-y-2">
        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
          General Notes
        </label>
        <textarea
          placeholder="Track referrals, interviews, salary notes..."
          defaultValue={job.notes || ''}
          onBlur={(e) => onSaveNotes(job.id, e.target.value)}
          className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs min-h-[80px]"
        />
      </div>

      <div className="space-y-2 border-t border-slate-50 pt-4">
        <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
          Job Description
        </h4>
        <div className="text-xs text-slate-600 leading-relaxed max-h-[240px] overflow-auto whitespace-pre-wrap">
          {job.description}
        </div>
      </div>
    </div>
  );
}
