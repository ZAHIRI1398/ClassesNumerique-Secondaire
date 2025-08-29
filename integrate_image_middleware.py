"""
Script d'intégration du middleware de gestion des images QCM Multichoix
Ce script modifie app.py pour ajouter le middleware de gestion des images
"""

import os
import re
import shutil
from datetime import datetime

# Fichiers à modifier
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_FILE = os.path.join(BASE_DIR, 'app.py')
BACKUP_DIR = os.path.join(BASE_DIR, f'backups/image_middleware_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

def create_backup():
    """Crée une sauvegarde du fichier app.py"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    backup_path = os.path.join(BACKUP_DIR, os.path.basename(APP_FILE))
    shutil.copy2(APP_FILE, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    return backup_path

def add_middleware_import(content):
    """Ajoute l'import du middleware dans app.py"""
    # Vérifier si l'import existe déjà
    if "from utils.image_fallback_middleware import register_image_fallback_middleware" in content:
        print("Import du middleware déjà présent")
        return content
    
    # Trouver la section des imports
    import_section = re.search(r'(from flask import .*?\n)', content, re.DOTALL)
    if not import_section:
        print("Section d'imports non trouvée")
        return content
    
    # Ajouter l'import après la section des imports Flask
    new_import = "from utils.image_fallback_middleware import register_image_fallback_middleware\n"
    modified_content = content.replace(
        import_section.group(0),
        import_section.group(0) + new_import
    )
    
    print("Import du middleware ajouté")
    return modified_content

def add_middleware_initialization(content):
    """Ajoute l'initialisation du middleware dans app.py"""
    # Vérifier si l'initialisation existe déjà
    if "register_image_fallback_middleware(app)" in content:
        print("Initialisation du middleware déjà présente")
        return content
    
    # Trouver la section d'initialisation des extensions
    init_section = re.search(r'(# Initialiser les extensions.*?)\n\n', content, re.DOTALL)
    if not init_section:
        # Essayer une autre approche
        init_section = re.search(r'(db\.init_app\(app\).*?)\n', content, re.DOTALL)
    
    if not init_section:
        print("Section d'initialisation des extensions non trouvée")
        return content
    
    # Ajouter l'initialisation après la section d'initialisation des extensions
    middleware_init = "\n# Initialiser le middleware de gestion des images\nregister_image_fallback_middleware(app)\n"
    modified_content = content.replace(
        init_section.group(0),
        init_section.group(0) + middleware_init
    )
    
    print("Initialisation du middleware ajoutée")
    return modified_content

def add_qcm_multichoix_directory_creation(content):
    """Ajoute la création du répertoire qcm_multichoix dans app.py"""
    # Vérifier si la création du répertoire existe déjà
    if "os.makedirs('static/uploads/qcm_multichoix', exist_ok=True)" in content:
        print("Création du répertoire qcm_multichoix déjà présente")
        return content
    
    # Trouver la section de création des répertoires
    dir_section = re.search(r'(os\.makedirs.*?exist_ok=True\).*?)\n', content, re.DOTALL)
    if not dir_section:
        print("Section de création des répertoires non trouvée")
        return content
    
    # Ajouter la création du répertoire après la section existante
    dir_creation = "\nos.makedirs('static/uploads/qcm_multichoix', exist_ok=True)"
    modified_content = content.replace(
        dir_section.group(0),
        dir_section.group(0) + dir_creation
    )
    
    print("Création du répertoire qcm_multichoix ajoutée")
    return modified_content

def integrate_middleware():
    """Intègre le middleware dans l'application Flask"""
    print("=== Intégration du middleware de gestion des images QCM Multichoix ===\n")
    
    # 1. Créer une sauvegarde
    backup_path = create_backup()
    
    try:
        # 2. Lire le contenu du fichier app.py
        with open(APP_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 3. Ajouter l'import du middleware
        content = add_middleware_import(content)
        
        # 4. Ajouter l'initialisation du middleware
        content = add_middleware_initialization(content)
        
        # 5. Ajouter la création du répertoire qcm_multichoix
        content = add_qcm_multichoix_directory_creation(content)
        
        # 6. Écrire le contenu modifié dans app.py
        with open(APP_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n[SUCCES] Middleware intégré avec succès dans app.py")
        print(f"[SUCCES] Sauvegarde disponible dans {backup_path}")
        
        # 7. Créer le répertoire qcm_multichoix s'il n'existe pas
        qcm_dir = os.path.join(BASE_DIR, 'static', 'uploads', 'qcm_multichoix')
        if not os.path.exists(qcm_dir):
            os.makedirs(qcm_dir, exist_ok=True)
            print(f"[SUCCES] Répertoire {qcm_dir} créé")
        
        print("\nPour tester le middleware, accédez à la route /admin/verify-qcm-multichoix-images")
        print("Cette route vérifiera toutes les images QCM Multichoix et corrigera les chemins problématiques")
        
    except Exception as e:
        print(f"\n[ERREUR] Erreur lors de l'intégration du middleware: {str(e)}")
        print(f"La sauvegarde est disponible dans {backup_path}")

if __name__ == "__main__":
    integrate_middleware()
