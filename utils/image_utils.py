import os

def normalize_image_path(path):
    """
    Normalise le chemin d'image pour assurer un format cohérent
    
    Args:
        path (str): Le chemin d'image à normaliser
        
    Returns:
        str: Le chemin normalisé
    """
    if not path:
        return path
        
    # Extraire le répertoire et le nom du fichier
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    
    # Normaliser le nom du fichier (remplacer les espaces par des underscores, supprimer les apostrophes)
    normalized_filename = filename.replace(' ', '_').replace("'", '')
    
    # Reconstruire le chemin complet avec le nom de fichier normalisé
    if directory:
        return os.path.join(directory, normalized_filename).replace('\\', '/')
    else:
        return normalized_filename
