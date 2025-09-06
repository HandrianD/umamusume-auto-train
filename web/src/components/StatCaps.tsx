import { Input } from "./ui/input";

import type { Stat } from '../types';

type Props = {
  statCaps: Stat;
  setStatCaps: (stat: string, field: 'min' | 'max', value: number) => void;
};


export default function StatCaps({ statCaps, setStatCaps }: Props) {
  const handleChange = (stat: string, field: 'min' | 'max') => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const numValue = value === '' ? 0 : parseInt(value, 10);
    if (!isNaN(numValue) && numValue >= 0) {
      setStatCaps(stat, field, numValue);
    }
  };

  return (
    <div className="flex flex-col gap-2 w-fit px-4">
      <p className="text-xl">Stat Caps</p>
      <div className="flex flex-col gap-2">
        {Object.entries(statCaps).map(([stat, val]) => (
          <div key={stat} className="flex items-center gap-4">
            <span className="inline-block w-16">{stat.toUpperCase()}</span>
            <label className="flex items-center gap-1">
              <span className="text-xs text-gray-500">Min</span>
              <Input
                type="number"
                value={val.min}
                min={0}
                onChange={handleChange(stat, 'min')}
                className="w-20"
              />
            </label>
            <label className="flex items-center gap-1">
              <span className="text-xs text-gray-500">Max</span>
              <Input
                type="number"
                value={val.max}
                min={0}
                onChange={handleChange(stat, 'max')}
                className="w-20"
              />
            </label>
          </div>
        ))}
      </div>
    </div>
  );
}
