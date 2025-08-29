"""
Module amélioré pour corriger le problème d'upload d'images vides
"""

import os
import logging
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import shutil

def safe_file_upload(file, folder="uploads", exercise_type=None):
    """
    Version améliorée de la fonction d'upload qui vérifie la taille du fichier
    et assure qu'aucun fichier vide n'est sauvegardé
    
    Args:
        file: Objet fichier de Flask (request.files['file'])
        folder: Dossier de destination
        exercise_type: Type d'exercice pour déterminer le sous-dossier
        
    Returns:
        str: Chemin du fichier uploadé ou None en cas d'échec
    """
    if not file:
        try:
            current_app.logger.error("Aucun fichier fourni pour l'upload")
        except:
            print("Aucun fichier fourni pour l'upload")
        return None
    
    try:
        # 1. Vérifier la taille du fichier avant de commencer
        file.seek(0, 2)  # Aller à la fin
        file_size = file.tell()  # Obtenir la position (taille)
        file.seek(0)  # Revenir au début
        
        try:
            current_app.logger.info(f"Taille du fichier à uploader: {file_size} octets")
        except:
            print(f"Taille du fichier à uploader: {file_size} octets")
            
        if file_size == 0:
            try:
                current_app.logger.error("ERREUR: Le fichier est vide, upload annulé")
            except:
                print("ERREUR: Le fichier est vide, upload annulé")
            return None
        
        # 2. Générer un nom de fichier unique
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:6]
        
        # Ajouter le type d'exercice au nom si fourni
        if exercise_type:
            filename = f"{exercise_type}_{timestamp}_{unique_id}_{original_filename}"
            # Créer le sous-dossier pour le type d'exercice
            subfolder = f"static/uploads/exercises/{exercise_type}"
        else:
            filename = f"{timestamp}_{unique_id}_{original_filename}"
            subfolder = f"static/uploads/{folder}"
        
        # 3. Créer le dossier s'il n'existe pas
        os.makedirs(subfolder, exist_ok=True)
        
        # 4. Chemin complet du fichier
        filepath = os.path.join(subfolder, filename)
        
        # 5. Lire le contenu en mémoire
        file_content = file.read()
        
        if len(file_content) == 0:
            try:
                current_app.logger.error("ERREUR: Contenu du fichier vide après lecture")
            except:
                print("ERREUR: Contenu du fichier vide après lecture")
            return None
        
        # 6. Écrire le contenu sur le disque
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        # 7. Vérifier que le fichier a été correctement sauvegardé
        if os.path.exists(filepath):
            saved_size = os.path.getsize(filepath)
            if saved_size == 0:
                try:
                    current_app.logger.error(f"ERREUR: Fichier sauvegardé avec 0 octet: {filepath}")
                except:
                    print(f"ERREUR: Fichier sauvegardé avec 0 octet: {filepath}")
                # Supprimer le fichier vide
                os.remove(filepath)
                return None
            else:
                try:
                    current_app.logger.info(f"Fichier sauvegardé avec succès: {filepath} ({saved_size} octets)")
                except:
                    print(f"Fichier sauvegardé avec succès: {filepath} ({saved_size} octets)")
        else:
            try:
                current_app.logger.error(f"ERREUR: Fichier non créé: {filepath}")
            except:
                print(f"ERREUR: Fichier non créé: {filepath}")
            return None
        
        # 8. Retourner le chemin web pour l'affichage
        web_path = f"/{subfolder}/{filename}"
        return web_path
        
    except Exception as e:
        try:
            current_app.logger.error(f"Erreur lors de l'upload: {str(e)}")
        except:
            print(f"Erreur lors de l'upload: {str(e)}")
        return None

def fix_cloud_storage_module():
    """
    Fonction pour intégrer la correction dans le module cloud_storage.py
    """
    try:
        # Chemin du module cloud_storage.py
        module_path = "cloud_storage.py"
        
        # Sauvegarder une copie de sauvegarde
        backup_path = f"cloud_storage.py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(module_path, backup_path)
        print(f"Sauvegarde créée: {backup_path}")
        
        # Lire le contenu actuel
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer la fonction upload_file par notre version améliorée
        if "def upload_file(" in content:
            # Trouver le début et la fin de la fonction
            start = content.find("def upload_file(")
            end = content.find("def ", start + 1)
            if end == -1:  # Si c'est la dernière fonction
                end = len(content)
            
            # Remplacer la fonction
            new_content = content[:start] + """def upload_file(file, folder="uploads", exercise_type=None):
    \"\"\"
    Upload un fichier vers Cloudinary ou en local selon la configuration
    Version améliorée qui vérifie la taille du fichier et évite les fichiers vides
    
    Args:
        file: Objet fichier de Flask (request.files['file'])
        folder: Dossier de destination (ignoré si exercise_type est fourni)
        exercise_type: Type d'exercice pour déterminer le dossier automatiquement
        
    Returns:
        str: URL du fichier uploadé (Cloudinary ou local)
    \"\"\"
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
        return None""" + content[end:]
            
            # Sauvegarder le fichier modifié
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Module {module_path} mis à jour avec succès!")
            return True
        else:
            print(f"Fonction upload_file non trouvée dans {module_path}")
            return False
    except Exception as e:
        print(f"Erreur lors de la mise à jour du module: {e}")
        return False

if __name__ == "__main__":
    # Créer une fonction d'upload sécurisée
    print("=== CORRECTION DU PROBLÈME D'UPLOAD D'IMAGES VIDES ===")
    
    # Appliquer la correction au module cloud_storage.py
    if fix_cloud_storage_module():
        print("\nLe module cloud_storage.py a été mis à jour avec succès!")
        print("La nouvelle version vérifie la taille des fichiers et évite les fichiers vides.")
    else:
        print("\nLa mise à jour automatique a échoué.")
        print("Veuillez intégrer manuellement la fonction safe_file_upload dans votre code.")
    
    print("\n=== INSTRUCTIONS SUPPLÉMENTAIRES ===")
    print("1. Redémarrez l'application Flask pour appliquer les changements")
    print("2. Testez l'upload d'images pour vérifier que les fichiers vides ne sont plus créés")
    print("3. Si des problèmes persistent, utilisez la fonction safe_file_upload directement")
