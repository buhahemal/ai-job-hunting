import React, { useState } from 'react';
import { AlertCircle, Copy, Check, FileText, Code, Printer, Award, Download } from 'lucide-react';
import { listJobResumes, type JobResumeVersion } from '../api/client';
import { Job } from '../types';

interface ResumePreviewProps {
  job: Job;
  pdfUrl?: string;
  onSaveTailored: (resumeLaTeX: string, coverLetter: string) => Promise<void>;
  onApplyDirectly: () => void;
}

/** Render a small subset of LaTeX inline markup as React nodes (no innerHTML). */
function renderLatexInline(text: string, keyPrefix: string): React.ReactNode {
  const nodes: React.ReactNode[] = [];
  const pattern = /\\textbf\{([^}]+)\}|\\%/g;
  let last = 0;
  let match: RegExpExecArray | null;
  let partIndex = 0;

  const pushPlain = (chunk: string) => {
    if (!chunk) return;
    nodes.push(chunk.replace(/\\&/g, '&').replace(/\\/g, ''));
  };

  while ((match = pattern.exec(text)) !== null) {
    pushPlain(text.slice(last, match.index));
    if (match[0] === '\\%') {
      nodes.push('%');
    } else {
      nodes.push(<strong key={`${keyPrefix}-b-${partIndex++}`}>{match[1]}</strong>);
    }
    last = pattern.lastIndex;
  }
  pushPlain(text.slice(last));

  if (nodes.length === 0) return null;
  if (nodes.length === 1) return nodes[0];
  return nodes;
}

export default function ResumePreview({
  job,
  pdfUrl,
  onSaveTailored,
  onApplyDirectly,
}: ResumePreviewProps) {
  const [activeTab, setActiveTab] = useState<'resume' | 'coverLetter'>('resume');
  const [isEditing, setIsEditing] = useState(false);
  const [editedLaTeX, setEditedLaTeX] = useState(job.tailoredResumeLaTeX || '');
  const [editedCoverLetter, setEditedCoverLetter] = useState(job.tailoredCoverLetter || '');
  const [copied, setCopied] = useState(false);
  const [saving, setSaving] = useState(false);
  const [resumeVersions, setResumeVersions] = useState<JobResumeVersion[]>([]);

  React.useEffect(() => {
    setEditedLaTeX(job.tailoredResumeLaTeX || '');
    setEditedCoverLetter(job.tailoredCoverLetter || '');
  }, [job]);

  React.useEffect(() => {
    let cancelled = false;
    void listJobResumes(job.id)
      .then((items) => {
        if (!cancelled) setResumeVersions(items);
      })
      .catch(() => {
        if (!cancelled) setResumeVersions([]);
      });
    return () => {
      cancelled = true;
    };
  }, [job.id, pdfUrl]);

  const handleCopy = () => {
    const textToCopy = activeTab === 'resume' ? editedLaTeX : editedCoverLetter;
    void navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSaveTailored(editedLaTeX, editedCoverLetter);
      setIsEditing(false);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  // Basic regex parser to turn LaTeX commands into clean readable UI paragraphs for paper preview
  const parseLaTeXForPreview = (latex: string) => {
    if (!latex)
      return (
        <div className="text-gray-400 italic">
          No resume data generated yet. Click "AI Tailor Resume" to start.
        </div>
      );

    const lines = latex.split('\n');
    const elements: React.ReactNode[] = [];
    let inItemize = false;
    let itemsList: string[] = [];

    lines.forEach((line, index) => {
      const cleanLine = line.trim();
      if (!cleanLine || cleanLine.startsWith('%')) return;

      // Skip document wrapper setup commands
      if (
        cleanLine.startsWith('\\documentclass') ||
        cleanLine.startsWith('\\usepackage') ||
        cleanLine.startsWith('\\geometry') ||
        cleanLine.startsWith('\\begin{document}') ||
        cleanLine.startsWith('\\end{document}')
      ) {
        return;
      }

      // Title & Name
      if (cleanLine.includes('\\Huge')) {
        const nameMatch = cleanLine.match(/\\textbf\{([^}]+)\}/);
        if (nameMatch) {
          elements.push(
            <h1
              key={`name-${index}`}
              className="text-3xl font-bold text-gray-900 tracking-tight text-center"
            >
              {nameMatch[1]}
            </h1>,
          );
        }
        return;
      }

      // Contact detail lines
      if (cleanLine.includes('@') && cleanLine.includes('|')) {
        elements.push(
          <p
            key={`contact-${index}`}
            className="text-xs text-gray-600 text-center font-mono mt-1 mb-4 border-b border-gray-200 pb-3"
          >
            {cleanLine.replace(/\\/g, '')}
          </p>,
        );
        return;
      }

      // Sections
      if (cleanLine.startsWith('\\section*')) {
        const sectMatch = cleanLine.match(/\\section\*\{([^}]+)\}/);
        if (sectMatch) {
          elements.push(
            <h2
              key={`sect-${index}`}
              className="text-sm font-semibold text-slate-800 tracking-wider uppercase border-b-2 border-slate-300 mt-5 mb-2 pb-0.5"
            >
              {sectMatch[1]}
            </h2>,
          );
        }
        return;
      }

      // Lists
      if (cleanLine.startsWith('\\begin{itemize}')) {
        inItemize = true;
        itemsList = [];
        return;
      }

      if (cleanLine.startsWith('\\end{itemize}')) {
        inItemize = false;
        elements.push(
          <ul key={`list-${index}`} className="list-disc pl-5 space-y-1 my-1 text-xs text-gray-700">
            {itemsList.map((item, idx) => (
              <li key={idx}>{renderLatexInline(item, `item-${index}-${idx}`)}</li>
            ))}
          </ul>,
        );
        return;
      }

      if (inItemize && cleanLine.startsWith('\\item')) {
        const itemText = cleanLine.replace('\\item', '').trim();
        itemsList.push(itemText);
        return;
      }

      // Standard paragraphs / headings
      if (!inItemize) {
        const formattedText = cleanLine.replace(/\\hfill/g, ' \u00A0 ');
        elements.push(
          <p key={`p-${index}`} className="text-xs text-gray-700 leading-relaxed my-1">
            {renderLatexInline(formattedText, `p-${index}`)}
          </p>,
        );
      }
    });

    return <div className="font-sans space-y-2 p-4">{elements}</div>;
  };

  return (
    <div
      id="tailoring-suite"
      className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden"
    >
      {/* Top Banner Control Panel */}
      <div className="bg-slate-900 text-white p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-emerald-400" />
            <span className="text-xs tracking-wider uppercase font-semibold text-slate-400">
              Tailoring Workspace
            </span>
          </div>
          <h3 className="text-lg font-bold text-slate-100">{job.title}</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            {job.company} &bull; {job.location}
          </p>
          <p className="text-[10px] text-slate-500 mt-2">
            Deterministic tailoring reorders skills and bullets for this job. Facts stay unchanged.
          </p>
        </div>

        {/* ATS Quality Score Ring */}
        {job.atsScore && (
          <div className="flex items-center gap-3 bg-slate-800/80 px-4 py-2 rounded-lg border border-slate-700">
            <Award className="h-5 w-5 text-emerald-400" />
            <div>
              <div className="text-xs text-slate-400 leading-none">ATS Score</div>
              <div className="text-lg font-bold text-emerald-400 leading-none mt-1">
                {job.atsScore}%
              </div>
            </div>
            <div className="h-8 w-[1px] bg-slate-700" />
            <div className="text-[10px] text-slate-400 max-w-[120px]">
              {job.atsScore >= 85 ? 'Excellent keyword match' : 'Good keyword density'}
            </div>
          </div>
        )}
      </div>

      {resumeVersions.length > 0 ? (
        <div className="border-b border-slate-100 bg-slate-50 px-4 py-2 flex flex-wrap items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-wide text-slate-500">
            Saved versions
          </span>
          {resumeVersions.map((entry) =>
            entry.pdfUrl ? (
              <a
                key={entry.version}
                href={entry.pdfUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[10px] px-2 py-1 rounded-md border border-slate-200 bg-white text-indigo-700 hover:bg-indigo-50 font-medium"
              >
                {entry.version}
                {entry.atsScore != null ? ` · ${entry.atsScore}% ATS` : ''}
              </a>
            ) : (
              <span
                key={entry.version}
                className="text-[10px] px-2 py-1 rounded-md border border-slate-200 bg-white text-slate-500"
              >
                {entry.version}
              </span>
            ),
          )}
        </div>
      ) : null}

      {job.matchInsights &&
      (job.matchInsights.matchedSkills.length > 0 ||
        job.matchInsights.missingKeywords.length > 0) ? (
        <div className="grid gap-3 border-b border-slate-100 bg-white px-4 py-3 md:grid-cols-2">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wide text-emerald-700">
              Matched ATS keywords
            </p>
            <div className="mt-1 flex flex-wrap gap-1">
              {job.matchInsights.matchedSkills.slice(0, 10).map((keyword) => (
                <span
                  key={keyword}
                  className="rounded bg-emerald-50 px-2 py-0.5 text-[10px] text-emerald-700"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wide text-amber-700">
              Missing keywords to verify
            </p>
            <div className="mt-1 flex flex-wrap gap-1">
              {job.matchInsights.missingKeywords.slice(0, 10).map((keyword) => (
                <span
                  key={keyword}
                  className="rounded bg-amber-50 px-2 py-0.5 text-[10px] text-amber-700"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        </div>
      ) : null}

      {/* Mode Switches */}
      <div className="border-b border-slate-100 bg-slate-50 p-2 flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-1 bg-slate-200/60 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('resume')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'resume'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            LaTeX Resume
          </button>
          <button
            onClick={() => setActiveTab('coverLetter')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'coverLetter'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Cover Letter
          </button>
        </div>

        <div className="flex items-center gap-2">
          {isEditing ? (
            <>
              <button
                onClick={handleSave}
                disabled={saving}
                className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-3 py-1.5 rounded-md font-medium transition-colors"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                onClick={() => {
                  setIsEditing(false);
                  setEditedLaTeX(job.tailoredResumeLaTeX || '');
                  setEditedCoverLetter(job.tailoredCoverLetter || '');
                }}
                className="bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs px-3 py-1.5 rounded-md font-medium transition-colors"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="bg-slate-900 hover:bg-slate-800 text-white text-xs px-3 py-1.5 rounded-md font-medium transition-all"
              >
                Edit Raw Source
              </button>
              <button
                onClick={handleCopy}
                className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-2.5 py-1.5 rounded-md border border-slate-200 flex items-center gap-1.5 font-medium"
              >
                {copied ? (
                  <Check className="h-3.5 w-3.5 text-emerald-600" />
                ) : (
                  <Copy className="h-3.5 w-3.5" />
                )}
                {copied ? 'Copied!' : 'Copy Code'}
              </button>
              <button
                onClick={handlePrint}
                className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-2.5 py-1.5 rounded-md border border-slate-200 flex items-center gap-1.5 font-medium"
              >
                <Printer className="h-3.5 w-3.5" />
                Print
              </button>
              {pdfUrl ? (
                <a
                  href={pdfUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-2.5 py-1.5 rounded-md flex items-center gap-1.5 font-medium"
                >
                  <Download className="h-3.5 w-3.5" />
                  Download PDF
                </a>
              ) : null}
            </>
          )}
        </div>
      </div>

      {/* Dual Screen Workspace */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left Side: Code Editor */}
        <div
          className={`w-full lg:w-1/2 flex flex-col border-r border-slate-100 ${isEditing ? 'bg-slate-950' : 'bg-slate-900'} overflow-hidden`}
        >
          <div className="p-2 bg-slate-800/80 text-slate-300 text-[10px] font-mono tracking-wider uppercase flex items-center justify-between border-b border-slate-700/50">
            <span className="flex items-center gap-1">
              <Code className="h-3 w-3 text-sky-400" />
              {activeTab === 'resume' ? 'LaTeX Code Editor' : 'Plain Text Editor'}
            </span>
            {isEditing && (
              <span className="text-emerald-400 animate-pulse font-semibold">
                &bull; Live Editing Mode
              </span>
            )}
          </div>

          <div className="flex-1 p-2 overflow-auto font-mono text-xs leading-relaxed">
            {activeTab === 'resume' ? (
              <textarea
                value={editedLaTeX}
                onChange={(e) => setEditedLaTeX(e.target.value)}
                disabled={!isEditing}
                className={`w-full h-full p-3 border-0 bg-transparent text-slate-200 focus:ring-0 resize-none font-mono text-xs focus:outline-none ${
                  !isEditing ? 'cursor-not-allowed text-slate-400' : ''
                }`}
                placeholder="\\documentclass..."
              />
            ) : (
              <textarea
                value={editedCoverLetter}
                onChange={(e) => setEditedCoverLetter(e.target.value)}
                disabled={!isEditing}
                className={`w-full h-full p-3 border-0 bg-transparent text-slate-200 focus:ring-0 resize-none font-mono text-xs focus:outline-none ${
                  !isEditing ? 'cursor-not-allowed text-slate-400' : ''
                }`}
                placeholder="Dear Hiring Team..."
              />
            )}
          </div>
        </div>

        {/* Right Side: Rendered Paper Preview */}
        <div className="w-full lg:w-1/2 bg-slate-100 p-6 overflow-auto flex justify-center items-start">
          <div
            className="w-full max-w-[8.5in] bg-white shadow-md rounded-sm border border-slate-200 min-h-[11in] relative overflow-hidden print:shadow-none print:border-none print:m-0"
            id="resume-print-paper"
          >
            {/* Elegant Letterhead Strip for Cover Letters or Resume watermark */}
            <div className="h-1.5 bg-slate-800 w-full" />

            <div className="p-8">
              {activeTab === 'resume' ? (
                parseLaTeXForPreview(editedLaTeX)
              ) : (
                <div className="font-sans text-xs text-gray-800 leading-relaxed whitespace-pre-wrap p-4 max-w-full">
                  {editedCoverLetter || (
                    <div className="text-gray-400 italic">
                      No cover letter has been compiled. Click "AI Tailor Resume" to generate
                      automatically.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Application Trigger */}
      <div className="p-3 bg-slate-50 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-center gap-2 text-slate-500 text-xs">
          <AlertCircle className="h-4 w-4 text-emerald-500 shrink-0" />
          <span>Tailored contents are ready. Review paper visualizer prior to copy.</span>
        </div>
        <button
          onClick={onApplyDirectly}
          className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-4 py-2 rounded-lg font-medium shadow-sm transition-all self-end"
        >
          Proceed to Apply Site
        </button>
      </div>
    </div>
  );
}
