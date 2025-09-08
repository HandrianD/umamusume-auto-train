#!/usr/bin/env python3

"""
Test script for learned events database functionality
"""

import sys
import os

# Add the project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import core.state as state

def test_learned_database():
    """Test the learned events database functionality"""
    print("=== Learned Events Database Test ===")
    
    # Test 1: Check "Just a Little Closer" event
    print("\n1. Testing 'Just a Little Closer' event...")
    choices = state.get_event_choices_from_database("Just a Little Closer", "support")
    print(f"   Result: {len(choices)} choices found")
    print(f"   Choices: {choices}")
    
    # Test with the exact text from event data
    print("\n2. Testing 'Just a Little Closer...' event (with dots)...")
    choices2 = state.get_event_choices_from_database("Just a Little Closer...", "support")
    print(f"   Result: {len(choices2)} choices found")
    print(f"   Choices: {choices2}")
    
    # Test 3: Check "Acupuncture" event  
    print("\n3. Testing 'Acupuncture' event...")
    choices3 = state.get_event_choices_from_database("Acupuncture (Just an Acupuncturist, No Worries! ☆)", "character")
    print(f"   Result: {len(choices3)} choices found")
    print(f"   Choices: {choices3}")
    
    # Test 4: Get optimal choice for events
    print("\n4. Testing optimal choice selection...")
    try:
        optimal1, from_db1 = state.get_optimal_event_choice_from_database("Just a Little Closer", "support")
        print(f"   'Just a Little Closer' -> Choice {optimal1} (from_db: {from_db1})")
        
        optimal2, from_db2 = state.get_optimal_event_choice_from_database("Acupuncture (Just an Acupuncturist, No Worries! ☆)", "character")
        print(f"   'Acupuncture' -> Choice {optimal2} (from_db: {from_db2})")
        
    except Exception as e:
        print(f"   Error testing optimal choices: {e}")
    
    print("\n=== Test Complete ===")
    print("Summary:")
    print("- Now using LEARNED EVENTS ONLY (event_data.json)")
    print("- Removed static database fallback")
    print("- Should find correct number of choices from your gameplay data")

if __name__ == "__main__":
    test_learned_database()
