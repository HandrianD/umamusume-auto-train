import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Input } from "./ui/input";
import type { SupportCard } from "../types";

interface SupportCardSelectorProps {
  selectedCard: SupportCard | null;
  onSelectCard: (card: SupportCard | null) => void;
  cardIndex: number;
}

export default function SupportCardSelector({ selectedCard, onSelectCard, cardIndex }: SupportCardSelectorProps) {
  const [availableCards, setAvailableCards] = useState<SupportCard[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  // Filter cards based on search term
  const filteredCards = availableCards.filter(card =>
    card.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    // Load available support cards from the API
    const loadSupportCards = async () => {
      try {
        const response = await fetch('/support-cards');
        const data = await response.json();
        setAvailableCards(data.support_cards || []);
      } catch (error) {
        console.error("Failed to load support cards:", error);
      }
    };

    loadSupportCards();
  }, []);

  const handleSelectCard = async (card: SupportCard) => {
    setLoading(true);
    try {
      // Load the JSON data for the selected card
      const response = await fetch(card.jsonUrl);
      const data = await response.json();
      const fullCard: SupportCard = {
        ...card,
        data: data
      };
      onSelectCard(fullCard);
      setIsOpen(false);
    } catch (error) {
      console.error("Failed to load card data:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <p className="text-lg font-medium">Support Card {cardIndex + 1}</p>
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 min-h-[120px] flex items-center justify-center">
        {selectedCard ? (
          <div className="flex flex-col items-center gap-2">
            <img
              src={selectedCard.imageUrl}
              alt={selectedCard.name}
              className="w-20 h-20 object-contain rounded"
            />
            <p className="text-sm font-medium text-center">{selectedCard.name}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onSelectCard(null)}
              disabled={loading}
            >
              Remove
            </Button>
          </div>
        ) : (
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="w-full h-full min-h-[100px]">
                Select Support Card
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh]">
              <DialogHeader>
                <DialogTitle>Select Support Card {cardIndex + 1}</DialogTitle>
                <div className="mt-4">
                  <Input
                    type="text"
                    placeholder="Search support cards..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
              </DialogHeader>
              <div className="overflow-y-auto h-[60vh]">
                {availableCards.length > 0 ? (
                  <div className="grid grid-cols-4 gap-4 p-4">
                    {filteredCards.map((card) => (
                      <div
                        key={card.id}
                        className="border rounded-lg p-3 cursor-pointer hover:bg-gray-50 transition-colors"
                        onClick={() => handleSelectCard(card)}
                      >
                        <img
                          src={card.imageUrl}
                          alt={card.name}
                          className="w-full h-24 object-contain rounded mb-2"
                        />
                        <p className="text-xs text-center font-medium">{card.name}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-32">
                    <p>Loading support cards...</p>
                  </div>
                )}
                {availableCards.length > 0 && filteredCards.length === 0 && (
                  <div className="flex items-center justify-center h-32">
                    <p className="text-gray-500">No support cards found matching "{searchTerm}"</p>
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
