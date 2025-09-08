#!/usr/bin/env python3

"""
Quick test for Just a Little Closer event choice detection
"""

import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import core.state as state

def test_little_closer_event():
    """Test that Just a Little Closer event returns correct choice count"""
    print("=== Just a Little Closer Event Test ===")
    
    # Test the event from the logs
    event_text = "Just a Little Closer"
    
    print(f"Testing event: '{event_text}'")
    
    # Test 1: Check learned events
    choices = state.get_choices_from_learned_events(event_text)
    if choices:
        print(f"   Found in learned events: {len(choices)} choices")
        print(f"   Choices: {choices}")
    else:
        print("   Not found in learned events")
    
    # Test 2: Check database choices
    db_choices = state.get_event_choices_from_database(event_text, "support")
    if db_choices:
        print(f"   Found in database: {len(db_choices)} choices")
        print(f"   Choices: {db_choices}")
    else:
        print("   Not found in database")
    
    # Test 3: Check optimal choice
    choice, from_db = state.get_optimal_event_choice_from_database(event_text, "support")
    print(f"   Optimal choice: {choice}, from database: {from_db}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_little_closer_event()
