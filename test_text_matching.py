#!/usr/bin/env python3
"""
Test script to verify text matching works correctly for OCR issues
"""

# Import the text similarity function
import sys
sys.path.append('.')
from core.state import calculate_text_similarity

def test_miracle_escape_matching():
    """Test that OCR text 'Miracle X Escapel' matches database text 'Miracle ☆ Escape!'"""
    
    # OCR text (what the bot sees)
    ocr_text = "Miracle X Escapel"
    
    # Database text (what's in the static database)
    db_text = "Miracle ☆ Escape!"
    
    # Test the similarity
    similarity = calculate_text_similarity(ocr_text, db_text)
    
    print(f"OCR Text: '{ocr_text}'")
    print(f"Database Text: '{db_text}'")
    print(f"Similarity Score: {similarity:.3f}")
    
    if similarity > 0.5:
        print("✅ MATCH! The text matching should work correctly.")
        return True
    else:
        print("❌ NO MATCH! The text matching needs improvement.")
        return False

def test_additional_cases():
    """Test additional OCR cases"""
    test_cases = [
        ("Miracle X Escape", "Miracle ☆ Escape!"),
        ("Miracle * Escape", "Miracle ☆ Escape!"), 
        ("miracle x escapel", "Miracle ☆ Escape!"),
        ("Princess Escapel", "Princess Escape!"),
        ("Wonderful X Mistake", "Wonderful ☆ Mistake!"),
    ]
    
    print("\n--- Additional Test Cases ---")
    for ocr, db in test_cases:
        similarity = calculate_text_similarity(ocr, db)
        status = "✅" if similarity > 0.5 else "❌"
        print(f"{status} '{ocr}' vs '{db}' -> {similarity:.3f}")

if __name__ == "__main__":
    print("Testing OCR text matching improvements...")
    main_result = test_miracle_escape_matching()
    test_additional_cases()
    
    if main_result:
        print("\n🎉 Main test passed! The bot should now correctly match the Miracle event.")
    else:
        print("\n⚠️  Main test failed. Need to improve text matching further.")
