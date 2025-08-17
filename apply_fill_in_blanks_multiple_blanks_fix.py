#!/usr/bin/env python3
"""
Script pour appliquer la correction du problème de scoring des exercices "texte à trous"
avec plusieurs blancs dans une ligne.

Ce script:
1. Fait une sauvegarde du fichier app.py actuel
2. Identifie la section de code à modifier dans app.py
3. Applique la correction pour le traitement des exercices fill_in_blanks
4. Enregistre le fichier modifié
"""

import os
import re
import shutil
import datetime

def backup_app_py():
    """Crée une sauvegarde du fichier app.py actuel."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"app.py.bak.{timestamp}"
    
    try:
        shutil.copy2("app.py", backup_filename)
        print(f"Sauvegarde créée: {backup_filename}")
        return True
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {e}")
        return False

def find_fill_in_blanks_section(content):
    """
    Trouve la section de code qui traite les exercices fill_in_blanks.
    
    Args:
        content (str): Le contenu du fichier app.py
        
    Returns:
        tuple: (start_index, end_index, section_content) ou (None, None, None) si non trouvé
    """
    # Recherche du pattern pour la section fill_in_blanks
    pattern = r"elif\s+exercise\.exercise_type\s*==\s*['\"]fill_in_blanks['\"].*?(?=elif|else|return)"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.start(), match.end(), match.group(0)
    
    return None, None, None

def apply_fix(app_content):
    """
    Applique la correction pour le traitement des exercices fill_in_blanks.
    
    Args:
        app_content (str): Le contenu du fichier app.py
        
    Returns:
        str: Le contenu modifié du fichier app.py
    """
    start_idx, end_idx, section = find_fill_in_blanks_section(app_content)
    
    if not section:
        print("Section fill_in_blanks non trouvée dans app.py")
        return app_content
    
    print("Section fill_in_blanks trouvée:")
    print("-" * 40)
    print(section[:200] + "..." if len(section) > 200 else section)
    print("-" * 40)
    
    # Vérifier si la section contient déjà la correction
    if "if 'sentences' in content:" in section and "elif 'text' in content:" in section:
        print("La correction semble déjà être appliquée (if/elif trouvé)")
        return app_content
    
    # Rechercher le pattern spécifique à corriger
    pattern_to_fix = r"(total_blanks_in_content\s*=\s*0.*?)(if\s*['\"]\s*text\s*['\"].*?total_blanks_in_content\s*\+=\s*text_blanks.*?)(if\s*['\"]\s*sentences\s*['\"].*?total_blanks_in_content\s*\+=\s*sentences_blanks)"
    
    match_to_fix = re.search(pattern_to_fix, section, re.DOTALL)
    
    if not match_to_fix:
        print("Pattern spécifique à corriger non trouvé")
        return app_content
    
    # Construire la section corrigée
    fixed_section = section.replace(match_to_fix.group(0), """total_blanks_in_content = 0
        
        # CORRECTION: Utiliser if/elif au lieu de if/if pour éviter le double comptage
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
            
            # Log détaillé pour chaque phrase et ses blancs
            for i, sentence in enumerate(content['sentences']):
                blanks_in_sentence = sentence.count('___')
                current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'text' détecté: {text_blanks} blancs dans text")""")
    
    # Remplacer la section dans le contenu complet
    modified_content = app_content[:start_idx] + fixed_section + app_content[end_idx:]
    
    return modified_content

def main():
    """Fonction principale pour appliquer la correction."""
    print("Application de la correction pour les exercices 'texte à trous' avec plusieurs blancs")
    
    # Vérifier que app.py existe
    if not os.path.exists("app.py"):
        print("Erreur: app.py non trouvé dans le répertoire courant")
        return False
    
    # Créer une sauvegarde
    if not backup_app_py():
        print("Erreur lors de la création de la sauvegarde. Arrêt du script.")
        return False
    
    # Lire le contenu du fichier app.py
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture de app.py: {e}")
        return False
    
    # Appliquer la correction
    modified_content = apply_fix(app_content)
    
    # Si le contenu n'a pas été modifié, arrêter
    if modified_content == app_content:
        print("Aucune modification n'a été apportée au fichier app.py")
        return False
    
    # Écrire le contenu modifié dans app.py
    try:
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(modified_content)
        print("Correction appliquée avec succès à app.py")
        return True
    except Exception as e:
        print(f"Erreur lors de l'écriture dans app.py: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\nCORRECTION APPLIQUÉE AVEC SUCCÈS")
        print("Pour vérifier que la correction fonctionne correctement:")
        print("1. Exécutez le script de test: python test_multiple_blanks_fix.py")
        print("2. Testez un exercice 'texte à trous' avec plusieurs blancs dans une ligne")
        print("3. Vérifiez que le scoring est correct")
    else:
        print("\nÉCHEC DE L'APPLICATION DE LA CORRECTION")
        print("Veuillez vérifier les erreurs ci-dessus et réessayer")
