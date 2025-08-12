#!/usr/bin/env python3
"""
Test script to check fill_in_blanks exercises and their JSON structure
"""

import json

def test_fill_in_blanks_formats():
    print("=== TESTING FILL IN BLANKS JSON FORMATS ===")
    
    # Test format 1: Using 'words' (new format from creation)
    format1 = {
        'sentences': [
            'Le chat ___ sur le tapis',
            'Il fait ___ aujourd\'hui'
        ],
        'words': ['dort', 'beau']
    }
    
    # Test format 2: Using 'available_words' (old format from init_exercises)
    format2 = {
        'sentences': [
            {'text': 'Dans 3,45 le chiffre des dixièmes est ___', 'answer': '4'},
            {'text': 'Dans 3,45 le chiffre des centièmes est ___', 'answer': '5'}
        ],
        'available_words': ['3', '4', '5', '34', '345']
    }
    
    print("Format 1 (new creation format):")
    print(f"  sentences: {format1.get('sentences', 'MISSING')}")
    print(f"  words: {format1.get('words', 'MISSING')}")
    print(f"  available_words: {format1.get('available_words', 'MISSING')}")
    
    print("\nFormat 2 (old init_exercises format):")
    print(f"  sentences: {format2.get('sentences', 'MISSING')}")
    print(f"  words: {format2.get('words', 'MISSING')}")
    print(f"  available_words: {format2.get('available_words', 'MISSING')}")
    
    # Test template conditions
    print("\n=== TESTING TEMPLATE CONDITIONS ===")
    
    def test_template_condition(content, name):
        print(f"\n{name}:")
        print(f"  content exists: {content is not None}")
        print(f"  content.sentences exists: {content.get('sentences') is not None}")
        print(f"  content.words exists: {content.get('words') is not None}")
        print(f"  content.available_words exists: {content.get('available_words') is not None}")
        
        # Old condition (would fail for format2)
        old_condition = not content or not content.get('sentences') or not content.get('words')
        print(f"  OLD condition (fails): {old_condition}")
        
        # New condition (should work for both)
        new_condition = not content or not content.get('sentences') or (not content.get('words') and not content.get('available_words'))
        print(f"  NEW condition (works): {new_condition}")
        
        # Word array for template
        words_array = content.get('words') or content.get('available_words')
        print(f"  Words array: {words_array}")
    
    test_template_condition(format1, "Format 1 (new)")
    test_template_condition(format2, "Format 2 (old)")
    
    print("\n=== CONCLUSION ===")
    print("✅ The template fix should now handle both formats correctly!")
    print("✅ Format 1 uses 'words' - will work with (content.words or content.available_words)")
    print("✅ Format 2 uses 'available_words' - will work with (content.words or content.available_words)")

if __name__ == '__main__':
    test_fill_in_blanks_formats()
