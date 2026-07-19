import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  Calendar,
  BarChart2,
  User,
  Plus,
  RefreshCw,
  ChevronRight,
  X,
  Sparkles,
  MapPin,
  DollarSign,
  Info,
  Radar,
} from 'lucide-react';
import * as api from './api/client';
import { getProfileInitials } from './api/defaultProfile';
import ProfileView from './components/profile/ProfileView';
import { Profile, Job, Interview } from './types';
import AnalyticsView from './components/AnalyticsView';
import InterviewTracker from './components/InterviewTracker';
import JobDetailPanel from './components/JobDetailPanel';
import JobFilters, { filterJobs, type JobFilterState } from './components/JobFilters';
import ScanInsightsView from './components/ScanInsightsView';

export default function App() {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'scanInsights' | 'interviews' | 'analytics' | 'profile'
  >('dashboard');

  // App States
  const [profile, setProfile] = useState<Profile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [scanning, setScanning] = useState(false);

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

  const handleScan = async () => {
    setScanning(true);
    try {
      const res = await api.scanJobs();
      showNotif(
        `Scan completed! Discovered ${res.addedCount || 0} qualifying high-match career leads.`,
        'success',
      );
      await fetchJobs();
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Scan request failed.', 'error');
    } finally {
      setScanning(false);
    }
  };

  const handleManualImport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const added = await api.addCustomJob({
        title: newManualJob.title,
        company: newManualJob.company,
        location: newManualJob.location || 'Remote',
        remoteType: newManualJob.remoteType,
        url: newManualJob.url || '',
        description: newManualJob.description,
      });
      showNotif(
        `Imported "${added.title}" at ${added.company}. AI match rescore triggered!`,
        'success',
      );
      setManualImportOpen(false);
      setNewManualJob({
        title: '',
        company: '',
        location: '',
        remoteType: 'Remote',
        url: '',
        description: '',
      });
      await fetchJobs();
      setSelectedJob(added);
    } catch (err) {
      showNotif(err instanceof Error ? err.message : 'Manual import failed.', 'error');
    }
  };

  const handleUpdateStatus = async (jobId: string, status: Job['status'], note?: string) => {
    try {
      const updated = await api.updateJobStatus(jobId, status, note);
      setJobs((prev) => prev.map((j) => (j.id === jobId ? updated : j)));
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob(updated);
      }
      showNotif(
        `Job status set to "${status}"${note ? ` with note "${note}"` : ''}. Action recorded.`,
        'success',
      );
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Failed to update job status.', 'error');
    }
  };

  const handleSaveNotes = async (jobId: string, notes: string) => {
    try {
      const updated = await api.updateJobNotes(jobId, notes);
      setJobs((prev) => prev.map((j) => (j.id === jobId ? updated : j)));
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob(updated);
      }
      showNotif('Notes saved.', 'success');
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Failed to save notes.', 'error');
    }
  };

  const handleAddInterview = async (interviewData: Omit<Interview, 'id' | 'status'>) => {
    try {
      await api.addInterview(interviewData);
      showNotif('Upcoming interview round recorded.', 'success');
      await fetchJobs();
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Failed to add interview.', 'error');
    }
  };

  const handleUpdateInterviewStatus = async (interviewId: string, status: Interview['status']) => {
    try {
      await api.updateInterviewStatus(interviewId, status);
      showNotif(`Interview status updated to "${status}".`, 'success');
      await fetchJobs();
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Failed to update interview status.', 'error');
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
    <div className="flex flex-col md:flex-row h-screen bg-slate-50 font-sans text-slate-800 overflow-hidden">
      {/* Mobile Glass Header (< md) */}
      <header className="md:hidden glass-nav border-b border-slate-200 sticky top-0 z-40 px-4 py-3 flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-indigo-600 rounded-lg text-white">
            <Briefcase className="h-4 w-4" />
          </div>
          <span className="text-sm font-extrabold tracking-tight text-slate-900">
            AI Job Hunter
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleScan}
            disabled={scanning}
            className="bg-indigo-600 hover:bg-indigo-700 text-white text-[11px] font-bold px-2.5 py-1.5 rounded-lg flex items-center gap-1 shadow-xs disabled:opacity-75"
          >
            <RefreshCw className={`h-3 w-3 ${scanning ? 'animate-spin' : ''}`} />
            <span>{scanning ? 'Scanning…' : 'Scan'}</span>
          </button>

          {profile?.fullName && (
            <div className="h-7 w-7 bg-slate-900 text-white rounded-full flex items-center justify-center text-[10px] font-bold">
              {getProfileInitials(profile.fullName)}
            </div>
          )}
        </div>
      </header>

      {/* Desktop Sidebar Panel (>= md) */}
      <aside className="hidden md:flex md:w-60 lg:w-64 bg-slate-950 text-white flex-col justify-between shrink-0 border-r border-slate-800/80 shadow-lg">
        <div>
          {/* Logo and App Title */}
          <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
            <div className="p-2 bg-indigo-500/20 rounded-xl border border-indigo-500/30 text-indigo-400">
              <Briefcase className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-sm font-extrabold tracking-wide uppercase text-slate-100">
                AI Job Hunter
              </h1>
              <p className="text-[10px] text-slate-400 font-bold uppercase mt-0.5 tracking-wider">
                Autonomous Career Agent
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold tracking-wide uppercase transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <Briefcase className="h-4 w-4" />
              Job Leads
            </button>

            <button
              onClick={() => setActiveTab('scanInsights')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold tracking-wide uppercase transition-all ${
                activeTab === 'scanInsights'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <Radar className="h-4 w-4" />
              Scan Insights
            </button>

            <button
              onClick={() => setActiveTab('interviews')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold tracking-wide uppercase transition-all ${
                activeTab === 'interviews'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <Calendar className="h-4 w-4" />
              Interview Prep
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold tracking-wide uppercase transition-all ${
                activeTab === 'analytics'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <BarChart2 className="h-4 w-4" />
              Analytics & KPI
            </button>

            <button
              onClick={() => setActiveTab('profile')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold tracking-wide uppercase transition-all ${
                activeTab === 'profile'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <User className="h-4 w-4" />
              Profile & Settings
            </button>
          </nav>
        </div>

        {/* User profile Summary footer */}
        {profile?.fullName && (
          <div className="p-3.5 border-t border-slate-800/80 bg-slate-900/50 m-3 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 bg-indigo-500 rounded-full flex items-center justify-center text-xs font-bold text-white uppercase shrink-0 shadow-xs">
                {getProfileInitials(profile.fullName)}
              </div>
              <div className="overflow-hidden">
                <div className="text-xs font-bold truncate text-slate-200">{profile.fullName}</div>
                <div className="text-[10px] text-slate-400 truncate mt-0.5">{profile.email}</div>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Main Workspace Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden pb-16 md:pb-0">
        {/* Banner Alert Toast */}
        {notif && (
          <div
            className={`p-3 text-xs font-semibold text-center flex items-center justify-center gap-2 border-b animate-slide-up ${
              notif.type === 'success'
                ? 'bg-emerald-500 text-white border-emerald-600'
                : notif.type === 'error'
                  ? 'bg-rose-500 text-white border-rose-600'
                  : 'bg-indigo-600 text-white border-indigo-700'
            }`}
          >
            <Info className="h-4 w-4 shrink-0" />
            <span>{notif.message}</span>
            <button onClick={() => setNotif(null)} className="ml-auto p-0.5 hover:opacity-80">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )}

        {/* Content View Container */}
        <div className="flex-1 p-4 sm:p-6 lg:p-8 overflow-auto">
          {/* TAB 1: Job Leads */}
          {activeTab === 'dashboard' && (
            <div className="space-y-5 max-w-7xl mx-auto">
              {/* Header block controls */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-xs">
                <div>
                  <h2 className="text-xl sm:text-2xl font-black tracking-tight text-slate-900">
                    Career Leads & Discovery
                  </h2>
                  <p className="text-xs text-slate-500 mt-1 font-medium">
                    Discover high-priority engineering openings enriched with AI match insights,
                    score breakdowns, and ATS suggestions.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-2 sm:gap-2.5 pt-2 sm:pt-0">
                  <button
                    onClick={() => setManualImportOpen(true)}
                    className="flex-1 sm:flex-none bg-slate-50 border border-slate-200 text-slate-700 text-xs px-3.5 py-2.5 rounded-xl font-bold hover:bg-slate-100 transition-all flex items-center justify-center gap-1.5 active:scale-95"
                  >
                    <Plus className="h-4 w-4 text-indigo-600" />
                    <span>Paste Job Description</span>
                  </button>
                  <button
                    onClick={handleScan}
                    disabled={scanning}
                    className="flex-1 sm:flex-none bg-indigo-600 hover:bg-indigo-700 disabled:opacity-75 text-white text-xs px-4 py-2.5 rounded-xl font-bold shadow-md shadow-indigo-600/20 transition-all flex items-center justify-center gap-1.5 active:scale-95"
                  >
                    <RefreshCw className={`h-4 w-4 ${scanning ? 'animate-spin' : ''}`} />
                    <span>{scanning ? 'Scanning Boards…' : 'Scan Career Boards'}</span>
                  </button>
                </div>
              </div>

              <JobFilters
                filters={filters}
                sources={sourceOptions}
                roles={roleOptions}
                onChange={(patch) => setFilters((prev) => ({ ...prev, ...patch }))}
              />

              {/* Feed List & Detail Panel Container */}
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">
                {/* Leads Feed Column */}
                <div className="xl:col-span-2 space-y-3.5">
                  {filteredJobs.length === 0 ? (
                    <div className="bg-white p-12 text-center rounded-2xl border border-dashed border-slate-200 space-y-3">
                      <Briefcase className="h-10 w-10 text-slate-300 mx-auto" />
                      <h4 className="text-sm font-bold text-slate-800">
                        No matching career leads found
                      </h4>
                      <p className="text-xs text-slate-500 max-w-sm mx-auto">
                        Try broadening search parameters or click "Scan Career Boards" to discover
                        fresh listings.
                      </p>
                    </div>
                  ) : (
                    filteredJobs.map((job) => (
                      <div
                        key={job.id}
                        onClick={() => setSelectedJob(job)}
                        className={`bg-white rounded-2xl border p-4 sm:p-5 flex flex-col justify-between hover:shadow-md transition-all cursor-pointer ${
                          selectedJob && selectedJob.id === job.id
                            ? 'border-indigo-500 ring-2 ring-indigo-500/10 shadow-sm'
                            : 'border-slate-200/80 hover:border-indigo-200'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="space-y-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-[10px] font-bold text-indigo-600 uppercase tracking-wide font-mono bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-100">
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

                            <h3 className="text-base font-extrabold text-slate-900 hover:text-indigo-600 transition-colors">
                              {job.title}
                            </h3>
                            <p className="text-xs font-semibold text-slate-600">{job.company}</p>
                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {job.canonicalRole && (
                                <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-bold uppercase">
                                  {job.canonicalRole}
                                </span>
                              )}
                              {job.priority && (
                                <span className="text-[10px] px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-200/60 font-bold uppercase">
                                  {job.priority} Priority
                                </span>
                              )}
                              {job.primaryStack && (
                                <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200 text-slate-600 font-medium">
                                  {job.primaryStack}
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Match Fit Score Badge */}
                          {job.score !== undefined && (
                            <div
                              className={`shrink-0 px-3 py-2 rounded-xl text-center shadow-2xs ${
                                job.score >= 85
                                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                                  : job.score >= 70
                                    ? 'bg-amber-50 text-amber-800 border border-amber-200'
                                    : 'bg-slate-100 text-slate-700 border border-slate-200'
                              }`}
                            >
                              <div className="text-[9px] font-black uppercase tracking-wider leading-none">
                                Match
                              </div>
                              <div className="text-lg font-black leading-none mt-1">
                                {job.score}%
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Metadata Row */}
                        <div className="flex flex-wrap items-center gap-4 mt-3.5 pt-3 border-t border-slate-100 text-[11px] text-slate-500 font-mono">
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3.5 w-3.5 text-slate-400" />
                            {job.location}
                          </span>

                          {job.salaryEstimate && (
                            <span className="flex items-center gap-1">
                              <DollarSign className="h-3.5 w-3.5 text-emerald-600" />
                              <span className="text-emerald-700 font-bold">
                                {job.salaryEstimate}
                              </span>
                            </span>
                          )}

                          {job.seniority && (
                            <span className="bg-slate-100 px-2 py-0.5 rounded text-[10px] font-bold uppercase text-slate-600">
                              {job.seniority}
                            </span>
                          )}
                        </div>

                        {/* Extracted Skills tags */}
                        {job.extractedSkills && job.extractedSkills.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-3">
                            {job.extractedSkills.slice(0, 5).map((skill) => (
                              <span
                                key={skill}
                                className="bg-slate-50 border border-slate-200 text-slate-600 text-[10px] px-2 py-0.5 rounded-md font-semibold"
                              >
                                {skill}
                              </span>
                            ))}
                            {job.extractedSkills.length > 5 && (
                              <span className="text-[10px] text-slate-400 font-semibold pl-1 self-center">
                                +{job.extractedSkills.length - 5} more
                              </span>
                            )}
                          </div>
                        )}

                        {/* Quick Action Controls */}
                        <div
                          className="flex items-center justify-between gap-3 pt-3 border-t border-slate-100 mt-3"
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
                              className="bg-white border border-slate-200 text-slate-700 text-xs rounded-lg px-2 py-1 font-bold focus:ring-1 focus:ring-indigo-500 focus:outline-none"
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

                          <button
                            onClick={() => setSelectedJob(job)}
                            className="text-indigo-600 text-xs font-bold hover:text-indigo-800 flex items-center gap-1 py-1 px-2.5 rounded-lg hover:bg-indigo-50 transition-colors"
                          >
                            <span>Inspect & Notes</span>
                            <ChevronRight className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Desktop Detail Panel Column (>= xl) */}
                <div className="hidden xl:block">
                  <JobDetailPanel
                    job={selectedJob}
                    onClose={() => setSelectedJob(null)}
                    onSaveNotes={handleSaveNotes}
                    onUpdateStatus={handleUpdateStatus}
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'scanInsights' && <ScanInsightsView />}

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

      {/* Mobile/Tablet Slide-over Modal Drawer (< xl) when Job is selected */}
      {selectedJob && (
        <div className="xl:hidden fixed inset-0 z-50 flex justify-end">
          <div
            className="mobile-drawer-overlay animate-fade-in"
            onClick={() => setSelectedJob(null)}
          />
          <div className="mobile-drawer-content animate-slide-up p-4 sm:p-6 overflow-auto">
            <div className="flex justify-end pb-2">
              <button
                onClick={() => setSelectedJob(null)}
                className="p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <JobDetailPanel
              job={selectedJob}
              onClose={() => setSelectedJob(null)}
              onSaveNotes={handleSaveNotes}
              onUpdateStatus={handleUpdateStatus}
            />
          </div>
        </div>
      )}

      {/* Mobile Bottom Sticky Navigation Bar (< md) */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 glass-nav border-t border-slate-200/80 z-40 px-2 py-1.5 flex items-center justify-around shadow-lg">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase transition-all ${
            activeTab === 'dashboard' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-500'
          }`}
        >
          <Briefcase className="h-4 w-4" />
          <span>Leads</span>
        </button>

        <button
          onClick={() => setActiveTab('scanInsights')}
          className={`flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase transition-all ${
            activeTab === 'scanInsights' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-500'
          }`}
        >
          <Radar className="h-4 w-4" />
          <span>Insights</span>
        </button>

        <button
          onClick={() => setActiveTab('interviews')}
          className={`flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase transition-all ${
            activeTab === 'interviews' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-500'
          }`}
        >
          <Calendar className="h-4 w-4" />
          <span>Interviews</span>
        </button>

        <button
          onClick={() => setActiveTab('analytics')}
          className={`flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase transition-all ${
            activeTab === 'analytics' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-500'
          }`}
        >
          <BarChart2 className="h-4 w-4" />
          <span>KPIs</span>
        </button>

        <button
          onClick={() => setActiveTab('profile')}
          className={`flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase transition-all ${
            activeTab === 'profile' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-500'
          }`}
        >
          <User className="h-4 w-4" />
          <span>Profile</span>
        </button>
      </nav>

      {/* Manual Import Overlay Form Modal */}
      {manualImportOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex justify-center items-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-slide-up">
            <div className="p-4 sm:p-5 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-600" />
                <h3 className="text-base font-extrabold text-slate-900">
                  Paste External Job Description
                </h3>
              </div>
              <button
                onClick={() => setManualImportOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1.5 rounded-full hover:bg-slate-100 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form
              onSubmit={handleManualImport}
              className="p-4 sm:p-6 flex-1 overflow-auto space-y-4"
            >
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                Found a job on LinkedIn, Indeed, or a corporate blog? Paste the requirements here.
                The AI matcher will analyze skills and score suitability automatically.
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
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 focus:outline-none"
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
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 focus:outline-none"
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
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 focus:outline-none"
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
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 focus:outline-none"
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
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 focus:outline-none"
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
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 focus:outline-none font-sans leading-relaxed"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setManualImportOpen(false)}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-4 py-2.5 rounded-xl font-bold transition-colors"
                >
                  Discard
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-5 py-2.5 rounded-xl font-bold shadow-md shadow-indigo-600/20 transition-all active:scale-95"
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
