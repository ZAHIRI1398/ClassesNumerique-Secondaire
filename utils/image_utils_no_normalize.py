import os

def normalize_image_path(path, exercise_type=None):
    """
    Normalise le chemin d'image pour assurer un format cohérent avec le préfixe /static/
    et organise les images dans des sous-dossiers selon le type d'exercice
    
    Args:
        path (str): Le chemin d'image à normaliser
        exercise_type (str, optional): Le type d'exercice pour organiser les images dans des sous-dossiers
        
    Returns:
        str: Le chemin normalisé avec préfixe /static/ et sous-dossier du type d'exercice si nécessaire
    """
    if not path:
        return path
        
    # Normaliser le nom du fichier (remplacer les espaces par des underscores, supprimer les apostrophes)
    path = path.replace(' ', '_').replace("'", '')
    
    # Ignorer les URLs externes
    if path.startswith(('http://', 'https://')):
        return path
    
    # Cas spécifique: /static/uploads/general/general_TIMESTAMP_...
    if '/static/uploads/general/general_' in path:
        # Extraire le nom du fichier
        filename = path.split('/')[-1]
        
        # Si le nom commence par 'general_' et qu'on a un type d'exercice spécifique,
        # remplacer 'general_' par le type d'exercice
        if exercise_type and exercise_type != 'general' and filename.startswith('general_'):
            # Enlever le préfixe 'general_' pour éviter la duplication
            clean_filename = filename[8:]  # Longueur de 'general_'
            return f'/static/uploads/{exercise_type}/{exercise_type}_{clean_filename}'
        elif exercise_type and exercise_type != 'general':
            # Garder le nom tel quel mais changer le dossier
            return f'/static/uploads/{exercise_type}/{filename}'
        else:
            # Garder le chemin générique si pas de type spécifique
            return f'/static/uploads/{filename}'
    
    # Extraire le nom du fichier pour les autres cas
    filename = path.split('/')[-1]
    
    # Construire le chemin normalisé avec le type d'exercice si spécifié
    if exercise_type and exercise_type != 'general':
        return f'/static/uploads/{exercise_type}/{filename}'
    else:
        return f'/static/uploads/{filename}'

