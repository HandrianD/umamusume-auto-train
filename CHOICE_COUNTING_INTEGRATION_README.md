# Choice Counting Integration Test

This document explains how to test the integrated choice counting system in your core project.

## What Was Added

The area-based choice detection logic from `test_ocr_choice_detection.py` has been integrated into `core/execute.py` with the following functions:

- `detect_and_count_choices(debug=True)` - Core detection function
- `test_choice_counting_integration(debug=True)` - Test wrapper with debug output
- `run_choice_counting_test()` - Convenience function for easy calling

## How to Test

### Method 1: Command Line Test
```bash
python main.py test-choice
```

### Method 2: Standalone Test Script
```bash
python test_choice_counting_integration.py
```

### Method 3: Direct Function Call
```python
from core.execute import run_choice_counting_test
run_choice_counting_test()
```

## What It Does

1. **Template Detection**: Checks 5 predefined areas for choice templates (`event_choice_*.png`)
2. **Choice Counting**: Counts how many choices are present (1-5)
3. **Position Mapping**: Returns which positions contain choices
4. **Debug Output**: Shows detailed detection process and results

## Expected Output

When choices are detected, you'll see output like:
```
🧪 AREA-BASED CHOICE DETECTION TEST (CORE INTEGRATION)
============================================================
[DETECT] Starting area-based choice detection...
[DETECT] Checking area 1: (260, 264, 52, 86)
[DETECT] ❌ No templates found in area 1
[DETECT] Checking area 4: (260, 600, 52, 86)
[DETECT] ✅ Found assets/icons/event_choice_4.png in area 4 at Box(left=260, top=600, width=52, height=86)
[DETECT] Checking area 5: (260, 714, 52, 86)
[DETECT] ✅ Found assets/icons/event_choice_5.png in area 5 at Box(left=260, top=714, width=52, height=86)
[DETECT] ✅ Area detection successful: 2 choices found in areas [4, 5]

🎯 CHOICE COUNTING INTEGRATION TEST
============================================================
[TEST] Detected 2 choices at positions: [4, 5]
[TEST] Processing 2 choice positions...

[TEST] Position 4: Region (260, 600) to (312, 686)
✅ Position 4: CHOICE DETECTED

[TEST] Position 5: Region (260, 714) to (312, 797)
✅ Position 5: CHOICE DETECTED

📊 ANALYSIS RESULTS
============================================================
🎯 Total choices detected: 2
🎯 Choice positions: [4, 5]
📍 Detected choices at positions:
   Position 4: ✅ Present
   Position 5: ✅ Present
🎯 Pattern: Choices detected at positions [4, 5]

💡 RECOMMENDATION:
   Found 2 choice(s) at positions [4, 5]
   Ready for database-driven decision making
```

## Integration Benefits

✅ **No OCR Complexity**: Uses reliable template matching instead of OCR
✅ **Database Ready**: Returns choice count and positions for your bot's decision system
✅ **Debug Friendly**: Comprehensive logging shows exactly what's detected
✅ **Core Integration**: Works seamlessly with your existing bot architecture

## Next Steps

Once tested and working, you can integrate this into your main bot logic by calling:
```python
num_choices, choice_positions = detect_and_count_choices(debug=False)
```

This will give you the choice count and positions for your database-driven decision making!</content>
<parameter name="filePath">c:\Users\HandrianD\umamusume-auto-train\CHOICE_COUNTING_INTEGRATION_README.md
