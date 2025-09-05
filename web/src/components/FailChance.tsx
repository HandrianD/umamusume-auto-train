import { Input } from "./ui/input";

type Props = {
  maximumFailure: number;
  setFail: (newFail: number) => void;
};

export default function FailChance({ maximumFailure, setFail }: Props) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const numValue = value === '' ? 0 : parseInt(value, 10);

    // Only update if it's a valid number
    if (!isNaN(numValue) && numValue >= 0 && numValue <= 100) {
      setFail(numValue);
    }
  };

  return (
    <div className="w-fit px-4">
      <div className="flex flex-col gap-2">
        <label htmlFor="fail" className="text-xl font-medium">
          Max Failure Chance
        </label>
        <div className="flex items-center gap-2 ml-4">
          <Input
            className="w-32 text-center text-lg font-medium"
            type="number"
            name="fail"
            id="fail"
            min={0}
            max={100}
            value={maximumFailure}
            onChange={handleChange}
            placeholder="25"
          />
          <span className="text-lg font-medium">%</span>
        </div>
      </div>
    </div>
  );
}
