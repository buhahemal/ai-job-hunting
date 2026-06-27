import { useState } from 'react';
import { Calendar, Clock, CheckCircle, XCircle, BookOpen, Plus } from 'lucide-react';
import { Job, Interview } from '../types';

interface InterviewTrackerProps {
  interviews: Interview[];
  jobs: Job[];
  onAddInterview: (interview: Omit<Interview, 'id' | 'status'>) => Promise<void>;
  onUpdateStatus: (
    id: string,
    status: 'Scheduled' | 'Completed' | 'Cancelled' | 'Passed' | 'Failed',
  ) => Promise<void>;
}

export default function InterviewTracker({
  interviews,
  jobs,
  onAddInterview,
  onUpdateStatus,
}: InterviewTrackerProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState('');
  const [date, setDate] = useState('');
  const [type, setType] = useState('Technical Interview');
  const [notes, setNotes] = useState('');

  // Eligible jobs are those we applied for or shortlisted
  const eligibleJobs = jobs.filter((j) => j.status !== 'Ignored' && j.status !== 'Rejected');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedJobId || !date) return;

    const selectedJob = jobs.find((j) => j.id === selectedJobId);
    if (!selectedJob) return;

    await onAddInterview({
      jobId: selectedJobId,
      role: selectedJob.title,
      company: selectedJob.company,
      date,
      type,
      notes,
    });

    // Reset Form
    setSelectedJobId('');
    setDate('');
    setType('Technical Interview');
    setNotes('');
    setShowAddForm(false);
  };

  return (
    <div className="space-y-6">
      {/* Header and Add button */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <Calendar className="h-5.5 w-5.5 text-indigo-500" />
            Interview Preparation & Tracking
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Manage scheduled interview rounds, structure system design notes, and trace progress
            results.
          </p>
        </div>

        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-3.5 py-2 rounded-lg font-medium shadow-sm flex items-center gap-1.5 transition-all self-start"
        >
          <Plus className="h-4 w-4" />
          Schedule Interview
        </button>
      </div>

      {/* Add Interview Form Panel */}
      {showAddForm && (
        <form
          onSubmit={handleSubmit}
          className="bg-slate-50 p-5 rounded-xl border border-slate-200 shadow-inner space-y-4 max-w-2xl"
        >
          <h3 className="text-xs font-bold tracking-wider uppercase text-slate-500">
            Record Upcoming Interview Round
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[11px] font-bold text-slate-600 uppercase">
                Linked Company / Job
              </label>
              <select
                value={selectedJobId}
                onChange={(e) => setSelectedJobId(e.target.value)}
                required
                className="w-full bg-white border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
              >
                <option value="">-- Choose Job --</option>
                {eligibleJobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.company} - {j.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-bold text-slate-600 uppercase">Round Type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full bg-white border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
              >
                <option value="Technical Interview">Technical Interview</option>
                <option value="System Design Round">System Design Round</option>
                <option value="Behavioral Interview">Behavioral Interview</option>
                <option value="Technical Take-home Assessment">
                  Technical Take-home Assessment
                </option>
                <option value="HR / Hiring Manager Round">HR / Hiring Manager Round</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-bold text-slate-600 uppercase">Date & Time</label>
              <input
                type="datetime-local"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
                className="w-full bg-white border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-bold text-slate-600 uppercase">
              Preparation / Study Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="List specific talking points, system architecture design items, questions to ask the interviewer..."
              rows={3}
              className="w-full bg-white border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-1">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs px-3 py-1.5 rounded-lg font-medium transition-colors"
            >
              Discard
            </button>
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-4 py-1.5 rounded-lg font-medium shadow-sm transition-colors"
            >
              Add Scheduled Round
            </button>
          </div>
        </form>
      )}

      {/* Interviews Board / Cards list */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {interviews.length === 0 ? (
          <div className="col-span-full bg-slate-50 p-12 text-center rounded-xl border border-dashed border-slate-200 space-y-3">
            <Calendar className="h-10 w-10 text-slate-300 mx-auto" />
            <h4 className="text-sm font-bold text-slate-700">No scheduled interviews recorded</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Click "Schedule Interview" above to log and prepare for your upcoming corporate hiring
              rounds.
            </p>
          </div>
        ) : (
          interviews.map((i) => (
            <div
              key={i.id}
              className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden flex flex-col justify-between hover:border-indigo-100 hover:shadow-md transition-all"
            >
              {/* Header card state */}
              <div className="p-5 border-b border-slate-50">
                <div className="flex justify-between items-start gap-2">
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${
                      i.status === 'Scheduled'
                        ? 'bg-sky-50 text-sky-700 border border-sky-100'
                        : i.status === 'Passed'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                          : i.status === 'Failed'
                            ? 'bg-rose-50 text-rose-700 border border-rose-100'
                            : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {i.status}
                  </span>

                  <span className="text-[10px] font-mono text-slate-400 font-semibold uppercase">
                    {i.type}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-slate-800 mt-3">{i.role}</h3>
                <p className="text-xs font-semibold text-slate-500 mt-0.5">{i.company}</p>

                <div className="flex items-center gap-2 mt-4 text-[11px] font-mono text-slate-500 bg-slate-50 p-2 rounded-lg border border-slate-100">
                  <Clock className="h-3.5 w-3.5 text-indigo-500 shrink-0" />
                  <span>
                    {new Date(i.date).toLocaleString([], {
                      dateStyle: 'medium',
                      timeStyle: 'short',
                    })}
                  </span>
                </div>
              </div>

              {/* Notes block */}
              {i.notes && (
                <div className="p-5 bg-slate-50/50 flex-1 border-b border-slate-50">
                  <div className="flex items-center gap-1 text-[10px] uppercase font-bold text-slate-400 mb-1.5">
                    <BookOpen className="h-3 w-3" />
                    <span>Interview Study Notes</span>
                  </div>
                  <p className="text-xs text-slate-600 line-clamp-4 whitespace-pre-wrap leading-relaxed">
                    {i.notes}
                  </p>
                </div>
              )}

              {/* Status Actions */}
              <div className="p-4 bg-slate-50 flex items-center justify-between gap-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Set Outcome:</span>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => onUpdateStatus(i.id, 'Passed')}
                    disabled={i.status !== 'Scheduled'}
                    title="Mark as Passed"
                    className={`p-1 rounded-md border text-xs transition-all flex items-center gap-1 px-2 font-medium ${
                      i.status === 'Passed'
                        ? 'bg-emerald-600 text-white border-emerald-600'
                        : 'bg-white text-emerald-600 border-slate-200 hover:bg-emerald-50'
                    } ${i.status !== 'Scheduled' && i.status !== 'Passed' ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <CheckCircle className="h-3.5 w-3.5" />
                    <span>Pass</span>
                  </button>

                  <button
                    onClick={() => onUpdateStatus(i.id, 'Failed')}
                    disabled={i.status !== 'Scheduled'}
                    title="Mark as Rejected"
                    className={`p-1 rounded-md border text-xs transition-all flex items-center gap-1 px-2 font-medium ${
                      i.status === 'Failed'
                        ? 'bg-rose-600 text-white border-rose-600'
                        : 'bg-white text-rose-600 border-slate-200 hover:bg-rose-50'
                    } ${i.status !== 'Scheduled' && i.status !== 'Failed' ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <XCircle className="h-3.5 w-3.5" />
                    <span>Fail</span>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
