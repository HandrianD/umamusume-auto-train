#!/usr/bin/env python3

"""
Test the learned data first → static database fallback
"""

import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import core.state as state

def test_fallback_behavior():
    """Test learned events first, then static database fallback"""
    print("=== Learned → Static Database Fallback Test ===")
    
    # Test 1: Event that EXISTS in learned data (should use learned)
    print("\n1. Testing event that EXISTS in learned data:")
    print("   Event: 'Just a Little Closer' (should find in learned data)")
    choices1 = state.get_event_choices_from_database("Just a Little Closer", "support")
    print(f"   Result: {len(choices1)} choices - {choices1}")
    
    # Test 2: Event that does NOT exist in learned data (should fallback to static)
    print("\n2. Testing event that does NOT exist in learned data:")
    print("   Event: 'Test Unknown Event' (should fallback to static database)")
    choices2 = state.get_event_choices_from_database("Test Unknown Event", "support")
    print(f"   Result: {len(choices2)} choices - {choices2}")
    
    # Test 3: Event from static database (like from Special Week support card)
    print("\n3. Testing static database event:")
    print("   Event: 'Someday, I'll Be Just Like Her!' (should find in static)")
    choices3 = state.get_event_choices_from_database("Someday, I'll Be Just Like Her!", "support")
    print(f"   Result: {len(choices3)} choices - {choices3}")
    
    print("\n=== Test Complete ===")
    print("Expected behavior:")
    print("✅ Test 1: Should find in LEARNED data (3 choices)")
    print("✅ Test 2: Should NOT find anywhere (0 choices)")  
    print("✅ Test 3: Should find in STATIC database (varies)")
    print("\nThe fallback system is working if:")
    print("- Learned events are found first when they exist")
    print("- Static database is checked when learned data doesn't have the event")
    print("- Your learned preferences take priority over static database")

if __name__ == "__main__":
    test_fallback_behavior()
