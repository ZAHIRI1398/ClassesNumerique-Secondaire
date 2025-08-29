"""
Module de gestion du stockage cloud pour les images
Version corrigée avec une fonction get_cloudinary_url améliorée
"""

import os
import logging
from flask import current_app
from utils.image_path_manager import ImagePathManager
from utils.image_utils_no_normalize import normalize_image_path

def get_cloudinary_url(image_path):
    """
    Version corrigée de la fonction get_cloudinary_url
    Retourne une URL valide pour une image, en vérifiant que le fichier existe
    
    Args:
        image_path: Le chemin de l'image
        
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
    
    print(f"[DEBUG] get_cloudinary_url appelée avec image_path={image_path}")
    
    # Si c'est déjà une URL Cloudinary ou une URL externe, la retourner telle quelle
    if 'cloudinary.com' in image_path or image_path.startswith('http'):
        print(f"[DEBUG] URL externe détectée: {image_path}")
        return image_path
    
    # Nettoyer les chemins dupliqués
    cleaned_path = ImagePathManager.clean_duplicate_paths(image_path)
    if cleaned_path != image_path:
        print(f"[DEBUG] Chemin nettoyé: {cleaned_path} (original: {image_path})")
        image_path = cleaned_path
    
    # Extraire le nom de fichier
    filename = os.path.basename(image_path)
    print(f"[DEBUG] Nom de fichier extrait: {filename}")
    
    # Vérifier si le fichier existe directement avec ce chemin
    direct_path = image_path
    if direct_path.startswith('/'):
        direct_path = direct_path[1:]
    direct_exists = os.path.exists(direct_path)
    print(f"[DEBUG] Le fichier existe directement: {direct_exists}")
    
    # Si le chemin commence par /static/ ou static/, normaliser et retourner
    if image_path.startswith('/static/') or image_path.startswith('static/'):
        normalized_path = normalize_image_path(image_path if image_path.startswith('/') else f"/{image_path}")
        
        # Vérifier si le fichier existe avec ce chemin normalisé
        normalized_exists = os.path.exists(normalized_path[1:] if normalized_path.startswith('/') else normalized_path)
        print(f"[DEBUG] Le fichier existe avec le chemin normalisé: {normalized_exists}")
        
        if normalized_exists:
            # Remplacer les backslashes par des slashes pour la cohérence des URLs
            normalized_path = normalized_path.replace('\\', '/')
            print(f"[DEBUG] Retour du chemin normalisé: {normalized_path}")
            return normalized_path
    
    # Vérifier les chemins possibles
    possible_paths = [
        os.path.join("static", "uploads", filename),
        os.path.join("static", "uploads", "flashcards", filename),
        os.path.join("static", "uploads", "general", filename),
        os.path.join("static", "exercises", "flashcards", filename),
        os.path.join("static", "exercises", filename),
        os.path.join("static", "exercises", "general", filename)
    ]
    
    # Chercher le fichier dans les chemins possibles
    for path in possible_paths:
        if os.path.exists(path):
            # Remplacer les backslashes par des slashes pour la cohérence des URLs
            web_path = f"/{path.replace('\\', '/')}"  
            print(f"[DEBUG] Fichier trouvé à: {path}, URL retournée: {web_path}")
            return web_path
    
    # Si le chemin commence par "uploads/", essayer avec "/static/uploads/"
    if image_path.startswith('uploads/'):
        corrected_path = f"/static/{image_path}"
        corrected_path = corrected_path.replace('\\', '/')
        print(f"[DEBUG] Correction du chemin uploads/: {corrected_path}")
        
        # Vérifier si le fichier existe avec ce chemin corrigé
        corrected_exists = os.path.exists(corrected_path[1:] if corrected_path.startswith('/') else corrected_path)
        if corrected_exists:
            print(f"[DEBUG] Le fichier existe avec le chemin corrigé: {corrected_exists}")
            return corrected_path
    
    # Dernier recours: essayer de construire un chemin web avec ImagePathManager
    try:
        web_path = ImagePathManager.get_web_path(image_path)
        web_path = web_path.replace('\\', '/')
        print(f"[DEBUG] Chemin web généré par ImagePathManager: {web_path}")
        
        # Vérifier si le fichier existe avec ce chemin web
        web_exists = os.path.exists(web_path[1:] if web_path.startswith('/') else web_path)
        if web_exists:
            print(f"[DEBUG] Le fichier existe avec le chemin web: {web_exists}")
            return web_path
    except Exception as e:
        print(f"[ERROR] Erreur lors de la génération du chemin web: {str(e)}")
    
    # Si aucun fichier n'a été trouvé, retourner le chemin original avec /static/ préfixé si nécessaire
    if not image_path.startswith('/'):
        if not image_path.startswith('static/'):
            final_path = f"/static/uploads/{filename}"
        else:
            final_path = f"/{image_path}"
    else:
        final_path = image_path
    
    final_path = final_path.replace('\\', '/')
    print(f"[WARNING] Aucun fichier trouvé, retour du chemin par défaut: {final_path}")
    return final_path
