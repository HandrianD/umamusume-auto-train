"""
Test script to demonstrate the dual-mode race position selection
"""

import sys
sys.path.append('.')

from core.state import reload_config, POSITION_SELECTION_ENABLED, PREFERRED_POSITION
import json

def test_position_modes():
    """Test both manual and auto position selection modes"""
    
    print("=== Testing Race Position Selection Modes ===\n")
    
    # Load current config
    reload_config()
    
    print("Current Configuration:")
    print(f"  Position Selection Enabled: {POSITION_SELECTION_ENABLED}")
    print(f"  Preferred Position: {PREFERRED_POSITION}")
    
    print("\n=== Mode 1: Manual (Config-based) ===")
    if POSITION_SELECTION_ENABLED:
        print("✅ Manual mode is ACTIVE")
        print(f"   Bot will use configured position: {PREFERRED_POSITION}")
        
        # Show position mapping
        position_mapping = {
            "front": "Inside (button 1)",
            "pace": "Middle (button 2)",  
            "late": "Middle (button 2)",
            "end": "Outside (button 3)"
        }
        button_desc = position_mapping.get(PREFERRED_POSITION, "Middle (button 2)")
        print(f"   This maps to: {button_desc}")
    else:
        print("❌ Manual mode is DISABLED")
        print("   Bot will use automatic stat-based selection")
    
    print("\n=== Mode 2: Auto (Stat-based) ===")
    print("When manual mode is disabled, bot will use:")
    print("  • Speed > 800: Inside position (button 1)")
    print("  • Stamina > 800: Outside position (button 3)")  
    print("  • Otherwise: Middle position (button 2)")
    
    print("\n=== How to Switch Modes ===")
    print("1. Enable Manual Mode:")
    print("   - Set 'position_selection_enabled': true in config")
    print("   - Configure your preferred positions in the web UI")
    print("   - Bot will always use your configured positions")
    print()
    print("2. Enable Auto Mode:")
    print("   - Set 'position_selection_enabled': false in config")
    print("   - Bot will analyze stats and choose position automatically")
    
    print("\n=== Testing Config Toggle ===")
    
    # Test toggling the setting
    print("\nTesting what happens if we disable position selection...")
    
    # Load and modify config temporarily
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    original_setting = config.get("position_selection_enabled", False)
    
    # Show what would happen in auto mode
    config["position_selection_enabled"] = False
    print(f"If position_selection_enabled = False:")
    print("  → Bot would use automatic stat-based position selection")
    print("  → Speed/Stamina stats determine position")
    
    # Show what happens in manual mode
    config["position_selection_enabled"] = True  
    print(f"\nIf position_selection_enabled = True:")
    print(f"  → Bot would use configured position: {config.get('preferred_position', 'front')}")
    print("  → Same position used for all races (unless position_by_race is enabled)")

if __name__ == "__main__":
    test_position_modes()
