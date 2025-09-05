import { Input } from "./ui/input";

type Props = {
  statCaps: {
    spd: number;
    sta: number;
    pwr: number;
    guts: number;
    wit: number;
  };
  setStatCaps: (keys: string, value: number) => void;
};

export default function StatCaps({ statCaps, setStatCaps }: Props) {
  const handleChange = (stat: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const numValue = value === '' ? 0 : parseInt(value, 10);

    // Only update if it's a valid number
    if (!isNaN(numValue) && numValue >= 0) {
      setStatCaps(stat, numValue);
    }
  };

  return (
    <div className="flex flex-col gap-2 w-fit px-4">
      <p className="text-xl">Stat Caps</p>
      <div className="flex flex-col gap-2">
        {Object.entries(statCaps).map(([stat, val]) => (
          <label key={stat} className="flex items-center gap-4">
            <span className="inline-block w-16">{stat.toUpperCase()}</span>
            <Input
              type="number"
              value={val}
              min={0}
              onChange={handleChange(stat)}
            />
          </label>
        ))}
      </div>
    </div>
  );
}
