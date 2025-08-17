#!/usr/bin/env python3
"""
Script pour restaurer une version fonctionnelle de app.py à partir d'une sauvegarde
et appliquer correctement la correction du scoring fill_in_blanks.
"""

import os
import glob
import re
from datetime import datetime

def find_latest_backup():
    """Trouve la dernière sauvegarde de app.py avant nos modifications"""
    backups = glob.glob("app.py.bak.*")
    if not backups:
        return None
    
    # Trier par date de modification (la plus récente en premier)
    backups.sort(key=os.path.getmtime, reverse=True)
    
    # Trouver la sauvegarde avant nos modifications
    for backup in backups:
        # Vérifier si c'est une sauvegarde avant nos modifications
        if "20250815_17" not in backup:  # Exclure nos sauvegardes récentes
            return backup
    
    # Si aucune sauvegarde appropriée n'est trouvée, utiliser la plus ancienne
    return backups[-1]

def restore_from_backup(backup_path):
    """Restaure app.py à partir d'une sauvegarde"""
    try:
        with open(backup_path, 'r', encoding='utf-8') as source:
            content = source.read()
        
        # Créer une sauvegarde de l'état actuel avant restauration
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        current_backup = f"app.py.broken.{timestamp}"
        with open('app.py', 'r', encoding='utf-8') as current:
            with open(current_backup, 'w', encoding='utf-8') as backup:
                backup.write(current.read())
        print(f"Sauvegarde de l'état actuel créée: {current_backup}")
        
        # Restaurer à partir de la sauvegarde
        with open('app.py', 'w', encoding='utf-8') as target:
            target.write(content)
        
        print(f"Restauration à partir de {backup_path} effectuée avec succès")
        return content
    except Exception as e:
        print(f"Erreur lors de la restauration: {str(e)}")
        return None

def apply_fix_to_content(content):
    """Applique la correction du scoring fill_in_blanks au contenu"""
    # Motif pour trouver la première implémentation
    pattern = r"(    elif exercise\.exercise_type == 'fill_in_blanks':\n)(\s+user_answers = \[\]\n\s+correct_answers = content\.get\('answers', \[\]\)\n.*?score = \(score / max_score\) \* 100 if max_score > 0 else 0\n)"
    
    # Remplacement avec seulement les commentaires et le pass
    replacement = r"\1        # Cette implémentation a été désactivée car elle est en conflit avec l'implémentation plus complète ci-dessous\n        # qui utilise la même logique que pour les exercices word_placement.\n        # Voir lignes ~3415-3510 pour l'implémentation active.\n        pass  # La logique de scoring est maintenant gérée dans la section dédiée plus bas\n"
    
    # Appliquer le remplacement
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Vérifier si le remplacement a été effectué
    if modified_content == content:
        print("Aucune modification n'a été effectuée. Le motif n'a pas été trouvé.")
        return None
    
    return modified_content

def save_modified_content(content):
    """Sauvegarde le contenu modifié dans app.py"""
    try:
        with open('app.py', 'w', encoding='utf-8') as file:
            file.write(content)
        print("Modifications appliquées avec succès à app.py")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier modifié: {str(e)}")
        return False

def main():
    print("Restauration d'une version fonctionnelle de app.py et application de la correction...")
    
    # Trouver la dernière sauvegarde
    backup_path = find_latest_backup()
    if not backup_path:
        print("Aucune sauvegarde trouvée.")
        return
    
    print(f"Sauvegarde trouvée: {backup_path}")
    
    # Restaurer à partir de la sauvegarde
    content = restore_from_backup(backup_path)
    if not content:
        print("La restauration a échoué.")
        return
    
    # Appliquer la correction
    modified_content = apply_fix_to_content(content)
    if not modified_content:
        print("L'application de la correction a échoué.")
        return
    
    # Sauvegarder les modifications
    if save_modified_content(modified_content):
        print("\nRestauration et correction terminées avec succès!")
        print("La logique de scoring des exercices fill_in_blanks est maintenant cohérente.")
        print("Vous devriez maintenant obtenir un score de 100% si toutes les réponses sont correctes.")
        print("\nIMPORTANT: N'oubliez pas de redémarrer l'application Flask pour que les modifications prennent effet.")
    else:
        print("La sauvegarde des modifications a échoué.")

if __name__ == "__main__":
    main()
