#!/usr/bin/env python3
"""
Script pour corriger complètement la première implémentation de scoring
des exercices fill_in_blanks dans app.py.
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

def fix_scoring_implementation(content):
    """
    Corrige complètement la première implémentation de scoring
    en supprimant tout le code après le pass.
    """
    # Motif pour trouver la section à remplacer
    pattern = r"elif exercise\.exercise_type == 'fill_in_blanks':(.*?)elif exercise\.exercise_type == 'word_placement':"
    
    # Remplacement avec seulement les commentaires et le pass
    replacement = """elif exercise.exercise_type == 'fill_in_blanks':
        # Cette implémentation a été désactivée car elle est en conflit avec l'implémentation plus complète ci-dessous
        # qui utilise la même logique que pour les exercices word_placement.
        # Voir lignes ~3415-3510 pour l'implémentation active.
        pass  # La logique de scoring est maintenant gérée dans la section dédiée plus bas
    
    elif exercise.exercise_type == 'word_placement':"""
    
    # Appliquer le remplacement
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Vérifier si le remplacement a été effectué
    if modified_content == content:
        print("Aucune modification n'a été effectuée. Le motif n'a pas été trouvé.")
        return None
    
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
    print("Correction de la première implémentation de scoring pour les exercices fill_in_blanks...")
    
    # Créer une sauvegarde et récupérer le contenu
    original_content = backup_app_py()
    if not original_content:
        print("Impossible de continuer sans le contenu original.")
        return
    
    # Corriger la logique de scoring
    modified_content = fix_scoring_implementation(original_content)
    if not modified_content:
        print("La correction a échoué.")
        return
    
    # Sauvegarder les modifications
    if save_modified_content(modified_content):
        print("Correction terminée avec succès!")
        print("La logique de scoring des exercices fill_in_blanks est maintenant cohérente.")
        print("Vous devriez maintenant obtenir un score de 100% si toutes les réponses sont correctes.")
        print("\nIMPORTANT: N'oubliez pas de redémarrer l'application Flask pour que les modifications prennent effet.")
    else:
        print("La sauvegarde des modifications a échoué.")

if __name__ == "__main__":
    main()
