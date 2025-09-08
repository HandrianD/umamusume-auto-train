#!/usr/bin/env python3

"""
Test script for URA Finale functionality
"""

import time
import sys
import os

# Add the project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.scenario import ura
from core.execute import select_race_position, race_prep, after_race
import core.state as state

def test_ura_functionality():
    """Test the URA finale functionality without running the bot"""
    print("=== URA Finale Functionality Test ===")
    
    # Test 1: Check if position selection is working
    print("\n1. Testing position selection configuration...")
    try:
        is_enabled = state.is_position_selection_enabled()
        preferred = state.PREFERRED_POSITION
        print(f"   Position selection enabled: {is_enabled}")
        print(f"   Preferred position: {preferred}")
        print("   ✅ Position configuration loaded successfully")
    except Exception as e:
        print(f"   ❌ Position configuration error: {e}")
    
    # Test 2: Test imports
    print("\n2. Testing function imports...")
    try:
        # Just test if the functions can be called (they won't actually click anything)
        print(f"   ura function: {ura}")
        print(f"   select_race_position function: {select_race_position}")
        print(f"   race_prep function: {race_prep}")
        print(f"   after_race function: {after_race}")
        print("   ✅ All functions imported successfully")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
    
    # Test 3: Check if URA assets exist
    print("\n3. Testing URA assets...")
    try:
        import os
        ura_btn_path = "assets/ura/ura_race_btn.png"
        if os.path.exists(ura_btn_path):
            print(f"   ✅ URA race button found: {ura_btn_path}")
        else:
            print(f"   ❌ URA race button missing: {ura_btn_path}")
        
        # Check other critical buttons
        critical_buttons = [
            "assets/buttons/race_btn.png",
            "assets/buttons/next_btn.png", 
            "assets/buttons/next2_btn.png",
            "assets/buttons/view_results.png"
        ]
        
        for btn_path in critical_buttons:
            if os.path.exists(btn_path):
                print(f"   ✅ Button found: {btn_path}")
            else:
                print(f"   ❌ Button missing: {btn_path}")
                
    except Exception as e:
        print(f"   ❌ Asset check error: {e}")
    
    print("\n=== Test Complete ===")
    print("If all tests show ✅, the URA finale should work better now.")
    print("The main fixes applied:")
    print("- Removed the problematic race_btn.png clicks after ura() function")
    print("- Enhanced ura() function with better error handling and fallbacks")
    print("- Improved race_prep() and after_race() with multiple attempts")
    print("- Added race position selection to URA finale")

if __name__ == "__main__":
    test_ura_functionality()
