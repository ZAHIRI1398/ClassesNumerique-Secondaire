#!/usr/bin/env python3
"""
Simple test to understand drag-and-drop scoring logic
"""

def test_drag_drop_logic():
    # Example from init_exercises.py
    draggable_items = ["0,8", "0,08", "0,85", "0,9"]
    correct_order = [1, 0, 2, 3]  # This means: 0,08, 0,8, 0,85, 0,9 (ascending order)
    
    print("=== DRAG AND DROP SCORING TEST ===")
    print(f"Draggable items: {draggable_items}")
    print(f"Correct order: {correct_order}")
    
    print("\nCorrect placement should be:")
    for i, correct_idx in enumerate(correct_order):
        print(f"  Zone {i}: item {correct_idx} ('{draggable_items[correct_idx]}')")
    
    print("\nThis gives us the ascending order: 0,08 -> 0,8 -> 0,85 -> 0,9")
    
    # Test 1: Perfect answer
    print("\n=== TEST 1: Perfect Answer ===")
    user_order = [1, 0, 2, 3]  # Same as correct_order
    score_count = 0
    
    for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
        is_correct = (user_idx == correct_idx) and (user_idx != -1)
        user_item = draggable_items[user_idx] if 0 <= user_idx < len(draggable_items) else "Vide"
        correct_item = draggable_items[correct_idx] if 0 <= correct_idx < len(draggable_items) else "Vide"
        
        print(f"Zone {i}: user={user_idx}('{user_item}'), correct={correct_idx}('{correct_item}'), match={is_correct}")
        
        if is_correct:
            score_count += 1
    
    max_score = len(correct_order)
    perfect_score = round((score_count / max_score) * 100) if max_score > 0 else 0
    print(f"Perfect score: {perfect_score}% ({score_count}/{max_score})")
    
    # Test 2: Sequential order (wrong)
    print("\n=== TEST 2: Sequential Order (Wrong) ===")
    user_order = [0, 1, 2, 3]  # Sequential order
    score_count = 0
    
    for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
        is_correct = (user_idx == correct_idx) and (user_idx != -1)
        user_item = draggable_items[user_idx] if 0 <= user_idx < len(draggable_items) else "Vide"
        correct_item = draggable_items[correct_idx] if 0 <= correct_idx < len(draggable_items) else "Vide"
        
        print(f"Zone {i}: user={user_idx}('{user_item}'), correct={correct_idx}('{correct_item}'), match={is_correct}")
        
        if is_correct:
            score_count += 1
    
    sequential_score = round((score_count / max_score) * 100) if max_score > 0 else 0
    print(f"Sequential score: {sequential_score}% ({score_count}/{max_score})")
    
    # Test 3: Half correct
    print("\n=== TEST 3: Half Correct ===")
    user_order = [1, 1, 2, 3]  # First two zones wrong, last two correct
    score_count = 0
    
    for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
        is_correct = (user_idx == correct_idx) and (user_idx != -1)
        user_item = draggable_items[user_idx] if 0 <= user_idx < len(draggable_items) else "Vide"
        correct_item = draggable_items[correct_idx] if 0 <= correct_idx < len(draggable_items) else "Vide"
        
        print(f"Zone {i}: user={user_idx}('{user_item}'), correct={correct_idx}('{correct_item}'), match={is_correct}")
        
        if is_correct:
            score_count += 1
    
    half_score = round((score_count / max_score) * 100) if max_score > 0 else 0
    print(f"Half correct score: {half_score}% ({score_count}/{max_score})")

if __name__ == '__main__':
    test_drag_drop_logic()
