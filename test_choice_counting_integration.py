#!/usr/bin/env python3
"""
TEST SCRIPT: Test the integrated choice counting system in core/execute.py
This script demonstrates the choice detection working within the core system
"""

import sys
import os
import time

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the integrated choice detection function
from core.execute import test_choice_counting_integration

def main():
    print("🚀 Testing Choice Counting Integration")
    print("This script tests the area-based choice detection integrated into core/execute.py")
    print("\n⏳ Positioning phase...")
    for i in range(5, 0, -1):
        print(f"   Make sure Uma Musume is visible on screen... {i}")
        time.sleep(1)

    print("\n🧪 Running choice detection test...")
    results = test_choice_counting_integration(debug=True)

    print("\n" + "="*60)
    print("🏁 TEST COMPLETE")
    print("="*60)

    if results:
        print(f"✅ Successfully detected {len(results)} choices")
        print(f"📍 Choice positions: {sorted(results.keys())}")
    else:
        print("❌ No choices detected")
        print("💡 Make sure you're on an event screen with choices visible")

if __name__ == "__main__":
    main()
