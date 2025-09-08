#!/usr/bin/env python3

"""
Test script for acupuncture event hardcoded choice 4
"""

import sys
import os

# Add the project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import core.state as state

def test_acupuncture_hardcoded():
    """Test that acupuncture events are hardcoded to choice 4"""
    print("=== Acupuncture Event Hardcoded Test ===")
    
    # Test the exact event text from your event_data.json
    event_text = "Acupuncture (Just an Acupuncturist, No Worries! ☆)"
    
    # Test 1: Check if it's detected as acupuncture event
    print(f"\n1. Testing acupuncture detection for: '{event_text}'")
    is_acupuncture = state._is_acupuncture_event(event_text)
    print(f"   Acupuncture detected: {is_acupuncture}")
    
    if is_acupuncture:
        print("   ✅ Acupuncture event correctly detected")
    else:
        print("   ❌ Acupuncture event NOT detected - check patterns")
    
    # Test 2: Check if optimal choice returns 4
    print(f"\n2. Testing optimal choice selection...")
    try:
        choice, from_database = state.get_optimal_event_choice_from_database(event_text, "support")
        print(f"   Recommended choice: {choice}")
        print(f"   From database: {from_database}")
        
        if choice == 4:
            print("   ✅ Correctly hardcoded to choice 4")
        else:
            print(f"   ❌ Expected choice 4, got choice {choice}")
    except Exception as e:
        print(f"   ❌ Error getting optimal choice: {e}")
    
    # Test 3: Test other variations
    print(f"\n3. Testing other acupuncture variations...")
    test_variations = [
        "acupuncture treatment",
        "Just an Acupuncturist", 
        "Acupuncture (no worries)",
        "ACUPUNCTURE EVENT"  # Test case insensitive
    ]
    
    for variation in test_variations:
        is_detected = state._is_acupuncture_event(variation)
        print(f"   '{variation}' -> {is_detected}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_acupuncture_hardcoded()
