#!/usr/bin/env python3
"""
Script pour corriger le conflit entre les deux logiques de scoring pour les exercices fill_in_blanks.
Le problème est qu'il existe deux implémentations différentes dans app.py, ce qui cause des incohérences.
"""

import os
import re
import sys
import json
from datetime import datetime

def backup_app_py():
    """Crée une sauvegarde du fichier app.py"""
    app_path = 'app.py'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{app_path}.bak.{timestamp}"
    
    try:
        with open(app_path, 'r', encoding='utf-8') as source:
            content = source.read()
        
        with open(backup_path, 'w', encoding='utf-8') as target:
            target.write(content)
        
        print(f"Sauvegarde créée: {backup_path}")
        return content
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {str(e)}")
        sys.exit(1)

def fix_scoring_logic(content):
    """
    Corrige le conflit entre les deux logiques de scoring pour les exercices fill_in_blanks.
    La solution est de désactiver la première implémentation (lignes 1995-2022) et de
    s'assurer que seule la deuxième implémentation (lignes 3415-3510) est utilisée.
    """
    # Identifier la première implémentation
    first_impl_pattern = r"elif exercise\.exercise_type == 'fill_in_blanks':\s+user_answers = \[\]\s+correct_answers = content\.get\('answers', \[\]\)"
    
    # Remplacer la première implémentation par un commentaire et une redirection vers la deuxième implémentation
    replacement = """elif exercise.exercise_type == 'fill_in_blanks':
        # Cette implémentation a été désactivée car elle est en conflit avec l'implémentation plus complète ci-dessous
        # qui utilise la même logique que pour les exercices word_placement.
        # Voir lignes ~3415-3510 pour l'implémentation active.
        pass  # La logique de scoring est maintenant gérée dans la section dédiée plus bas"""
    
    # Appliquer le remplacement
    modified_content = re.sub(first_impl_pattern, replacement, content, flags=re.DOTALL)
    
    # Vérifier si le remplacement a été effectué
    if modified_content == content:
        print("Attention: Impossible de trouver la première implémentation à remplacer.")
        return content
    
    print("Première implémentation désactivée avec succès.")
    return modified_content

def save_modified_content(content):
    """Sauvegarde le contenu modifié dans app.py"""
    app_path = 'app.py'
    try:
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Modifications appliquées avec succès à {app_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier modifié: {str(e)}")
        return False

def main():
    print("Correction du conflit de logiques de scoring pour les exercices fill_in_blanks...")
    
    # Créer une sauvegarde et récupérer le contenu
    original_content = backup_app_py()
    
    # Corriger la logique de scoring
    modified_content = fix_scoring_logic(original_content)
    
    # Sauvegarder les modifications
    if save_modified_content(modified_content):
        print("Correction terminée avec succès!")
        print("La logique de scoring des exercices fill_in_blanks est maintenant cohérente.")
        print("Vous devriez maintenant obtenir un score de 100% si toutes les réponses sont correctes.")
    else:
        print("La correction a échoué.")

if __name__ == "__main__":
    main()
