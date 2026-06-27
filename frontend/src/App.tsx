import React, { useState, useEffect } from 'react';
import { 
  Briefcase, Calendar, BarChart2, User, FileText, Search, Filter, 
  Plus, Play, CheckCircle, RefreshCw, ChevronRight, X, Sparkles, 
  MapPin, DollarSign, Clock, FileCheck, HelpCircle, Save, Info, AlertTriangle, ArrowUpRight
} from 'lucide-react';
import * as api from './api/client';
import { Profile, Job, Interview } from './types';
import ResumePreview from './components/ResumePreview';
import AnalyticsView from './components/AnalyticsView';
import InterviewTracker from './components/InterviewTracker';

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'tailor' | 'interviews' | 'analytics' | 'profile'>('dashboard');
  
  // App States
  const [profile, setProfile] = useState<Profile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [scanning, setScanning] = useState(false);
  const [tailoringId, setTailoringId] = useState<string | null>(null);
  
  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [scoreFilter, setScoreFilter] = useState('All');
  const [remoteFilter, setRemoteFilter] = useState('All');

  // Modals & Forms
  const [manualImportOpen, setManualImportOpen] = useState(false);
  const [newManualJob, setNewManualJob] = useState({
    title: '',
    company: '',
    location: '',
    remoteType: 'Remote' as 'Remote' | 'Hybrid' | 'On-site',
    url: '',
    description: ''
  });

  // Profile Form States
  const [profileForm, setProfileForm] = useState<Profile | null>(null);
  const [newSkill, setNewSkill] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);

  // General Notification Log
  const [notif, setNotif] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  const showNotif = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    setNotif({ type, message });
    setTimeout(() => setNotif(null), 5000);
  };

  // 1. Initial Load Sync
  useEffect(() => {
    fetchProfile();
    fetchJobs();
  }, []);

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

  // 2. Scan Careers Boards trigger
  const handleScan = async () => {
    setScanning(true);
    showNotif('Scanning active job boards and target consulting portals...', 'info');
    try {
      const data = await api.scanJobs();
      await fetchJobs();
      showNotif(`Scan completed successfully! Discovered and scored ${data.addedCount} new matching leads.`, 'success');
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
      setJobs(prev => prev.map(j => j.id === jobId ? job : j));
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob(job);
      }
      showNotif(`Application status updated to ${status}.`, 'success');
    } catch (e) {
      showNotif('Failed to update status.', 'error');
    }
  };

  // 4. Save notes
  const handleSaveNotes = async (jobId: string, notes: string) => {
    try {
      const job = await api.updateJobNotes(jobId, notes);
      setJobs(prev => prev.map(j => j.id === jobId ? job : j));
      showNotif('Notes saved successfully.', 'success');
    } catch (e) {
      showNotif('Failed to save notes.', 'error');
    }
  };

  // 5. Tailor Resume/Cover Letter with AI
  const handleTailorJob = async (jobId: string) => {
    setTailoringId(jobId);
    showNotif('Gemini AI is analyzing job keywords and rewriting LaTeX bullets...', 'info');
    try {
      const job = await api.tailorJob(jobId);
      setJobs(prev => prev.map(j => j.id === jobId ? job : j));
      setSelectedJob(job);
      setActiveTab('tailor');
      showNotif('LaTeX Resume and Cover Letter compiled successfully! Check the Tailor Suite.', 'success');
    } catch (e) {
      showNotif(e instanceof Error ? e.message : 'Failed to tailor with AI.', 'error');
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
      setJobs(prev => prev.map(j => j.id === selectedJob.id ? job : j));
      setSelectedJob(job);
      showNotif('Tailored resume code modifications saved successfully.', 'success');
    } catch (e) {
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
      setNewManualJob({ title: '', company: '', location: '', remoteType: 'Remote', url: '', description: '' });
      showNotif(`Job import complete. Ranked with Match Score of ${job.score}%.`, 'success');
      setSelectedJob(job);
    } catch (e) {
      showNotif('Failed to manually import job.', 'error');
    }
  };

  // 8. Add Scheduled Interview
  const handleAddInterview = async (interviewData: Omit<Interview, 'id' | 'status'>) => {
    try {
      await api.addInterview(interviewData);
      await fetchJobs();
      showNotif('Upcoming interview round booked successfully!', 'success');
    } catch (e) {
      showNotif('Failed to schedule interview.', 'error');
    }
  };

  // 9. Update Interview Status
  const handleUpdateInterviewStatus = async (id: string, status: Interview['status']) => {
    try {
      await api.updateInterviewStatus(id, status);
      await fetchJobs();
      showNotif(`Interview round status transitioned to ${status}.`, 'success');
    } catch (e) {
      showNotif('Failed to save interview status.', 'error');
    }
  };

  // 10. Save Profile Settings
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profileForm) return;
    setSavingProfile(true);
    try {
      const saved = await api.saveProfile(profileForm);
      setProfile(saved);
      setProfileForm(saved);
      showNotif('Master Profile and scoring parameters updated successfully.', 'success');
    } catch (e) {
      showNotif('Failed to save profile.', 'error');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleAddSkill = () => {
    if (newSkill && profileForm && !profileForm.skills.includes(newSkill)) {
      setProfileForm({
        ...profileForm,
        skills: [...profileForm.skills, newSkill]
      });
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skill: string) => {
    if (profileForm) {
      setProfileForm({
        ...profileForm,
        skills: profileForm.skills.filter(s => s !== skill)
      });
    }
  };

  // Filter & Search computation
  const filteredJobs = jobs.filter(job => {
    const matchesSearch = 
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (job.extractedSkills && job.extractedSkills.some(s => s.toLowerCase().includes(searchQuery.toLowerCase())));
    
    const matchesStatus = statusFilter === 'All' ? true : job.status === statusFilter;
    
    let matchesScore = true;
    if (scoreFilter === 'Excellent') matchesScore = (job.score || 0) >= 85;
    else if (scoreFilter === 'Good') matchesScore = (job.score || 0) >= 70 && (job.score || 0) < 85;
    else if (scoreFilter === 'Fair') matchesScore = (job.score || 0) < 70;

    const matchesRemote = remoteFilter === 'All' ? true : job.remoteType === remoteFilter;

    return matchesSearch && matchesStatus && matchesScore && matchesRemote;
  });

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
              <h1 className="text-sm font-extrabold tracking-wide uppercase text-slate-100">AI Job Hunter</h1>
              <p className="text-[10px] text-slate-500 font-bold uppercase mt-0.5">Autonomous Career Agent</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'dashboard' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Briefcase className="h-4 w-4" />
              Job Leads
            </button>

            <button
              onClick={() => setActiveTab('tailor')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'tailor' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <FileText className="h-4 w-4" />
              Tailoring Suite
            </button>

            <button
              onClick={() => setActiveTab('interviews')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'interviews' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Calendar className="h-4 w-4" />
              Interview Prep
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'analytics' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <BarChart2 className="h-4 w-4" />
              Analytics & KPI
            </button>

            <button
              onClick={() => setActiveTab('profile')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide uppercase transition-all ${
                activeTab === 'profile' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <User className="h-4 w-4" />
              Profile & Settings
            </button>
          </nav>
        </div>

        {/* User profile Summary footer */}
        {profile && (
          <div className="p-4 border-t border-slate-800 bg-slate-950/40 m-4 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 bg-indigo-500 rounded-full flex items-center justify-center text-xs font-bold text-white uppercase">
                {profile.fullName.split(' ').map(n => n[0]).join('')}
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
          <div className={`p-3 text-xs font-medium text-center flex items-center justify-center gap-2 border-b transition-all ${
            notif.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-100' :
            notif.type === 'error' ? 'bg-rose-50 text-rose-800 border-rose-100' :
            'bg-indigo-50 text-indigo-800 border-indigo-100'
          }`}>
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
                  <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">Career Leads & Discovery</h2>
                  <p className="text-xs text-slate-500 mt-1">Discover high-priority engineering openings, analyze alignment using Gemini, and schedule auto-tailor pipelines.</p>
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

              {/* Filtering Block */}
              <div className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex flex-wrap gap-4 items-center justify-between">
                <div className="flex-1 min-w-[240px] relative">
                  <Search className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    placeholder="Search roles, companies, or key technologies (e.g. Terraform)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-slate-50 pl-9 pr-4 py-2 rounded-lg text-xs border border-slate-200/80 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <Filter className="h-3.5 w-3.5 text-slate-400" />
                    <span className="text-[11px] font-bold text-slate-500 uppercase">Filters:</span>
                  </div>

                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="All">All Statuses</option>
                    <option value="New">New Leads</option>
                    <option value="Shortlisted">Shortlisted</option>
                    <option value="Applied">Applied</option>
                    <option value="Interviewing">Interviewing</option>
                    <option value="Offer">Offers Received</option>
                    <option value="Rejected">Rejected</option>
                  </select>

                  <select
                    value={scoreFilter}
                    onChange={(e) => setScoreFilter(e.target.value)}
                    className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="All">All Match Levels</option>
                    <option value="Excellent">Excellent (&gt;85%)</option>
                    <option value="Good">Good (70-85%)</option>
                    <option value="Fair">Fair (&lt;70%)</option>
                  </select>

                  <select
                    value={remoteFilter}
                    onChange={(e) => setRemoteFilter(e.target.value)}
                    className="bg-slate-50 border border-slate-200 text-slate-600 rounded-lg px-2 py-1.5 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="All">All Settings</option>
                    <option value="Remote">Remote</option>
                    <option value="Hybrid">Hybrid</option>
                    <option value="On-site">On-site</option>
                  </select>
                </div>
              </div>

              {/* Feed List Grid */}
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">
                
                {/* Leads Column */}
                <div className="xl:col-span-2 space-y-4">
                  {filteredJobs.length === 0 ? (
                    <div className="bg-white p-12 text-center rounded-xl border border-dashed border-slate-200 space-y-3">
                      <Briefcase className="h-10 w-10 text-slate-300 mx-auto" />
                      <h4 className="text-sm font-bold text-slate-700">No matching career leads found</h4>
                      <p className="text-xs text-slate-400 max-w-sm mx-auto">Try broading search parameters or click "Scan Career Boards" to discover fresh listings.</p>
                    </div>
                  ) : (
                    filteredJobs.map(job => (
                      <div 
                        key={job.id} 
                        onClick={() => setSelectedJob(job)}
                        className={`bg-white rounded-xl border p-5 flex flex-col justify-between hover:shadow-md transition-all cursor-pointer ${
                          selectedJob && selectedJob.id === job.id ? 'border-indigo-500 ring-1 ring-indigo-500/10 shadow-sm' : 'border-slate-100'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide font-mono">{job.source}</span>
                              <span className="text-slate-300">&bull;</span>
                              <span className="text-[10px] text-slate-500 font-semibold">{new Date(job.postedAt).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
                            </div>
                            
                            <h3 className="text-sm font-bold text-slate-800 mt-1 hover:text-indigo-600 transition-colors">{job.title}</h3>
                            <p className="text-xs font-semibold text-slate-500 mt-0.5">{job.company}</p>
                          </div>

                          {/* Fit Score Badge */}
                          {job.score !== undefined && (
                            <div className={`shrink-0 px-3 py-1.5 rounded-lg text-center ${
                              job.score >= 85 ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' :
                              job.score >= 70 ? 'bg-amber-50 text-amber-700 border border-amber-100' :
                              'bg-slate-100 text-slate-600'
                            }`}>
                              <div className="text-[10px] font-bold uppercase tracking-wider leading-none">Match</div>
                              <div className="text-base font-extrabold leading-none mt-1">{job.score}%</div>
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
                            {job.extractedSkills.slice(0, 5).map(skill => (
                              <span key={skill} className="bg-slate-50 border border-slate-200 text-slate-600 text-[10px] px-2 py-0.5 rounded-md font-medium">
                                {skill}
                              </span>
                            ))}
                            {job.extractedSkills.length > 5 && (
                              <span className="text-[10px] text-slate-400 font-medium pl-1 self-center">+{job.extractedSkills.length - 5} more</span>
                            )}
                          </div>
                        )}

                        {/* Quick state controls */}
                        <div className="flex items-center justify-between gap-3 pt-4 border-t border-slate-50 mt-4" onClick={(e) => e.stopPropagation()}>
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] font-bold text-slate-400 uppercase">Status:</span>
                            <select
                              value={job.status}
                              onChange={(e) => handleUpdateStatus(job.id, e.target.value as Job['status'])}
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

                {/* Sliding details panel / right details view */}
                <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm sticky top-6 space-y-6">
                  {selectedJob ? (
                    <>
                      {/* Top Row Title */}
                      <div className="flex justify-between items-start gap-3 border-b border-slate-50 pb-4">
                        <div>
                          <span className="text-[10px] font-mono font-bold uppercase text-slate-400">{selectedJob.source}</span>
                          <h3 className="text-base font-bold text-slate-800 mt-1">{selectedJob.title}</h3>
                          <p className="text-xs font-semibold text-slate-500 mt-0.5">{selectedJob.company} &bull; {selectedJob.location}</p>
                        </div>
                        <button
                          onClick={() => setSelectedJob(null)}
                          className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>

                      {/* AI Deep Insight Box */}
                      <div className="bg-gradient-to-br from-indigo-50 to-sky-50/50 rounded-xl border border-indigo-100/30 p-4.5 space-y-3.5">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-800 uppercase tracking-wide">
                          <Sparkles className="h-4 w-4 text-indigo-500" />
                          <span>Gemini AI Profile Assessment</span>
                        </div>

                        {selectedJob.fitExplanation ? (
                          <p className="text-xs text-slate-700 leading-relaxed font-medium">{selectedJob.fitExplanation}</p>
                        ) : (
                          <div className="space-y-2">
                            <p className="text-xs text-slate-600 italic">No AI match score has been computed for this custom job yet.</p>
                            <button
                              onClick={() => handleTailorJob(selectedJob.id)}
                              className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-3 py-1.5 rounded-md font-medium"
                            >
                              Analyze Alignment
                            </button>
                          </div>
                        )}

                        {selectedJob.score !== undefined && (
                          <div className="flex items-center justify-between border-t border-indigo-100/40 pt-3 text-xs">
                            <span className="text-slate-500 font-semibold uppercase text-[10px]">Suitability Index:</span>
                            <span className={`font-black uppercase text-xs px-2.5 py-0.5 rounded-full ${
                              selectedJob.score >= 85 ? 'bg-emerald-100 text-emerald-800' :
                              selectedJob.score >= 70 ? 'bg-amber-100 text-amber-800' :
                              'bg-slate-200 text-slate-800'
                            }`}>
                              {selectedJob.score >= 85 ? 'Highly Recommended' : selectedJob.score >= 70 ? 'Feasible Match' : 'High Barrier'}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Action trigger banner */}
                      <div className="space-y-2.5">
                        <button
                          onClick={() => handleTailorJob(selectedJob.id)}
                          disabled={tailoringId === selectedJob.id}
                          className="w-full bg-slate-900 hover:bg-slate-800 disabled:opacity-70 text-white text-xs py-2.5 rounded-lg font-semibold tracking-wide uppercase transition-all shadow-sm flex items-center justify-center gap-1.5"
                        >
                          {tailoringId === selectedJob.id ? (
                            <>
                              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                              <span>Tailoring LaTeX Template...</span>
                            </>
                          ) : (
                            <>
                              <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
                              <span>Tailor Resume & Cover Letter</span>
                            </>
                          )}
                        </button>

                        {selectedJob.url && (
                          <a
                            href={selectedJob.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-full bg-white border border-slate-200 text-slate-700 text-xs py-2.5 rounded-lg font-semibold tracking-wide uppercase transition-all flex items-center justify-center gap-1 hover:bg-slate-50"
                          >
                            <span>Open Career Portal</span>
                            <ArrowUpRight className="h-4 w-4" />
                          </a>
                        )}
                      </div>

                      {/* Notes Box */}
                      <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">My Tracking Notes</label>
                        <textarea
                          placeholder="Write down referral contacts, application login passwords, salary negotiations, or general updates..."
                          defaultValue={selectedJob.notes || ''}
                          onBlur={(e) => handleSaveNotes(selectedJob.id, e.target.value)}
                          className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none min-h-[80px]"
                        />
                      </div>

                      {/* Full Job description scroll block */}
                      <div className="space-y-2 border-t border-slate-50 pt-4">
                        <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Job Description Summary</h4>
                        <div className="text-xs text-slate-600 leading-relaxed max-h-[300px] overflow-auto whitespace-pre-wrap pr-1 font-sans">
                          {selectedJob.description}
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-12 text-slate-400 space-y-3">
                      <Info className="h-8 w-8 text-slate-300 mx-auto" />
                      <p className="text-xs">Select a job lead from the list to view comprehensive Gemini AI assessments, study missing skills keywords, and compile tailored resumes instantly.</p>
                    </div>
                  )}
                </div>

              </div>

            </div>
          )}

          {/* TAB 2: Tailor Suite (Split screen previewer) */}
          {activeTab === 'tailor' && (
            <div className="h-full flex flex-col space-y-4">
              {/* Help message if no job chosen or selected job lacks tailoring */}
              {(!selectedJob || (!selectedJob.tailoredResumeLaTeX && !selectedJob.tailoredCoverLetter)) ? (
                <div className="bg-white rounded-xl border border-slate-100 p-8 text-center max-w-2xl mx-auto space-y-4">
                  <Sparkles className="h-12 w-12 text-indigo-400 mx-auto" />
                  <h3 className="text-base font-bold text-slate-800">No tailored workspace loaded</h3>
                  <p className="text-xs text-slate-500">
                    To tailor your resume, select a high-priority job lead from the **Job Leads** tab, and click **"Tailor Resume & Cover Letter"**. 
                    Gemini will automatically restructure your skills and projects dynamically based on the job requirements.
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
          {activeTab === 'analytics' && (
            <AnalyticsView jobs={jobs} interviews={interviews} />
          )}

          {/* TAB 5: Profile & Settings */}
          {activeTab === 'profile' && profileForm && (
            <form onSubmit={handleSaveProfile} className="space-y-6 max-w-4xl">
              <div>
                <h2 className="text-xl font-bold text-slate-900">Profile & Scoring Parameters</h2>
                <p className="text-xs text-slate-500 mt-1">Configure your master engineering qualifications, list targeted tech keywords, and customize the foundational LaTeX resume template.</p>
              </div>

              {/* Master Credentials */}
              <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Master Personal Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-slate-600 uppercase">Full Name</label>
                    <input
                      type="text"
                      value={profileForm.fullName}
                      onChange={(e) => setProfileForm({ ...profileForm, fullName: e.target.value })}
                      required
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-slate-600 uppercase">Email Address</label>
                    <input
                      type="email"
                      value={profileForm.email}
                      onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                      required
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-slate-600 uppercase">Phone Number</label>
                    <input
                      type="text"
                      value={profileForm.phone}
                      onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-slate-600 uppercase">Geographical Location</label>
                    <input
                      type="text"
                      value={profileForm.location}
                      onChange={(e) => setProfileForm({ ...profileForm, location: e.target.value })}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Skills Tags Setup */}
              <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Profile Skills Inventory</h3>
                
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="e.g. Terraform, Kubernetes, Go..."
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    className="bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none flex-1 max-w-sm"
                  />
                  <button
                    type="button"
                    onClick={handleAddSkill}
                    className="bg-slate-900 text-white text-xs px-4 py-2 rounded-lg font-semibold hover:bg-slate-850"
                  >
                    Add Skill
                  </button>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-2">
                  {profileForm.skills.map(skill => (
                    <span key={skill} className="bg-slate-100 border border-slate-200 text-slate-700 text-xs px-2.5 py-1 rounded-md flex items-center gap-1.5 font-medium">
                      {skill}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill)}
                        className="text-slate-400 hover:text-slate-600 font-bold"
                      >
                        &times;
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Master Resume LaTeX Editor */}
              <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Master LaTeX Template Source</h3>
                  <span className="text-[10px] text-indigo-600 font-mono font-bold">Standard starting code template</span>
                </div>
                
                <p className="text-xs text-slate-500">
                  This LaTeX code constitutes your baseline resume. When Gemini optimizes your resume for any shortlisted target job, 
                  it rewrites this LaTeX code (re-emphasizing bullets, matching skill hierarchies) while keeping personal history facts strictly identical.
                </p>

                <div className="border border-slate-200 rounded-lg overflow-hidden">
                  <textarea
                    value={profileForm.masterResumeLaTeX}
                    onChange={(e) => setProfileForm({ ...profileForm, masterResumeLaTeX: e.target.value })}
                    rows={12}
                    className="w-full bg-slate-950 text-slate-200 font-mono text-xs p-4 focus:ring-0 focus:outline-none"
                  />
                </div>
              </div>

              {/* Save profile submit */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={savingProfile}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-6 py-2.5 rounded-lg font-bold shadow-sm transition-colors flex items-center gap-2"
                >
                  <Save className="h-4 w-4" />
                  {savingProfile ? 'Saving Config...' : 'Save Profile & Settings'}
                </button>
              </div>

            </form>
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
                Our Gemini AI recruiter will analyze the skills requirements and evaluate suitability.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-600 uppercase">Job Title *</label>
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
                  <label className="text-[10px] font-bold text-slate-600 uppercase">Company Name *</label>
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
                  <label className="text-[10px] font-bold text-slate-600 uppercase">Geographical Location</label>
                  <input
                    type="text"
                    value={newManualJob.location}
                    onChange={(e) => setNewManualJob({ ...newManualJob, location: e.target.value })}
                    placeholder="e.g. New York, NY (Hybrid)"
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-600 uppercase">Working Setting</label>
                  <select
                    value={newManualJob.remoteType}
                    onChange={(e) => setNewManualJob({ ...newManualJob, remoteType: e.target.value as any })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="Remote">Remote</option>
                    <option value="Hybrid">Hybrid</option>
                    <option value="On-site">On-site</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-600 uppercase">Job Board / Referral URL</label>
                <input
                  type="url"
                  value={newManualJob.url}
                  onChange={(e) => setNewManualJob({ ...newManualJob, url: e.target.value })}
                  placeholder="https://company.com/career/post"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-600 uppercase">Full Job Description Requirements *</label>
                <textarea
                  required
                  value={newManualJob.description}
                  onChange={(e) => setNewManualJob({ ...newManualJob, description: e.target.value })}
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
