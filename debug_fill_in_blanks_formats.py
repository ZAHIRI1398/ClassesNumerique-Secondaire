#!/usr/bin/env python3
"""
Script de diagnostic pour analyser les formats d'exercices fill_in_blanks
"""

import sys
import json
sys.path.append('.')

from app import app, db, Exercise

def analyze_fill_in_blanks_formats():
    """Analyser les formats d'exercices fill_in_blanks"""
    
    with app.app_context():
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        print(f"Nombre d'exercices fill_in_blanks: {len(exercises)}")
        print()
        
        for ex in exercises:
            print(f"Exercice {ex.id}: {ex.title}")
            content = json.loads(ex.content)
            print(f"  Format: {list(content.keys())}")
            
            if 'text' in content:
                text = content['text']
                print(f"  Text: {text}")
                # Compter les blancs dans text
                blank_count = text.count('___')
                print(f"  Blancs dans text: {blank_count}")
            
            if 'sentences' in content:
                sentences = content['sentences']
                print(f"  Sentences: {sentences}")
                # Compter les blancs dans sentences
                total_blanks = sum(sentence.count('___') for sentence in sentences)
                print(f"  Blancs dans sentences: {total_blanks}")
            
            words = content.get('words', [])
            print(f"  Words: {words} (count: {len(words)})")
            
            # Vérifier la cohérence
            if 'text' in content:
                text_blanks = content['text'].count('___')
                word_count = len(words)
                if text_blanks != word_count:
                    print(f"  PROBLEME: {text_blanks} blancs mais {word_count} mots!")
            
            print()

if __name__ == '__main__':
    analyze_fill_in_blanks_formats()
