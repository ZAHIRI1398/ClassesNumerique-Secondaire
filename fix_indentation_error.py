#!/usr/bin/env python3
"""
Script pour corriger l'erreur d'indentation dans app.py
"""

import os
import re
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
        return None

def fix_indentation_error(content):
    """
    Corrige l'erreur d'indentation dans le bloc fill_in_blanks
    """
    # Rechercher le bloc problématique avec une regex précise
    pattern = r"(\s+)elif exercise\.exercise_type == 'fill_in_blanks':\n(\s+)# Cette implémentation"
    
    # Vérifier si le motif est trouvé
    match = re.search(pattern, content)
    if match:
        indent_level = match.group(1)  # Niveau d'indentation du elif
        
        # Construire le bloc correctement indenté
        fixed_block = f"{indent_level}elif exercise.exercise_type == 'fill_in_blanks':\n"
        fixed_block += f"{indent_level}    # Cette implémentation a été désactivée car elle est en conflit avec l'implémentation plus complète ci-dessous\n"
        fixed_block += f"{indent_level}    # qui utilise la même logique que pour les exercices word_placement.\n"
        fixed_block += f"{indent_level}    # Voir lignes ~3415-3510 pour l'implémentation active.\n"
        fixed_block += f"{indent_level}    pass  # La logique de scoring est maintenant gérée dans la section dédiée plus bas"
        
        # Remplacer le bloc problématique
        content_fixed = re.sub(
            r"(\s+)elif exercise\.exercise_type == 'fill_in_blanks':\n(\s+)# Cette implémentation.*?pass  # La logique de scoring est maintenant gérée dans la section dédiée plus bas",
            fixed_block,
            content,
            flags=re.DOTALL
        )
        
        return content_fixed
    else:
        print("Le bloc problématique n'a pas été trouvé.")
        return content

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
    print("Correction de l'erreur d'indentation dans app.py...")
    
    # Créer une sauvegarde et récupérer le contenu
    original_content = backup_app_py()
    if not original_content:
        print("Impossible de continuer sans le contenu original.")
        return
    
    # Corriger l'erreur d'indentation
    modified_content = fix_indentation_error(original_content)
    if modified_content == original_content:
        print("Aucune modification n'a été effectuée.")
        return
    
    # Sauvegarder les modifications
    if save_modified_content(modified_content):
        print("Correction terminée avec succès!")
        print("L'erreur d'indentation a été corrigée.")
        print("\nIMPORTANT: N'oubliez pas de redémarrer l'application Flask pour que les modifications prennent effet.")
    else:
        print("La sauvegarde des modifications a échoué.")

if __name__ == "__main__":
    main()
