import React from 'react';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Sliders, RotateCcw, AlertTriangle } from 'lucide-react';
import { Button } from './ui/button';

interface PriorityWeightsProps {
  priorityWeights: number[];
  onPriorityWeightsChange: (weights: number[]) => void;
  priorityWeight: string;
}

const PriorityWeights: React.FC<PriorityWeightsProps> = ({
  priorityWeights,
  onPriorityWeightsChange,
  priorityWeight
}) => {
  const handleWeightChange = (index: number, value: string) => {
    const numValue = parseFloat(value) || 0;
    if (numValue >= 0 && numValue <= 3) {
      const newWeights = [...priorityWeights];
      newWeights[index] = numValue;
      onPriorityWeightsChange(newWeights);
    }
  };

  const resetToDefaults = () => {
    switch (priorityWeight) {
      case 'HEAVY':
        onPriorityWeightsChange([1.5, 1.2, 1.0, 0.7, 0.4]);
        break;
      case 'LIGHT':
        onPriorityWeightsChange([1.2, 1.1, 1.0, 0.9, 0.8]);
        break;
      default:
        onPriorityWeightsChange([1.0, 0.8, 0.6, 0.4, 0.2]);
        break;
    }
  };

  const getPositionLabel = (index: number) => {
    const positions = ['1st Priority', '2nd Priority', '3rd Priority', '4th Priority', '5th Priority'];
    return positions[index] || `Priority ${index + 1}`;
  };

  const getWeightColor = (weight: number, index: number) => {
    if (index === 0 && weight < priorityWeights[1]) return 'border-red-300 bg-red-50';
    if (index > 0 && weight > priorityWeights[index - 1]) return 'border-orange-300 bg-orange-50';
    if (weight > 2) return 'border-purple-300 bg-purple-50';
    return 'border-gray-300';
  };

  const hasWarnings = () => {
    for (let i = 0; i < priorityWeights.length - 1; i++) {
      if (priorityWeights[i] < priorityWeights[i + 1]) return true;
    }
    return priorityWeights.some(w => w > 2);
  };

  const isDisabled = priorityWeight === 'NONE';

  return (
    <div className={`space-y-4 ${isDisabled ? 'opacity-50' : ''}`}>
      <div className="flex items-center gap-2">
        <Sliders className="h-5 w-5 text-blue-500" />
        <h4 className="text-lg font-medium text-gray-800">Priority Weights Configuration</h4>
        {hasWarnings() && !isDisabled && (
          <AlertTriangle className="h-4 w-4 text-orange-500" />
        )}
      </div>

      {isDisabled && (
        <div className="bg-gray-100 p-3 rounded-md">
          <p className="text-sm text-gray-600">
            Priority weight system is disabled. Enable it on the left to configure custom weights.
          </p>
        </div>
      )}
      
      {!isDisabled && (
        <>
          <div className="grid grid-cols-5 gap-3">
            {priorityWeights.map((weight, index) => (
              <div key={index} className="space-y-2">
                <Label htmlFor={`weight-${index}`} className="text-xs font-medium text-center block">
                  {getPositionLabel(index)}
                </Label>
                <Input
                  id={`weight-${index}`}
                  type="number"
                  min="0"
                  max="3"
                  step="0.1"
                  value={weight.toFixed(1)}
                  onChange={(e) => handleWeightChange(index, e.target.value)}
                  className={`text-center text-sm ${getWeightColor(weight, index)}`}
                  placeholder="1.0"
                />
                <p className="text-xs text-gray-500 text-center">
                  x{weight.toFixed(1)}
                </p>
              </div>
            ))}
          </div>

          <div className="flex flex-col space-y-3">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={resetToDefaults}
              className="flex items-center gap-2 self-start"
            >
              <RotateCcw className="h-4 w-4" />
              Reset to {priorityWeight} Defaults
            </Button>
            
            {hasWarnings() && (
              <div className="bg-orange-50 p-3 rounded-md border border-orange-200">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-orange-600 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-orange-800">
                    <p className="font-medium">Configuration Warning:</p>
                    <ul className="mt-1 text-xs space-y-1">
                      {priorityWeights.some(w => w > 2) && (
                        <li>• Very high weights (&gt;2.0) may cause extreme training bias</li>
                      )}
                      {(() => {
                        for (let i = 0; i < priorityWeights.length - 1; i++) {
                          if (priorityWeights[i] < priorityWeights[i + 1]) {
                            return <li key={i}>• Higher priority position has lower weight than lower priority</li>;
                          }
                        }
                        return null;
                      })()}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="bg-blue-50 p-3 rounded-md text-sm">
            <p className="text-blue-800 font-medium mb-1">How it works:</p>
            <p className="text-blue-700 text-xs">
            The Order of this is based on your priority stat order in the settings.
            Each stat gets multiplied by its priority weight during training decisions. 
            Higher weights make that priority position more attractive for training.
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default PriorityWeights;
