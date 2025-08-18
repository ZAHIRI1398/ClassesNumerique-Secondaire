"""
Script de test pour vérifier le fonctionnement complet du bouton École et du flux d'inscription/paiement
"""
from models import db, User
from sqlalchemy import func
import logging
import sys
import os

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_ecole_button_flow.log", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Importer l'application Flask existante
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, db

def test_ecole_button_flow():
    """
    Teste le flux complet du bouton École et de l'inscription/paiement
    """
    with app.app_context():
        try:
            logger.info("=== DÉBUT DU TEST DU BOUTON ÉCOLE ===")
            
            # 1. Vérifier que le template login.html contient le bouton École
            login_template_path = os.path.join('templates', 'login.html')
            if os.path.exists(login_template_path):
                with open(login_template_path, 'r', encoding='utf-8') as f:
                    login_template_content = f.read()
                    
                if 'École' in login_template_content and 'fa-school' in login_template_content:
                    logger.info("[OK] Le template login.html contient le bouton École")
                else:
                    logger.error("[ERREUR] Le template login.html ne contient pas le bouton École")
            else:
                logger.error(f"[ERREUR] Le template login.html n'existe pas à {login_template_path}")
            
            # 2. Vérifier si la route register_school est définie dans app.py
            with open('app.py', 'r', encoding='utf-8') as f:
                app_content = f.read()
                if "@app.route('/register/school'" in app_content and "def register_school():" in app_content:
                    logger.info("[OK] La route register_school est définie dans app.py")
                else:
                    logger.error("[ERREUR] La route register_school n'est pas définie dans app.py")
            
            # 3. Vérifier le flux d'inscription d'école
            try:
                # Vérifier les écoles avec abonnement actif
                schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
                    filter(User.school_name != None).\
                    filter(User.school_name != '').\
                    filter(User.subscription_type == 'school').\
                    filter(User.subscription_status == 'approved').\
                    group_by(User.school_name).all()
                
                logger.info(f"[INFO] Nombre d'écoles avec abonnement actif: {len(schools_with_subscription)}")
                
                for school, count in schools_with_subscription:
                    logger.info(f"[INFO] École: {school}, Utilisateurs: {count}")
                
                # Vérifier que l'école "École Bruxelles II" apparaît dans la liste
                bruxelles_school = next((school for school, count in schools_with_subscription if school == "École Bruxelles II"), None)
                if bruxelles_school:
                    logger.info("[OK] L'école 'École Bruxelles II' est présente dans la liste")
                else:
                    logger.warning("[ATTENTION] L'école 'École Bruxelles II' n'est PAS présente dans la liste")
                
            except Exception as e:
                logger.error(f"[ERREUR] Erreur lors de la vérification des écoles: {str(e)}")
            
            # 4. Vérifier l'existence des templates nécessaires
            template_paths = [
                'templates/payment/select_school.html',
                'templates/auth/register_school_connected.html',
                'templates/auth/register_school_simplified.html'
            ]
            
            for path in template_paths:
                if os.path.exists(path):
                    logger.info(f"[OK] Le template {path} existe")
                else:
                    logger.error(f"[ERREUR] Le template {path} n'existe pas")
            
            # 5. Vérifier l'existence des blueprints de correction
            if os.path.exists('fix_payment_select_school.py'):
                logger.info("[OK] Le blueprint fix_payment_select_school.py existe")
                
                with open('fix_payment_select_school.py', 'r', encoding='utf-8') as f:
                    fix_content = f.read()
                    if "fix_payment_select_school_bp = Blueprint('fix_payment_select_school'" in fix_content:
                        logger.info("[OK] Le blueprint fix_payment_select_school_bp est défini")
                    else:
                        logger.error("[ERREUR] Le blueprint fix_payment_select_school_bp n'est pas défini")
            else:
                logger.error("[ERREUR] Le blueprint fix_payment_select_school.py n'existe pas")
            
            logger.info("=== FIN DU TEST DU BOUTON ÉCOLE ===")
            
        except Exception as e:
            logger.error(f"[ERREUR] Erreur générale: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_ecole_button_flow()
    print("Test terminé. Consultez le fichier test_ecole_button_flow.log pour les résultats.")
