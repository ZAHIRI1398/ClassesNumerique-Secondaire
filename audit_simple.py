#!/usr/bin/env python3
"""
Audit simplifié pour vérifier l'affichage des exercices sans dépendances externes
"""

import os
import json
from pathlib import Path

def check_template_files():
    """Vérifie que tous les templates d'affichage existent"""
    print("=== VERIFICATION DES TEMPLATES D'AFFICHAGE ===")
    
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
        print("\n[SUCCES] Tous les templates d'affichage sont presents")
        return True

def check_template_quality():
    """Vérifie la qualité des templates (pas de debug, etc.)"""
    print("=== VERIFICATION DE LA QUALITE DES TEMPLATES ===")
    
    templates_dir = "templates/exercise_types"
    templates_to_check = [
        'qcm.html',
        'fill_in_blanks.html', 
        'word_placement.html',
        'word_search.html',
        'pairs.html',
        'drag_and_drop.html',
        'underline_words.html'
    ]
    
    issues_found = []
    
    for template in templates_to_check:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Rechercher des éléments problématiques
                debug_patterns = [
                    'DEBUG INFO',
                    'debug info',
                    'TODO',
                    'FIXME',
                    'BUG',
                    'console.log',
                    'alert alert-info.*DEBUG'
                ]
                
                template_issues = []
                for pattern in debug_patterns:
                    if pattern.lower() in content.lower():
                        # Compter les occurrences pour plus de précision
                        count = content.lower().count(pattern.lower())
                        template_issues.append(f"{pattern}({count})")
                
                if template_issues:
                    print(f"[PROBLEME] {template}: {', '.join(template_issues)}")
                    issues_found.extend(template_issues)
                else:
                    print(f"[OK] {template}")
                    
            except Exception as e:
                print(f"[ERREUR] Impossible de lire {template}: {e}")
                issues_found.append(f"Erreur lecture {template}")
    
    if issues_found:
        print(f"\n[ATTENTION] {len(issues_found)} probleme(s) de qualite detecte(s)")
        return False
    else:
        print("\n[SUCCES] Tous les templates sont de bonne qualite")
        return True

def check_creation_interface():
    """Vérifie l'interface de création d'exercices"""
    print("=== VERIFICATION DE L'INTERFACE DE CREATION ===")
    
    creation_template = "templates/exercise_types/create_exercise_simple.html"
    
    if not os.path.exists(creation_template):
        print(f"[ERREUR] Template de creation manquant: {creation_template}")
        return False
    
    try:
        with open(creation_template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la présence des sections pour chaque type d'exercice
        required_sections = [
            'qcm_section',
            'fill_in_blanks_section',
            'word_placement_section',
            'word_search_section',
            'pairs_section',
            'drag_and_drop_section',
            'underline_words_section'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
            else:
                print(f"[OK] Section {section}")
        
        if missing_sections:
            print(f"\n[ATTENTION] {len(missing_sections)} section(s) manquante(s):")
            for section in missing_sections:
                print(f"  - {section}")
            return False
        else:
            print("\n[SUCCES] Toutes les sections de creation sont presentes")
            return True
            
    except Exception as e:
        print(f"[ERREUR] Impossible de verifier l'interface de creation: {e}")
        return False

def check_backend_logic():
    """Vérifie la logique backend pour la création d'exercices"""
    print("=== VERIFICATION DE LA LOGIQUE BACKEND ===")
    
    backend_file = "modified_submit.py"
    
    if not os.path.exists(backend_file):
        print(f"[ERREUR] Fichier backend manquant: {backend_file}")
        return False
    
    try:
        with open(backend_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la présence de la logique pour chaque type d'exercice
        exercise_types_to_check = [
            'qcm',
            'fill_in_blanks',
            'word_placement',
            'word_search',
            'pairs',
            'drag_and_drop',
            'underline_words'
        ]
        
        missing_logic = []
        for exercise_type in exercise_types_to_check:
            # Chercher les deux patterns possibles
            pattern1 = f"if exercise_type == '{exercise_type}'"
            pattern2 = f"elif exercise_type == '{exercise_type}'"
            if pattern1 in content or pattern2 in content:
                print(f"[OK] Logique backend pour {exercise_type}")
            else:
                print(f"[MANQUANT] Logique backend pour {exercise_type}")
                missing_logic.append(exercise_type)
        
        if missing_logic:
            print(f"\n[ATTENTION] {len(missing_logic)} logique(s) backend manquante(s)")
            return False
        else:
            print("\n[SUCCES] Toutes les logiques backend sont presentes")
            return True
            
    except Exception as e:
        print(f"[ERREUR] Impossible de verifier la logique backend: {e}")
        return False

if __name__ == '__main__':
    print("Demarrage de l'audit simplifie des exercices...")
    print()
    
    # Vérifications
    templates_ok = check_template_files()
    print()
    
    quality_ok = check_template_quality()
    print()
    
    creation_ok = check_creation_interface()
    print()
    
    backend_ok = check_backend_logic()
    print()
    
    # Résultat final
    all_ok = templates_ok and quality_ok and creation_ok and backend_ok
    
    if all_ok:
        print("[AUDIT REUSSI] Tous les composants sont correctement configures")
        print("Les exercices devraient s'afficher et se creer correctement!")
    else:
        print("[AUDIT PARTIEL] Certains problemes ont ete detectes")
        print("Voir les details ci-dessus pour les corrections necessaires")
    
    print(f"\nResultat: {4 - [templates_ok, quality_ok, creation_ok, backend_ok].count(False)}/4 verifications reussies")
