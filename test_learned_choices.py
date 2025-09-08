#!/usr/bin/env python3

"""
Test script for the learned events choice detection fix
"""

import sys
import os
import json

# Add the project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import core.state as state

def test_learned_choice_detection():
    """Test the learned choice detection fix"""
    print("=== Testing Learned Choice Detection Fix ===")
    
    # First, let's see what's actually in the event data
    print("\n1. Checking event_data.json content:")
    try:
        with open("event_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        events = data.get("events", [])
        
        for event in events:
            event_text = event.get("event_text", "")
            if "Just a Little Closer" in event_text:
                print(f"   Found event: '{event_text}'")
                print(f"   Detected choices: {event.get('detected_choices')}")
                print(f"   Type: {type(event.get('detected_choices'))}")
                print(f"   Choice made: {event.get('choice_made')}")
    except Exception as e:
        print(f"   ❌ Error loading event data: {e}")
    
    # Test the specific event that was causing issues
    event_texts_to_test = [
        "Just a Little Closer...",
        "Just a Little Closer",
        "(❯❯) Just a Little Closer"
    ]
    
    for event_text in event_texts_to_test:
        print(f"\n2. Testing event: '{event_text}'")
        
        # Test get_choices_from_learned_events
        try:
            choices = state.get_choices_from_learned_events(event_text)
            print(f"   Learned choices found: {len(choices)}")
            print(f"   Choices: {choices}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    test_learned_choice_detection()
