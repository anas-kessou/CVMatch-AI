

import { useState } from 'react';
import { useScoringSettings } from '@/hooks/useScoringSettings';

interface SettingsTabProps {
  excellentThreshold: number;
  setExcellentThreshold: (val: number) => void;
  goodThreshold: number;
  setGoodThreshold: (val: number) => void;
}

const SettingsTab = ({
  excellentThreshold,
  setExcellentThreshold,
  goodThreshold,
  setGoodThreshold,
}: SettingsTabProps) => {
  const { weights, updateWeight, saveSettings, resetToDefault, isLoading, isSaving, error: apiError } = useScoringSettings();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const totalWeights = Object.values(weights).reduce((a, b) => a + b, 0);

  const weightKeys = [
    { key: 'skills' as const, label: 'Poids - Compétences Techniques' },
    { key: 'experience' as const, label: 'Poids - Expérience' },
    { key: 'education' as const, label: "Poids - Niveau d'études" },
    { key: 'softSkills' as const, label: 'Poids - Soft Skills' },
  ];

  const handleSave = async () => {
    setSuccessMsg(null);
    try {
      await saveSettings();
      setSuccessMsg('Pondérations sauvegardées avec succès !');
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err) {
      // Error is handled by the hook
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-bold text-gray-800 border-l-4 border-emerald-500 pl-3">Configuration du Scoring</h3>
          <div className="px-4 py-2 rounded-lg text-sm font-bold bg-emerald-50 text-emerald-600 border border-emerald-200">
            Total : {totalWeights}%
          </div>
        </div>
        
        {apiError && (
          <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-md text-red-600 text-sm">
            ⚠️ {apiError}
          </div>
        )}

        {successMsg && (
          <div className="mb-6 p-3 bg-emerald-50 border border-emerald-200 rounded-md text-emerald-600 text-sm">
            ✅ {successMsg}
          </div>
        )}

        {isLoading ? (
          <div className="text-gray-500 text-sm">Chargement des paramètres...</div>
        ) : (
          <div className="space-y-6">
            {weightKeys.map(({ key, label }) => (
              <div key={key}>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-semibold text-gray-700">
                    {label}
                  </label>
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-bold text-emerald-600">{weights[key]}%</span>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={weights[key]}
                    onChange={(e) => updateWeight(key, Number(e.target.value))}
                    className="flex-1 accent-emerald-600"
                  />
                  <input 
                    type="number" 
                    min="0" 
                    max="100" 
                    value={weights[key]} 
                    onChange={(e) => updateWeight(key, Number(e.target.value))}
                    className="w-16 p-1 text-center border rounded-md text-sm font-bold focus:outline-none focus:ring-2 border-gray-200 focus:ring-emerald-500"
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 flex justify-end gap-4">
          <button
            onClick={resetToDefault}
            disabled={isSaving || isLoading}
            className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
          >
            Réinitialiser
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || isLoading}
            className="px-6 py-2 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors shadow-sm"
          >
            {isSaving ? 'Enregistrement...' : 'Enregistrer'}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-6 border-l-4 border-emerald-500 pl-3">Seuils de scoring (définition des couleurs)</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Seuil Excellent */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-sm font-semibold text-gray-700">Seuil Excellent Match</label>
              <span className="text-sm font-bold text-emerald-600">{excellentThreshold}%</span>
            </div>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min={goodThreshold + 1}
                max="100"
                value={excellentThreshold}
                onChange={(e) => setExcellentThreshold(Number(e.target.value))}
                className="flex-1 accent-emerald-600"
              />
              <input 
                type="number" 
                min={goodThreshold + 1}
                max="100" 
                value={excellentThreshold} 
                onChange={(e) => setExcellentThreshold(Math.max(goodThreshold + 1, Math.min(100, Number(e.target.value))))}
                className="w-16 p-1 text-center border rounded-md text-sm font-bold focus:outline-none focus:ring-2 border-gray-200 focus:ring-emerald-500"
              />
            </div>
          </div>

          {/* Seuil Bon */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-sm font-semibold text-gray-700">Seuil Bon Match</label>
              <span className="text-sm font-bold text-blue-600">{goodThreshold}%</span>
            </div>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max={excellentThreshold - 1}
                value={goodThreshold}
                onChange={(e) => setGoodThreshold(Number(e.target.value))}
                className="flex-1 accent-blue-600"
              />
              <input 
                type="number" 
                min="0"
                max={excellentThreshold - 1} 
                value={goodThreshold} 
                onChange={(e) => setGoodThreshold(Math.max(0, Math.min(excellentThreshold - 1, Number(e.target.value))))}
                className="w-16 p-1 text-center border rounded-md text-sm font-bold focus:outline-none focus:ring-2 border-gray-200 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-200">
            <p className="font-bold text-emerald-700">Excellent match</p>
            <p className="text-2xl font-bold text-emerald-800">≥ {excellentThreshold}%</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="font-bold text-blue-700">Bon match</p>
            <p className="text-2xl font-bold text-blue-800">{goodThreshold}-{excellentThreshold - 1}%</p>
          </div>
          <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
            <p className="font-bold text-amber-700">À revoir</p>
            <p className="text-2xl font-bold text-amber-800">&lt; {goodThreshold}%</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsTab;
