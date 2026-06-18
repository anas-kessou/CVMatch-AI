import type { Candidate, JobDescription } from '@/types/app';

export const createMockJobDescription = (): JobDescription => ({
  title: 'Data Scientist (NLP / CV Scoring)',
  company: 'TalentOps',
  description:
    'Analyser des CV et recommander des candidats. Le système doit comparer les compétences techniques, l\'expérience, l\'éducation et les soft skills en contexte de recrutement.',
  requiredHardSkills: ['Python', 'NLP', 'Machine Learning', 'FastAPI', 'Vector Embeddings'],
  requiredSoftSkills: ['Communication', 'Esprit d\'équipe', 'Autonomie'],
  minExperience: 2,
  educationLevel: 'Master (ou équivalent)',
});

const makeCandidate = (id: number, partial: Partial<Candidate>): Candidate => {
  const base: Candidate = {
    id,
    name: 'Candidate',
    email: `candidate${id}@example.com`,
    phone: 'Non spécifié',
    location: 'Non spécifié',
    score: 0,
    hardSkills: [],
    softSkills: [],
    experience: 0,
    education: 'Non spécifié',
    experiences: [],
    educations: [],
    status: 'pending',
    ollamaJudgement: null,
    matchDetails: {
      technical: 0,
      experience: 0,
      education: 0,
      softSkills: 0,
    },
  };

  return {
    ...base,
    ...partial,
    matchDetails: {
      technical: partial.matchDetails?.technical ?? partial.score ?? 0,
      experience: partial.matchDetails?.experience ?? 70,
      education: partial.matchDetails?.education ?? 75,
      softSkills: partial.matchDetails?.softSkills ?? 65,
    },
  };
};

export const createMockCandidates = (): Candidate[] => {
  const candidates: Candidate[] = [
    makeCandidate(1, {
      name: 'Sarah Martin',
      email: 'sarah.martin@example.com',
      phone: '+33 6 12 34 56 78',
      location: 'Paris',
      score: 92,
      status: 'matched',
      experience: 4,
      education: 'Master Informatique',
      hardSkills: [
        { name: 'Python', match: true, level: 90 },
        { name: 'NLP', match: true, level: 85 },
        { name: 'FastAPI', match: true, level: 80 },
        { name: 'Vector Embeddings', match: true, level: 78 },
      ],
      softSkills: [
        { name: 'Communication', match: true },
        { name: 'Esprit d\'équipe', match: true },
      ],
      experiences: [
        { title: 'Data Scientist', company: 'NovaAI', duration: '2022 - 2025' },
        { title: 'Machine Learning Engineer', company: 'FinSight', duration: '2020 - 2022' },
      ],
      educations: [
        { degree: 'Master Informatique', school: 'Sorbonne Université', year: '2019' },
      ],
      matchDetails: { technical: 92, experience: 88, education: 86, softSkills: 80 },
      ollamaJudgement: 'Très bon profil: maîtrise NLP et pipelines CV scoring.',
    }),
    makeCandidate(2, {
      name: 'Karim Benali',
      email: 'karim.benali@example.com',
      phone: '+33 7 45 67 89 01',
      location: 'Lyon',
      score: 84,
      status: 'reviewed',
      experience: 3,
      education: 'Master Data Science',
      hardSkills: [
        { name: 'Python', match: true, level: 85 },
        { name: 'Machine Learning', match: true, level: 82 },
        { name: 'FastAPI', match: true, level: 70 },
        { name: 'NLP', match: true, level: 75 },
      ],
      softSkills: [
        { name: 'Communication', match: true },
        { name: 'Autonomie', match: true },
      ],
      experiences: [
        { title: 'ML Engineer', company: 'RetailSense', duration: '2021 - 2024' },
      ],
      educations: [
        { degree: 'Master Data Science', school: 'INSA Lyon', year: '2020' },
      ],
      matchDetails: { technical: 84, experience: 80, education: 78, softSkills: 76 },
      ollamaJudgement: 'Bon niveau: manque légèrement d\'expertise sur les embeddings.',
    }),
    makeCandidate(3, {
      name: 'Inès Durand',
      email: 'ines.durand@example.com',
      phone: '+33 6 98 76 54 32',
      location: 'Marseille',
      score: 66,
      status: 'pending',
      experience: 2,
      education: 'Licence Informatique',
      hardSkills: [
        { name: 'Python', match: true, level: 70 },
        { name: 'NLP', match: false, level: 30 },
        { name: 'Machine Learning', match: true, level: 60 },
      ],
      softSkills: [
        { name: 'Esprit d\'équipe', match: true },
      ],
      experiences: [{ title: 'Data Analyst', company: 'MediCare', duration: '2020 - 2022' }],
      educations: [{ degree: 'Licence Informatique', school: 'Aix-Marseille Université', year: '2018' }],
      matchDetails: { technical: 62, experience: 65, education: 60, softSkills: 70 },
      ollamaJudgement: 'Potentiel: à renforcer sur NLP et architecture API.',
    }),
    makeCandidate(4, {
      name: 'Thomas Leroy',
      email: 'thomas.leroy@example.com',
      phone: '+33 6 20 11 02 93',
      location: 'Nantes',
      score: 73,
      status: 'matched',
      experience: 3,
      education: 'Master',
      hardSkills: [
        { name: 'Machine Learning', match: true, level: 75 },
        { name: 'NLP', match: true, level: 70 },
        { name: 'Embeddings', match: false, level: 0 },
      ],
      softSkills: [
        { name: 'Autonomie', match: true },
        { name: 'Communication', match: true },
      ],
      experiences: [{ title: 'AI Engineer', company: 'DocuFlow', duration: '2019 - 2022' }],
      educations: [{ degree: 'Master IA', school: 'Université de Nantes', year: '2019' }],
      matchDetails: { technical: 74, experience: 72, education: 78, softSkills: 68 },
      ollamaJudgement: 'Bon candidat: embeddings à approfondir.',
    }),
  ];

  return candidates;
};

