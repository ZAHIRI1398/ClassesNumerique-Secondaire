#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import Exercise

def check_pairs():
    with app.app_context():
        # Vérifier les exercices de type pairs
        pairs_exercises = Exercise.query.filter_by(exercise_type='pairs').all()
        print(f'Nombre d\'exercices pairs trouvés: {len(pairs_exercises)}')
        
        for ex in pairs_exercises:
            print(f'ID: {ex.id}, Titre: {ex.title}')
            content = ex.get_content()
            print(f'Clés: {list(content.keys()) if content else "Aucun contenu"}')
            
            if content and 'pairs' in content:
                print('Structure pairs:')
                for i, pair in enumerate(content['pairs'][:2]):  # Afficher les 2 premières
                    left = pair.get('left', {})
                    right = pair.get('right', {})
                    print(f'  Pair {i+1}: left_type={left.get("type")}, right_type={right.get("type")}')
                    print(f'    Left: {left.get("content", "")[:30]}...')
                    print(f'    Right: {right.get("content", "")[:30]}...')
            print('---')

if __name__ == '__main__':
    check_pairs()
