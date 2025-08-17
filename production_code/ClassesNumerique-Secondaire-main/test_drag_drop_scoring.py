#!/usr/bin/env python3
"""
Test script to analyze drag-and-drop scoring issue
"""

import json
from models import Exercise, db
from app import app

def test_drag_drop_scoring():
    with app.app_context():
        # Find a drag-and-drop exercise
        exercise = Exercise.query.filter_by(exercise_type='drag_and_drop').first()
        if not exercise:
            print('No drag-and-drop exercise found')
            return
            
        content = json.loads(exercise.content)
        print(f'Exercise ID: {exercise.id}')
        print(f'Title: {exercise.title}')
        print(f'Draggable items: {content.get("draggable_items", [])}')
        print(f'Drop zones: {content.get("drop_zones", [])}')
        print(f'Correct order: {content.get("correct_order", [])}')
        
        # Show what the correct answer should be
        correct_order = content.get('correct_order', [])
        draggable_items = content.get('draggable_items', [])
        
        print('\nCorrect placement:')
        for i, correct_idx in enumerate(correct_order):
            if correct_idx < len(draggable_items):
                print(f'  Zone {i}: should contain item {correct_idx} ("{draggable_items[correct_idx]}")')
        
        # Test scoring logic with perfect answers
        print('\n=== Testing Perfect Score ===')
        user_order = correct_order.copy()
        score_count = 0
        
        for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
            user_item = draggable_items[user_idx] if 0 <= user_idx < len(draggable_items) else "Vide"
            correct_item = draggable_items[correct_idx] if 0 <= correct_idx < len(draggable_items) else "Vide"
            is_correct = (user_idx == correct_idx) and (user_idx != -1)
            
            print(f'Zone {i}: user={user_idx}("{user_item}"), correct={correct_idx}("{correct_item}"), match={is_correct}')
            
            if is_correct:
                score_count += 1
        
        max_score = len(correct_order)
        perfect_score = round((score_count / max_score) * 100) if max_score > 0 else 0
        print(f'Perfect score: {perfect_score}% ({score_count}/{max_score})')
        
        # Test scoring logic with wrong answers
        print('\n=== Testing Wrong Score ===')
        wrong_order = [0, 1, 2, 3]  # Sequential order (likely wrong)
        score_count = 0
        
        for i, (user_idx, correct_idx) in enumerate(zip(wrong_order, correct_order)):
            user_item = draggable_items[user_idx] if 0 <= user_idx < len(draggable_items) else "Vide"
            correct_item = draggable_items[correct_idx] if 0 <= correct_idx < len(draggable_items) else "Vide"
            is_correct = (user_idx == correct_idx) and (user_idx != -1)
            
            print(f'Zone {i}: user={user_idx}("{user_item}"), correct={correct_idx}("{correct_item}"), match={is_correct}')
            
            if is_correct:
                score_count += 1
        
        wrong_score = round((score_count / max_score) * 100) if max_score > 0 else 0
        print(f'Wrong score: {wrong_score}% ({score_count}/{max_score})')

if __name__ == '__main__':
    test_drag_drop_scoring()
