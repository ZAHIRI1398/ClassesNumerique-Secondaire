import os
import json
import sqlite3
import logging
import datetime

# Configuration du logging
log_file = f"qcm_images_verification_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler(log_file, encoding="utf-8"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Chemin de la base de données
DB_PATH = "instance/app.db"

# Chemins alternatifs pour rechercher les images
ALTERNATIVE_PATHS = [
    "static/uploads/exercises/qcm/",
    "static/uploads/qcm/",
    "static/uploads/",
    "static/uploads/exercises/"
]

def check_image_exists_locally(image_path):
    # Supprimer le slash initial si présent
    if image_path.startswith("/"):
        image_path = image_path[1:]
    
    # Vérifier le chemin principal
    if os.path.exists(image_path):
        return True, image_path
    
    # Extraire le nom du fichier
    filename = os.path.basename(image_path)
    
    # Vérifier les chemins alternatifs
    for alt_path in ALTERNATIVE_PATHS:
        full_path = os.path.join(alt_path, filename)
        if os.path.exists(full_path):
            return True, full_path
    
    return False, None

def verify_qcm_images():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices QCM avec leur titre
        cursor.execute("SELECT id, title, content, image_path FROM exercise WHERE exercise_type = 'qcm'")
        exercises = cursor.fetchall()
        
        logger.info(f"Vérification de {len(exercises)} exercices QCM")
        
        issues = []
        for exercise_id, title, content_json, db_image_path in exercises:
            try:
                # Vérifier l'image dans le champ image_path de la table
                if db_image_path:
                    image_path = db_image_path
                    source = "image_path"
                else:
                    # Vérifier l'image dans le contenu JSON
                    content = json.loads(content_json) if content_json else {}
                    image_path = content.get("image", "")
                    source = "content.image"
                
                if image_path:
                    # Vérifier si l'image existe localement
                    exists_locally, local_path = check_image_exists_locally(image_path)
                    
                    if not exists_locally:
                        issues.append({
                            "exercise_id": exercise_id,
                            "title": title,
                            "image_path": image_path,
                            "source": source
                        })
                        logger.warning(f"Image non trouvée: {image_path} pour l'exercice #{exercise_id} ({title})")
                    else:
                        logger.info(f"Image trouvée: {image_path} → {local_path} pour l'exercice #{exercise_id} ({title})")
                else:
                    logger.info(f"Pas d'image définie pour l'exercice #{exercise_id} ({title})")
            except json.JSONDecodeError:
                logger.error(f"Contenu JSON invalide pour l'exercice #{exercise_id} ({title})")
                continue
            except Exception as e:
                logger.error(f"Erreur lors de la vérification de l'exercice #{exercise_id} ({title}): {e}")
                continue
        
        # Afficher un résumé
        if issues:
            logger.warning(f"{len(issues)} images non trouvées sur {len(exercises)} exercices QCM")
            for issue in issues:
                logger.warning(f"  - Exercice #{issue['exercise_id']} ({issue['title']}): {issue['image_path']}")
        else:
            logger.info(f"Toutes les images des {len(exercises)} exercices QCM sont accessibles")
        
        return issues
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des images QCM: {e}")
        return []
    finally:
        if "conn" in locals() and conn:
            conn.close()

def generate_report(issues):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"qcm_images_report_{timestamp}.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Rapport de vérification des images QCM\n\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if not issues:
            f.write("✅ Toutes les images des exercices QCM sont accessibles.\n")
        else:
            f.write(f"⚠️ {len(issues)} images non trouvées:\n\n")
            f.write("| ID | Titre | Chemin d'image | Source |\n")
            f.write("|----|-------|----------------|--------|\n")
            
            for issue in issues:
                f.write(f"| {issue['exercise_id']} | {issue['title'][:20]}... | {issue['image_path']} | {issue['source']} |\n")
            
            f.write("\n## Actions recommandées\n\n")
            f.write("1. Vérifier que les images existent dans un des répertoires suivants:\n")
            for path in ALTERNATIVE_PATHS:
                f.write(f"   - {path}\n")
            f.write("2. Copier les images manquantes vers le répertoire static/uploads/exercises/qcm/\n")
            f.write("3. Mettre à jour les chemins dans la base de données\n")
    
    logger.info(f"Rapport généré: {report_path}")
    return report_path

def main():
    logger.info("Début de la vérification des images QCM")
    logger.info(f"Fichier de log: {log_file}")
    
    # Exécuter la vérification
    issues = verify_qcm_images()
    
    # Générer le rapport
    report_path = generate_report(issues)
    
    # Afficher un résumé final
    if issues:
        logger.warning(f"Vérification terminée avec {len(issues)} problèmes détectés.")
        logger.warning(f"Consultez le rapport {report_path} pour plus de détails.")
    else:
        logger.info("Vérification terminée avec succès. Aucun problème détecté.")
    
    logger.info("Fin de la vérification des images QCM")

if __name__ == "__main__":
    main()
