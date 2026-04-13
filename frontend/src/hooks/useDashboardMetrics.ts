import { useMemo } from 'react';

import type { Candidate } from '@/types/app';

interface RadarDatum {
  subject: string;
  candidat: number;
  requis: number;
}

interface ScoreDistributionDatum {
  range: string;
  count: number;
}

export const useDashboardMetrics = (candidates: Candidate[], selectedCandidate: Candidate | null) => {
  const avgScore = useMemo(() => {
    if (candidates.length === 0) {
      return 0;
    }

    const sum = candidates.reduce((acc, candidate) => acc + candidate.score, 0);
    return Math.round(sum / candidates.length);
  }, [candidates]);

  const matchedCount = useMemo(
    () => candidates.filter((candidate) => candidate.status === 'matched').length,
    [candidates],
  );

  const scoreDistribution = useMemo<ScoreDistributionDatum[]>(() => ([
    { range: '90-100%', count: candidates.filter((candidate) => candidate.score >= 90).length },
    { range: '75-89%', count: candidates.filter((candidate) => candidate.score >= 75 && candidate.score < 90).length },
    { range: '60-74%', count: candidates.filter((candidate) => candidate.score >= 60 && candidate.score < 75).length },
    { range: '<60%', count: candidates.filter((candidate) => candidate.score < 60).length },
  ]), [candidates]);

  const radarData = useMemo<RadarDatum[]>(() => {
    if (!selectedCandidate) {
      return [];
    }

    return [
      { subject: 'Technique', candidat: selectedCandidate.matchDetails.technical, requis: 85 },
      { subject: 'Expérience', candidat: selectedCandidate.matchDetails.experience, requis: 80 },
      { subject: 'Éducation', candidat: selectedCandidate.matchDetails.education, requis: 85 },
      { subject: 'Soft Skills', candidat: selectedCandidate.matchDetails.softSkills, requis: 80 },
    ];
  }, [selectedCandidate]);

  return {
    avgScore,
    matchedCount,
    scoreDistribution,
    radarData,
  };
};
