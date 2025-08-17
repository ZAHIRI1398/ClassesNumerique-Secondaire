import os
import shutil
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"check_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Chemin du répertoire de production
PRODUCTION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             "production_code", "ClassesNumerique-Secondaire-main")

def check_templates_structure():
    """Vérifier la structure des templates en production"""
    logger.info("=== Vérification de la structure des templates ===")
    
    # Vérifier le répertoire templates
    templates_dir = os.path.join(PRODUCTION_DIR, "templates")
    if not os.path.exists(templates_dir):
        logger.error(f"Le répertoire templates n'existe pas à {templates_dir}")
        return False
    
    # Vérifier le répertoire payment
    payment_dir = os.path.join(templates_dir, "payment")
    if not os.path.exists(payment_dir):
        logger.warning(f"Le répertoire payment n'existe pas à {payment_dir}")
        logger.info(f"Création du répertoire {payment_dir}")
        os.makedirs(payment_dir, exist_ok=True)
    
    # Vérifier le fichier select_school.html
    select_school_path = os.path.join(payment_dir, "select_school.html")
    if not os.path.exists(select_school_path):
        logger.warning(f"Le fichier select_school.html n'existe pas à {select_school_path}")
        
        # Chercher le fichier dans le répertoire local
        local_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                     "templates", "payment", "select_school.html")
        
        if os.path.exists(local_template):
            logger.info(f"Copie du fichier local {local_template} vers {select_school_path}")
            shutil.copy2(local_template, select_school_path)
        else:
            logger.error(f"Impossible de trouver le template select_school.html localement")
            return False
    else:
        logger.info(f"Le fichier select_school.html existe à {select_school_path}")
    
    # Vérifier les permissions
    try:
        with open(select_school_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"Le fichier {select_school_path} est lisible")
            logger.info(f"Taille du fichier: {len(content)} caractères")
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {select_school_path}: {str(e)}")
        return False
    
    logger.info("=== Vérification terminée ===")
    return True

def fix_templates_structure():
    """Corriger la structure des templates en production"""
    logger.info("=== Correction de la structure des templates ===")
    
    # Vérifier d'abord la structure
    if check_templates_structure():
        logger.info("La structure des templates semble correcte")
    
    # Vérifier si le fichier existe dans le répertoire racine
    root_template = os.path.join(PRODUCTION_DIR, "select_school.html")
    if os.path.exists(root_template):
        logger.warning(f"Le fichier select_school.html existe à la racine: {root_template}")
        
        # Déplacer vers le bon répertoire
        payment_dir = os.path.join(PRODUCTION_DIR, "templates", "payment")
        os.makedirs(payment_dir, exist_ok=True)
        target_path = os.path.join(payment_dir, "select_school.html")
        
        if not os.path.exists(target_path):
            logger.info(f"Déplacement du fichier {root_template} vers {target_path}")
            shutil.copy2(root_template, target_path)
            logger.info(f"Fichier copié avec succès")
        else:
            logger.info(f"Le fichier existe déjà à {target_path}")
    
    # Vérifier si le fichier existe dans le répertoire fix_payment_select_school.html
    fix_template = os.path.join(PRODUCTION_DIR, "templates", "payment", "fix_payment_select_school.html")
    if os.path.exists(fix_template):
        logger.info(f"Le fichier fix_payment_select_school.html existe à {fix_template}")
        
        # Copier vers select_school.html s'il n'existe pas
        target_path = os.path.join(PRODUCTION_DIR, "templates", "payment", "select_school.html")
        if not os.path.exists(target_path):
            logger.info(f"Copie du fichier {fix_template} vers {target_path}")
            shutil.copy2(fix_template, target_path)
            logger.info(f"Fichier copié avec succès")
    
    # Vérifier à nouveau la structure
    check_templates_structure()
    
    logger.info("=== Correction terminée ===")
    logger.info("Pour déployer la correction:")
    logger.info("1. Exécutez: git add production_code/ClassesNumerique-Secondaire-main/templates/payment/")
    logger.info("2. Exécutez: git commit -m \"Fix: Ajout du template select_school.html manquant\"")
    logger.info("3. Exécutez: git push")
    logger.info("4. Vérifiez le déploiement sur Railway")

if __name__ == "__main__":
    fix_templates_structure()
