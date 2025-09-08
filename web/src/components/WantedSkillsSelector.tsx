import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useEffect, useMemo, useState } from "react";

type Skill = {
  id: string;
  name: string;
  name_jp: string;
  description: string;
  icon_url: string;
  scraped_at: string;
  source: string;
};

type Props = {
  list: string[];
  addWantedSkill: (skillName: string) => void;
  removeWantedSkill: (skillName: string) => void;
};

export default function WantedSkillsSelector({ list, addWantedSkill, removeWantedSkill }: Props) {
  const [data, setData] = useState<Skill[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const getSkillData = async () => {
      try {
        // Try simple server first
        const res = await fetch("/skills");
        const skillResponse = await res.json();
        const skills: Skill[] = skillResponse.skills || [];
        setData(skills);
        console.log(`Loaded ${skills.length} skills from simple server`);
      } catch (error) {
        console.error("Failed to fetch skills from simple server:", error);
        // Fallback to GitHub if server fails
        try {
          const res = await fetch("https://raw.githubusercontent.com/samsulpanjul/umamusume-auto-train/refs/heads/dev/data/skills.json");
          const skills: any[] = await res.json();
          // Transform old format to new format
          const transformedSkills: Skill[] = skills.map(skill => ({
            id: "",
            name: skill.name || "",
            name_jp: "",
            description: skill.description || "",
            icon_url: "",
            scraped_at: "",
            source: "fallback"
          }));
          setData(transformedSkills);
          console.log(`Loaded ${transformedSkills.length} skills from GitHub fallback`);
        } catch (fallbackError) {
          console.error("Failed to fetch skills from fallback:", fallbackError);
        }
      }
    };

    getSkillData();
  }, []);

  const filtered = useMemo(() => {
    if (!search.trim()) {
      return data;
    }

    // Use local filtering for client-side search
    return data.filter((skill) =>
      skill.name.toLowerCase().includes(search.toLowerCase()) ||
      skill.name_jp.toLowerCase().includes(search.toLowerCase()) ||
      skill.description.toLowerCase().includes(search.toLowerCase())
    );
  }, [data, search]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  return (
    <div>
      <p className="text-m mb-4">Select skills Hint From Events</p>
      <p className="text-m mb-4">The System Will Handle if the event show up.</p>
      <Dialog>
        <DialogTrigger asChild>
          <Button className="cursor-pointer font-semibold">Open</Button>
        </DialogTrigger>
        <DialogContent className="min-h-[512px] max-w-4xl">
          <DialogHeader>
            <DialogTitle>Wanted Skills</DialogTitle>
          </DialogHeader>

          <div className="flex gap-6 min-h-[400px]">
            {/* LEFT SIDE */}
            <div className="w-9/12 flex flex-col">
              <Input placeholder="Search..." type="search" value={search} onChange={handleSearch} />

              <div className="mt-4 grid grid-cols-2 gap-4 overflow-auto pr-2 max-h-[420px]">
                {filtered.map(
                  (skill) =>
                    !list.includes(skill.name) && (
                      <div key={skill.name} className="w-full border-2 border-border rounded-lg px-3 py-2 cursor-pointer hover:border-neutral-600 transition" onClick={() => addWantedSkill(skill.name)}>
                        <p className="text-lg font-semibold">{skill.name}</p>
                        <p className="text-sm text-neutral-600">{skill.description}</p>
                      </div>
                    )
                )}
              </div>
            </div>

            {/* RIGHT SIDE */}
            <div className="w-3/12 flex flex-col">
              <p className="font-semibold mb-2">Wanted Skills</p>
              <div className="flex flex-col gap-2 overflow-auto pr-2 max-h-[420px]">
                {list.map((item) => (
                  <div key={item} className="px-4 py-2 cursor-pointer border-2 border-border rounded-lg flex justify-between items-center hover:border-red-500 transition" onClick={() => removeWantedSkill(item)}>
                    <p>{item}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
