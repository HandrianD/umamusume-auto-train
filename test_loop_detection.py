#!/usr/bin/env python3
"""
Test the loop detection and fallback system for event choice selection
"""

import sys
sys.path.append('.')

# Test the loop detection by simulating repeated calls
def test_loop_detection():
    from core.execute import select_event_choice
    import time
    
    print("Testing loop detection system...")
    print("This will simulate the bot getting stuck on the same event")
    
    # Simulate the same event being detected multiple times
    event_text = "Miracle ☆ Escape!"
    event_type = "support"
    choice_index = 1
    
    print(f"\n--- Simulating repeated attempts on: {event_text} ---")
    
    # First attempt (should try hardcoded coordinates)
    print(f"\n🔄 Attempt 1: First try")
    result1 = select_event_choice(choice_index, event_text, event_type)
    print(f"Result 1: {result1}")
    
    # Second attempt (should still try hardcoded but mark as failed)
    print(f"\n🔄 Attempt 2: Second try (should detect first failure)")
    result2 = select_event_choice(choice_index, event_text, event_type)
    print(f"Result 2: {result2}")
    
    # Third attempt (should force template detection due to loop detection)
    print(f"\n🔄 Attempt 3: Third try (should trigger loop detection)")
    result3 = select_event_choice(choice_index, event_text, event_type)
    print(f"Result 3: {result3}")

if __name__ == "__main__":
    print("🔄 Testing Loop Detection System for Event Choice Selection")
    test_loop_detection()
    print("\n✅ Loop detection test complete!")
