import { useState, useEffect } from "react";
import defaultConfig from "../../config.json";
import { useConfig } from "./hooks/useConfig";
import { useConfigPreset } from "./hooks/useConfigPreset";
import { URL } from "./constants";

import CharacterSelector from "./components/CharacterSelector";
import ScenarioSelector from "./components/ScenarioSelector";
import SupportCardSelector from "./components/SupportCardSelector";
import SkillList from "./components/SkillList";
import WantedSkillsSelector from "./components/WantedSkillsSelector";
import IsPositionSelectionEnabled from "./components/race/IsPositionSelectionEnabled";
import PreferredPosition from "./components/race/PreferredPosition";
import IsPositionByRace from "./components/race/IsPositionByRace";
import PositionByRace from "./components/race/PositionByRace";
import PriorityStat from "./components/PriorityStat";
import StatCaps from "./components/StatCaps";
import Mood from "./components/Mood";
import FailChance from "./components/FailChance";
import PrioritizeG1 from "./components/PrioritizeG1";
import EventDataCollection from "./components/EventDataCollection";
import EnergyManagement from "./components/EnergyManagement";
import PriorityWeight from "./components/PriorityWeight";
import PriorityWeights from "./components/PriorityWeights";
import type { Character, SupportCard, Scenario } from "./types";


function App() {
  const { config } = useConfig(defaultConfig);
  const { activeIndex, activeConfig, presets, setActiveIndex, savePreset } = useConfigPreset();
  
  // Helper function to normalize stat caps
  const normalizeStatCaps = (caps: any) => {
    const defaultCaps = {
      spd: { min: 0, max: 1200 },
      sta: { min: 0, max: 800 },
      pwr: { min: 0, max: 800 },
      guts: { min: 0, max: 350 },
      wit: { min: 0, max: 400 }
    };
    
    if (!caps || typeof caps !== 'object') return defaultCaps;
    
    const result: any = {};
    ['spd', 'sta', 'pwr', 'guts', 'wit'].forEach(stat => {
      const val = caps[stat];
      if (typeof val === 'object' && val !== null) {
        const typedVal = val as { min?: number, max?: number };
        result[stat] = { 
          min: typedVal.min ?? 0, 
          max: typedVal.max ?? defaultCaps[stat as keyof typeof defaultCaps].max 
        };
      } else if (typeof val === 'number') {
        result[stat] = { min: val, max: defaultCaps[stat as keyof typeof defaultCaps].max };
      } else {
        result[stat] = defaultCaps[stat as keyof typeof defaultCaps];
      }
    });
    
    return result;
  };
  
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
  const [selectedSupportCards, setSelectedSupportCards] = useState<(SupportCard | null)[]>(Array(6).fill(null));
  const [priorityStat, setPriorityStat] = useState<string[]>(activeConfig?.priority_stat || config.priority_stat || []);
  const [statCaps, setStatCaps] = useState(normalizeStatCaps(activeConfig?.stat_caps || config.stat_caps));
  const [minimumMood, setMinimumMood] = useState(activeConfig?.minimum_mood || config.minimum_mood || "GOOD");
  const [maximumFailure, setMaximumFailure] = useState(activeConfig?.maximum_failure || config.maximum_failure || 25);
  const [prioritizeG1, setPrioritizeG1] = useState(activeConfig?.prioritize_g1_race || config.prioritize_g1_race || false);
  const [isAutoBuySkill, setIsAutoBuySkill] = useState(activeConfig?.skill?.is_auto_buy_skill || config.skill?.is_auto_buy_skill || false);
  const [skillPtsCheck, setSkillPtsCheck] = useState(activeConfig?.skill?.skill_pts_check || config.skill?.skill_pts_check || 400);
  const [skillList, setSkillList] = useState<string[]>(activeConfig?.skill?.skill_list || config.skill?.skill_list || []);
  const [wantedSkills, setWantedSkills] = useState<string[]>(activeConfig?.wanted_skills || config.wanted_skills || []);
  const [positionSelectionEnabled, setPositionSelectionEnabled] = useState(activeConfig?.position_selection_enabled || config.position_selection_enabled || false);
  const [preferredPosition, setPreferredPosition] = useState(activeConfig?.preferred_position || config.preferred_position || "front");
  const [enablePositionsByRace, setEnablePositionsByRace] = useState(activeConfig?.enable_positions_by_race || config.enable_positions_by_race || false);
  const [positionsByRace, setPositionsByRace] = useState(activeConfig?.positions_by_race || config.positions_by_race || {
    sprint: "front",
    mile: "pace",
    medium: "late",
    long: "end"
  });
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
      user_intervention_timeout: 10,
    }
  );
  const [energyManagement, setEnergyManagement] = useState(
    (activeConfig as any)?.energy_management || (config as any).energy_management || {
      enabled: true,
      never_rest_energy: 70,
      skip_training_energy: 30,
      skip_infirmary_unless_missing_energy: true,
    }
  );
  const [priorityWeight, setPriorityWeight] = useState<string>(
    (activeConfig as any)?.priority_weight || (config as any).priority_weight || "NONE"
  );
  const [priorityWeights, setPriorityWeights] = useState<number[]>(
    (activeConfig as any)?.priority_weights || (config as any).priority_weights || [1.0, 1.0, 1.0, 1.0, 1.0]
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
      setStatCaps(normalizeStatCaps(activeConfig.stat_caps));
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
        user_intervention_timeout: 10,
      });
      setEnergyManagement((activeConfig as any).energy_management || {
        enabled: true,
        never_rest_energy: 70,
        skip_training_energy: 30,
        skip_infirmary_unless_missing_energy: true,
      });
      setPriorityWeight((activeConfig as any).priority_weight || "NONE");
      setPriorityWeights((activeConfig as any).priority_weights || [1.0, 1.0, 1.0, 1.0, 1.0]);
    }
  }, [activeIndex, activeConfig]);

  const handleSelectSupportCard = (index: number) => (card: SupportCard | null) => {
    const newCards = [...selectedSupportCards];
    newCards[index] = card;
    setSelectedSupportCards(newCards);
  };

  const handleSetStatCaps = (stat: string, field: 'min' | 'max', value: number) => {
    setStatCaps((prev: any) => ({
      ...prev,
      [stat as keyof typeof prev]: {
        ...prev[stat as keyof typeof prev],
        [field]: value,
      },
    }));
  };

  const handleAddSkill = (skillName: string) => {
    setSkillList(prev => [...prev, skillName]);
  };

  const handleDeleteSkill = (skillName: string) => {
    setSkillList(prev => prev.filter(skill => skill !== skillName));
  };

  const handleAddWantedSkill = (skillName: string) => {
    setWantedSkills(prev => [...prev, skillName]);
  };

  const handleRemoveWantedSkill = (skillName: string) => {
    setWantedSkills(prev => prev.filter(skill => skill !== skillName));
  };

  const ensureStatCapsObject = (caps: any) => {
    // Ensure all stats are objects with min/max
    const defaultMax = { spd: 1200, sta: 800, pwr: 800, guts: 350, wit: 400 };
    const defaultCaps = {
      spd: { min: 0, max: 1200 },
      sta: { min: 0, max: 800 },
      pwr: { min: 0, max: 800 },
      guts: { min: 0, max: 350 },
      wit: { min: 0, max: 400 }
    };
    
    const result: any = {};
    
    // Ensure all required stats are present
    ['spd', 'sta', 'pwr', 'guts', 'wit'].forEach(stat => {
      const val = caps[stat];
      if (typeof val === 'object' && val !== null) {
        const typedVal = val as { min?: number, max?: number };
        result[stat] = { 
          min: typedVal.min ?? 0, 
          max: typedVal.max ?? defaultMax[stat as keyof typeof defaultMax] 
        };
      } else if (typeof val === 'number') {
        // If only a number, treat as min, use default max
        result[stat] = { min: val, max: defaultMax[stat as keyof typeof defaultMax] };
      } else {
        // fallback to defaults
        result[stat] = defaultCaps[stat as keyof typeof defaultCaps];
      }
    });
    
    return result;
  };

  const handleSavePreset = async () => {
    // Create simplified config for saving to server (only essential data)
    const serverConfig = {
      ...config,
      priority_stat: priorityStat,
      stat_caps: ensureStatCapsObject(statCaps),
      minimum_mood: minimumMood,
      maximum_failure: maximumFailure,
      prioritize_g1_race: prioritizeG1,
      skill: {
        is_auto_buy_skill: isAutoBuySkill,
        skill_pts_check: skillPtsCheck,
        skill_list: skillList,
      },
      position_selection_enabled: positionSelectionEnabled,
      preferred_position: preferredPosition,
      enable_positions_by_race: enablePositionsByRace,
      positions_by_race: positionsByRace,
      wanted_skills: wantedSkills,
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
      energy_management: energyManagement,
      priority_weight: priorityWeight,
      priority_weights: priorityWeights,
    };
    
    // Save to localStorage preset (with full data)
    const fullConfig = {
      ...config,
      priority_stat: priorityStat,
      stat_caps: ensureStatCapsObject(statCaps),
      minimum_mood: minimumMood,
      maximum_failure: maximumFailure,
      prioritize_g1_race: prioritizeG1,
      skill: {
        is_auto_buy_skill: isAutoBuySkill,
        skill_pts_check: skillPtsCheck,
        skill_list: skillList,
      },
      position_selection_enabled: positionSelectionEnabled,
      preferred_position: preferredPosition,
      enable_positions_by_race: enablePositionsByRace,
      positions_by_race: positionsByRace,
      wanted_skills: wantedSkills,
      character: selectedCharacter,
      scenario: selectedScenario,
      support_cards: selectedSupportCards,
      event_data_collection: eventDataCollectionSettings,
      energy_management: energyManagement,
      priority_weight: priorityWeight,
      priority_weights: priorityWeights,
    };
    savePreset(fullConfig as any);
    
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

        {/* Main Layout */}
        <div className="space-y-8">
          {/* Top Section: Character & Scenario Selection + Support Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left: Character & Scenario Selection */}
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

            {/* Right: Support Card Selection */}
            <div className="bg-white rounded-lg border p-6 shadow-sm">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">Support Cards</h3>
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
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
          </div>

          {/* Middle Section: Training Configuration */}
          <div className="bg-white rounded-lg border p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-6 text-gray-800">Training Configuration</h3>
            
            {/* Basic Training Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
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

            {/* Priority Weight System */}
            <div className="border-t pt-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PriorityWeight
                  priorityWeight={priorityWeight}
                  onPriorityWeightChange={setPriorityWeight}
                />
                <PriorityWeights
                  priorityWeights={priorityWeights}
                  onPriorityWeightsChange={setPriorityWeights}
                  priorityWeight={priorityWeight}
                />
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left */}
            <div className="bg-white rounded-lg border p-6 shadow-sm">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">Race Planner</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <PrioritizeG1
                prioritizeG1Race={prioritizeG1}
                setPrioritizeG1={setPrioritizeG1}
              />
              <p>This will be new project to select race you want to participate.</p>
              </div>
            </div>

            {/* Right */}
            <div className="bg-white rounded-lg border p-6 shadow-sm">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">Race Position</h3>
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="flex flex-col gap-2">
                {/* ENABLE POSITIONS BY RACE */}
                <IsPositionSelectionEnabled positionSelectionEnabled={positionSelectionEnabled} setPositionSelectionEnabled={(val) => setPositionSelectionEnabled(val)} />

                {/* PREFERRED POSITION */}
                <PreferredPosition
                  preferredPosition={preferredPosition}
                  setPreferredPosition={(val) => setPreferredPosition(val)}
                  enablePositionsByRace={enablePositionsByRace}
                  positionSelectionEnabled={positionSelectionEnabled}
                />
                {/* IS POSITION BY RACE ENABLED */}
                <IsPositionByRace enablePositionsByRace={enablePositionsByRace} setPositionByRace={(val) => setEnablePositionsByRace(val)} positionSelectionEnabled={positionSelectionEnabled} />

                {/* POSITION BY RACE */}
                <PositionByRace
                  positionByRace={positionsByRace}
                  setPositionByRace={(key, val) => setPositionsByRace(prev => ({ ...prev, [key]: val }))}
                  enablePositionsByRace={enablePositionsByRace}
                  positionSelectionEnabled={positionSelectionEnabled}
                />
              </div>
              </div>
            </div>
          </div>

          {/* Middle Section: Skill Configuration */}
          <div className="bg-white rounded-lg border p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-6 text-gray-800">Energy Configuration</h3>
              <div className="border-t pt-4">
                <EnergyManagement
                  energyManagement={energyManagement}
                  setEnergyManagement={setEnergyManagement}
                />
              </div>

            

            {/* */}
            <div className="border-t pt-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              </div>
            </div>
          </div>

          {/* Middle Section: Skill Configuration */}
          <div className="bg-white rounded-lg border p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-6 text-gray-800">Skills Configuration</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              {/* Skill Configuration */}
                <div className="space-y-4">
                  <h4 className="text-lg font-medium mb-3 text-gray-700">Auto Buy Skills</h4>
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
                <div className="space-y-4">
              <h4 className="text-lg font-medium mb-3 text-gray-700">Wanted Skills Hint</h4>
              <WantedSkillsSelector
                list={wantedSkills}
                addWantedSkill={handleAddWantedSkill}
                removeWantedSkill={handleRemoveWantedSkill}
              />
            </div>
              </div>
            

            {/* */}
            <div className="border-t pt-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              </div>
            </div>
          </div>

          {/* Bottom Section: Race Settings & Data Collection */}
          <div className="bg-white rounded-lg border p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Data Collection C</h3>
              
              <div className="border-t pt-4">
                <EventDataCollection
                  settings={eventDataCollectionSettings}
                  onSettingsChange={setEventDataCollectionSettings}
                />
              </div>
              
              <div className="border-t pt-4">
                
              </div>
            
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
