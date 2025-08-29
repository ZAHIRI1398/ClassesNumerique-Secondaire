import os
import logging
from flask import current_app
from utils.image_utils import normalize_image_path
from utils.image_path_manager import ImagePathManager

# Variable pour simuler cloudinary_configured
cloudinary_configured = False

def upload_file(file, folder="uploads", exercise_type=None):
    """
    Upload un fichier en local uniquement (sans Cloudinary)
    
    Args:
        file: Objet fichier Flask
        folder: Dossier de destination (ignoré, utilise toujours 'exercises')
        exercise_type: Type d'exercice (optionnel)
    
    Returns:
        str: Chemin web vers le fichier uploadé
    """
    if not file or not file.filename:
        return None
    
    # Générer un nom de fichier unique
    unique_filename = ImagePathManager.generate_unique_filename(file.filename, exercise_type)
    
    try:
        # Stockage local uniquement
        file.seek(0)
        file_content = file.read()
        
        print(f"DEBUG: Contenu lu en mémoire: {len(file_content)} octets")
        
        if len(file_content) == 0:
            print("ERREUR: Fichier vide détecté")
            return None
        
        # Déterminer le chemin de sauvegarde (toujours dans exercises)
        upload_folder = os.path.join(current_app.root_path, 'static', 'exercises')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Chemin complet du fichier
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Écrire le contenu sur disque
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Vérifier que le fichier a été écrit correctement
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"DEBUG: Fichier sauvegardé: {file_path} ({file_size} octets)")
            
            if file_size > 0:
                # Retourner le chemin web
                web_path = f'/static/exercises/{unique_filename}'
                print(f"DEBUG: Chemin web retourné: {web_path}")
                return web_path
            else:
                print("ERREUR: Fichier sauvegardé mais vide")
                os.remove(file_path)
                return None
        else:
            print("ERREUR: Fichier non sauvegardé")
            return None
            
    except Exception as e:
        print(f"ERREUR lors de l'upload: {str(e)}")
        return None
