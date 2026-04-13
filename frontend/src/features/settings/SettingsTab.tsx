import { Search } from 'lucide-react';

const SettingsTab = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-6">Configuration du Scoring</h3>
        <div className="space-y-6">
          {[40, 30, 20, 10].map((value, index) => (
            <div key={value}>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-semibold text-gray-700">
                  {index === 0 && 'Poids - Compétences Techniques'}
                  {index === 1 && 'Poids - Expérience'}
                  {index === 2 && 'Poids - Niveau d\'études'}
                  {index === 3 && 'Poids - Soft Skills'}
                </label>
                <span className="text-sm text-emerald-600 font-bold">{value}%</span>
              </div>
              <input type="range" defaultValue={value} className="w-full accent-emerald-600" disabled />
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-6">Seuils de scoring</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-200">
            <p className="font-bold text-emerald-700">Excellent match</p>
            <p className="text-2xl font-bold text-emerald-800">≥ 85%</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="font-bold text-blue-700">Bon match</p>
            <p className="text-2xl font-bold text-blue-800">70-84%</p>
          </div>
          <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
            <p className="font-bold text-amber-700">À revoir</p>
            <p className="text-2xl font-bold text-amber-800">{'< 70%'}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Sites de recherche académique</h3>
        <div className="grid grid-cols-2 gap-4">
          {[
            { name: 'Google Scholar', url: 'https://scholar.google.com', desc: 'Recherche d\'articles académiques' },
            { name: 'ScienceDirect', url: 'https://sciencedirect.com', desc: 'Publications scientifiques' },
            { name: 'IEEE Xplore', url: 'https://ieeexplore.ieee.org', desc: 'Ingénierie et technologie' },
            { name: 'Scopus', url: 'https://scopus.com', desc: 'Base de données bibliographique' },
          ].map((site) => (
            <a
              key={site.name}
              href={site.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-emerald-300 transition-all group"
            >
              <div className="p-2 bg-slate-100 rounded-lg group-hover:bg-emerald-100 transition-colors">
                <Search className="w-5 h-5 text-gray-600 group-hover:text-emerald-600 transition-colors" />
              </div>
              <div>
                <p className="font-semibold text-gray-800 group-hover:text-emerald-700 transition-colors">{site.name}</p>
                <p className="text-sm text-gray-500">{site.desc}</p>
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SettingsTab;
