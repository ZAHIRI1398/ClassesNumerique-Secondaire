import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import current_app

# Configuration de Cloudinary
def configure_cloudinary():
    """Configure Cloudinary avec les variables d'environnement"""
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        secure=True
    )
    current_app.logger.info("Cloudinary configuré avec succès")

def upload_file(file, folder="uploads"):
    """
    Upload un fichier vers Cloudinary
    
    Args:
        file: Objet fichier de Flask (request.files['file'])
        folder: Dossier de destination sur Cloudinary
        
    Returns:
        URL publique de l'image uploadée
    """
    try:
        # Vérifier que Cloudinary est configuré
        if not os.environ.get('CLOUDINARY_CLOUD_NAME'):
            # En développement, utiliser le stockage local
            current_app.logger.info("Cloudinary non configuré, utilisation du stockage local")
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            # Générer un nom unique
            import time
            timestamp = str(int(time.time()))
            unique_filename = f"{timestamp}_{filename}"
            
            # Sauvegarder localement
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            return f"static/uploads/{unique_filename}"
        
        # En production, utiliser Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto"
        )
        current_app.logger.info(f"Fichier uploadé sur Cloudinary: {result['secure_url']}")
        return result['secure_url']
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'upload sur Cloudinary: {str(e)}")
        # En cas d'erreur, essayer de sauvegarder localement
        try:
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            import time
            timestamp = str(int(time.time()))
            unique_filename = f"{timestamp}_{filename}"
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            return f"static/uploads/{unique_filename}"
        except Exception as local_error:
            current_app.logger.error(f"Erreur lors de la sauvegarde locale: {str(local_error)}")
            return None

def delete_file(public_id):
    """
    Supprime un fichier de Cloudinary
    
    Args:
        public_id: ID public du fichier sur Cloudinary
        
    Returns:
        True si supprimé avec succès, False sinon
    """
    try:
        # Vérifier que Cloudinary est configuré
        if not os.environ.get('CLOUDINARY_CLOUD_NAME'):
            # En développement, supprimer le fichier local
            current_app.logger.info(f"Cloudinary non configuré, suppression locale de {public_id}")
            # Si l'URL est locale, extraire le chemin du fichier
            if public_id.startswith('static/uploads/'):
                filepath = os.path.join(current_app.root_path, public_id)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    return True
            return False
            
        # En production, supprimer de Cloudinary
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la suppression sur Cloudinary: {str(e)}")
        return False

def get_cloudinary_url(image_path):
    """
    Convertit un chemin d'image en URL Cloudinary si nécessaire
    
    Args:
        image_path: Chemin de l'image (peut être une URL Cloudinary ou un chemin local)
        
    Returns:
        URL de l'image (Cloudinary ou locale)
    """
    # Si c'est déjà une URL Cloudinary, la retourner telle quelle
    if image_path and ('cloudinary.com' in image_path or image_path.startswith('http')):
        return image_path
        
    # Sinon, construire l'URL locale
    if image_path and image_path.startswith('static/'):
        return f"/{image_path}"
    elif image_path:
        return f"/static/uploads/{image_path.split('/')[-1]}"
    
    return None
