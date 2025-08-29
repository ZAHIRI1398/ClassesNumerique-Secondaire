"""
Script pour corriger le problème d'upload des fichiers audio MP3 dans les exercices de type dictée
"""

import os
import shutil
import time
from datetime import datetime

# Créer une sauvegarde de app.py avant modification
def backup_file(file_path):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.bak_dictation_audio_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    return backup_path

# Correction du code dans modified_submit.py
def fix_dictation_audio_upload():
    file_path = 'modified_submit.py'
    backup_path = backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Correction 1: Utiliser un timestamp au lieu de exercise_id qui n'est pas encore défini
    old_code = """                        # Sauvegarder le fichier audio
                        filename = secure_filename(f'dictation_{exercise_id}_{i}_{audio_file.filename}')
                        audio_path = os.path.join('static/uploads/audio', filename)"""
    
    new_code = """                        # Sauvegarder le fichier audio avec un timestamp unique
                        timestamp = int(time.time())
                        filename = secure_filename(f'dictation_{timestamp}_{i}_{audio_file.filename}')
                        audio_path = os.path.join('static/uploads/audio', filename)"""
    
    content = content.replace(old_code, new_code)
    
    # Correction 2: Assurer la cohérence des chemins
    old_path = """                        audio_files.append(f'/static/exercises/audio/{filename}')"""
    new_path = """                        audio_files.append(f'/static/uploads/audio/{filename}')"""
    
    content = content.replace(old_path, new_path)
    
    # Écrire les modifications dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Correction appliquée avec succès dans modified_submit.py")
    
    # Vérifier si le dossier d'upload audio existe
    audio_dir = os.path.join('static', 'uploads', 'audio')
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir, exist_ok=True)
        print(f"Dossier créé: {audio_dir}")
    else:
        print(f"Le dossier {audio_dir} existe déjà")
    
    return True

if __name__ == "__main__":
    print("Début de la correction du problème d'upload des fichiers audio MP3...")
    success = fix_dictation_audio_upload()
    if success:
        print("Correction terminée avec succès!")
        print("Vous pouvez maintenant redémarrer l'application pour appliquer les modifications.")
    else:
        print("Une erreur est survenue lors de la correction.")
