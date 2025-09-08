"""
Temporary position selection workaround
This disables position selection until you get the missing button assets
"""

import json

def disable_position_selection():
    """Temporarily disable position selection until assets are obtained"""
    
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Temporarily disable position selection
    config['position_selection_enabled'] = False
    print("[TEMP] Disabled position selection until assets are obtained")
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("[TEMP] Position selection disabled. Enable after getting button assets:")
    print("- info_btn.png")
    print("- change_btn.png")
    print("- skip_btn_big.png") 
    print("- race_exclamation_btn.png")
    print("- positions/front_position_btn.png")
    print("- positions/pace_position_btn.png")
    print("- positions/late_position_btn.png")
    print("- positions/end_position_btn.png")

def enable_position_selection():
    """Re-enable position selection after getting assets"""
    
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['position_selection_enabled'] = True
    print("[TEMP] Enabled position selection")
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "enable":
        enable_position_selection()
    else:
        disable_position_selection()
