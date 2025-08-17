#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json

def check_pairs_exercises():
    """Vérifier la structure des exercices de type 'pairs' en base"""
    
    # Connexion à la base de données
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Rechercher tous les exercices de type 'pairs'
    cursor.execute('SELECT id, title, exercise_type, content FROM Exercise WHERE exercise_type = "pairs"')
    exercises = cursor.fetchall()
    
    print('=== EXERCICES DE TYPE "PAIRS" ===')
    print(f'Nombre d\'exercices trouvés: {len(exercises)}')
    print()
    
    for ex_id, title, ex_type, content_str in exercises:
        print(f'ID: {ex_id}')
        print(f'Titre: {title}')
        print(f'Type: {ex_type}')
        
        try:
            content = json.loads(content_str)
            print(f'Clés disponibles: {list(content.keys())}')
            
            # Vérifier la structure 'pairs'
            if 'pairs' in content:
                print(f'Nombre de paires: {len(content["pairs"])}')
                print('STRUCTURE DES PAIRES:')
                for i, pair in enumerate(content['pairs']):
                    left = pair.get('left', {})
                    right = pair.get('right', {})
                    print(f'  Paire {i+1}:')
                    print(f'    Gauche: type="{left.get("type", "N/A")}", content="{left.get("content", "N/A")[:50]}..."')
                    print(f'    Droite: type="{right.get("type", "N/A")}", content="{right.get("content", "N/A")[:50]}..."')
            
            # Vérifier la structure 'left_items/right_items'
            if 'left_items' in content:
                print(f'LEFT_ITEMS: {len(content["left_items"])} éléments')
                for i, item in enumerate(content['left_items'][:3]):  # Afficher les 3 premiers
                    if isinstance(item, dict):
                        print(f'  Item {i+1}: type="{item.get("type", "N/A")}", content="{str(item.get("content", "N/A"))[:30]}..."')
                    else:
                        print(f'  Item {i+1}: "{str(item)[:30]}..."')
            
            if 'right_items' in content:
                print(f'RIGHT_ITEMS: {len(content["right_items"])} éléments')
                for i, item in enumerate(content['right_items'][:3]):  # Afficher les 3 premiers
                    if isinstance(item, dict):
                        print(f'  Item {i+1}: type="{item.get("type", "N/A")}", content="{str(item.get("content", "N/A"))[:30]}..."')
                    else:
                        print(f'  Item {i+1}: "{str(item)[:30]}..."')
            
            if 'shuffled_right_items' in content:
                print(f'SHUFFLED_RIGHT_ITEMS: {len(content["shuffled_right_items"])} éléments')
                
        except Exception as e:
            print(f'Erreur parsing JSON: {e}')
        
        print('-' * 60)
        print()
    
    conn.close()

if __name__ == '__main__':
    check_pairs_exercises()
