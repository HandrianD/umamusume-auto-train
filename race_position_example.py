"""
Race Position Automation Example
This file shows how to use the race position configuration in your bot logic.
"""

from core.state import (
    reload_config, 
    get_race_position_for_type, 
    is_position_selection_enabled,
    POSITION_SELECTION_ENABLED,
    PREFERRED_POSITION,
    ENABLE_POSITIONS_BY_RACE,
    POSITIONS_BY_RACE
)

def should_enter_race(race_info):
    """
    Example function to decide whether to enter a race based on position preferences.
    
    Args:
        race_info: Dictionary containing race information like:
                  {"name": "Hopeful Stakes", "type": "sprint", "grade": "G3", ...}
    
    Returns:
        bool: True if the bot should enter this race, False otherwise
    """
    if not is_position_selection_enabled():
        # If position selection is disabled, enter all races (or use other criteria)
        return True
    
    race_type = race_info.get("type", "unknown").lower()
    preferred_position = get_race_position_for_type(race_type)
    
    if preferred_position is None:
        # Position selection enabled but no preference set
        return True
    
    # Here you would add logic to check if the current uma musume
    # is suitable for the preferred position
    # This is just an example - you'll need to implement the actual logic
    
    print(f"[RACE] {race_info.get('name', 'Unknown Race')} ({race_type}) - Preferred position: {preferred_position}")
    
    # Example: Always enter races for now, but log the preferred position
    return True

def get_training_strategy_for_position(position):
    """
    Example function to adjust training based on preferred race position.
    
    Args:
        position: String like "front", "pace", "late", "end"
    
    Returns:
        dict: Training strategy adjustments
    """
    strategies = {
        "front": {
            "priority_stats": ["spd", "pwr", "guts"],
            "description": "Focus on speed and power for front-running"
        },
        "pace": {
            "priority_stats": ["spd", "sta", "wit"],
            "description": "Balanced speed and stamina for pace-setting"
        },
        "late": {
            "priority_stats": ["spd", "sta", "wit"],
            "description": "Stamina and wisdom for late positioning"
        },
        "end": {
            "priority_stats": ["sta", "pwr", "guts"],
            "description": "Stamina and power for strong finishes"
        }
    }
    
    return strategies.get(position, strategies["front"])

def main_race_logic():
    """
    Example main function showing how to integrate race position logic
    """
    # Make sure config is loaded
    reload_config()
    
    print("=== Race Position Configuration ===")
    print(f"Position Selection Enabled: {POSITION_SELECTION_ENABLED}")
    print(f"Preferred Position: {PREFERRED_POSITION}")
    print(f"Position by Race Enabled: {ENABLE_POSITIONS_BY_RACE}")
    print(f"Positions by Race: {POSITIONS_BY_RACE}")
    
    # Example race scenarios
    example_races = [
        {"name": "Hopeful Stakes", "type": "sprint", "grade": "G3"},
        {"name": "Tokyo Yushun", "type": "mile", "grade": "G1"},
        {"name": "Tenno Sho", "type": "medium", "grade": "G1"},
        {"name": "Kikuka Sho", "type": "long", "grade": "G1"}
    ]
    
    print("\n=== Race Decisions ===")
    for race in example_races:
        should_enter = should_enter_race(race)
        preferred_pos = get_race_position_for_type(race["type"])
        strategy = get_training_strategy_for_position(preferred_pos) if preferred_pos else None
        
        print(f"\nRace: {race['name']} ({race['type']})")
        print(f"  Enter Race: {should_enter}")
        print(f"  Preferred Position: {preferred_pos}")
        if strategy:
            print(f"  Training Strategy: {strategy['description']}")
            print(f"  Priority Stats: {', '.join(strategy['priority_stats'])}")

if __name__ == "__main__":
    main_race_logic()
