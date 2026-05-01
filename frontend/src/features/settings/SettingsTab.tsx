

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


    </div>
  );
};

export default SettingsTab;
