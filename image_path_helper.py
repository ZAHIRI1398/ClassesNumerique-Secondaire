"""
Fonctions d'aide pour la gestion des chemins d'images
À intégrer dans app.py
"""
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
        
    # Extraire juste le nom du fichier
    filename = os.path.basename(path)
    
    # Normaliser le nom du fichier (remplacer les espaces par des underscores, supprimer les apostrophes)
    normalized_filename = filename.replace(' ', '_').replace("'", '')
    
    # Retourner le chemin standard
    return f"/static/uploads/exercises/image_labeling/{normalized_filename}"

# Instructions pour l'intégration dans app.py:
# 1. Ajouter cette fonction au début du fichier app.py, après les imports
# 2. Remplacer les lignes suivantes dans la fonction d'upload d'image:
#    - Ligne ~4169: main_image_url = f"/static/uploads/exercises/image_labeling/{os.path.basename(temp_path)}"
#      Par: main_image_url = normalize_image_path(temp_path)
#    - Ligne ~4177: dest_path = os.path.join(dest_folder, os.path.basename(temp_path))
#      Par: dest_path = os.path.join(dest_folder, os.path.basename(temp_path).replace(' ', '_').replace("'", ''))
