import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Input } from "./ui/input";
import type { Scenario } from "../types";

interface ScenarioSelectorProps {
  selectedScenario: Scenario | null;
  onSelectScenario: (scenario: Scenario | null) => void;
}

export default function ScenarioSelector({ selectedScenario, onSelectScenario }: ScenarioSelectorProps) {
  const [availableScenarios, setAvailableScenarios] = useState<Scenario[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  // Filter scenarios based on search term
  const filteredScenarios = availableScenarios.filter(scenario =>
    scenario.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    // Load available scenarios from the API
    const loadScenarios = async () => {
      try {
        const response = await fetch('/scenarios');
        const data = await response.json();
        setAvailableScenarios(data.scenarios || []);
      } catch (error) {
        console.error("Failed to load scenarios:", error);
      }
    };

    loadScenarios();
  }, []);

  const handleSelectScenario = async (scenario: Scenario) => {
    setLoading(true);
    try {
      onSelectScenario(scenario);
      setIsOpen(false);
    } catch (error) {
      console.error("Failed to select scenario:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <p className="text-lg font-medium">Scenario Selection</p>
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 min-h-[120px] flex items-center justify-center">
        {selectedScenario ? (
          <div className="flex flex-col items-center gap-2">
            <img
              src={selectedScenario.imageUrl}
              alt={selectedScenario.name}
              className="w-20 h-20 object-contain rounded"
            />
            <p className="text-sm font-medium text-center">{selectedScenario.name}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onSelectScenario(null)}
              disabled={loading}
            >
              Remove
            </Button>
          </div>
        ) : (
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="w-full h-full min-h-[100px]">
                Select Scenario
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh]">
              <DialogHeader>
                <DialogTitle>Select Scenario</DialogTitle>
                <div className="mt-4">
                  <Input
                    type="text"
                    placeholder="Search scenarios..."
                    value={searchTerm}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
              </DialogHeader>
              <div className="overflow-y-auto h-[60vh]">
                {availableScenarios.length > 0 ? (
                  <div className="grid grid-cols-4 gap-4 p-4">
                    {filteredScenarios.map((scenario) => (
                      <div
                        key={scenario.id}
                        className="border rounded-lg p-3 cursor-pointer hover:bg-gray-50 transition-colors"
                        onClick={() => handleSelectScenario(scenario)}
                      >
                        <img
                          src={scenario.imageUrl}
                          alt={scenario.name}
                          className="w-full h-24 object-contain rounded mb-2"
                        />
                        <p className="text-xs text-center font-medium">{scenario.name}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-32">
                    <p>Loading scenarios...</p>
                  </div>
                )}
                {availableScenarios.length > 0 && filteredScenarios.length === 0 && (
                  <div className="flex items-center justify-center h-32">
                    <p className="text-gray-500">No scenarios found matching "{searchTerm}"</p>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </div>
);
}
