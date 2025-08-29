"""
Script pour corriger l'affichage des images dans l'interface d'édition d'exercice
"""

import os
import logging
import json
import shutil
import re

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('fix_image_display_edit.log'), 
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

def normalize_filename(filename):
    """
    Normalise un nom de fichier en remplaçant les caractères spéciaux
    comme le fait l'application lors de l'enregistrement en base de données
    """
    if not filename:
        return filename
        
    # Remplacer les apostrophes et espaces par des underscores
    normalized = filename.replace("'", "_").replace(" ", "_")
    
    # Remplacer les caractères accentués
    normalized = normalized.replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e")
    normalized = normalized.replace("à", "a").replace("â", "a").replace("ä", "a")
    normalized = normalized.replace("î", "i").replace("ï", "i")
    normalized = normalized.replace("ô", "o").replace("ö", "o")
    normalized = normalized.replace("ù", "u").replace("û", "u").replace("ü", "u")
    normalized = normalized.replace("ç", "c")
    
    # Remplacer d'autres caractères spéciaux
    normalized = re.sub(r'[^a-zA-Z0-9_.-]', '_', normalized)
    
    return normalized

def normalize_image_path(path):
    """
    Normalise un chemin d'image
    """
    if not path:
        return path
    
    # Remplacer les backslashes par des slashes
    path = path.replace('\\', '/')
    
    # Ajouter le préfixe /static/ si nécessaire
    if not path.startswith('/'):
        if path.startswith('static/'):
            path = f"/{path}"
        elif path.startswith('uploads/'):
            path = f"/static/{path}"
        else:
            # Extraire le nom du fichier
            filename = os.path.basename(path)
            path = f"/static/uploads/{filename}"
    
    # Nettoyer les chemins dupliqués
    duplicates = [
        ('/static/uploads/static/uploads/', '/static/uploads/'),
        ('static/uploads/static/uploads/', '/static/uploads/'),
        ('/static/exercises/static/exercises/', '/static/exercises/'),
        ('static/exercises/static/exercises/', '/static/exercises/'),
        ('/static/uploads/uploads/', '/static/uploads/'),
        ('static/uploads/uploads/', '/static/uploads/'),
        ('/static/exercises/exercises/', '/static/exercises/'),
        ('static/exercises/exercises/', '/static/exercises/')
    ]
    
    for duplicate, replacement in duplicates:
        if duplicate in path:
            path = path.replace(duplicate, replacement)
    
    return path

def check_image_file_exists(path):
    """
    Vérifie si un fichier image existe
    """
    if not path:
        return False
    
    # Enlever le préfixe /
    if path.startswith('/'):
        path = path[1:]
    
    return os.path.exists(path)

def find_image_file(path):
    """
    Cherche un fichier image dans différents répertoires
    """
    if not path:
        return None
    
    # Extraire le nom du fichier
    filename = os.path.basename(path)
    
    # Essayer avec le nom normalisé également
    normalized_filename = normalize_filename(filename)
    
    # Chemins possibles
    possible_paths = [
        os.path.join("static", "uploads", filename),
        os.path.join("static", "uploads", "exercices", filename),
        os.path.join("static", "uploads", "exercices", "qcm", filename),
        os.path.join("static", "uploads", "exercices", "flashcards", filename),
        os.path.join("static", "uploads", "exercices", "word_placement", filename),
        os.path.join("static", "uploads", "exercices", "image_labeling", filename),
        os.path.join("static", "uploads", "exercices", "legend", filename),
        os.path.join("static", "exercises", filename),
        os.path.join("static", "exercises", "qcm", filename),
        os.path.join("static", "exercises", "flashcards", filename),
        os.path.join("static", "exercises", "word_placement", filename),
        os.path.join("static", "exercises", "image_labeling", filename),
        os.path.join("static", "exercises", "legend", filename)
    ]
    
    # Chercher le fichier avec le nom original
    for possible_path in possible_paths:
        if os.path.exists(possible_path):
            # Normaliser le chemin pour le web
            return f"/{possible_path.replace('\\', '/')}"
    
    # Si non trouvé, essayer avec le nom normalisé
    normalized_possible_paths = [
        p.replace(filename, normalized_filename) for p in possible_paths
    ]
    
    # Chercher le fichier avec le nom normalisé
    for possible_path in normalized_possible_paths:
        if os.path.exists(possible_path):
            # Normaliser le chemin pour le web
            return f"/{possible_path.replace('\\', '/')}"
    
    # Essayer également avec le chemin original mais nom de fichier normalisé
    dir_path = os.path.dirname(path)
    if dir_path:
        normalized_path = os.path.join(dir_path, normalized_filename).replace('\\', '/')
        if normalized_path.startswith('/'):
            normalized_path = normalized_path[1:]
        if os.path.exists(normalized_path):
            return f"/{normalized_path}"
    
    return None

def enhance_get_cloudinary_url():
    """
    Améliore la fonction get_cloudinary_url pour mieux gérer les chemins d'images
    """
    from image_url_service import ImageUrlService
    
    # Sauvegarder l'ancienne méthode
    original_get_image_url = ImageUrlService.get_image_url
    
    def enhanced_get_image_url(image_path):
        """
        Version améliorée de get_image_url qui vérifie plus de chemins possibles
        et gère les problèmes de caractères spéciaux dans les noms de fichiers
        """
        logger = logging.getLogger('enhanced_image_url_service')
        
        if not image_path:
            logger.warning("get_image_url appelée avec un chemin vide")
            return None
        
        # Vérifier le type de chemin d'image
        if not isinstance(image_path, str):
            logger.warning(f"Type de chemin d'image non valide: {type(image_path)}")
            return None
        
        logger.debug(f"get_image_url appelée avec image_path={image_path}")
        
        # Si c'est déjà une URL externe, la retourner telle quelle
        if image_path.startswith('http'):
            logger.debug(f"URL externe détectée: {image_path}")
            return image_path
        
        # Normaliser le chemin
        normalized_path = normalize_image_path(image_path)
        if normalized_path != image_path:
            logger.debug(f"Chemin normalisé: {normalized_path} (original: {image_path})")
        
        # Extraire le nom du fichier et le normaliser
        filename = os.path.basename(normalized_path)
        normalized_filename = normalize_filename(filename)
        if normalized_filename != filename:
            logger.debug(f"Nom de fichier normalisé: {normalized_filename} (original: {filename})")
            # Remplacer le nom de fichier dans le chemin
            normalized_path_with_normalized_filename = normalized_path.replace(filename, normalized_filename)
            logger.debug(f"Chemin avec nom de fichier normalisé: {normalized_path_with_normalized_filename}")
        else:
            normalized_path_with_normalized_filename = normalized_path
        
        # Vérifier si le fichier existe avec ce chemin normalisé
        file_path = normalized_path[1:] if normalized_path.startswith('/') else normalized_path
        if os.path.exists(file_path):
            logger.debug(f"Fichier trouvé avec le chemin normalisé: {normalized_path}")
            return normalized_path
        
        # Essayer de trouver le fichier dans d'autres répertoires
        found_path = find_image_file(normalized_path)
        if found_path:
            logger.debug(f"Fichier trouvé à: {found_path}")
            return found_path
        
        # Si aucun fichier n'a été trouvé, essayer avec l'ancienne méthode
        result = original_get_image_url(image_path)
        logger.debug(f"Résultat de l'ancienne méthode: {result}")
        
        return result
    
    # Remplacer la méthode
    ImageUrlService.get_image_url = enhanced_get_image_url
    logger.info("Fonction get_cloudinary_url améliorée")

def copy_missing_image(image_path):
    """
    Copie une image manquante de /static/exercises/ vers /static/uploads/ si nécessaire
    """
    if not image_path:
        return None
        
    # Normaliser le chemin d'image
    normalized_path = normalize_image_path(image_path)
    
    # Extraire et normaliser le nom du fichier
    filename = os.path.basename(normalized_path)
    normalized_filename = normalize_filename(filename)
    if normalized_filename != filename:
        # Remplacer le nom de fichier dans le chemin
        normalized_path = normalized_path.replace(filename, normalized_filename)
    
    # Vérifier si le fichier existe
    file_path = normalized_path[1:] if normalized_path.startswith('/') else normalized_path
    if not os.path.exists(file_path):
        # Si le fichier n'existe pas dans /static/uploads/, vérifier dans /static/exercises/
        if '/static/uploads/' in normalized_path:
            exercises_path = normalized_path.replace('/static/uploads/', '/static/exercises/')
            exercises_file_path = exercises_path[1:] if exercises_path.startswith('/') else exercises_path
            
            if os.path.exists(exercises_file_path):
                # Créer le répertoire de destination si nécessaire
                uploads_dir = os.path.dirname(file_path)
                os.makedirs(uploads_dir, exist_ok=True)
                
                # Copier le fichier
                shutil.copy2(exercises_file_path, file_path)
                logger.info(f"Image copiée de {exercises_file_path} vers {file_path}")
                return normalized_path
    
    return normalized_path if os.path.exists(file_path) else None

def apply_fixes():
    """
    Applique toutes les corrections
    """
    logger.info("Début de la correction des problèmes d'affichage des images")
    
    # Améliorer la fonction get_cloudinary_url
    enhance_get_cloudinary_url()
    logger.info("Fonction get_cloudinary_url améliorée")
    
    # Tester la normalisation des noms de fichiers
    test_filenames = [
        "Capture d'écran 2025-08-12 180016.png",
        "Image avec des espaces.jpg",
        "Image-avec-tirets.png",
        "Image_avec_underscores.jpg",
        "Image avec caractères spéciaux éèàç.png"
    ]
    
    logger.info("Test de normalisation des noms de fichiers:")
    for filename in test_filenames:
        normalized = normalize_filename(filename)
        logger.info(f"  Original: {filename} -> Normalisé: {normalized}")
    
    logger.info("Correction des problèmes d'affichage des images terminée")
    
    return {
        "status": "success",
        "message": "Fonction get_cloudinary_url améliorée pour mieux gérer les chemins d'images et les caractères spéciaux"
    }

if __name__ == "__main__":
    results = apply_fixes()
    print(f"Résultats de la correction:")
    print(f"- Statut: {results['status']}")
    print(f"- Message: {results['message']}")
    print("\nLa fonction get_cloudinary_url a été améliorée pour mieux gérer les chemins d'images.")
