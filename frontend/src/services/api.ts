import { api } from '@/lib/axios';

export type MatchStatus = 'matched' | 'pending' | 'reviewed';

export interface ScoringRequestPayload {
  job: {
    title: string;
    company: string;
    description: string;
    required_hard_skills: string[];
    required_soft_skills: string[];
    min_experience: number;
    education_level: 'none' | 'license' | 'master' | 'doctorat' | 'other';
  };
  candidates: Array<{
    id: number;
    name: string;
    email?: string | null;
    phone?: string | null;
    location?: string | null;
    headline?: string | null;
    summary?: string | null;
    raw_text: string;
    hard_skills?: string[];
    soft_skills?: string[];
    experience_years?: number;
    education_level?: 'none' | 'license' | 'master' | 'doctorat' | 'other';
    experiences?: Array<{
      title: string;
      company?: string | null;
      duration?: string | null;
    }>;
    educations?: Array<{
      degree: string;
      school?: string | null;
      year?: string | null;
    }>;
  }>;
}

export interface RankedCandidate {
  id: number | null;
  name: string;
  email: string | null;
  score: number;
  status: MatchStatus;
  extracted_hard_skills: string[];
  extracted_soft_skills: string[];
  extracted_experience_years: number;
  extracted_education_level: string;
  match_details: {
    technical: number;
    experience: number;
    education: number;
    soft_skills: number;
    semantic: number;
  };
  rationale: string;
}

export interface ScoringResponsePayload {
  ranked_candidates: RankedCandidate[];
  count: number;
}

export interface HealthPayload {
  status: string;
  environment: string;
  ollama_enabled: string;
  ollama_model: string;
}

export interface UploadParsedCandidate {
  file_name: string;
  candidate: {
    id: number;
    name: string;
    email: string | null;
    phone: string | null;
    location: string | null;
    headline: string | null;
    summary: string | null;
    raw_text: string;
    hard_skills: string[];
    soft_skills: string[];
    experience_years: number;
    education_level: 'none' | 'license' | 'master' | 'doctorat' | 'other';
    experiences: Array<{
      title: string;
      company: string | null;
      duration: string | null;
    }>;
    educations: Array<{
      degree: string;
      school: string | null;
      year: string | null;
    }>;
  };
}

export interface UploadCvResponsePayload {
  accepted: string[];
  rejected: string[];
  count: number;
  parsed_candidates: UploadParsedCandidate[];
}

export interface IngestionJobCreatePayload {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
}

export interface IngestionJobStatusPayload {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  total_files: number;
  processed_files: number;
  accepted: string[];
  rejected: string[];
  parsed_candidates: UploadParsedCandidate[];
  error_message: string | null;
}

export async function fetchApiHealth(): Promise<HealthPayload> {
  const response = await api.get<HealthPayload>('/api/v1/health');
  return response.data;
}

export async function scoreCandidates(payload: ScoringRequestPayload): Promise<ScoringResponsePayload> {
  const response = await api.post<ScoringResponsePayload>('/api/v1/score', payload);
  return response.data;
}

export async function uploadCvFiles(files: File[]): Promise<IngestionJobCreatePayload> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await api.post<IngestionJobCreatePayload>('/api/v1/cvs/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

export async function getIngestionJobStatus(jobId: string): Promise<IngestionJobStatusPayload> {
  const response = await api.get<IngestionJobStatusPayload>(`/api/v1/cvs/ingestion-jobs/${jobId}`);
  return response.data;
}
