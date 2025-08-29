
def safe_file_save(file, filepath):
    """Sauvegarder un fichier de manière sécurisée avec vérification de taille"""
    try:
        # Créer le répertoire parent s'il n'existe pas
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Sauvegarder le fichier
        file.save(filepath)
        
        # Vérifier que le fichier a été sauvegardé correctement
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            current_app.logger.info(f"[UPLOAD_SUCCESS] Fichier sauvegardé: {filepath} ({os.path.getsize(filepath)} bytes)")
            return True
        else:
            current_app.logger.error(f"[UPLOAD_ERROR] Fichier vide ou non sauvegardé: {filepath}")
            # Supprimer le fichier vide s'il existe
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
    except Exception as e:
        current_app.logger.error(f"[UPLOAD_ERROR] Erreur lors de la sauvegarde: {str(e)}")
        return False

def generate_consistent_image_path(filename):
    """Générer un chemin d'image cohérent"""
    return f'/static/uploads/{filename}'
