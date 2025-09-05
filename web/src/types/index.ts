export type Stat = {
  spd: number;
  sta: number;
  pwr: number;
  guts: number;
  wit: number;
};

export type Skill = {
  is_auto_buy_skill: boolean;
  skill_pts_check: number;
  skill_list: string[];
};

export type SupportCardEvent = {
  name: string;
  options: any[]; // Will be populated with event options
};

export type SupportCardCategory = {
  category: string;
  events: SupportCardEvent[];
};

export type SupportCard = {
  id: string;
  name: string;
  imageUrl: string;
  jsonUrl: string;
  data?: SupportCardCategory[];
};

export type CharacterEvent = {
  name: string;
  options?: any[];
};

export type CharacterCategory = {
  category: string;
  events: CharacterEvent[] | string[]; // Can be array of strings or objects
};

export type Character = {
  id: string;
  name: string;
  imageUrl: string;
  jsonUrl: string;
  data?: CharacterCategory[];
};

export type Scenario = {
  id: string;
  name: string;
  imageUrl: string;
  jsonUrl: string;
};

// Simplified types for config.json storage
export type ConfigSupportCard = {
  id: string;
  name: string;
};

export type ConfigCharacter = {
  id: string;
  name: string;
};

export type ConfigScenario = {
  id: string;
  name: string;
};

export type Config = {
  priority_stat: string[];
  minimum_mood: string;
  maximum_failure: number;
  prioritize_g1_race: boolean;
  cancel_consecutive_race: boolean;
  stat_caps: Stat;
  skill: Skill;
  support_cards: (ConfigSupportCard | null)[]; // Simplified for config storage
  character: ConfigCharacter | null; // Simplified for config storage
  scenario: ConfigScenario | null; // Simplified for config storage
  event_data_collection?: any; // Optional for backward compatibility
};
