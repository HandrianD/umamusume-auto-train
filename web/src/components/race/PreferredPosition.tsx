import { POSITION } from "../../constants";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";

type Props = {
  preferredPosition: string;
  setPreferredPosition: (val: string) => void;
  enablePositionsByRace: boolean;
  positionSelectionEnabled: boolean;
};

export default function PreferredPosition({ preferredPosition, setPreferredPosition, enablePositionsByRace, positionSelectionEnabled }: Props) {
  return (
    <label htmlFor="preferred-position" className="flex gap-2 items-center">
      <span className="text-xl shrink-0">Preferred Position</span>
      <Select disabled={!(positionSelectionEnabled && !enablePositionsByRace)} value={preferredPosition} onValueChange={(val) => setPreferredPosition(val)}>
        <SelectTrigger className="w-24">
          <SelectValue placeholder="Position" />
        </SelectTrigger>
        <SelectContent>
          {POSITION.map((pos) => (
            <SelectItem key={pos} value={pos}>
              {pos.toUpperCase()}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </label>
  );
}
