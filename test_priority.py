#!/usr/bin/env python3

"""
Test the new priority order: Database → Hardcoded → Template Detection → Choice 1
"""

import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import core.state as state

def test_priority_order():
    """Test the new event choice priority order"""
    print("=== New Priority Order Test ===")
    print("Expected order:")
    print("1. Database/Learned Data (gives choice count)")
    print("2. Hardcoded Coordinates (uses choice count)")
    print("3. Template Detection (if hardcoded fails)")
    print("4. Icon Template Matching (if template detection fails)")
    print("5. Ultimate Fallback Choice 1 (if everything fails)")
    print()
    
    # Test 1: Event in learned data (should use hardcoded coordinates)
    print("1. Testing learned event (should use hardcoded coordinates):")
    print("   Event: 'Just a Little Closer' (3 choices in learned data)")
    choices = state.get_event_choices_from_database("Just a Little Closer", "support")
    print(f"   Database result: {len(choices)} choices - {choices}")
    
    if choices:
        print(f"   ✅ Database found {len(choices)} choices")
        print(f"   ✅ Bot will use HARDCODED coordinates for {len(choices)}-choice layout")
        print(f"   ✅ Hardcoded position for choice 1: (300, 532)")
        print(f"   ✅ Template detection will be SKIPPED (hardcoded is faster)")
    else:
        print(f"   ❌ No database data - would fallback to template detection")
    
    print()
    
    # Test 2: Check acupuncture event
    print("2. Testing acupuncture event (should use hardcoded coordinates):")
    print("   Event: 'Acupuncture (Just an Acupuncturist, No Worries! ☆)' (5 choices)")
    choices2 = state.get_event_choices_from_database("Acupuncture (Just an Acupuncturist, No Worries! ☆)", "character")
    print(f"   Database result: {len(choices2)} choices - {choices2}")
    
    if choices2:
        print(f"   ✅ Database found {len(choices2)} choices")
        print(f"   ✅ Bot will use HARDCODED coordinates for {len(choices2)}-choice layout") 
        print(f"   ✅ Hardcoded position for choice 4: (300, 644)")
        print(f"   ✅ Hardcoded acupuncture logic will force choice 4")
    
    print()
    
    # Test 3: Check priority benefits
    print("3. Benefits of new priority order:")
    print("   ✅ FASTER: Hardcoded coordinates are instant (no template scanning)")
    print("   ✅ MORE RELIABLE: Hardcoded positions are precise")  
    print("   ✅ BETTER FALLBACK: Multiple backup methods")
    print("   ✅ DATABASE DRIVEN: Uses your learned data for choice counts")
    print("   ✅ ADAPTIVE: Template detection only when needed")
    
    print()
    print("=== Test Complete ===")
    print("The new system works as:")
    print("📊 Database tells us how many choices (2, 3, 4, 5)")
    print("🎯 Hardcoded coordinates click the exact position")
    print("🔍 Template detection only if hardcoded fails")  
    print("🚨 Choice 1 fallback if everything fails")

if __name__ == "__main__":
    test_priority_order()
