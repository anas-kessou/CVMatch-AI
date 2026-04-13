import React, { useEffect, useMemo, useState } from 'react';
import { fetchApiHealth } from './services/api';
import { useIngestionPolling } from './hooks/useIngestionPolling';
import { useScoringWorkflow } from './hooks/useScoringWorkflow';
import { useDashboardMetrics } from './hooks/useDashboardMetrics';
import Sidebar from './components/layout/Sidebar';
import TopHeader from './components/layout/TopHeader';
import UploadCvPanel from './components/upload-cv/UploadCvPanel';
import DashboardTab from './features/dashboard/DashboardTab';
import JobTab from './features/job-post/JobTab';
import CandidatesTab from './features/candidates/CandidatesTab';
import AnalyticsTab from './features/analytics/AnalyticsTab';
import SettingsTab from './features/settings/SettingsTab';
import CandidateDetailModal from './components/candidates/CandidateDetailModal';
import JobFormModal from './components/job-post/JobFormModal';
import type { ActiveTab, Candidate, JobDescription } from './types/app';

const initialJobDescription: JobDescription = {
  title: 'Data Scientist Senior',
  company: 'TechCorp Solutions',
  description: 'Nous recherchons un Data Scientist Senior pour des projets IA et Machine Learning.',
  requiredHardSkills: ['Python', 'Machine Learning', 'SQL'],
  requiredSoftSkills: ['Communication', 'Travail d équipe'],
  minExperience: 3,
  educationLevel: 'Master',
};

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('dashboard');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [jobDesc, setJobDesc] = useState<JobDescription>(initialJobDescription);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [uploadedCvFiles, setUploadedCvFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'unknown' | 'online' | 'offline'>('unknown');
  const [apiModel, setApiModel] = useState<string>('N/A');
  const [healthError, setHealthError] = useState<string>('');
  const [showJobForm, setShowJobForm] = useState(false);
  const { poll: pollIngestionJob } = useIngestionPolling();

  const {
    isAnalyzing,
    analysisError,
    ingestionMessage,
    ingestionStatus,
    analyzeCandidates,
    clearAnalysisError,
  } = useScoringWorkflow({
    jobDesc,
    uploadedCvFiles,
    pollIngestionJob,
    setCandidates,
    setSelectedCandidate,
    setActiveTab,
    setApiStatus,
  });

  const {
    avgScore,
    matchedCount,
    scoreDistribution,
    radarData,
  } = useDashboardMetrics(candidates, selectedCandidate);

  useEffect(() => {
    const loadHealth = async () => {
      try {
        const health = await fetchApiHealth();
        setApiStatus('online');
        setApiModel(health.ollama_model);
        setHealthError('');
      } catch (_error) {
        setApiStatus('offline');
        setHealthError('Backend indisponible. Vérifiez FastAPI + Ollama.');
      }
    };

    void loadHealth();
  }, []);

  const filteredCandidates = useMemo(
    () => candidates.filter((candidate) => {
      const normalizedSearch = searchTerm.toLowerCase().trim();
      const matchesSearch =
        candidate.name.toLowerCase().includes(normalizedSearch)
        || candidate.email.toLowerCase().includes(normalizedSearch);
      const matchesStatus = filterStatus === 'all' || candidate.status === filterStatus;
      return matchesSearch && matchesStatus;
    }).sort((a, b) => b.score - a.score),
    [candidates, filterStatus, searchTerm],
  );

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-amber-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 85) return 'bg-emerald-50 border-emerald-200';
    if (score >= 70) return 'bg-blue-50 border-blue-200';
    if (score >= 50) return 'bg-amber-50 border-amber-200';
    return 'bg-red-50 border-red-200';
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 85) return 'bg-emerald-500';
    if (score >= 70) return 'bg-blue-500';
    if (score >= 50) return 'bg-amber-500';
    return 'bg-red-500';
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setIsUploading(true);
      clearAnalysisError();

      setTimeout(() => {
        setUploadedFiles(prev => [...prev, ...selectedFiles.map((f) => f.name)]);
        setUploadedCvFiles(prev => [...prev, ...selectedFiles]);
        setIsUploading(false);
      }, 600);

      e.target.value = '';
    }
  };

  const handleJobSubmit = (payload: JobDescription) => {
    setJobDesc(payload);
    clearAnalysisError();
    setShowJobForm(false);
  };

  const handleDeleteFile = (fileIndex: number) => {
    clearAnalysisError();
    setUploadedFiles(prev => prev.filter((_fileName, index) => index !== fileIndex));
    setUploadedCvFiles(prev => prev.filter((_file, index) => index !== fileIndex));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar activeTab={activeTab} onChangeTab={setActiveTab} />

      {/* Main Content */}
      <div className="ml-64">
        <TopHeader
          activeTab={activeTab}
          candidatesCount={candidates.length}
          filteredCount={filteredCandidates.length}
          uploadedCount={uploadedFiles.length}
          jobTitle={jobDesc.title}
          searchTerm={searchTerm}
          onSearchTermChange={setSearchTerm}
          apiStatus={apiStatus}
          apiModel={apiModel}
        />

        {/* Content Area */}
        <main className="p-8">
          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <DashboardTab
              candidates={candidates}
              filteredCandidates={filteredCandidates}
              matchedCount={matchedCount}
              avgScore={avgScore}
              jobDesc={jobDesc}
              onSelectCandidate={setSelectedCandidate}
              onGoCandidates={() => setActiveTab('candidates')}
              onGoJob={() => setActiveTab('job')}
              getScoreColor={getScoreColor}
              getScoreBarColor={getScoreBarColor}
            />
          )}

          {/* Job Tab */}
          {activeTab === 'job' && (
            <JobTab jobDesc={jobDesc} onOpenForm={() => setShowJobForm(true)} />
          )}

          {/* Upload Tab */}
          {activeTab === 'upload' && (
            <div className="space-y-6">
              <UploadCvPanel
                uploadedFiles={uploadedFiles}
                isUploading={isUploading}
                isAnalyzing={isAnalyzing}
                apiError={analysisError || healthError}
                ingestionMessage={ingestionMessage}
                ingestionStatus={ingestionStatus}
                onFileUpload={handleFileUpload}
                onAnalyze={analyzeCandidates}
                onDeleteFile={handleDeleteFile}
              />

              {/* Stack Technique */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-6">Stack Technique Suggérée</h3>
                <div className="grid grid-cols-4 gap-4">
                  {[
                    { name: 'PyMuPDF', desc: 'Extraction PDF', color: 'bg-blue-50 text-blue-700 border-blue-200' },
                    { name: 'SpaCy', desc: 'NER & NLP', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
                    { name: 'FastAPI', desc: 'Backend API', color: 'bg-teal-50 text-teal-700 border-teal-200' },
                    { name: 'React', desc: 'Frontend', color: 'bg-cyan-50 text-cyan-700 border-cyan-200' },
                    { name: 'Sentence-Transformers', desc: 'Similarité sémantique', color: 'bg-amber-50 text-amber-700 border-amber-200' },
                    { name: 'PostgreSQL', desc: 'Base de données', color: 'bg-slate-50 text-slate-700 border-slate-200' },
                    { name: 'ChromaDB', desc: 'Vector store', color: 'bg-orange-50 text-orange-700 border-orange-200' },
                    { name: 'LangChain', desc: 'Orchestration LLM', color: 'bg-green-50 text-green-700 border-green-200' },
                  ].map((tech) => (
                    <div key={tech.name} className={`p-4 rounded-lg border ${tech.color} hover:shadow-md transition-shadow`}>
                      <p className="font-bold">{tech.name}</p>
                      <p className="text-xs opacity-75">{tech.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Candidates Tab */}
          {activeTab === 'candidates' && (
            <CandidatesTab
              candidates={candidates}
              filteredCandidates={filteredCandidates}
              filterStatus={filterStatus}
              onFilterStatusChange={setFilterStatus}
              onSelectCandidate={setSelectedCandidate}
              getScoreColor={getScoreColor}
              getScoreBgColor={getScoreBgColor}
            />
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <AnalyticsTab scoreDistribution={scoreDistribution} />
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <SettingsTab />
          )}
        </main>
      </div>

      <CandidateDetailModal
        candidate={selectedCandidate}
        radarData={radarData}
        onClose={() => setSelectedCandidate(null)}
        getScoreColor={getScoreColor}
        getScoreBgColor={getScoreBgColor}
      />

      {/* Job Form Modal */}
      <JobFormModal
        open={showJobForm}
        jobDesc={jobDesc}
        onClose={() => setShowJobForm(false)}
        onSubmit={handleJobSubmit}
      />
    </div>
  );
};

export default App;