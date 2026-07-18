import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  Calendar,
  BarChart2,
  User,
  FileText,
  Plus,
  RefreshCw,
  ChevronRight,
  X,
  Sparkles,
  MapPin,
  DollarSign,
  FileCheck,
  Info,
  Radar,
} from 'lucide-react';
import * as api from './api/client';
import { getProfileInitials } from './api/defaultProfile';
import ProfileView from './components/profile/ProfileView';
import { isProfileCompleteForMatching } from '@ai-job-hunter/database';
import { Profile, Job, Interview } from './types';
import ResumePreview from './components/ResumePreview';
import AnalyticsView from './components/AnalyticsView';
import InterviewTracker from './components/InterviewTracker';
import JobDetailPanel from './components/JobDetailPanel';
import JobFilters, { filterJobs, type JobFilterState } from './components/JobFilters';
import ScanInsightsView from './components/ScanInsightsView';

export default function App() {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'scanInsights' | 'tailor' | 'interviews' | 'analytics' | 'profile'
  >('dashboard');

  // App States
  const [profile, setProfile] = useState<Profile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [scanning, setScanning] = useState(false);
  const [tailoringId, setTailoringId] = useState<string | null>(null);

  const [filters, setFilters] = useState<JobFilterState>({
    searchQuery: '',
    statusFilter: 'All',
    scoreFilter: 'All',
    remoteFilter: 'All',
    seniorityFilter: 'All',
    sourceFilter: 'All',
    roleFilter: 'All',
    priorityFilter: 'All',
    hideDuplicates: true,
  });

  // Modals & Forms
  const [manualImportOpen, setManualImportOpen] = useState(false);
  const [newManualJob, setNewManualJob] = useState({
    title: '',
    company: '',
    location: '',
    remoteType: 'Remote' as 'Remote' | 'Hybrid' | 'On-site',
    url: '',
    description: '',
  });

  // Profile Form States
  const [profileForm, setProfileForm] = useState<Profile | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [tailoredResumeMeta, setTailoredResumeMeta] = useState<
    api.TailorJobResult['resume'] | null
  >(null);

  // General Notification Log
  const [notif, setNotif] = useState<{
    type: 'success' | 'error' | 'info';
    message: string;
  } | null>(null);

  const showNotif = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    setNotif({ type, message });
    setTimeout(() => setNotif(null), 5000);
  };

  const fetchProfile = async () => {
    try {
      const data = await api.getProfile();
      setProfile(data);
      setProfileForm(data);
    } catch (e) {
      console.error('Failed to fetch profile', e);
    }
  };

  const fetchJobs = async () => {
    try {
      const data = await api.getJobs();
      setJobs(data.jobs || []);
      setInterviews(data.interviews || []);
    } catch (e) {
      console.error('Failed to fetch jobs', e);
    }
  };

  // 1. Initial Load Sync
  useEffect(() => {
    void fetchProfile();
    void fetchJobs();
  }, []);

  // 2. Scan Careers Boards trigger
  const handleScan = async () => {
    setScanning(true);
    showNotif('Scanning active job boards and target consulting portals...', 'info');
    try {
      const data = await api.scanJobs();
      await fetchJobs();
      showNotif(
        `Scan completed successfully! Discovered and scored ${data.addedCount} new matching leads.`,
        'success',
      );
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Scan encountered an error.', 'error');
    } finally {
      setScanning(false);
    }
  };

  // 3. Update Status
  const handleUpdateStatus = async (jobId: string, status: Job['status']) => {
    try {
      const job = await api.updateJobStatus(jobId, status);
      setJobs((prev) => prev.map((j) => (j.id === jobId ? job : j)));
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob(job);
      }
      showNotif(`Application status updated to ${status}.`, 'success');
    } catch (_e) {
      showNotif('Failed to update status.', 'error');
    }
  };

  // 4. Save notes
  const handleSaveNotes = async (jobId: string, notes: string) => {
    try {
      const job = await api.updateJobNotes(jobId, notes);
      setJobs((prev) => prev.map((j) => (j.id === jobId ? job : j)));
      showNotif('Notes saved successfully.', 'success');
    } catch (_e) {
      showNotif('Failed to save notes.', 'error');
    }
  };

  // 5. Tailor Resume/Cover Letter with AI
  const handleTailorJob = async (jobId: string) => {
    if (profile && !isProfileCompleteForMatching(profile)) {
      showNotif('Complete your profile before tailoring (Profile tab).', 'error');
      setActiveTab('profile');
      return;
    }
    setTailoringId(jobId);
    showNotif('Tailoring resume: reordering skills and bullets for this job...', 'info');
    try {
      const result = await api.tailorJob(jobId);
      setJobs((prev) => prev.map((j) => (j.id === jobId ? result.job : j)));
      setSelectedJob(result.job);
      setTailoredResumeMeta(result.resume ?? null);
      setActiveTab('tailor');
      showNotif(
        result.resume?.pdfUrl
          ? 'Resume tailored and PDF compiled. Preview or download in the Tailor tab.'
          : 'Resume tailored. LaTeX preview is ready in the Tailor tab.',
        'success',
      );
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Failed to tailor resume.', 'error');
    } finally {
      setTailoringId(null);
    }
  };

  // 6. Save tailored changes manually (LaTeX editor)
  const handleSaveTailored = async (latex: string, coverLetter: string) => {
    if (!selectedJob) return;
    try {
      const job = await api.saveTailoredJob(selectedJob.id, {
        tailoredResumeLaTeX: latex,
        tailoredCoverLetter: coverLetter,
      });
      setJobs((prev) => prev.map((j) => (j.id === selectedJob.id ? job : j)));
      setSelectedJob(job);
      showNotif('Tailored resume code modifications saved successfully.', 'success');
    } catch (_e) {
      showNotif('Failed to save tailored changes.', 'error');
    }
  };

  // 7. Manual job import submit
  const handleManualImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newManualJob.title || !newManualJob.company || !newManualJob.description) {
      showNotif('Please complete all required fields.', 'error');
      return;
    }
    showNotif('Importing job description & computing AI Match Score...', 'info');
    try {
      const job = await api.addCustomJob(newManualJob);
      await fetchJobs();
      setManualImportOpen(false);
      setNewManualJob({
        title: '',
        company: '',
        location: '',
        remoteType: 'Remote',
        url: '',
        description: '',
      });
      showNotif(`Job import complete. Ranked with Match Score of ${job.score}%.`, 'success');
      setSelectedJob(job);
    } catch (_e) {
      showNotif('Failed to manually import job.', 'error');
    }
  };

  // 8. Add Scheduled Interview
  const handleAddInterview = async (interviewData: Omit<Interview, 'id' | 'status'>) => {
    try {
      await api.addInterview(interviewData);
      await fetchJobs();
      showNotif('Upcoming interview round booked successfully!', 'success');
    } catch (_e) {
      showNotif('Failed to schedule interview.', 'error');
    }
  };

  // 9. Update Interview Status
  const handleUpdateInterviewStatus = async (id: string, status: Interview['status']) => {
    try {
      await api.updateInterviewStatus(id, status);
      await fetchJobs();
      showNotif(`Interview round status transitioned to ${status}.`, 'success');
    } catch (_e) {
      showNotif('Failed to save interview status.', 'error');
    }
  };

  const handleSaveProfile = async (options?: { rescan?: boolean }) => {
    if (!profileForm) return;
    setSavingProfile(true);
    try {
      const saved = await api.saveProfile(profileForm, options);
      setProfile(saved);
      setProfileForm(saved);
      const rescanNote = options?.rescan ? ' Scan insights re-score was requested.' : '';
      showNotif(`Profile saved and master resume regenerated.${rescanNote}`, 'success');
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Failed to save profile.', 'error');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleImportProfile = async (payload: Partial<Profile>) => {
    setSavingProfile(true);
    try {
      const imported = await api.importProfile(payload);
      setProfile(imported);
      setProfileForm(imported);
      showNotif('Profile imported successfully. Review fields and save.', 'success');
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Failed to import profile.', 'error');
    } finally {
      setSavingProfile(false);
    }
  };

  const filteredJobs = filterJobs(jobs, filters);
  const sourceOptions = [...new Set(jobs.map((job) => job.source).filter(Boolean))].sort();
  const roleOptions = [
    ...new Set(jobs.map((job) => job.canonicalRole).filter(Boolean)),
  ].sort() as string[];

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-800 overflow-hidden">
      {/* 1. Sidebar Panel */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col justify-between shrink-0 border-r border-slate-800">
        <div>
          {/* Logo and App Title */}
          <div className="p-6 border-b border-slate-800 flex items-center gap-2.5">
            <div className="p-2 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
              <Briefcase className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <h1 className="text-sm font-extrabold tracking-wide uppercase text-slate-100">
                AI Job Hunter
              </h1>
              <p className="text-[10px] text-slate-500 font-bold uppercase mt-0.5">
                Autonomous Career Agent
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Briefcase className="h-4 w-4" />
              Job Leads
            </button>

            <button
              onClick={() => setActiveTab('scanInsights')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'scanInsights'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Radar className="h-4 w-4" />
              Scan Insights
            </button>

            <button
              onClick={() => setActiveTab('tailor')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'tailor'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <FileText className="h-4 w-4" />
              Tailoring Suite
            </button>

            <button
              onClick={() => setActiveTab('interviews')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'interviews'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Calendar className="h-4 w-4" />
              Interview Prep
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'analytics'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <BarChart2 className="h-4 w-4" />
              Analytics & KPI
            </button>

            <button
              onClick={() => setActiveTab('profile')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'profile'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <User className="h-4 w-4" />
              Profile & Settings
            </button>
          </nav>
        </div>

        {/* User profile Summary footer */}
        {profile?.fullName && (
          <div className="p-4 border-t border-slate-800 bg-slate-950/40 m-4 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 bg-indigo-500 rounded-full flex items-center justify-center text-xs font-bold text-white uppercase">
                {getProfileInitials(profile.fullName)}
              </div>
              <div className="overflow-hidden">
                <div className="text-xs font-bold truncate text-slate-200">{profile.fullName}</div>
                <div className="text-[10px] text-slate-500 truncate mt-0.5">{profile.email}</div>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* 2. Main Workspace */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Banner Alert Toast */}
        {notif && (
          <div
            className={`p-3 text-xs font-medium text-center flex items-center justify-center gap-2 border-b transition-all ${
              notif.type === 'success'
                ? 'bg-emerald-50 text-emerald-800 border-emerald-100'
                : notif.type === 'error'
                  ? 'bg-rose-50 text-rose-800 border-rose-100'
                  : 'bg-indigo-50 text-indigo-800 border-indigo-100'
            }`}
          >
            <Info className="h-4 w-4 shrink-0" />
            <span>{notif.message}</span>
          </div>
        )}

        {/* Content Area */}
        <div className="flex-1 p-6 md:p-8 overflow-auto">
          {/* TAB 1: Job Leads */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Header block with controls */}
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">
                    Career Leads & Discovery
                  </h2>
                  <p className="text-xs text-slate-500 mt-1">
                    Discover high-priority engineering openings with enriched match insights, score
                    breakdowns, and resume guidance.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-2.5">
                  <button
                    onClick={() => setManualImportOpen(true)}
                    className="bg-white border border-slate-200 text-slate-700 text-xs px-3.5 py-2 rounded-lg font-medium shadow-sm hover:bg-slate-50 transition-colors flex items-center gap-1.5"
                  >
                    <Plus className="h-4 w-4" />
                    Paste Job Description
                  </button>
                  <button
                    onClick={handleScan}
                    disabled={scanning}
                    className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-75 text-white text-xs px-3.5 py-2 rounded-lg font-semibold shadow-sm transition-all flex items-center gap-1.5"
                  >
                    <RefreshCw className={`h-4 w-4 ${scanning ? 'animate-spin' : ''}`} />
                    {scanning ? 'Scanning Boards...' : 'Scan Career Boards'}
                  </button>
                </div>
              </div>

              <JobFilters
                filters={filters}
                sources={sourceOptions}
                roles={roleOptions}
                onChange={(patch) => setFilters((prev) => ({ ...prev, ...patch }))}
              />

              {/* Feed List Grid */}
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">
                {/* Leads Column */}
                <div className="xl:col-span-2 space-y-4">
                  {filteredJobs.length === 0 ? (
                    <div className="bg-white p-12 text-center rounded-xl border border-dashed border-slate-200 space-y-3">
                      <Briefcase className="h-10 w-10 text-slate-300 mx-auto" />
                      <h4 className="text-sm font-bold text-slate-700">
                        No matching career leads found
                      </h4>
                      <p className="text-xs text-slate-400 max-w-sm mx-auto">
                        Try broadening search parameters or click "Scan Career Boards" to discover
                        fresh listings.
                      </p>
                    </div>
                  ) : (
                    filteredJobs.map((job) => (
                      <div
                        key={job.id}
                        onClick={() => setSelectedJob(job)}
                        className={`bg-white rounded-xl border p-5 flex flex-col justify-between hover:shadow-md transition-all cursor-pointer ${
                          selectedJob && selectedJob.id === job.id
                            ? 'border-indigo-500 ring-1 ring-indigo-500/10 shadow-sm'
                            : 'border-slate-100'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide font-mono">
                                {job.source}
                              </span>
                              <span className="text-slate-300">&bull;</span>
                              <span className="text-[10px] text-slate-500 font-semibold">
                                {new Date(job.postedAt).toLocaleDateString([], {
                                  month: 'short',
                                  day: 'numeric',
                                })}
                              </span>
                            </div>

                            <h3 className="text-sm font-bold text-slate-800 mt-1 hover:text-indigo-600 transition-colors">
                              {job.title}
                            </h3>
                            <p className="text-xs font-semibold text-slate-500 mt-0.5">
                              {job.company}
                            </p>
                            <div className="flex flex-wrap gap-1.5 mt-2">
                              {job.canonicalRole && (
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold uppercase">
                                  {job.canonicalRole}
                                </span>
                              )}
                              {job.priority && (
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-bold uppercase">
                                  {job.priority}
                                </span>
                              )}
                              {job.primaryStack && (
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-50 border border-slate-200 text-slate-600 font-medium">
                                  {job.primaryStack}
                                </span>
                              )}
                              {job.remoteType === 'Remote' && (
                                <span
                                  className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${
                                    (job.matchInsights?.remoteMatchScore ?? 0) >= 90
                                      ? 'bg-emerald-50 text-emerald-700'
                                      : 'bg-amber-50 text-amber-700'
                                  }`}
                                >
                                  {(job.matchInsights?.remoteMatchScore ?? 0) >= 90
                                    ? 'Worldwide fit'
                                    : 'Check region'}
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Fit Score Badge */}
                          {job.score !== undefined && (
                            <div
                              className={`shrink-0 px-3 py-1.5 rounded-lg text-center ${
                                job.score >= 85
                                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                                  : job.score >= 70
                                    ? 'bg-amber-50 text-amber-700 border border-amber-100'
                                    : 'bg-slate-100 text-slate-600'
                              }`}
                            >
                              <div className="text-[10px] font-bold uppercase tracking-wider leading-none">
                                Match
                              </div>
                              <div className="text-base font-extrabold leading-none mt-1">
                                {job.score}%
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Metadata Row */}
                        <div className="flex flex-wrap items-center gap-4 mt-4 text-[11px] text-slate-500 font-mono">
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3.5 w-3.5 text-slate-400" />
                            {job.location}
                          </span>

                          {job.salaryEstimate && (
                            <span className="flex items-center gap-1">
                              <DollarSign className="h-3.5 w-3.5 text-slate-400" />
                              {job.salaryEstimate}
                            </span>
                          )}

                          {job.seniority && (
                            <span className="flex items-center gap-1 bg-slate-100 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase text-slate-600">
                              {job.seniority}
                            </span>
                          )}
                        </div>

                        {/* Extracted Skills tags */}
                        {job.extractedSkills && job.extractedSkills.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-4">
                            {job.extractedSkills.slice(0, 5).map((skill) => (
                              <span
                                key={skill}
                                className="bg-slate-50 border border-slate-200 text-slate-600 text-[10px] px-2 py-0.5 rounded-md font-medium"
                              >
                                {skill}
                              </span>
                            ))}
                            {job.extractedSkills.length > 5 && (
                              <span className="text-[10px] text-slate-400 font-medium pl-1 self-center">
                                +{job.extractedSkills.length - 5} more
                              </span>
                            )}
                          </div>
                        )}

                        {/* Quick state controls */}
                        <div
                          className="flex items-center justify-between gap-3 pt-4 border-t border-slate-50 mt-4"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] font-bold text-slate-400 uppercase">
                              Status:
                            </span>
                            <select
                              value={job.status}
                              onChange={(e) =>
                                handleUpdateStatus(job.id, e.target.value as Job['status'])
                              }
                              className="bg-white border border-slate-200 text-[11px] rounded px-1.5 py-1 font-semibold focus:outline-none"
                            >
                              <option value="New">New Lead</option>
                              <option value="Shortlisted">Shortlisted</option>
                              <option value="Applied">Applied</option>
                              <option value="Interviewing">Interviewing</option>
                              <option value="Offer">Offer</option>
                              <option value="Rejected">Rejected</option>
                              <option value="Ignored">Ignored</option>
                            </select>
                          </div>

                          <div className="flex gap-2">
                            {job.status === 'Shortlisted' && (
                              <span className="bg-indigo-50 text-indigo-700 text-[10px] px-2 py-1 rounded font-bold uppercase border border-indigo-100 flex items-center gap-1 animate-pulse">
                                <Sparkles className="h-3 w-3" /> Ready to Tailor
                              </span>
                            )}

                            {job.tailoredResumeLaTeX && (
                              <span className="bg-emerald-50 text-emerald-700 text-[10px] px-2 py-1 rounded font-bold uppercase border border-emerald-100 flex items-center gap-1">
                                <FileCheck className="h-3 w-3" /> CV Generated
                              </span>
                            )}

                            <button
                              onClick={() => setSelectedJob(job)}
                              className="text-indigo-600 text-[11px] font-bold hover:underline flex items-center gap-0.5"
                            >
                              Deep Analyze <ChevronRight className="h-3 w-3" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <JobDetailPanel
                  job={selectedJob}
                  tailoring={tailoringId === selectedJob?.id}
                  profileComplete={profile ? isProfileCompleteForMatching(profile) : false}
                  onClose={() => setSelectedJob(null)}
                  onTailor={handleTailorJob}
                  onSaveNotes={handleSaveNotes}
                />
              </div>
            </div>
          )}

          {activeTab === 'scanInsights' && <ScanInsightsView />}

          {/* TAB 2: Tailor Suite (Split screen previewer) */}
          {activeTab === 'tailor' && (
            <div className="h-full flex flex-col space-y-4">
              {/* Help message if no job chosen or selected job lacks tailoring */}
              {!selectedJob ||
              (!selectedJob.tailoredResumeLaTeX && !selectedJob.tailoredCoverLetter) ? (
                <div className="bg-white rounded-xl border border-slate-100 p-8 text-center max-w-2xl mx-auto space-y-4">
                  <Sparkles className="h-12 w-12 text-indigo-400 mx-auto" />
                  <h3 className="text-base font-bold text-slate-800">
                    No tailored workspace loaded
                  </h3>
                  <p className="text-xs text-slate-500">
                    Step 1: Complete your profile. Step 2: Select a job lead and click Tailor. Step
                    3: Preview the tailored resume here and download the PDF when available.
                  </p>
                  <button
                    onClick={() => setActiveTab('dashboard')}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-4 py-2 rounded-lg font-medium shadow-sm transition-colors"
                  >
                    Go back to Job Leads
                  </button>
                </div>
              ) : (
                <div className="flex-1 overflow-hidden">
                  <ResumePreview
                    job={selectedJob}
                    pdfUrl={tailoredResumeMeta?.pdfUrl ?? undefined}
                    onSaveTailored={handleSaveTailored}
                    onApplyDirectly={() => {
                      if (selectedJob.url) {
                        window.open(selectedJob.url, '_blank');
                      }
                    }}
                  />
                </div>
              )}
            </div>
          )}

          {/* TAB 3: Interview Prep */}
          {activeTab === 'interviews' && (
            <InterviewTracker
              interviews={interviews}
              jobs={jobs}
              onAddInterview={handleAddInterview}
              onUpdateStatus={handleUpdateInterviewStatus}
            />
          )}

          {/* TAB 4: Analytics */}
          {activeTab === 'analytics' && <AnalyticsView jobs={jobs} interviews={interviews} />}

          {/* TAB 5: Profile & Settings */}
          {activeTab === 'profile' && profileForm && (
            <ProfileView
              profile={profileForm}
              saving={savingProfile}
              onChange={setProfileForm}
              onSave={handleSaveProfile}
              onImport={handleImportProfile}
            />
          )}
        </div>
      </main>

      {/* Manual Import Overlay Form Modal */}
      {manualImportOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex justify-center items-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl border border-slate-200 max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-5 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-500" />
                <h3 className="text-sm font-bold text-slate-900">Paste External Job Description</h3>
              </div>
              <button
                onClick={() => setManualImportOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleManualImport} className="p-5 flex-1 overflow-auto space-y-4">
              <p className="text-xs text-slate-500 leading-relaxed">
                Found a job on LinkedIn, Indeed, or a corporate blog? Paste the requirements here.
                The AI matcher will analyze skills and score suitability.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-600 uppercase">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={newManualJob.title}
                    onChange={(e) => setNewManualJob({ ...newManualJob, title: e.target.value })}
                    placeholder="e.g. Senior DevOps Consultant"
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-600 uppercase">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={newManualJob.company}
                    onChange={(e) => setNewManualJob({ ...newManualJob, company: e.target.value })}
                    placeholder="e.g. Globant India"
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-600 uppercase">
                    Geographical Location
                  </label>
                  <input
                    type="text"
                    value={newManualJob.location}
                    onChange={(e) => setNewManualJob({ ...newManualJob, location: e.target.value })}
                    placeholder="e.g. New York, NY (Hybrid)"
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-600 uppercase">
                    Working Setting
                  </label>
                  <select
                    value={newManualJob.remoteType}
                    onChange={(e) =>
                      setNewManualJob({
                        ...newManualJob,
                        remoteType: e.target.value as Job['remoteType'],
                      })
                    }
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="Remote">Remote</option>
                    <option value="Hybrid">Hybrid</option>
                    <option value="On-site">On-site</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-600 uppercase">
                  Job Board / Referral URL
                </label>
                <input
                  type="url"
                  value={newManualJob.url}
                  onChange={(e) => setNewManualJob({ ...newManualJob, url: e.target.value })}
                  placeholder="https://company.com/career/post"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-600 uppercase">
                  Full Job Description Requirements *
                </label>
                <textarea
                  required
                  value={newManualJob.description}
                  onChange={(e) =>
                    setNewManualJob({ ...newManualJob, description: e.target.value })
                  }
                  placeholder="Paste the complete text from the job board posting here..."
                  rows={6}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none font-sans"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setManualImportOpen(false)}
                  className="bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Discard
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-5 py-2 rounded-lg font-semibold shadow-sm transition-colors"
                >
                  Analyze & Rank Lead
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
