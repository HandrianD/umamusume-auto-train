import { useState, useEffect } from "react";
import { Checkbox } from "./ui/checkbox";

interface EventDataCollectionSettings {
  enabled: boolean;
  event_types: {
    character_events: boolean;
    support_card_events: boolean;
    random_events: boolean;
    special_events: boolean;
  };
  data_to_collect: {
    stat_changes: boolean;
    mood_changes: boolean;
    skill_gains: boolean;
    training_efficiency: boolean;
  };
  context_tracking: {
    current_stats: boolean;
    support_cards: boolean;
    training_year: boolean;
  };
  learning_features: {
    personal_learning: boolean;
    smart_defaults: boolean;
    minimum_importance_threshold: number;
  };
}

interface EventDataCollectionProps {
  settings: EventDataCollectionSettings;
  onSettingsChange: (settings: EventDataCollectionSettings) => void;
}

export default function EventDataCollection({ settings, onSettingsChange }: EventDataCollectionProps) {
  const [localSettings, setLocalSettings] = useState<EventDataCollectionSettings>(settings);

  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const updateSettings = (updates: Partial<EventDataCollectionSettings>) => {
    const newSettings = { ...localSettings, ...updates };
    setLocalSettings(newSettings);
    onSettingsChange(newSettings);
  };

  const updateNestedSetting = (
    category: keyof EventDataCollectionSettings,
    key: string,
    value: boolean | number
  ) => {
    const categorySettings = localSettings[category] as any;
    const newSettings = {
      ...localSettings,
      [category]: {
        ...categorySettings,
        [key]: value
      }
    };
    setLocalSettings(newSettings);
    onSettingsChange(newSettings);
  };

  return (
    <div className="space-y-6 p-4 border rounded-lg bg-card">
      <div className="flex items-center space-x-2">
        <Checkbox
          id="data-collection-enabled"
          checked={localSettings.enabled}
          onCheckedChange={(checked) => updateSettings({ enabled: checked as boolean })}
        />
        <label htmlFor="data-collection-enabled" className="text-sm font-medium">
          Enable Event Data Collection
        </label>
      </div>

      {localSettings.enabled && (
        <>
          {/* Event Types Section */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground">Event Types to Track</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="character-events"
                  checked={localSettings.event_types.character_events}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('event_types', 'character_events', checked as boolean)
                  }
                />
                <label htmlFor="character-events" className="text-sm">Character Events</label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="support-card-events"
                  checked={localSettings.event_types.support_card_events}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('event_types', 'support_card_events', checked as boolean)
                  }
                />
                <label htmlFor="support-card-events" className="text-sm">Support Card Events</label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="random-events"
                  checked={localSettings.event_types.random_events}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('event_types', 'random_events', checked as boolean)
                  }
                />
                <label htmlFor="random-events" className="text-sm">Random Events</label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="special-events"
                  checked={localSettings.event_types.special_events}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('event_types', 'special_events', checked as boolean)
                  }
                />
                <label htmlFor="special-events" className="text-sm">Special Events</label>
              </div>
            </div>
          </div>

          {/* Data to Collect Section */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground">Data to Collect</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="stat-changes"
                  checked={localSettings.data_to_collect.stat_changes}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('data_to_collect', 'stat_changes', checked as boolean)
                  }
                />
                <label htmlFor="stat-changes" className="text-sm">Stat Changes</label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="mood-changes"
                  checked={localSettings.data_to_collect.mood_changes}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('data_to_collect', 'mood_changes', checked as boolean)
                  }
                />
                <label htmlFor="mood-changes" className="text-sm">Mood Changes</label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="skill-gains"
                  checked={localSettings.data_to_collect.skill_gains}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('data_to_collect', 'skill_gains', checked as boolean)
                  }
                />
                <label htmlFor="skill-gains" className="text-sm">Skill Gains</label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="training-efficiency"
                  checked={localSettings.data_to_collect.training_efficiency}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('data_to_collect', 'training_efficiency', checked as boolean)
                  }
                />
                <label htmlFor="training-efficiency" className="text-sm">Training Efficiency</label>
              </div>
            </div>
          </div>

          {/* Context Tracking Section */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground">Context Information</h3>
            <div className="grid grid-cols-1 gap-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="current-stats"
                  checked={localSettings.context_tracking.current_stats}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('context_tracking', 'current_stats', checked as boolean)
                  }
                />
                <label htmlFor="current-stats" className="text-sm">Current Stats</label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="support-cards"
                  checked={localSettings.context_tracking.support_cards}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('context_tracking', 'support_cards', checked as boolean)
                  }
                />
                <label htmlFor="support-cards" className="text-sm">Active Support Cards</label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="training-year"
                  checked={localSettings.context_tracking.training_year}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('context_tracking', 'training_year', checked as boolean)
                  }
                />
                <label htmlFor="training-year" className="text-sm">Training Year/Season</label>
              </div>
            </div>
          </div>

          {/* Learning Features Section */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground">Learning Features</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="personal-learning"
                  checked={localSettings.learning_features.personal_learning}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('learning_features', 'personal_learning', checked as boolean)
                  }
                />
                <label htmlFor="personal-learning" className="text-sm">Personal Learning</label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="smart-defaults"
                  checked={localSettings.learning_features.smart_defaults}
                  onCheckedChange={(checked) =>
                    updateNestedSetting('learning_features', 'smart_defaults', checked as boolean)
                  }
                />
                <label htmlFor="smart-defaults" className="text-sm">Smart Defaults</label>
              </div>

              <div className="flex items-center justify-between">
                <label htmlFor="importance-threshold" className="text-sm">Importance Threshold</label>
                <select
                  id="importance-threshold"
                  value={localSettings.learning_features.minimum_importance_threshold}
                  onChange={(e) =>
                    updateNestedSetting('learning_features', 'minimum_importance_threshold', parseInt(e.target.value))
                  }
                  className="px-2 py-1 text-sm border rounded"
                >
                  <option value={1}>Low (1)</option>
                  <option value={2}>Medium (2)</option>
                  <option value={3}>High (3)</option>
                  <option value={4}>Very High (4)</option>
                  <option value={5}>Maximum (5)</option>
                </select>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
