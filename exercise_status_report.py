import os
import json
import sqlite3
import logging
from datetime import datetime
from tabulate import tabulate

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'exercise_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def generate_exercise_report():
    """
    Génère un rapport complet sur l'état des exercices dans la base de données.
    """
    try:
        # Connexion à la base de données
        db_path = 'instance/app.db'
        if not os.path.exists(db_path):
            logger.error(f"Base de données non trouvée: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices
        cursor.execute("""
            SELECT e.id, e.title, e.description, e.exercise_type, e.image_path, 
                   e.teacher_id, u.username, u.email
            FROM exercise e
            LEFT JOIN user u ON e.teacher_id = u.id
            ORDER BY e.id
        """)
        exercises = cursor.fetchall()
        
        if not exercises:
            logger.warning("Aucun exercice trouvé dans la base de données.")
            return False
        
        # Statistiques générales
        logger.info(f"=== RAPPORT SUR L'ÉTAT DES EXERCICES ===")
        logger.info(f"Date du rapport: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Nombre total d'exercices: {len(exercises)}")
        
        # Compter les exercices par type
        exercise_types = {}
        for exercise in exercises:
            exercise_type = exercise[3]  # exercise_type est à l'index 3
            if exercise_type in exercise_types:
                exercise_types[exercise_type] += 1
            else:
                exercise_types[exercise_type] = 1
        
        # Afficher les statistiques par type d'exercice
        logger.info("\n=== EXERCICES PAR TYPE ===")
        type_stats = []
        for exercise_type, count in exercise_types.items():
            type_stats.append([exercise_type, count])
        logger.info("\n" + tabulate(type_stats, headers=["Type d'exercice", "Nombre"], tablefmt="grid"))
        
        # Afficher la liste des exercices
        logger.info("\n=== LISTE DES EXERCICES ===")
        exercise_list = []
        for exercise in exercises:
            exercise_id, title, description, exercise_type, image_path, teacher_id, username, email = exercise
            
            # Vérifier si l'image existe
            image_status = "✓" if image_path and os.path.exists(os.path.join('static', image_path.lstrip('/'))) else "✗"
            
            # Récupérer le contenu pour analyse
            cursor.execute("SELECT content FROM exercise WHERE id = ?", (exercise_id,))
            content_row = cursor.fetchone()
            content_str = content_row[0] if content_row else None
            
            # Analyser le contenu JSON
            content_status = "N/A"
            if content_str:
                try:
                    content = json.loads(content_str)
                    # Vérifier la structure selon le type d'exercice
                    if exercise_type == "qcm":
                        if "questions" in content and isinstance(content["questions"], list):
                            content_status = f"✓ ({len(content['questions'])} questions)"
                        else:
                            content_status = "✗ (structure invalide)"
                    elif exercise_type == "fill_in_blanks":
                        if ("sentences" in content or "text" in content) and ("available_words" in content or "words" in content):
                            content_status = "✓"
                        else:
                            content_status = "✗ (structure invalide)"
                    elif exercise_type == "pairs":
                        if "left_items" in content and "right_items" in content and "correct_pairs" in content:
                            content_status = f"✓ ({len(content['left_items'])} paires)"
                        else:
                            content_status = "✗ (structure invalide)"
                    elif exercise_type == "drag_and_drop":
                        if "draggable_items" in content and "drop_zones" in content:
                            content_status = f"✓ ({len(content['draggable_items'])} éléments)"
                        else:
                            content_status = "✗ (structure invalide)"
                    elif exercise_type == "legend":
                        if "mode" in content:
                            content_status = f"✓ (mode: {content['mode']})"
                        else:
                            content_status = "✗ (structure invalide)"
                    elif exercise_type == "word_placement":
                        if "sentences" in content and "words" in content and "answers" in content:
                            content_status = f"✓ ({len(content['sentences'])} phrases)"
                        else:
                            content_status = "✗ (structure invalide)"
                    elif exercise_type == "image_labeling":
                        if "image" in content and "labels" in content:
                            content_status = f"✓ ({len(content['labels'])} étiquettes)"
                        else:
                            content_status = "✗ (structure invalide)"
                    else:
                        content_status = "? (type inconnu)"
                except json.JSONDecodeError:
                    content_status = "✗ (JSON invalide)"
                except Exception as e:
                    content_status = f"✗ (erreur: {str(e)})"
            
            exercise_list.append([
                exercise_id,
                title[:30] + "..." if title and len(title) > 30 else title,
                exercise_type,
                image_status,
                content_status,
                username or "N/A"
            ])
        
        logger.info("\n" + tabulate(exercise_list, 
                                   headers=["ID", "Titre", "Type", "Image", "Contenu", "Créateur"], 
                                   tablefmt="grid"))
        
        # Vérifier les dossiers d'upload
        logger.info("\n=== VÉRIFICATION DES DOSSIERS D'UPLOAD ===")
        upload_dirs = [
            os.path.join('static', 'uploads', 'qcm'),
            os.path.join('static', 'uploads', 'fill_in_blanks'),
            os.path.join('static', 'uploads', 'pairs'),
            os.path.join('static', 'uploads', 'drag_and_drop'),
            os.path.join('static', 'uploads', 'legend'),
            os.path.join('static', 'uploads', 'word_placement'),
            os.path.join('static', 'uploads', 'image_labeling')
        ]
        
        dir_status = []
        for directory in upload_dirs:
            exists = os.path.exists(directory)
            status = "✓" if exists else "✗"
            file_count = len(os.listdir(directory)) if exists else 0
            dir_status.append([directory, status, file_count])
        
        logger.info("\n" + tabulate(dir_status, 
                                   headers=["Dossier", "Existe", "Nombre de fichiers"], 
                                   tablefmt="grid"))
        
        # Vérifier les utilisateurs
        logger.info("\n=== UTILISATEURS ENSEIGNANTS ===")
        cursor.execute("SELECT id, username, email, role FROM user WHERE role = 'teacher'")
        teachers = cursor.fetchall()
        
        teacher_list = []
        for teacher in teachers:
            teacher_id, username, email, role = teacher
            
            # Compter les exercices créés par cet enseignant
            cursor.execute("SELECT COUNT(*) FROM exercise WHERE teacher_id = ?", (teacher_id,))
            exercise_count = cursor.fetchone()[0]
            
            teacher_list.append([teacher_id, username, email, exercise_count])
        
        logger.info("\n" + tabulate(teacher_list, 
                                   headers=["ID", "Nom d'utilisateur", "Email", "Exercices créés"], 
                                   tablefmt="grid"))
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        return False

def main():
    """
    Fonction principale
    """
    logger.info("=== GÉNÉRATION DU RAPPORT SUR L'ÉTAT DES EXERCICES ===")
    
    try:
        # Vérifier si tabulate est installé
        import tabulate
    except ImportError:
        logger.warning("Le module 'tabulate' n'est pas installé. Installation en cours...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
        logger.info("Module 'tabulate' installé avec succès.")
    
    # Générer le rapport
    success = generate_exercise_report()
    
    if success:
        logger.info("""
=== RAPPORT GÉNÉRÉ AVEC SUCCÈS ===

Le rapport sur l'état des exercices a été généré avec succès.
Consultez le fichier de log pour les détails complets.

Résumé:
- Tous les exercices ont été vérifiés
- Les statistiques par type d'exercice ont été générées
- La structure du contenu de chaque exercice a été analysée
- Les dossiers d'upload ont été vérifiés
- Les utilisateurs enseignants ont été listés
""")
    else:
        logger.error("""
=== ÉCHEC DE LA GÉNÉRATION DU RAPPORT ===

La génération du rapport a échoué.
Vérifiez les messages d'erreur ci-dessus.
""")

if __name__ == "__main__":
    import sys
    main()
