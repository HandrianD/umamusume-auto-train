import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "./ui/button";
import { useEffect, useMemo, useState } from "react";

type RacePosition = {
  id: string;
  name: string;
  description: string;
};

type Props = {
  list: string[];
  addPosition: (positionId: string) => void;
  removePosition: (positionId: string) => void;
};

export default function RacePositionSelector({ list, addPosition, removePosition }: Props) {
  const [data, setData] = useState<RacePosition[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const getRacePositions = async () => {
      try {
        // Try simple server first
        const res = await fetch("/race-positions");
        const positionResponse = await res.json();
        const positions: RacePosition[] = positionResponse.race_positions || [];
        setData(positions);
        console.log(`Loaded ${positions.length} race positions from simple server`);
      } catch (error) {
        console.error("Failed to fetch race positions from simple server:", error);
        // Fallback to local data
        try {
          const fallbackPositions: RacePosition[] = [
            { id: "1st", name: "1st Place", description: "Prioritize winning first place in races" },
            { id: "2nd", name: "2nd Place", description: "Target second place finishes" },
            { id: "3rd", name: "3rd Place", description: "Aim for third place positions" },
            { id: "front-runner", name: "Front Runner", description: "Lead from the start of the race" },
            { id: "stalker", name: "Stalker", description: "Stay close to the leader" },
            { id: "closer", name: "Closer", description: "Make a strong finish from behind" }
          ];
          setData(fallbackPositions);
          console.log(`Loaded ${fallbackPositions.length} race positions from fallback`);
        } catch (fallbackError) {
          console.error("Failed to load fallback race positions:", fallbackError);
        }
      }
    };

    getRacePositions();
  }, []);

  const filtered = useMemo(() => {
    if (!search.trim()) {
      return data;
    }

    // Use local filtering for client-side search
    return data.filter((position) =>
      position.name.toLowerCase().includes(search.toLowerCase()) ||
      position.description.toLowerCase().includes(search.toLowerCase())
    );
  }, [data, search]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  return (
    <div>
      <p className="text-xl mb-4">Select preferred race positions</p>
      <Dialog>
        <DialogTrigger asChild>
          <Button className="cursor-pointer font-semibold">Open</Button>
        </DialogTrigger>
        <DialogContent className="min-h-[512px] max-w-4xl">
          <DialogHeader>
            <DialogTitle>Race Positions</DialogTitle>
          </DialogHeader>

          <div className="flex gap-6 min-h-[400px]">
            {/* LEFT SIDE */}
            <div className="w-9/12 flex flex-col">
              <input
                placeholder="Search..."
                type="search"
                value={search}
                onChange={handleSearch}
                className="px-3 py-2 border border-gray-300 rounded-md mb-4"
              />

              <div className="mt-4 grid grid-cols-1 gap-4 overflow-auto pr-2 max-h-[420px]">
                {filtered.map(
                  (position) =>
                    !list.includes(position.id) && (
                      <div key={position.id} className="w-full border-2 border-border rounded-lg px-3 py-2 cursor-pointer hover:border-neutral-600 transition" onClick={() => addPosition(position.id)}>
                        <p className="text-lg font-semibold">{position.name}</p>
                        <p className="text-sm text-neutral-600">{position.description}</p>
                      </div>
                    )
                )}
              </div>
            </div>

            {/* RIGHT SIDE */}
            <div className="w-3/12 flex flex-col">
              <p className="font-semibold mb-2">Selected Positions</p>
              <div className="flex flex-col gap-2 overflow-auto pr-2 max-h-[420px]">
                {list.map((positionId) => {
                  const position = data.find(p => p.id === positionId);
                  return (
                    <div key={positionId} className="px-4 py-2 cursor-pointer border-2 border-border rounded-lg flex justify-between items-center hover:border-red-500 transition" onClick={() => removePosition(positionId)}>
                      <p>{position ? position.name : positionId}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
