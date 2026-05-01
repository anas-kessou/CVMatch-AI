import { useCallback, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';

import {
  createJob,
  uploadCvFile,
  getJobRankings,
  getCvScoreDetail,
} from '@/services/api';

import type { ActiveTab, Candidate, JobDescription } from '@/types/app';

type ApiStatus = 'unknown' | 'online' | 'offline';

interface UseScoringWorkflowParams {
  jobDesc: JobDescription;
  uploadedCvFiles: File[];
  setCandidates: Dispatch<SetStateAction<Candidate[]>>;
  setSelectedCandidate: Dispatch<SetStateAction<Candidate | null>>;
  setActiveTab: Dispatch<SetStateAction<ActiveTab>>;
  setApiStatus: Dispatch<SetStateAction<ApiStatus>>;
}

export const useScoringWorkflow = ({
  jobDesc,
  uploadedCvFiles,
  setCandidates,
  setSelectedCandidate,
  setActiveTab,
  setApiStatus,
}: UseScoringWorkflowParams) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [ingestionMessage, setIngestionMessage] = useState('');

  const analyzeCandidates = useCallback(async () => {
    if (uploadedCvFiles.length === 0) {
      setAnalysisError('Ajoutez au moins un CV (PDF/DOCX) avant de lancer l\'analyse.');
      return;
    }

    if (jobDesc.title.trim().length < 2) {
      setAnalysisError('Renseignez un titre de poste (minimum 2 caractères) avant de lancer l\'analyse.');
      return;
    }

    if (jobDesc.description.trim().length < 10) {
      setAnalysisError('Ajoutez une description du poste (minimum 10 caractères) avant de lancer l\'analyse.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError('');
    setIngestionMessage('Création du poste...');

    try {
      // 1. Create Job
      const job = await createJob({
        title: jobDesc.title,
        description: jobDesc.description,
        required_hard_skills: jobDesc.requiredHardSkills || [],
        required_soft_skills: jobDesc.requiredSoftSkills || [],
        min_experience_years: jobDesc.minExperience || 0,
      });

      // 2. Upload and Parse CVs sequentially
      let processed = 0;
      const total = uploadedCvFiles.length;
      for (const file of uploadedCvFiles) {
        setIngestionMessage(`Analyse de ${file.name} (${processed + 1}/${total})...`);
        await uploadCvFile(job.id, file);
        processed++;
      }

      setIngestionMessage('Récupération du classement et des scores...');
      
      // 3. Get Rankings
      const rankingsData = await getJobRankings(job.id);
      
      // 4. Map to Frontend Candidate Type
      const transformed: Candidate[] = await Promise.all(rankingsData.rankings.map(async (r) => {
        // Just mock some details for now if we want to save API calls, but we can call getCvScoreDetail if needed.
        // Doing it to make the UI look populated.
        
        let details;
        try {
           details = await getCvScoreDetail(r.candidate_id);
        } catch(e) {
           console.error("Score detail error", e);
        }
        
        return {
          id: r.candidate_id,
          name: r.cv_filename.replace('.pdf','').replace('.docx',''),
          email: r.email || `${r.candidate_id}@example.com`,
          phone: "0000000000",
          location: "Location",
          score: r.global_score,
          hardSkills: details?.matched_skills?.map((s: string) => ({ name: s, match: true, level: 80 })) || [{name: "Skill", match: true, level: 80}],
          softSkills: [{ name: "Communication", match: true }],
          experience: 3, // mock
          education: "Master",
          experiences: [],
          educations: [],
          status: 'matched',
          matchDetails: {
            technical: details?.semantic_score ? details.semantic_score * 100 : 0,
            experience: 100,
            education: 100,
            softSkills: 100,
          },
        };
      }));

      setCandidates(transformed);
      setSelectedCandidate(null);
      setActiveTab('candidates');
      setApiStatus('online');
    } catch (error) {
      console.error(error);
      const message = error instanceof Error
        ? error.message
        : 'Erreur inattendue.';

      setAnalysisError(message);
      setApiStatus('offline');
      setIngestionMessage(`L'analyse a échoué: ${message}`);
    } finally {
      setIsAnalyzing(false);
    }
  }, [
    jobDesc,
    setActiveTab,
    setApiStatus,
    setCandidates,
    setSelectedCandidate,
    uploadedCvFiles,
  ]);

  const clearAnalysisError = useCallback(() => {
    setAnalysisError('');
  }, []);

  return {
    isAnalyzing,
    analysisError,
    ingestionMessage,
    // Provide a dummy ingestionStatus if components still look for it, or just null
    ingestionStatus: null,
    analyzeCandidates,
    clearAnalysisError,
  };
};
