import os
import logging
from flask import current_app

# Configuration de Cloudinary avec gestion d'erreurs robuste
def configure_cloudinary():
    """Configure Cloudinary avec les variables d'environnement"""
    try:
        # Import conditionnel pour éviter les erreurs si le module n'est pas disponible
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        
        # Vérifier que toutes les variables d'environnement nécessaires sont présentes
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        api_key = os.environ.get('CLOUDINARY_API_KEY')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET')
        
        if not all([cloud_name, api_key, api_secret]):
            current_app.logger.warning("Variables d'environnement Cloudinary manquantes. Utilisation du stockage local.")
            return False
            
        # Configuration de Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        current_app.logger.info("Cloudinary configuré avec succès")
        return True
    except ImportError:
        current_app.logger.warning("Module cloudinary non disponible. Utilisation du stockage local.")
        return False
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la configuration de Cloudinary: {str(e)}")
        return False

# Variable globale pour suivre l'état de configuration de Cloudinary
cloudinary_configured = False

def upload_file(file, folder="uploads"):
    """
    Upload un fichier vers Cloudinary ou en local selon la configuration
    
    Args:
        file: Objet fichier de Flask (request.files['file'])
        folder: Dossier de destination sur Cloudinary
        
    Returns:
        URL publique de l'image uploadée
    """
    global cloudinary_configured
    
    # Fonction pour sauvegarder localement
    def save_locally():
        try:
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            # Générer un nom unique
            import time
            timestamp = str(int(time.time()))
            unique_filename = f"{timestamp}_{filename}"
            
            # Sauvegarder localement
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            current_app.logger.info(f"Fichier sauvegardé localement: {unique_filename}")
            return f"static/uploads/{unique_filename}"
        except Exception as local_error:
            current_app.logger.error(f"Erreur lors de la sauvegarde locale: {str(local_error)}")
            return None
    
    try:
        # Vérifier si Cloudinary est configuré
        if not cloudinary_configured and os.environ.get('CLOUDINARY_CLOUD_NAME'):
            # Tenter de configurer Cloudinary si ce n'est pas déjà fait
            cloudinary_configured = configure_cloudinary()
        
        # Si Cloudinary n'est pas configuré, utiliser le stockage local
        if not cloudinary_configured:
            current_app.logger.info("Cloudinary non configuré, utilisation du stockage local")
            return save_locally()
        
        # En production avec Cloudinary configuré
        try:
            import cloudinary.uploader
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                resource_type="auto"
            )
            current_app.logger.info(f"Fichier uploadé sur Cloudinary: {result['secure_url']}")
            return result['secure_url']
        except Exception as cloud_error:
            current_app.logger.error(f"Erreur lors de l'upload sur Cloudinary: {str(cloud_error)}")
            # En cas d'erreur avec Cloudinary, fallback sur stockage local
            return save_locally()
    except Exception as e:
        current_app.logger.error(f"Erreur générale lors de l'upload: {str(e)}")
        # Tentative de sauvegarde locale en dernier recours
        return save_locally()

def delete_file(public_id):
    """
    Supprime un fichier de Cloudinary ou en local selon la configuration
    
    Args:
        public_id: ID public du fichier sur Cloudinary ou chemin local
        
    Returns:
        True si supprimé avec succès, False sinon
    """
    global cloudinary_configured
    
    # Fonction pour supprimer localement
    def delete_locally(path):
        try:
            # Si l'URL est locale, extraire le chemin du fichier
            if path.startswith('static/uploads/'):
                filepath = os.path.join(current_app.root_path, path)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    current_app.logger.info(f"Fichier supprimé localement: {path}")
                    return True
                else:
                    current_app.logger.warning(f"Fichier local introuvable: {path}")
            return False
        except Exception as local_error:
            current_app.logger.error(f"Erreur lors de la suppression locale: {str(local_error)}")
            return False
    
    try:
        # Vérifier si c'est une URL Cloudinary
        is_cloudinary_url = public_id and ('cloudinary.com' in public_id or not public_id.startswith('static/'))
        
        # Vérifier si Cloudinary est configuré
        if not cloudinary_configured and os.environ.get('CLOUDINARY_CLOUD_NAME'):
            # Tenter de configurer Cloudinary si ce n'est pas déjà fait
            cloudinary_configured = configure_cloudinary()
        
        # Si c'est une URL Cloudinary et que Cloudinary est configuré
        if is_cloudinary_url and cloudinary_configured:
            try:
                import cloudinary.uploader
                # Extraire l'ID public de l'URL Cloudinary si nécessaire
                if 'cloudinary.com' in public_id:
                    # Format: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/folder/file.jpg
                    parts = public_id.split('upload/')
                    if len(parts) > 1:
                        public_id = parts[1].split('/', 1)[1] if '/' in parts[1] else parts[1]
                
                result = cloudinary.uploader.destroy(public_id)
                success = result.get('result') == 'ok'
                if success:
                    current_app.logger.info(f"Fichier supprimé de Cloudinary: {public_id}")
                else:
                    current_app.logger.warning(f"Échec de suppression sur Cloudinary: {public_id}")
                return success
            except Exception as cloud_error:
                current_app.logger.error(f"Erreur lors de la suppression sur Cloudinary: {str(cloud_error)}")
                return False
        else:
            # Suppression locale
            current_app.logger.info(f"Suppression locale du fichier: {public_id}")
            return delete_locally(public_id)
    except Exception as e:
        current_app.logger.error(f"Erreur générale lors de la suppression: {str(e)}")
        return False

def get_cloudinary_url(image_path):
    """
    Convertit un chemin d'image en URL Cloudinary ou locale selon le contexte
    
    Args:
        image_path: Chemin de l'image (peut être une URL Cloudinary ou un chemin local)
        
    Returns:
        URL de l'image (Cloudinary ou locale)
    """
    try:
        # Si le chemin est None ou vide, retourner None
        if not image_path:
            return None
            
        # Si c'est déjà une URL Cloudinary ou une URL externe, la retourner telle quelle
        if 'cloudinary.com' in image_path or image_path.startswith('http'):
            return image_path
            
        # Construire l'URL locale selon le format du chemin
        if image_path.startswith('static/'):
            return f"/{image_path}"
        elif '/' in image_path:
            # Extraire juste le nom du fichier si c'est un chemin complet
            return f"/static/uploads/{image_path.split('/')[-1]}"
        else:
            # Si c'est juste un nom de fichier
            return f"/static/uploads/{image_path}"
    except Exception as e:
        # En cas d'erreur, logger et retourner None
        try:
            current_app.logger.error(f"Erreur lors de la génération d'URL: {str(e)}")
        except:
            # Si current_app n'est pas disponible (hors contexte Flask)
            pass
        return None
