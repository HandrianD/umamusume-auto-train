import { useState, useEffect } from "react";
import defaultConfig from "../../config.json";
import { useConfig } from "./hooks/useConfig";
import { useConfigPreset } from "./hooks/useConfigPreset";
import { URL } from "./constants";

import CharacterSelector from "./components/CharacterSelector";
import ScenarioSelector from "./components/ScenarioSelector";
import SupportCardSelector from "./components/SupportCardSelector";
import SkillList from "./components/SkillList";
import PriorityStat from "./components/PriorityStat";
import StatCaps from "./components/StatCaps";
import Mood from "./components/Mood";
import FailChance from "./components/FailChance";
import PrioritizeG1 from "./components/PrioritizeG1";
import EventDataCollection from "./components/EventDataCollection";
import type { Character, SupportCard, Scenario } from "./types";


function App() {
  const { config } = useConfig(defaultConfig);
  const { activeIndex, activeConfig, presets, setActiveIndex, savePreset } = useConfigPreset();
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
  const [selectedSupportCards, setSelectedSupportCards] = useState<(SupportCard | null)[]>(Array(6).fill(null));
  const [priorityStat, setPriorityStat] = useState<string[]>(activeConfig?.priority_stat || config.priority_stat || []);
  const [statCaps, setStatCaps] = useState(activeConfig?.stat_caps || config.stat_caps || { spd: 0, sta: 0, pwr: 0, guts: 0, wit: 0 });
  const [minimumMood, setMinimumMood] = useState(activeConfig?.minimum_mood || config.minimum_mood || "GOOD");
  const [maximumFailure, setMaximumFailure] = useState(activeConfig?.maximum_failure || config.maximum_failure || 25);
  const [prioritizeG1, setPrioritizeG1] = useState(activeConfig?.prioritize_g1_race || config.prioritize_g1_race || false);
  const [isAutoBuySkill, setIsAutoBuySkill] = useState(activeConfig?.skill?.is_auto_buy_skill || config.skill?.is_auto_buy_skill || false);
  const [skillPtsCheck, setSkillPtsCheck] = useState(activeConfig?.skill?.skill_pts_check || config.skill?.skill_pts_check || 400);
  const [skillList, setSkillList] = useState<string[]>(activeConfig?.skill?.skill_list || config.skill?.skill_list || []);
  const [eventDataCollectionSettings, setEventDataCollectionSettings] = useState(
    (activeConfig as any)?.event_data_collection || (config as any).event_data_collection || {
      enabled: true,
      event_types: {
        character_events: true,
        support_card_events: true,
        random_events: false,
        special_events: true,
      },
      data_to_collect: {
        stat_changes: true,
        mood_changes: true,
        skill_gains: true,
        training_efficiency: true,
      },
      context_tracking: {
        current_stats: true,
        support_cards: true,
        training_year: true,
      },
      learning_features: {
        personal_learning: true,
        smart_defaults: true,
        minimum_importance_threshold: 3,
      },
    }
  );

  console.log('Config loaded:', defaultConfig);
  console.log('useConfig working:', config);
  console.log('useConfigPreset working:', { activeIndex, presets });
  console.log('Character selected:', selectedCharacter);

  console.log('Support cards selected:', selectedSupportCards);
  console.log('Scenario selected:', selectedScenario);
  console.log('Training config:', { priorityStat, statCaps, minimumMood, maximumFailure, prioritizeG1 });

  // Update local state when active preset changes
  useEffect(() => {
    if (activeConfig) {
      setPriorityStat(activeConfig.priority_stat || []);
      setStatCaps(activeConfig.stat_caps || { spd: 0, sta: 0, pwr: 0, guts: 0, wit: 0 });
      setMinimumMood(activeConfig.minimum_mood || "GOOD");
      setMaximumFailure(activeConfig.maximum_failure || 25);
      setPrioritizeG1(activeConfig.prioritize_g1_race || false);
      setIsAutoBuySkill(activeConfig.skill?.is_auto_buy_skill || false);
      setSkillPtsCheck(activeConfig.skill?.skill_pts_check || 400);
      setSkillList(activeConfig.skill?.skill_list || []);
      setSelectedCharacter((activeConfig.character as any) || null);
      setSelectedScenario((activeConfig.scenario as any) || null);
      setSelectedSupportCards((activeConfig.support_cards as any) || Array(6).fill(null));
      setEventDataCollectionSettings((activeConfig as any).event_data_collection || {
        enabled: true,
        event_types: {
          character_events: true,
          support_card_events: true,
          random_events: false,
          special_events: true,
        },
        data_to_collect: {
          stat_changes: true,
          mood_changes: true,
          skill_gains: true,
          training_efficiency: true,
        },
        context_tracking: {
          current_stats: true,
          support_cards: true,
          training_year: true,
        },
        learning_features: {
          personal_learning: true,
          smart_defaults: true,
          minimum_importance_threshold: 3,
        },
      });
    }
  }, [activeIndex, activeConfig]);

  const handleSelectSupportCard = (index: number) => (card: SupportCard | null) => {
    const newCards = [...selectedSupportCards];
    newCards[index] = card;
    setSelectedSupportCards(newCards);
  };

  const handleSetStatCaps = (stat: string, value: number) => {
    setStatCaps(prev => ({ ...prev, [stat]: value }));
  };

  const handleAddSkill = (skillName: string) => {
    setSkillList(prev => [...prev, skillName]);
  };

  const handleDeleteSkill = (skillName: string) => {
    setSkillList(prev => prev.filter(skill => skill !== skillName));
  };

  const handleSavePreset = async () => {
    // Create simplified config for saving to server (only essential data)
    const serverConfig = {
      ...config,
      priority_stat: priorityStat,
      stat_caps: statCaps,
      minimum_mood: minimumMood,
      maximum_failure: maximumFailure,
      prioritize_g1_race: prioritizeG1,
      skill: {
        is_auto_buy_skill: isAutoBuySkill,
        skill_pts_check: skillPtsCheck,
        skill_list: skillList,
      },
      character: selectedCharacter ? {
        id: selectedCharacter.id,
        name: selectedCharacter.name
      } : null,
      scenario: selectedScenario ? {
        id: selectedScenario.id,
        name: selectedScenario.name
      } : null,
      support_cards: selectedSupportCards.map(card => 
        card ? { id: card.id, name: card.name } : null
      ),
      event_data_collection: eventDataCollectionSettings,
    };
    
    // Save to localStorage preset (with full data)
    const fullConfig = {
      ...config,
      priority_stat: priorityStat,
      stat_caps: statCaps,
      minimum_mood: minimumMood,
      maximum_failure: maximumFailure,
      prioritize_g1_race: prioritizeG1,
      skill: {
        is_auto_buy_skill: isAutoBuySkill,
        skill_pts_check: skillPtsCheck,
        skill_list: skillList,
      },
      character: selectedCharacter,
      scenario: selectedScenario,
      support_cards: selectedSupportCards,
      event_data_collection: eventDataCollectionSettings,
    };
    savePreset(fullConfig);
    
    // Save simplified config to server config.json
    try {
      const res = await fetch(`${URL}/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(serverConfig),
      });

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

      const data = await res.json();
      console.log("Configuration saved to server:", data);
      alert("Configuration saved successfully!");
    } catch (error) {
      console.error("Failed to save configuration:", error);
      alert("Failed to save configuration to server!");
    }
  };


  return (
    <div className="w-full flex justify-center">
      <div className="mt-8 w-11/12 max-w-7xl">
        <h1 className="text-4xl font-bold mb-8 text-center">Uma Auto Train</h1>
        <p className="text-center mb-8 text-gray-600">Complete training configuration interface</p>

        {/* Preset Management */}
        <div className="mb-8 p-4 bg-blue-50 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Preset Management</h3>
          <div className="flex flex-wrap gap-2 mb-4">
            {presets.map((preset, i) => (
              <button
                key={i}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  i === activeIndex 
                    ? 'bg-blue-500 text-white shadow-md' 
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
                onClick={() => setActiveIndex(i)}
              >
                {preset.name}
              </button>
            ))}
          </div>
          <button
            className="px-6 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors font-medium shadow-sm"
            onClick={handleSavePreset}
          >
            💾 Save Current Configuration
          </button>
        </div>

        {/* Main 2x2 Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Left: Character & Scenario Selection */}
          <div className="bg-white rounded-lg border p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Character & Scenario Selection</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <CharacterSelector
                selectedCharacter={selectedCharacter}
                onSelectCharacter={setSelectedCharacter}
              />
              <ScenarioSelector
                selectedScenario={selectedScenario}
                onSelectScenario={setSelectedScenario}
              />
            </div>
          </div>

          {/* Top Right: Training Configuration */}
          <div className="bg-white rounded-lg border p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Training Configuration</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PriorityStat
                priorityStat={priorityStat}
                setPriorityStat={setPriorityStat}
              />
              <StatCaps
                statCaps={statCaps}
                setStatCaps={handleSetStatCaps}
              />
              <Mood
                minimumMood={minimumMood}
                setMood={setMinimumMood}
              />
              <FailChance
                maximumFailure={maximumFailure}
                setFail={setMaximumFailure}
              />
            </div>
          </div>

          {/* Bottom Left: Support Card Selection */}
          <div className="bg-white rounded-lg border p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Support Cards</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {selectedSupportCards.map((_, index) => (
                <SupportCardSelector
                  key={index}
                  selectedCard={selectedSupportCards[index]}
                  onSelectCard={handleSelectSupportCard(index)}
                  cardIndex={index}
                />
              ))}
            </div>
          </div>

          {/* Bottom Right: Race Settings and Data Collection */}
          <div className="bg-white rounded-lg border p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Race Settings & Data Collection</h3>
            <div className="space-y-6">
              <PrioritizeG1
                prioritizeG1Race={prioritizeG1}
                setPrioritizeG1={setPrioritizeG1}
              />
              
              {/* Skill Configuration */}
              <div className="border-t pt-4">
                <h4 className="text-lg font-medium mb-3 text-gray-700">Skill Configuration</h4>
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="autoBuySkill"
                      checked={isAutoBuySkill}
                      onChange={(e) => setIsAutoBuySkill(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="autoBuySkill" className="text-sm font-medium">
                      Auto-buy skills when available
                    </label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <label htmlFor="skillPts" className="text-sm font-medium">
                      Skill Points Threshold:
                    </label>
                    <input
                      type="number"
                      id="skillPts"
                      value={skillPtsCheck}
                      onChange={(e) => setSkillPtsCheck(Number(e.target.value))}
                      className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                      min="0"
                      max="1000"
                    />
                  </div>
                  
                  <SkillList
                    list={skillList}
                    addSkillList={handleAddSkill}
                    deleteSkillList={handleDeleteSkill}
                  />
                </div>
              </div>
              
              <div className="border-t pt-4">
                <EventDataCollection
                  settings={eventDataCollectionSettings}
                  onSettingsChange={setEventDataCollectionSettings}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
