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
        logging.FileHandler(f"fix_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Chemin du répertoire de production
PRODUCTION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             "production_code", "ClassesNumerique-Secondaire-main")

def fix_template_permissions():
    """Corriger les permissions et s'assurer que les templates sont correctement déployés"""
    logger.info("=== Correction des permissions des templates ===")
    
    # Vérifier le répertoire templates/payment
    payment_dir = os.path.join(PRODUCTION_DIR, "templates", "payment")
    if not os.path.exists(payment_dir):
        logger.warning(f"Le répertoire payment n'existe pas à {payment_dir}")
        logger.info(f"Création du répertoire {payment_dir}")
        os.makedirs(payment_dir, exist_ok=True)
    
    # Vérifier le fichier select_school.html
    select_school_path = os.path.join(payment_dir, "select_school.html")
    
    # Créer une copie de sauvegarde si le fichier existe
    if os.path.exists(select_school_path):
        backup_path = f"{select_school_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Création d'une sauvegarde du template à {backup_path}")
        shutil.copy2(select_school_path, backup_path)
    
    # Copier le template depuis le répertoire local
    local_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "templates", "payment", "select_school.html")
    
    if os.path.exists(local_template):
        logger.info(f"Copie du fichier local {local_template} vers {select_school_path}")
        shutil.copy2(local_template, select_school_path)
        logger.info(f"Template copié avec succès")
    else:
        logger.warning(f"Template local non trouvé à {local_template}")
        
        # Essayer avec le template de correction
        fix_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   "templates", "payment", "fix_payment_select_school.html")
        
        if os.path.exists(fix_template):
            logger.info(f"Copie du template de correction {fix_template} vers {select_school_path}")
            shutil.copy2(fix_template, select_school_path)
            logger.info(f"Template de correction copié avec succès")
        else:
            logger.error(f"Aucun template source trouvé")
            return False
    
    # Vérifier les permissions
    try:
        # S'assurer que le fichier est accessible en lecture
        os.chmod(select_school_path, 0o644)
        logger.info(f"Permissions du fichier {select_school_path} mises à jour (644)")
        
        # Vérifier que le fichier est lisible
        with open(select_school_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"Le fichier {select_school_path} est lisible")
            logger.info(f"Taille du fichier: {len(content)} caractères")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des permissions: {str(e)}")
        return False
    
    # Créer un fichier .gitkeep dans le répertoire pour s'assurer qu'il est inclus dans Git
    gitkeep_path = os.path.join(payment_dir, ".gitkeep")
    with open(gitkeep_path, 'w') as f:
        f.write("# Ce fichier assure que le répertoire est inclus dans Git\n")
    logger.info(f"Fichier .gitkeep créé à {gitkeep_path}")
    
    logger.info("=== Correction terminée ===")
    logger.info("Pour déployer la correction:")
    logger.info("1. Exécutez: git add production_code/ClassesNumerique-Secondaire-main/templates/payment/")
    logger.info("2. Exécutez: git commit -m \"Fix: Correction des permissions du template select_school.html\"")
    logger.info("3. Exécutez: git push")
    logger.info("4. Vérifiez le déploiement sur Railway")
    
    return True

if __name__ == "__main__":
    fix_template_permissions()
