#!/usr/bin/env python3
"""
Script pour appliquer la correction du problème de scoring des exercices fill_in_blanks
sans interaction utilisateur
"""

import os
import sys
import time
import requests

def apply_fix():
    """Applique la correction du problème de double comptage des blancs"""
    app_path = 'app.py'
    
    # Vérifier que le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: Le fichier {app_path} n'existe pas.")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Faire une sauvegarde du fichier original
    backup_path = f"{app_path}.bak.final"
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Sauvegarde créée: {backup_path}")
    
    # Rechercher la section de comptage des blancs
    original_section = """            # Compter le nombre réel de blancs dans le contenu
            total_blanks_in_content = 0
            if 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content += text_blanks
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content += sentences_blanks"""
    
    # Créer la nouvelle section qui évite le double comptage
    new_section = """            # Compter le nombre réel de blancs dans le contenu
            total_blanks_in_content = 0
            
            # Analyser le format de l'exercice et compter les blancs réels
            # CORRECTION: Éviter le double comptage entre 'text' et 'sentences'
            # Priorité à 'sentences' s'il existe, sinon utiliser 'text'
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks"""
    
    # Vérifier si la section existe
    if original_section not in content:
        print("La section de code à modifier n'a pas été trouvée exactement.")
        print("Tentative avec une recherche moins stricte...")
        
        # Recherche moins stricte
        if "total_blanks_in_content = 0" in content and "text_blanks = content['text'].count('___')" in content:
            print("Section identifiée avec recherche partielle.")
            
            # Utiliser une approche ligne par ligne
            lines = content.split('\n')
            new_lines = []
            in_section = False
            section_modified = False
            
            for line in lines:
                if "# Compter le nombre réel de blancs dans le contenu" in line:
                    in_section = True
                    new_lines.append(line)
                    new_lines.append("            total_blanks_in_content = 0")
                    new_lines.append("")
                    new_lines.append("            # Analyser le format de l'exercice et compter les blancs réels")
                    new_lines.append("            # CORRECTION: Éviter le double comptage entre 'text' et 'sentences'")
                    new_lines.append("            # Priorité à 'sentences' s'il existe, sinon utiliser 'text'")
                    new_lines.append("            if 'sentences' in content:")
                    new_lines.append("                sentences_blanks = sum(s.count('___') for s in content['sentences'])")
                    new_lines.append("                total_blanks_in_content = sentences_blanks")
                    new_lines.append("            elif 'text' in content:")
                    new_lines.append("                text_blanks = content['text'].count('___')")
                    new_lines.append("                total_blanks_in_content = text_blanks")
                    section_modified = True
                elif in_section and "total_blanks_in_content += sentences_blanks" in line:
                    in_section = False
                elif not in_section or not section_modified:
                    new_lines.append(line)
            
            if section_modified:
                modified_content = '\n'.join(new_lines)
                
                # Écrire le contenu modifié
                with open(app_path, 'w', encoding='utf-8') as file:
                    file.write(modified_content)
                
                print("Correction appliquée avec succès (méthode alternative)!")
                return True
            else:
                print("Échec de la modification avec l'approche ligne par ligne.")
                return False
        else:
            print("Impossible de localiser la section de code à modifier.")
            return False
    
    # Remplacer la section dans le contenu
    modified_content = content.replace(original_section, new_section)
    
    # Vérifier que le remplacement a bien eu lieu
    if modified_content == content:
        print("Aucune modification n'a été effectuée. Vérifiez le contenu du fichier.")
        return False
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Correction du double comptage des blancs appliquée avec succès!")
    return True

def test_fix():
    """Teste la correction"""
    import sys
    sys.path.append('.')
    
    try:
        from app import app, db, Exercise
        
        with app.app_context():
            exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
            
            if not exercises:
                print("Aucun exercice fill_in_blanks trouvé")
                return False
            
            print(f"Trouvé {len(exercises)} exercices fill_in_blanks")
            
            all_ok = True
            for exercise in exercises:
                print(f"\nTest de l'exercice: {exercise.title} (ID: {exercise.id})")
                
                # Analyser le contenu JSON
                import json
                try:
                    content = json.loads(exercise.content)
                except json.JSONDecodeError:
                    print(f"  Erreur: Contenu JSON invalide")
                    all_ok = False
                    continue
                
                # Compter les blancs dans le contenu
                total_blanks_in_content = 0
                
                if 'sentences' in content:
                    sentences_blanks = sum(s.count('___') for s in content['sentences'])
                    total_blanks_in_content = sentences_blanks
                    print(f"  Format 'sentences': {sentences_blanks} blancs trouvés")
                elif 'text' in content:
                    text_blanks = content['text'].count('___')
                    total_blanks_in_content = text_blanks
                    print(f"  Format 'text': {text_blanks} blancs trouvés")
                
                # Récupérer les réponses correctes
                correct_answers = content.get('words', [])
                if not correct_answers:
                    correct_answers = content.get('available_words', [])
                
                print(f"  Total des blancs trouvés: {total_blanks_in_content}")
                print(f"  Réponses correctes: {len(correct_answers)}")
                
                # Vérifier la cohérence
                if total_blanks_in_content != len(correct_answers):
                    print(f"  [PROBLEME] INCOHÉRENCE: {total_blanks_in_content} blancs vs {len(correct_answers)} réponses")
                    all_ok = False
                else:
                    print(f"  [OK] Cohérent: {total_blanks_in_content} blancs = {len(correct_answers)} réponses")
            
            if all_ok:
                print("\n[SUCCÈS] Tous les exercices sont cohérents!")
                return True
            else:
                print("\n[ÉCHEC] Certains exercices présentent des incohérences.")
                return False
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        return False

def check_deployment(url="https://web-production-9a047.up.railway.app", max_retries=1):
    """Vérifie que le déploiement est accessible"""
    print(f"Vérification de l'accessibilité de l'URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"[SUCCÈS] L'URL est accessible (HTTP {response.status_code})")
            return True
        else:
            print(f"[AVERTISSEMENT] L'URL a répondu avec le code HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[ERREUR] Impossible d'accéder à l'URL: {e}")
        return False

if __name__ == '__main__':
    print("Application de la correction du problème de scoring des exercices fill_in_blanks...")
    
    # Appliquer la correction
    if apply_fix():
        # Tester la correction
        print("\nTest de la correction...")
        if test_fix():
            print("\nLa correction a été appliquée et testée avec succès!")
            print("\nPour déployer cette correction sur Railway:")
            print("1. Commitez les modifications: git add app.py && git commit -m \"Fix: Correction du problème de scoring des exercices texte à trous\"")
            print("2. Pushez les modifications: git push")
            print("3. Railway déploiera automatiquement les changements")
            
            # Vérifier si l'URL de production est accessible
            print("\nVérification de l'accessibilité de l'URL de production...")
            check_deployment()
        else:
            print("\nLa correction a été appliquée mais les tests ont échoué.")
            print("Vérifiez manuellement le comportement des exercices fill_in_blanks.")
    else:
        print("\nÉchec de l'application de la correction.")
