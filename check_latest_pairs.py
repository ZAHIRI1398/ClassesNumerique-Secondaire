#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import Exercise

def check_latest_pairs():
    with app.app_context():
        # Récupérer le dernier exercice créé de type pairs
        latest_pairs = Exercise.query.filter_by(exercise_type='pairs').order_by(Exercise.id.desc()).first()
        
        if not latest_pairs:
            print("Aucun exercice de type 'pairs' trouvé")
            return
            
        print(f"=== DERNIER EXERCICE PAIRS ===")
        print(f"ID: {latest_pairs.id}")
        print(f"Titre: {latest_pairs.title}")
        print(f"Description: {latest_pairs.description}")
        print(f"Type: {latest_pairs.exercise_type}")
        
        # Analyser le contenu JSON
        content = latest_pairs.get_content()
        print(f"\n=== CONTENU JSON ===")
        print(f"Clés disponibles: {list(content.keys()) if content else 'Aucun contenu'}")
        
        if content:
            # Afficher le contenu brut
            import json
            print(f"\nContenu complet:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
            
            # Analyser la structure pairs si elle existe
            if 'pairs' in content:
                print(f"\n=== STRUCTURE PAIRS ===")
                pairs = content['pairs']
                print(f"Nombre de paires: {len(pairs)}")
                
                for i, pair in enumerate(pairs):
                    print(f"\nPaire {i+1}:")
                    left = pair.get('left', {})
                    right = pair.get('right', {})
                    
                    print(f"  Gauche - Type: {left.get('type', 'N/A')}")
                    print(f"  Gauche - Contenu: {left.get('content', 'N/A')}")
                    print(f"  Droite - Type: {right.get('type', 'N/A')}")
                    print(f"  Droite - Contenu: {right.get('content', 'N/A')}")

if __name__ == '__main__':
    check_latest_pairs()
