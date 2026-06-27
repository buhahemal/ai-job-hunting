import { TrendingUp, BarChart2, Briefcase, CheckCircle, Clock, Globe, Star } from 'lucide-react';
import { Job, Interview } from '../types';

interface AnalyticsViewProps {
  jobs: Job[];
  interviews: Interview[];
}

export default function AnalyticsView({ jobs, interviews }: AnalyticsViewProps) {
  // 1. Pipeline Funnel stats
  const totalDiscovered = jobs.length;
  const shortlisted = jobs.filter(j => j.status === 'Shortlisted').length;
  const applied = jobs.filter(j => j.status === 'Applied').length;
  const interviewing = jobs.filter(j => j.status === 'Interviewing').length;
  const offer = jobs.filter(j => j.status === 'Offer' || j.status === 'Accepted').length;

  const averageScore = Math.round(
    jobs.filter(j => j.score !== undefined).reduce((acc, curr) => acc + (curr.score || 0), 0) / 
    Math.max(1, jobs.filter(j => j.score !== undefined).length)
  );

  // 2. Remote type distribution
  const remoteCount = jobs.filter(j => j.remoteType === 'Remote').length;
  const hybridCount = jobs.filter(j => j.remoteType === 'Hybrid').length;
  const onsiteCount = jobs.filter(j => j.remoteType === 'On-site').length;
  const totalRemoteMapped = Math.max(1, remoteCount + hybridCount + onsiteCount);

  // 3. Extract top skills occurring in job descriptions
  const skillOccurrences: { [key: string]: number } = {};
  jobs.forEach(job => {
    if (job.extractedSkills) {
      job.extractedSkills.forEach(skill => {
        skillOccurrences[skill] = (skillOccurrences[skill] || 0) + 1;
      });
    }
  });

  const sortedSkills = Object.entries(skillOccurrences)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);

  // 4. Calculate Conversion percentages
  const applyConversion = totalDiscovered > 0 ? Math.round((applied / totalDiscovered) * 100) : 0;
  const interviewConversion = applied > 0 ? Math.round((interviewing / applied) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg">
            <Briefcase className="h-6 w-6" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Discovered Jobs</div>
            <div className="text-2xl font-bold text-slate-800 mt-0.5">{totalDiscovered}</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
            <CheckCircle className="h-6 w-6" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Active Applications</div>
            <div className="text-2xl font-bold text-slate-800 mt-0.5">{applied + interviewing}</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-amber-50 text-amber-600 rounded-lg">
            <Clock className="h-6 w-6" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Interviews Booked</div>
            <div className="text-2xl font-bold text-slate-800 mt-0.5">{interviews.length}</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
            <Star className="h-6 w-6" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Avg AI Fit Score</div>
            <div className="text-2xl font-bold text-emerald-600 mt-0.5">{averageScore}%</div>
          </div>
        </div>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Funnel Conversion */}
        <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm lg:col-span-2 space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-indigo-500" />
              Application Funnel & Conversion
            </h3>
            <p className="text-xs text-slate-500 mt-1">Tracks your progression rates from initial lead discovery to official offer received.</p>
          </div>

          <div className="space-y-4">
            {/* Funnel bars */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-slate-700">
                <span>Discovered Leads</span>
                <span>{totalDiscovered} ({totalDiscovered > 0 ? '100%' : '0%'})</span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-slate-400 rounded-full" style={{ width: '100%' }} />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-slate-700">
                <span>Shortlisted / Tailored</span>
                <span>{shortlisted} ({totalDiscovered > 0 ? Math.round((shortlisted / totalDiscovered) * 100) : 0}%)</span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-sky-500 rounded-full" style={{ width: `${totalDiscovered > 0 ? (shortlisted / totalDiscovered) * 100 : 0}%` }} />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-slate-700">
                <span>Submitted Applications</span>
                <span>{applied} ({totalDiscovered > 0 ? Math.round((applied / totalDiscovered) * 100) : 0}%)</span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${totalDiscovered > 0 ? (applied / totalDiscovered) * 100 : 0}%` }} />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-slate-700">
                <span>Interviews Conducted</span>
                <span>{interviewing} ({totalDiscovered > 0 ? Math.round((interviewing / totalDiscovered) * 100) : 0}%)</span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 rounded-full" style={{ width: `${totalDiscovered > 0 ? (interviewing / totalDiscovered) * 100 : 0}%` }} />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-slate-700">
                <span>Job Offers Received</span>
                <span>{offer} ({totalDiscovered > 0 ? Math.round((offer / totalDiscovered) * 100) : 0}%)</span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${totalDiscovered > 0 ? (offer / totalDiscovered) * 100 : 0}%` }} />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-slate-100">
            <div className="bg-slate-50 p-4 rounded-xl text-center">
              <div className="text-2xl font-black text-slate-800">{applyConversion}%</div>
              <div className="text-xs text-slate-500 font-medium mt-1">Discovery to Submission</div>
            </div>
            <div className="bg-slate-50 p-4 rounded-xl text-center">
              <div className="text-2xl font-black text-slate-800">{interviewConversion}%</div>
              <div className="text-xs text-slate-500 font-medium mt-1">Application to Interview</div>
            </div>
          </div>
        </div>

        {/* Right Column: Work Style & Locations */}
        <div className="space-y-6">
          {/* Work Setting */}
          <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
              <Globe className="h-5 w-5 text-indigo-500" />
              Work Environment
            </h3>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs text-slate-600 mb-1.5">
                  <span>Remote roles</span>
                  <span className="font-semibold">{remoteCount} jobs</span>
                </div>
                <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${(remoteCount / totalRemoteMapped) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-600 mb-1.5">
                  <span>Hybrid roles</span>
                  <span className="font-semibold">{hybridCount} jobs</span>
                </div>
                <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(hybridCount / totalRemoteMapped) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-600 mb-1.5">
                  <span>On-site roles</span>
                  <span className="font-semibold">{onsiteCount} jobs</span>
                </div>
                <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-500 rounded-full" style={{ width: `${(onsiteCount / totalRemoteMapped) * 100}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* Frequently Demanded Skills */}
          <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
              <BarChart2 className="h-5 w-5 text-indigo-500" />
              In-Demand Technologies
            </h3>

            <div className="space-y-3">
              {sortedSkills.length === 0 ? (
                <p className="text-xs text-slate-400 italic py-2 text-center">Analyze more jobs to map keyword frequencies.</p>
              ) : (
                sortedSkills.map(([skill, count]) => {
                  const percent = Math.round((count / totalDiscovered) * 100);
                  return (
                    <div key={skill} className="flex items-center justify-between text-xs">
                      <span className="bg-slate-100 text-slate-800 font-mono px-2 py-0.5 rounded text-[11px] font-medium">{skill}</span>
                      <div className="flex items-center gap-2 w-1/2">
                        <div className="h-2 bg-slate-100 rounded-full flex-1 overflow-hidden">
                          <div className="h-full bg-slate-700 rounded-full" style={{ width: `${percent}%` }} />
                        </div>
                        <span className="text-slate-500 font-semibold font-mono text-[10px] min-w-[24px] text-right">{percent}%</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
