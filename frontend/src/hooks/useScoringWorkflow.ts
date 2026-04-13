import { useCallback, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';

import {
  scoreCandidates,
  type IngestionJobStatusPayload,
  uploadCvFiles,
} from '@/services/api';
import type { ActiveTab, Candidate, JobDescription } from '@/types/app';

type ApiStatus = 'unknown' | 'online' | 'offline';

interface UseScoringWorkflowParams {
  jobDesc: JobDescription;
  uploadedCvFiles: File[];
  pollIngestionJob: (
    jobId: string,
    maxAttempts?: number,
    onUpdate?: (status: IngestionJobStatusPayload) => void,
  ) => Promise<IngestionJobStatusPayload>;
  setCandidates: Dispatch<SetStateAction<Candidate[]>>;
  setSelectedCandidate: Dispatch<SetStateAction<Candidate | null>>;
  setActiveTab: Dispatch<SetStateAction<ActiveTab>>;
  setApiStatus: Dispatch<SetStateAction<ApiStatus>>;
}

const mapEducationLevelToApi = (level: string): 'none' | 'license' | 'master' | 'doctorat' | 'other' => {
  const normalized = level.toLowerCase();
  if (normalized.includes('doctor')) return 'doctorat';
  if (normalized.includes('master')) return 'master';
  if (normalized.includes('licence') || normalized.includes('license') || normalized.includes('bachelor')) return 'license';
  if (normalized.trim().length === 0) return 'none';
  return 'other';
};

export const useScoringWorkflow = ({
  jobDesc,
  uploadedCvFiles,
  pollIngestionJob,
  setCandidates,
  setSelectedCandidate,
  setActiveTab,
  setApiStatus,
}: UseScoringWorkflowParams) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [ingestionMessage, setIngestionMessage] = useState('');
  const [ingestionStatus, setIngestionStatus] = useState<IngestionJobStatusPayload | null>(null);

  const analyzeCandidates = useCallback(async () => {
    if (uploadedCvFiles.length === 0) {
      setAnalysisError('Ajoutez au moins un CV (PDF/DOCX) avant de lancer l\'analyse.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError('');
    setIngestionMessage('');
    setIngestionStatus(null);

    try {
      const job = await uploadCvFiles(uploadedCvFiles);
      setIngestionMessage(`Job ${job.job_id.slice(0, 8)} créé. Parsing en cours...`);

      const lastStatus = await pollIngestionJob(job.job_id, 90, (status) => {
        setIngestionStatus(status);
        const percentage = status.total_files > 0
          ? Math.round((status.processed_files / status.total_files) * 100)
          : 0;
        setIngestionMessage(`Job ${job.job_id.slice(0, 8)}: ${status.status} (${percentage}%)`);
      });

      if (lastStatus.status === 'failed') {
        throw new Error(lastStatus.error_message ?? 'Le job d\'ingestion a échoué.');
      }

      if (lastStatus.status !== 'completed') {
        throw new Error('Timeout ingestion: le parsing prend trop de temps.');
      }

      if (lastStatus.rejected.length > 0) {
        setAnalysisError(`Fichiers ignorés: ${lastStatus.rejected.join(', ')}`);
      }

      const response = await scoreCandidates({
        job: {
          title: jobDesc.title,
          company: jobDesc.company,
          description: jobDesc.description,
          required_hard_skills: jobDesc.requiredHardSkills,
          required_soft_skills: jobDesc.requiredSoftSkills,
          min_experience: jobDesc.minExperience,
          education_level: mapEducationLevelToApi(jobDesc.educationLevel),
        },
        candidates: lastStatus.parsed_candidates.map(({ candidate }) => ({
          id: candidate.id,
          name: candidate.name,
          email: candidate.email,
          phone: candidate.phone,
          location: candidate.location,
          headline: candidate.headline,
          summary: candidate.summary,
          raw_text: candidate.raw_text,
          hard_skills: candidate.hard_skills,
          soft_skills: candidate.soft_skills,
          experience_years: candidate.experience_years,
          education_level: candidate.education_level,
          experiences: candidate.experiences,
          educations: candidate.educations,
        })),
      });

      const parsedCandidateById = new Map(
        lastStatus.parsed_candidates.map(({ candidate }) => [candidate.id, candidate] as const),
      );

      const transformed = response.ranked_candidates.map((item, index): Candidate => {
        const requiredHardSkillSet = new Set(jobDesc.requiredHardSkills.map((skill) => skill.toLowerCase()));
        const requiredSoftSkillSet = new Set(jobDesc.requiredSoftSkills.map((skill) => skill.toLowerCase()));
        const parsedCandidate = item.id !== null ? parsedCandidateById.get(item.id) : undefined;

        return {
          id: item.id ?? index + 1,
          name: item.name,
          email: item.email ?? `candidate${index + 1}@example.com`,
          phone: parsedCandidate?.phone ?? 'N/A',
          location: parsedCandidate?.location ?? 'Non renseigné',
          score: item.score,
          hardSkills: item.extracted_hard_skills.map((skill) => ({
            name: skill,
            match: requiredHardSkillSet.has(skill.toLowerCase()),
            level: item.match_details.technical,
          })),
          softSkills: item.extracted_soft_skills.map((skill) => ({
            name: skill,
            match: requiredSoftSkillSet.has(skill.toLowerCase()),
          })),
          experience: item.extracted_experience_years,
          education: item.extracted_education_level,
          experiences: parsedCandidate?.experiences.length
            ? parsedCandidate.experiences.map((experience) => ({
                title: experience.title,
                company: experience.company ?? 'N/A',
                duration: experience.duration ?? 'N/A',
              }))
            : [
                {
                  title: 'Expérience extraite automatiquement',
                  company: 'N/A',
                  duration: `${item.extracted_experience_years} ans`,
                },
              ],
          educations: parsedCandidate?.educations.length
            ? parsedCandidate.educations.map((education) => ({
                degree: education.degree,
                school: education.school ?? 'N/A',
                year: education.year ?? 'N/A',
              }))
            : [
                {
                  degree: item.extracted_education_level,
                  school: 'Source CV',
                  year: 'N/A',
                },
              ],
          status: item.status,
          matchDetails: {
            technical: item.match_details.technical,
            experience: item.match_details.experience,
            education: item.match_details.education,
            softSkills: item.match_details.soft_skills,
          },
        };
      });

      setCandidates(transformed);
      setSelectedCandidate(null);
      setActiveTab('candidates');
      setApiStatus('online');
    } catch (error) {
      const message = error instanceof Error
        ? error.message
        : 'Analyse IA indisponible. Vérifiez que le backend FastAPI fonctionne sur le port 8000.';

      setAnalysisError(message);
      setApiStatus('offline');
      setIngestionMessage('Le job d\'ingestion a échoué.');
    } finally {
      setIsAnalyzing(false);
    }
  }, [
    jobDesc,
    pollIngestionJob,
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
    ingestionStatus,
    analyzeCandidates,
    clearAnalysisError,
  };
};
