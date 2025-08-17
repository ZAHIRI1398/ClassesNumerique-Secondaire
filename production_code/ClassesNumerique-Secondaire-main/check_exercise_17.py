#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier le contenu de l'exercice 17
et identifier pourquoi la zone 6 "Glande salivaire" n'apparaît pas dans l'exercice.
"""

from app import app, db, Exercise
import json

def check_exercise_17():
    """Vérifie le contenu de l'exercice 17 en base de données"""
    
    with app.app_context():
        exercise = Exercise.query.get(17)
        
        if not exercise:
            print("❌ ERREUR : Exercice 17 non trouvé en base")
            return
        
        print("=== DIAGNOSTIC EXERCICE 17 ===")
        print(f"Titre : {exercise.title}")
        print(f"Type : {exercise.exercise_type}")
        print(f"Description : {exercise.description}")
        print()
        
        try:
            # Parser le contenu JSON
            content = json.loads(exercise.content)
            
            print("=== CONTENU JSON ===")
            print(f"Clés disponibles : {list(content.keys())}")
            print()
            
            # Vérifier les zones
            zones = content.get('zones', [])
            print(f"=== ZONES ({len(zones)} trouvées) ===")
            
            for i, zone in enumerate(zones):
                print(f"Zone {i+1}:")
                print(f"  - ID: {zone.get('id', 'N/A')}")
                print(f"  - X: {zone.get('x', 'N/A')}")
                print(f"  - Y: {zone.get('y', 'N/A')}")
                print(f"  - Légende: '{zone.get('legend', 'N/A')}'")
                print()
            
            # Vérifier si la zone 6 "Glande salivaire" est présente
            zone_6_found = False
            glande_salivaire_found = False
            
            for zone in zones:
                if zone.get('id') == 6:
                    zone_6_found = True
                if 'glande salivaire' in zone.get('legend', '').lower():
                    glande_salivaire_found = True
            
            print("=== DIAGNOSTIC ZONE 6 ===")
            print(f"Zone avec ID=6 trouvée : {'✅ OUI' if zone_6_found else '❌ NON'}")
            print(f"Zone 'Glande salivaire' trouvée : {'✅ OUI' if glande_salivaire_found else '❌ NON'}")
            
            if not zone_6_found and not glande_salivaire_found:
                print("🚨 PROBLÈME CONFIRMÉ : La zone 6 'Glande salivaire' n'est PAS présente dans le JSON !")
                print("   Cela explique pourquoi elle n'apparaît pas dans l'exercice.")
            elif zone_6_found or glande_salivaire_found:
                print("✅ La zone 6 'Glande salivaire' EST présente dans le JSON.")
                print("   Le problème doit venir d'ailleurs (template ou logique d'affichage).")
            
        except json.JSONDecodeError as e:
            print(f"❌ ERREUR : Impossible de parser le JSON : {e}")
            print(f"Contenu brut : {exercise.content}")
        except Exception as e:
            print(f"❌ ERREUR : {e}")

if __name__ == "__main__":
    check_exercise_17()
