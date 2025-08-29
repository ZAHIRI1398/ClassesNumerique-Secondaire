import os
import logging
import importlib.util
from flask import current_app
from utils.image_utils_no_normalize import normalize_image_path
from utils.image_path_manager import ImagePathManager

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

def upload_file(file, folder="uploads", exercise_type=None):
    """
    Upload un fichier vers Cloudinary ou en local selon la configuration
    Version améliorée qui vérifie la taille du fichier et évite les fichiers vides
    
    Args:
        file: Objet fichier de Flask (request.files['file'])
        folder: Dossier de destination (ignoré si exercise_type est fourni)
        exercise_type: Type d'exercice pour déterminer le dossier automatiquement
        
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
    
    # DEBUG: Vérifier la taille initiale du fichier
    try:
        file.seek(0, 2)  # Aller à la fin
        file_size = file.tell()  # Obtenir la position (taille)
        file.seek(0)  # Revenir au début
        try:
            current_app.logger.info(f"DEBUG: Taille fichier initial: {file_size} octets")
        except:
            print(f"DEBUG: Taille fichier initial: {file_size} octets")
            
        # IMPORTANT: Vérifier si le fichier est vide et annuler l'upload
        if file_size == 0:
            try:
                current_app.logger.error("ERREUR: Le fichier est vide, upload annulé")
            except:
                print("ERREUR: Le fichier est vide, upload annulé")
            return None
    except Exception as e:
        try:
            current_app.logger.error(f"DEBUG: Erreur lecture taille fichier: {e}")
        except:
            print(f"DEBUG: Erreur lecture taille fichier: {e}")
        
    # Générer un nom de fichier unique avec le nouveau système
    unique_filename = ImagePathManager.generate_unique_filename(file.filename, exercise_type)
    
    try:
        # Si Cloudinary est disponible et n'est pas configuré, essayer de le configurer
        if cloudinary_available and not cloudinary_configured:
            cloudinary_configured = configure_cloudinary()
            
        # Si Cloudinary est disponible et configuré, upload vers Cloudinary
        if cloudinary_available and cloudinary_configured:
            try:
                # CORRECTION: Remettre le pointeur au début avant Cloudinary aussi
                file.seek(0)
                
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
            # SOLUTION ROBUSTE: Lire le contenu du fichier en mémoire puis l'écrire
            file.seek(0)
            file_content = file.read()
            
            try:
                current_app.logger.info(f"DEBUG: Contenu lu en mémoire: {len(file_content)} octets")
            except:
                print(f"DEBUG: Contenu lu en mémoire: {len(file_content)} octets")
            
            if len(file_content) == 0:
                try:
                    current_app.logger.error("ERREUR: Le fichier reçu est vide!")
                except:
                    print("ERREUR: Le fichier reçu est vide!")
                return None
            
            # Utiliser le nouveau système de gestion des dossiers
            if exercise_type:
                local_folder_path = ImagePathManager.get_upload_folder(exercise_type)
                ImagePathManager.ensure_directory_exists(exercise_type)
            else:
                local_folder_path = f"static/uploads/{folder}"
                os.makedirs(local_folder_path, exist_ok=True)
            
            # Écrire le contenu directement sur le disque
            local_path = os.path.join(local_folder_path, unique_filename)
            
            with open(local_path, 'wb') as f:
                f.write(file_content)
            
            try:
                current_app.logger.info(f"DEBUG: Fichier écrit directement: {local_path}")
            except:
                print(f"DEBUG: Fichier écrit directement: {local_path}")
            
            # Vérifier que le fichier a été sauvegardé correctement
            if os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                if file_size == 0:
                    try:
                        current_app.logger.error(f"ERREUR: Fichier sauvegardé avec 0 octets: {local_path}")
                    except:
                        print(f"ERREUR: Fichier sauvegardé avec 0 octets: {local_path}")
                    # CORRECTION: Supprimer le fichier vide
                    os.remove(local_path)
                    return None
                else:
                    try:
                        current_app.logger.info(f"Fichier sauvegardé avec succès: {local_path} ({file_size} octets)")
                    except:
                        print(f"Fichier sauvegardé avec succès: {local_path} ({file_size} octets)")
            else:
                try:
                    current_app.logger.error(f"ERREUR: Fichier non créé: {local_path}")
                except:
                    print(f"ERREUR: Fichier non créé: {local_path}")
                return None
            
            # Générer l'URL relative pour le fichier local
            relative_path = ImagePathManager.get_web_path(unique_filename, exercise_type)
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

def get_cloudinary_url(image_path, exercise_type=None):
    """
    Version corrigée de la fonction get_cloudinary_url
    Retourne une URL valide pour une image, en vérifiant que le fichier existe
    
    Args:
        image_path: Le chemin de l'image
        exercise_type: Le type d'exercice pour organiser les images dans des sous-dossiers
        
    Returns:
        L'URL de l'image
    """
    if not image_path:
        print(f"[WARNING] get_cloudinary_url appelée avec un chemin vide")
        return None
        
    # Vérifier le type de chemin d'image
    if not isinstance(image_path, str):
        print(f"Type de chemin d'image non valide: {type(image_path)}")
        return None
        
    # Log du chemin d'image pour débogage
    try:
        current_app.logger.debug(f"[IMAGE_PATH_DEBUG] Traitement du chemin d'image: {image_path}")
    except Exception:
        print(f"[DEBUG] get_cloudinary_url appelée avec image_path={image_path}")
        print(f"[IMAGE_PATH_DEBUG] Traitement du chemin d'image: {image_path}")
    
    try:
        # RÈGLE 1: Si c'est déjà une URL Cloudinary ou une URL externe, la retourner telle quelle
        if 'cloudinary.com' in image_path or image_path.startswith('http'):
            try:
                current_app.logger.debug(f"[IMAGE_PATH_DEBUG] URL externe ou Cloudinary détectée: {image_path}")
            except Exception:
                print(f"[IMAGE_PATH_DEBUG] URL externe ou Cloudinary détectée: {image_path}")
            return image_path
        
        # RÈGLE 2: Utiliser le nouveau système pour nettoyer les chemins dupliqués
        cleaned_path = ImagePathManager.clean_duplicate_paths(image_path)
        if cleaned_path != image_path:
            try:
                current_app.logger.debug(f"[IMAGE_PATH_DEBUG] Chemin nettoyé: {cleaned_path}")
            except Exception:
                print(f"[IMAGE_PATH_DEBUG] Chemin nettoyé: {cleaned_path}")
            return cleaned_path
            
        # RÈGLE 3: Gestion des chemins commençant par /static/ ou static/
        if image_path.startswith('/static/') or image_path.startswith('static/'):
            normalized_path = normalize_image_path(image_path if image_path.startswith('/') else f"/{image_path}", exercise_type)
            try:
                current_app.logger.debug(f"[IMAGE_PATH_DEBUG] Chemin static normalisé: {normalized_path}")
            except Exception:
                print(f"[IMAGE_PATH_DEBUG] Chemin static normalisé: {normalized_path}")
            return normalized_path
        
        # RÈGLE 4: Pour les noms de fichiers simples, utiliser le système de gestion
        filename = ImagePathManager.extract_filename_from_path(image_path)
        if filename:
            web_path = ImagePathManager.get_web_path(filename, exercise_type)
            try:
                current_app.logger.debug(f"[IMAGE_PATH_DEBUG] Chemin web généré: {web_path}")
            except Exception:
                print(f"[IMAGE_PATH_DEBUG] Chemin web généré: {web_path}")
            return web_path
        
        # Si aucune règle ne s'applique, retourner le chemin tel quel
        return image_path
        
    except Exception as e:
        # En cas d'erreur, logger et essayer de retourner un chemin utilisable
        try:
            current_app.logger.error(f"[IMAGE_PATH_ERROR] Erreur lors de la génération d'URL: {str(e)}")
        except Exception:
            print(f"[IMAGE_PATH_ERROR] Erreur lors de la génération d'URL: {str(e)}")
            
        # Tentative de récupération en cas d'erreur
        if image_path and isinstance(image_path, str):
            # Si c'est une URL externe ou Cloudinary, la retourner telle quelle
            if 'cloudinary.com' in image_path or image_path.startswith('http'):
                return image_path
                
            # Pour les autres cas, utiliser le système de gestion d'images
            try:
                filename = ImagePathManager.extract_filename_from_path(image_path)
                return ImagePathManager.get_web_path(filename, exercise_type) if filename else image_path
            except Exception:
                return image_path
        
        return image_path
