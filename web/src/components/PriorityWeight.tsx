import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Label } from './ui/label';
import { Info } from 'lucide-react';

interface PriorityWeightProps {
  priorityWeight: string;
  onPriorityWeightChange: (weight: string) => void;
}

const PriorityWeight: React.FC<PriorityWeightProps> = ({
  priorityWeight,
  onPriorityWeightChange
}) => {
  const weightDescriptions = {
    NONE: "Disabled - Use original training logic with auto balanced stats gain",
    LIGHT: "Subtle priority weighting (1.2x, 1.1x, 1.0x, 0.9x, 0.8x)",
    MEDIUM: "Moderate priority weighting - Uses custom weights",
    HEAVY: "Strong priority weighting (1.5x, 1.2x, 1.0x, 0.7x, 0.4x)"
  };

  const getWeightColor = (weight: string) => {
    switch (weight) {
      case 'NONE': return 'text-gray-500';
      case 'LIGHT': return 'text-green-600';
      case 'MEDIUM': return 'text-blue-600';
      case 'HEAVY': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  const getWeightBadge = (weight: string) => {
    const colors = {
      NONE: 'bg-gray-100 text-gray-700',
      LIGHT: 'bg-green-100 text-green-800',
      MEDIUM: 'bg-blue-100 text-blue-800',
      HEAVY: 'bg-red-100 text-red-800'
    };
    return colors[weight as keyof typeof colors] || colors.NONE;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Info className="h-5 w-5 text-blue-500" />
        <h4 className="text-lg font-medium text-gray-800">Priority Weight System</h4>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getWeightBadge(priorityWeight)}`}>
          {priorityWeight}
        </span>
      </div>
      
      <div className="space-y-3">
        <div className="space-y-2">
          <Label htmlFor="priority-weight" className="text-sm font-medium">
            Weight Level
          </Label>
          <Select value={priorityWeight} onValueChange={onPriorityWeightChange}>
            <SelectTrigger id="priority-weight" className="w-full">
              <SelectValue placeholder="Select weight level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="NONE">None (Disabled)</SelectItem>
              <SelectItem value="LIGHT">Light</SelectItem>
              <SelectItem value="MEDIUM">Medium</SelectItem>
              <SelectItem value="HEAVY">Heavy</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="bg-gray-50 p-3 rounded-md">
          <p className={`text-sm ${getWeightColor(priorityWeight)} font-medium`}>
            {weightDescriptions[priorityWeight as keyof typeof weightDescriptions] || 'Unknown weight level'}
          </p>
          {priorityWeight !== 'NONE' && (
            <p className="text-xs text-gray-600 mt-1">
              Training decisions will be weighted based on stat priority order. 
              Higher priority stats receive higher multipliers.
            </p>
          )}
        </div>
        
        {(priorityWeight !== 'NONE' ) && (
          <div className="bg-blue-50 p-3 rounded-md border border-blue-200">
            <p className="text-sm text-blue-800 font-medium">Custom Weights Mode</p>
            <p className="text-xs text-blue-600 mt-1">
              Configure individual multipliers for each priority position using the section on the right.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PriorityWeight;
