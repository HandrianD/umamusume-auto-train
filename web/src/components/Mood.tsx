import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { MOOD } from "@/constants";

type Props = {
  minimumMood: string;
  setMood: (newMood: string) => void;
};

export default function Mood({ minimumMood, setMood }: Props) {
  return (
    <div className="w-fit px-4">
      <div className="flex flex-col gap-2">
        <label htmlFor="mood" className="text-xl font-medium">
          Minimum Mood
        </label>
        <Select value={minimumMood} onValueChange={(val) => setMood(val)}>
          <SelectTrigger className="w-28 ml-4">
            <SelectValue placeholder="Mood" />
          </SelectTrigger>
          <SelectContent>
            {MOOD.map((m) => (
              <SelectItem key={m} value={m}>
                {m}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
