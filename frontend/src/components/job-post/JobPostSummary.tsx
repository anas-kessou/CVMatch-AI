import type { JobDescription } from '@/types/app';

interface JobPostSummaryProps {
  job: JobDescription;
}

const JobPostSummary = ({ job }: JobPostSummaryProps) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-3">Profil recherché</h3>
      <p className="text-xl font-bold text-gray-800">{job.title}</p>
      <p className="text-sm text-gray-500">{job.company}</p>
      <p className="text-sm text-gray-600 mt-2">{job.description}</p>
    </div>
  );
};

export default JobPostSummary;
