import os
import logging
import importlib.util
from flask import current_app

# Vérifier si le module cloudinary est disponible sans l'importer directement
cloudinary_available = importlib.util.find_spec("cloudinary") is not None

# Variable globale pour suivre l'état de configuration de Cloudinary
cloudinary_configured = False

# Configuration de Cloudinary avec gestion d'erreurs robuste
def configure_cloudinary():
    """Configure Cloudinary avec les variables d'environnement"""
    global cloudinary_available, cloudinary_configured
    
    # Si le module n'est pas disponible, sortir immédiatement
    if not cloudinary_available:
        try:
            current_app.logger.warning("Module cloudinary non disponible. Utilisation du stockage local.")
        except:
            # En cas d'erreur avec current_app (hors contexte Flask)
            print("Module cloudinary non disponible. Utilisation du stockage local.")
        return False
        
    try:
        # Import conditionnel maintenant qu'on sait que le module est disponible
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        
        # Vérifier que toutes les variables d'environnement nécessaires sont présentes
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        api_key = os.environ.get('CLOUDINARY_API_KEY')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET')
        
        if not all([cloud_name, api_key, api_secret]):
            try:
                current_app.logger.warning("Variables d'environnement Cloudinary manquantes. Utilisation du stockage local.")
            except:
                print("Variables d'environnement Cloudinary manquantes. Utilisation du stockage local.")
            return False
            
        # Configuration de Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        try:
            current_app.logger.info("Cloudinary configuré avec succès")
        except:
            print("Cloudinary configuré avec succès")
        cloudinary_configured = True
        return True
    except Exception as e:
        try:
            current_app.logger.error(f"Erreur lors de la configuration de Cloudinary: {str(e)}")
        except:
            print(f"Erreur lors de la configuration de Cloudinary: {str(e)}")
        return False

def upload_file(file, folder="uploads"):
    """
    Upload un fichier vers Cloudinary ou en local selon la configuration
    
    Args:
        file: Objet fichier de Flask (request.files['file'])
        folder: Dossier de destination sur Cloudinary
        
    Returns:
        str: URL du fichier uploadé (Cloudinary ou local)
    """
    global cloudinary_configured, cloudinary_available
    
    if not file:
        try:
            current_app.logger.error("Aucun fichier fourni pour l'upload")
        except:
            print("Aucun fichier fourni pour l'upload")
        return None
        
    # Générer un nom de fichier unique pour éviter les collisions
    import uuid
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{uuid.uuid4().hex}_{file.filename}"
    
    try:
        # Si Cloudinary est disponible et n'est pas configuré, essayer de le configurer
        if cloudinary_available and not cloudinary_configured:
            cloudinary_configured = configure_cloudinary()
            
        # Si Cloudinary est disponible et configuré, upload vers Cloudinary
        if cloudinary_available and cloudinary_configured:
            try:
                # Import conditionnel de cloudinary
                import cloudinary.uploader
                
                # Upload vers Cloudinary
                result = cloudinary.uploader.upload(
                    file,
                    public_id=f"{folder}/{unique_filename}",
                    overwrite=True,
                    resource_type="auto"
                )
                try:
                    current_app.logger.info(f"Fichier uploadé vers Cloudinary: {result['secure_url']}")
                except:
                    print(f"Fichier uploadé vers Cloudinary: {result['secure_url']}")
                return result['secure_url']
            except Exception as e:
                try:
                    current_app.logger.error(f"Erreur lors de l'upload vers Cloudinary: {str(e)}")
                except:
                    print(f"Erreur lors de l'upload vers Cloudinary: {str(e)}")
                # Fallback vers stockage local en cas d'erreur
        
        # Stockage local si Cloudinary n'est pas disponible ou a échoué
        try:
            # Créer le dossier s'il n'existe pas
            local_folder = os.path.join(current_app.static_folder, folder)
            os.makedirs(local_folder, exist_ok=True)
            
            # Sauvegarder le fichier localement
            local_path = os.path.join(local_folder, unique_filename)
            file.save(local_path)
            
            # Générer l'URL relative pour le fichier local
            relative_path = f"{folder}/{unique_filename}"
            try:
                current_app.logger.info(f"Fichier sauvegardé localement: {relative_path}")
            except:
                print(f"Fichier sauvegardé localement: {relative_path}")
            
            return relative_path
        except Exception as e:
            try:
                current_app.logger.error(f"Erreur lors de la sauvegarde locale: {str(e)}")
            except:
                print(f"Erreur lors de la sauvegarde locale: {str(e)}")
            return None
    except Exception as e:
        try:
            current_app.logger.error(f"Erreur lors de l'upload du fichier: {str(e)}")
        except:
            print(f"Erreur lors de l'upload du fichier: {str(e)}")
        return None

def delete_file(public_id):
    """
    Supprime un fichier de Cloudinary ou en local selon la configuration
    
    Args:
        public_id: ID public du fichier sur Cloudinary ou chemin local
        
    Returns:
        True si supprimé avec succès, False sinon
    """
    global cloudinary_configured, cloudinary_available
    
    # Fonction pour supprimer localement
    def delete_locally(path):
        try:
            # Si l'URL est locale, extraire le chemin du fichier
            if path.startswith('static/uploads/'):
                filepath = os.path.join(current_app.root_path, path)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    try:
                        current_app.logger.info(f"Fichier supprimé localement: {path}")
                    except:
                        print(f"Fichier supprimé localement: {path}")
                    return True
                else:
                    try:
                        current_app.logger.warning(f"Fichier local introuvable: {path}")
                    except:
                        print(f"Fichier local introuvable: {path}")
            return False
        except Exception as local_error:
            try:
                current_app.logger.error(f"Erreur lors de la suppression locale: {str(local_error)}")
            except:
                print(f"Erreur lors de la suppression locale: {str(local_error)}")
            return False
    
    try:
        # Vérifier si c'est une URL Cloudinary
        is_cloudinary_url = public_id and ('cloudinary.com' in public_id or not public_id.startswith('static/'))
        
        # Vérifier si Cloudinary est disponible et configuré
        if cloudinary_available and not cloudinary_configured and os.environ.get('CLOUDINARY_CLOUD_NAME'):
            # Tenter de configurer Cloudinary si ce n'est pas déjà fait
            cloudinary_configured = configure_cloudinary()
        
        # Si c'est une URL Cloudinary et que Cloudinary est disponible et configuré
        if is_cloudinary_url and cloudinary_available and cloudinary_configured:
            try:
                # Import conditionnel
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
                    try:
                        current_app.logger.info(f"Fichier supprimé de Cloudinary: {public_id}")
                    except:
                        print(f"Fichier supprimé de Cloudinary: {public_id}")
                else:
                    try:
                        current_app.logger.warning(f"Échec de suppression sur Cloudinary: {public_id}")
                    except:
                        print(f"Échec de suppression sur Cloudinary: {public_id}")
                return success
            except Exception as cloud_error:
                try:
                    current_app.logger.error(f"Erreur lors de la suppression sur Cloudinary: {str(cloud_error)}")
                except:
                    print(f"Erreur lors de la suppression sur Cloudinary: {str(cloud_error)}")
                return False
        else:
            # Suppression locale
            try:
                current_app.logger.info(f"Suppression locale du fichier: {public_id}")
            except:
                print(f"Suppression locale du fichier: {public_id}")
            return delete_locally(public_id)
    except Exception as e:
        try:
            current_app.logger.error(f"Erreur générale lors de la suppression: {str(e)}")
        except:
            print(f"Erreur générale lors de la suppression: {str(e)}")
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
        if 'cloudinary.com' in str(image_path) or str(image_path).startswith('http'):
            return image_path
            
        # Gérer le cas où image_path est un objet et pas une chaîne
        if not isinstance(image_path, str):
            try:
                image_path = str(image_path)
                try:
                    current_app.logger.info(f"Conversion du chemin d'image en chaîne: {image_path}")
                except:
                    print(f"Conversion du chemin d'image en chaîne: {image_path}")
            except:
                try:
                    current_app.logger.error(f"Type de chemin d'image non valide: {type(image_path)}")
                except:
                    print(f"Type de chemin d'image non valide: {type(image_path)}")
                return None
        
        # Log du chemin d'image pour débogage
        try:
            current_app.logger.debug(f"Traitement du chemin d'image: {image_path}")
        except:
            print(f"Traitement du chemin d'image: {image_path}")
        
        # Cas spécifique pour static/uploads qui doit être préservé tel quel
        if image_path.startswith('static/uploads/'):
            try:
                current_app.logger.debug(f"Chemin static/uploads détecté: {image_path}")
            except:
                print(f"Chemin static/uploads détecté: {image_path}")
            return f"/{image_path}"
            
        # Construire l'URL locale selon le format du chemin
        if image_path.startswith('static/'):
            return f"/{image_path}"
        elif image_path.startswith('/static/'):
            return image_path  # Déjà au bon format
        elif image_path.startswith('uploads/'):
            return f"/static/{image_path}"
        elif '/' in image_path:
            # Si c'est un chemin avec des dossiers
            if 'uploads' in image_path:
                parts = image_path.split('uploads/')
                if len(parts) > 1:
                    return f"/static/uploads/{parts[1]}"
                else:
                    return f"/static/uploads/{image_path.split('/')[-1]}"
            else:
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
            print(f"Erreur lors de la génération d'URL: {str(e)}")
        # En cas d'erreur, essayer de retourner le chemin original
        if image_path:
            if isinstance(image_path, str):
                # Si le chemin commence déjà par static/uploads, le préserver
                if 'static/uploads' in image_path:
                    if not image_path.startswith('/'):
                        return f"/{image_path}"
                    return image_path
                # Sinon, ajouter le préfixe standard
                elif not image_path.startswith('/'):
                    return f"/static/uploads/{image_path}"
            return image_path
        return None
