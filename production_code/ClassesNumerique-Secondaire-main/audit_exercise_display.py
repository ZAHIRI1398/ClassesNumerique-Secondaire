#!/usr/bin/env python3
"""
Script d'audit pour vérifier l'affichage et le contenu de tous les types d'exercices
"""

import sys
import os
import json
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def audit_exercise_content():
    """Audit du contenu des exercices pour identifier les problèmes d'affichage"""
    print("=== AUDIT DES EXERCICES - AFFICHAGE ET CONTENU ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from models import Exercise, db
        from app import app
        
        with app.app_context():
            # Récupérer tous les exercices
            exercises = Exercise.query.all()
            print(f"Nombre total d'exercices trouvés: {len(exercises)}")
            print()
            
            # Statistiques par type
            type_stats = {}
            problematic_exercises = []
            
            for exercise in exercises:
                exercise_type = exercise.exercise_type
                if exercise_type not in type_stats:
                    type_stats[exercise_type] = {'total': 0, 'valid': 0, 'invalid': 0}
                
                type_stats[exercise_type]['total'] += 1
                
                # Vérifier le contenu de l'exercice
                try:
                    content = exercise.get_content()
                    is_valid = validate_exercise_content(exercise_type, content)
                    
                    if is_valid:
                        type_stats[exercise_type]['valid'] += 1
                    else:
                        type_stats[exercise_type]['invalid'] += 1
                        problematic_exercises.append({
                            'id': exercise.id,
                            'title': exercise.title,
                            'type': exercise_type,
                            'issue': 'Contenu invalide ou manquant'
                        })
                        
                except Exception as e:
                    type_stats[exercise_type]['invalid'] += 1
                    problematic_exercises.append({
                        'id': exercise.id,
                        'title': exercise.title,
                        'type': exercise_type,
                        'issue': f'Erreur de parsing: {str(e)}'
                    })
            
            # Afficher les statistiques
            print("=== STATISTIQUES PAR TYPE D'EXERCICE ===")
            for exercise_type, stats in type_stats.items():
                print(f"{exercise_type}:")
                print(f"  Total: {stats['total']}")
                print(f"  Valides: {stats['valid']}")
                print(f"  Problématiques: {stats['invalid']}")
                if stats['invalid'] > 0:
                    print(f"  [ATTENTION] Taux d'erreur: {(stats['invalid']/stats['total']*100):.1f}%")
                print()
            
            # Afficher les exercices problématiques
            if problematic_exercises:
                print("=== EXERCICES PROBLÉMATIQUES ===")
                for ex in problematic_exercises:
                    print(f"ID {ex['id']}: {ex['title']} ({ex['type']})")
                    print(f"  Issue: {ex['issue']}")
                    print()
            else:
                print("[SUCCES] Aucun exercice problématique détecté!")
            
            return len(problematic_exercises) == 0
            
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'audit: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_exercise_content(exercise_type, content):
    """Valide le contenu d'un exercice selon son type"""
    if not content:
        return False
    
    try:
        # Validation spécifique par type d'exercice
        if exercise_type == 'qcm':
            return 'questions' in content and len(content['questions']) > 0
            
        elif exercise_type == 'fill_in_blanks':
            return ('sentences' in content and 'words' in content) or \
                   ('sentences' in content and 'available_words' in content)
                   
        elif exercise_type == 'word_placement':
            return 'sentences' in content and 'words' in content and \
                   len(content['sentences']) > 0 and len(content['words']) > 0
                   
        elif exercise_type == 'word_search':
            return 'words' in content and len(content['words']) > 0
            
        elif exercise_type == 'pairs':
            return 'pairs' in content and len(content['pairs']) > 0
            
        elif exercise_type == 'drag_and_drop':
            return 'draggable_items' in content and 'drop_zones' in content and \
                   'correct_order' in content
                   
        elif exercise_type == 'underline_words':
            return 'words' in content and len(content['words']) > 0
            
        elif exercise_type == 'flashcards':
            return 'cards' in content and len(content['cards']) > 0
            
        elif exercise_type == 'image_labeling':
            return 'labels' in content and 'zones' in content
            
        elif exercise_type == 'dictation':
            return 'sentences' in content and len(content['sentences']) > 0
            
        else:
            # Type d'exercice non reconnu
            print(f"[ATTENTION] Type d'exercice non reconnu: {exercise_type}")
            return True  # On considère comme valide pour ne pas bloquer
            
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la validation de {exercise_type}: {e}")
        return False

def check_template_files():
    """Vérifie que tous les templates d'affichage existent"""
    print("=== VÉRIFICATION DES TEMPLATES D'AFFICHAGE ===")
    
    templates_dir = "templates/exercise_types"
    required_templates = [
        'qcm.html',
        'fill_in_blanks.html', 
        'word_placement.html',
        'word_search.html',
        'pairs.html',
        'drag_and_drop.html',
        'underline_words.html',
        'flashcards.html',
        'image_labeling.html',
        'dictation.html'
    ]
    
    missing_templates = []
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f"[OK] {template}")
        else:
            print(f"[MANQUANT] {template}")
            missing_templates.append(template)
    
    if missing_templates:
        print(f"\n[ATTENTION] {len(missing_templates)} template(s) manquant(s)")
        return False
    else:
        print("\n[SUCCES] Tous les templates d'affichage sont présents")
        return True

if __name__ == '__main__':
    print("Démarrage de l'audit des exercices...")
    print()
    
    # Vérifier les templates
    templates_ok = check_template_files()
    print()
    
    # Auditer le contenu des exercices
    content_ok = audit_exercise_content()
    print()
    
    # Résultat final
    if templates_ok and content_ok:
        print("[AUDIT REUSSI] Tous les exercices semblent correctement configurés")
        sys.exit(0)
    else:
        print("[AUDIT ECHOUE] Des problèmes ont été détectés")
        sys.exit(1)
