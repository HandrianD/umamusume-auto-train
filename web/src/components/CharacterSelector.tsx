import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Input } from "./ui/input";
import type { Character } from "../types";

interface CharacterSelectorProps {
  selectedCharacter: Character | null;
  onSelectCharacter: (character: Character | null) => void;
}

export default function CharacterSelector({ selectedCharacter, onSelectCharacter }: CharacterSelectorProps) {
  const [availableCharacters, setAvailableCharacters] = useState<Character[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  // Filter characters based on search term
  const filteredCharacters = availableCharacters.filter(character =>
    character.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    // Load available characters from the API
    const loadCharacters = async () => {
      try {
        const response = await fetch('/characters');
        const data = await response.json();
        setAvailableCharacters(data.characters || []);
      } catch (error) {
        console.error("Failed to load characters:", error);
      }
    };

    loadCharacters();
  }, []);

  const handleSelectCharacter = async (character: Character) => {
    setLoading(true);
    try {
      // Load the JSON data for the selected character
      const response = await fetch(character.jsonUrl);
      const data = await response.json();
      const fullCharacter: Character = {
        ...character,
        data: data
      };
      onSelectCharacter(fullCharacter);
      setIsOpen(false);
    } catch (error) {
      console.error("Failed to load character data:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <p className="text-lg font-medium">Character Selection</p>
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 min-h-[120px] flex items-center justify-center">
        {selectedCharacter ? (
          <div className="flex flex-col items-center gap-2">
            <img
              src={selectedCharacter.imageUrl}
              alt={selectedCharacter.name}
              className="w-20 h-20 object-contain rounded"
            />
            <p className="text-sm font-medium text-center">{selectedCharacter.name}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onSelectCharacter(null)}
              disabled={loading}
            >
              Remove
            </Button>
          </div>
        ) : (
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="w-full h-full min-h-[100px]">
                Select Character
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh]">
              <DialogHeader>
                <DialogTitle>Select Character</DialogTitle>
                <div className="mt-4">
                  <Input
                    type="text"
                    placeholder="Search characters..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
              </DialogHeader>
              <div className="overflow-y-auto h-[60vh]">
                {availableCharacters.length > 0 ? (
                  <div className="grid grid-cols-4 gap-4 p-4">
                    {filteredCharacters.map((character) => (
                      <div
                        key={character.id}
                        className="border rounded-lg p-3 cursor-pointer hover:bg-gray-50 transition-colors"
                        onClick={() => handleSelectCharacter(character)}
                      >
                        <img
                          src={character.imageUrl}
                          alt={character.name}
                          className="w-full h-24 object-contain rounded mb-2"
                        />
                        <p className="text-xs text-center font-medium">{character.name}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-32">
                    <p>Loading characters...</p>
                  </div>
                )}
                {availableCharacters.length > 0 && filteredCharacters.length === 0 && (
                  <div className="flex items-center justify-center h-32">
                    <p className="text-gray-500">No characters found matching "{searchTerm}"</p>
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
