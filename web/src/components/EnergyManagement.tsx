import { Input } from "./ui/input";

type Props = {
  energyManagement: {
    enabled: boolean;
    never_rest_energy: number;
    skip_training_energy: number;
    skip_infirmary_unless_missing_energy: boolean;
  };
  setEnergyManagement: (settings: any) => void;
};

export default function EnergyManagement({ energyManagement, setEnergyManagement }: Props) {
  const handleEnabledChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEnergyManagement({ ...energyManagement, enabled: e.target.checked });
  };

  const handleNeverRestEnergyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Math.max(50, Math.min(100, parseInt(e.target.value) || 70));
    setEnergyManagement({ ...energyManagement, never_rest_energy: value });
  };

  const handleSkipTrainingEnergyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Math.max(10, Math.min(60, parseInt(e.target.value) || 30));
    setEnergyManagement({ ...energyManagement, skip_training_energy: value });
  };

  const handleSkipInfirmaryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEnergyManagement({ ...energyManagement, skip_infirmary_unless_missing_energy: e.target.checked });
  };

  return (
    <div className="w-fit px-4">
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-3">
          <label className="text-xl font-medium">⚡ Energy Management</label>
          <input
            type="checkbox"
            checked={energyManagement.enabled}
            onChange={handleEnabledChange}
            className="w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
        
        <p className="text-sm text-gray-600 dark:text-gray-400 -mt-2">
          Advanced energy level detection and smart energy-based decision making
        </p>

        {energyManagement.enabled && (
          <div className="ml-4 space-y-4 border-l-2 border-blue-200 dark:border-blue-700 pl-4">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium min-w-fit">Never Rest Energy Threshold:</label>
                <Input
                  type="number"
                  min="50"
                  max="100"
                  step="5"
                  value={energyManagement.never_rest_energy}
                  onChange={handleNeverRestEnergyChange}
                  disabled={!energyManagement.enabled}
                  className="w-20"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">%</span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                Above this energy level, the bot will be more aggressive with training choices and won't rest easily
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium min-w-fit">Skip Training Energy Threshold:</label>
                <Input
                  type="number"
                  min="10"
                  max="60"
                  step="5"
                  value={energyManagement.skip_training_energy}
                  onChange={handleSkipTrainingEnergyChange}
                  disabled={!energyManagement.enabled}
                  className="w-20"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">%</span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                Below this energy level, the bot will skip training and choose to rest instead
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium">Smart Infirmary Usage</label>
                <input
                  type="checkbox"
                  checked={energyManagement.skip_infirmary_unless_missing_energy}
                  onChange={handleSkipInfirmaryChange}
                  disabled={!energyManagement.enabled}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                />
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                When enabled, only go to infirmary when energy is critically low, not just when debuffed
              </p>
            </div>

            <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800/40 rounded-lg p-3">
              <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
                💡 How Energy Management Works
              </h4>
              <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1">
                <li>• <strong>High Energy ({energyManagement.never_rest_energy}%+):</strong> More aggressive training, even with fewer support cards</li>
                <li>• <strong>Normal Energy ({energyManagement.skip_training_energy}%-{energyManagement.never_rest_energy}%):</strong> Standard training logic</li>
                <li>• <strong>Low Energy (0%-{energyManagement.skip_training_energy}%):</strong> Skip training and rest to recover</li>
                <li>• <strong>Smart Infirmary:</strong> Only visit when energy is low AND debuffed</li>
              </ul>
            </div>
          </div>
        )}
        
        {!energyManagement.enabled && (
          <div className="text-center py-4 text-gray-500 dark:text-gray-400 ml-4">
            <p className="text-sm">Energy management is disabled</p>
            <p className="text-xs mt-1">Enable to use intelligent energy-based training decisions</p>
          </div>
        )}
      </div>
    </div>
  );
}
