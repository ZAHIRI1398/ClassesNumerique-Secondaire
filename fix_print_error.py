import os
import re

def fix_print_statements(file_path):
    """
    Remplace les appels print() par des appels à app.logger.info() dans app.py
    pour éviter les erreurs OSError liées à l'encodage.
    """
    print(f"Correction des appels print() dans {file_path}...")
    
    # Lire le contenu du fichier
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Créer une sauvegarde du fichier original
    backup_path = f"{file_path}.bak.print_fix"
    with open(backup_path, 'w', encoding='utf-8') as backup_file:
        backup_file.write(content)
    print(f"Sauvegarde créée: {backup_path}")
    
    # Remplacer les appels print() problématiques
    # 1. Remplacer print(f'[VIEW_EXERCISE_DEBUG] Starting view_exercise for ID {exercise_id}', flush=True)
    content = re.sub(
        r"print\(f'\[VIEW_EXERCISE_DEBUG\] Starting view_exercise for ID \{exercise_id\}', flush=True\)",
        r"app.logger.info(f'Starting view_exercise for ID {exercise_id}')",
        content
    )
    
    # 2. Remplacer print(f'[VIEW_EXERCISE_DEBUG] Exercise type: {exercise.exercise_type}')
    content = re.sub(
        r"print\(f'\[VIEW_EXERCISE_DEBUG\] Exercise type: \{exercise\.exercise_type\}'\)",
        r"app.logger.info(f'Exercise type: {exercise.exercise_type}')",
        content
    )
    
    # Écrire le contenu modifié dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Correction terminée. Les appels print() problématiques ont été remplacés par app.logger.info().")
    print(f"Vous pouvez maintenant redémarrer l'application Flask.")

if __name__ == "__main__":
    app_path = os.path.join(os.getcwd(), "app.py")
    fix_print_statements(app_path)
