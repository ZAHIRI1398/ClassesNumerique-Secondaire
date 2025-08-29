import os
import json
import sqlite3
import logging
import requests
import datetime
import shutil
from urllib.parse import urljoin

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

# URL de base de l'application en production
BASE_URL = "https://votre-application-production.com"  # À remplacer par l'URL réelle

# Chemins alternatifs pour rechercher les images
ALTERNATIVE_PATHS = [
    "static/uploads/exercises/qcm/",
    "static/uploads/qcm/",
    "static/uploads/",
    "static/uploads/exercises/"
]

def check_image_exists_locally(image_path):
    """Check if image exists locally in main path or alternative paths."""
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

def check_image_exists_remotely(image_url):
    """Check if image exists on remote server."""
    try:
        # Vérifier le chemin principal
        full_url = urljoin(BASE_URL, image_url)
        response = requests.head(full_url, timeout=5)
        if response.status_code == 200:
            return True, full_url
        
        # Extraire le nom du fichier
        filename = os.path.basename(image_url)
        
        # Vérifier les chemins alternatifs
        for alt_path in ALTERNATIVE_PATHS:
            alt_url = urljoin(BASE_URL, os.path.join(alt_path, filename))
            try:
                alt_response = requests.head(alt_url, timeout=5)
                if alt_response.status_code == 200:
                    return True, alt_url
            except Exception:
                continue
        
        return False, None
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'image distante: {e}")
        return False, None

def verify_qcm_images():
    """Verify that all QCM exercise images are accessible."""
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
                    
                    # Vérifier si l'image existe sur le serveur distant
                    exists_remotely, remote_url = False, None
                    if BASE_URL != "https://votre-application-production.com":
                        exists_remotely, remote_url = check_image_exists_remotely(image_path)
                    
                    if not exists_locally and not exists_remotely:
                        issues.append({
                            "exercise_id": exercise_id,
                            "title": title,
                            "image_path": image_path,
                            "source": source,
                            "exists_locally": exists_locally,
                            "local_path": local_path,
                            "exists_remotely": exists_remotely,
                            "remote_url": remote_url
                        })
                        logger.warning(f"Image non trouvée: {image_path} pour l'exercice #{exercise_id} ({title})")
                    else:
                        found_path = local_path if exists_locally else remote_url
                        logger.info(f"Image trouvée: {image_path} → {found_path} pour l'exercice #{exercise_id} ({title})")
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

def generate_fix_script(issues, timestamp):
    """Generate automatic fix script."""
    fix_script_path = f"fix_qcm_images_{timestamp}.py"
    
    with open(fix_script_path, "w", encoding="utf-8") as f:
        # Écrire les imports et la configuration
        f.write("import os\n")
        f.write("import json\n")
        f.write("import sqlite3\n")
        f.write("import shutil\n")
        f.write("import logging\n")
        f.write("from datetime import datetime\n\n")
        
        # Configuration du logging
        f.write("# Configuration du logging\n")
        f.write("logging.basicConfig(level=logging.INFO, format=\"%(asctime)s - %(levelname)s - %(message)s\")\n")
        f.write("logger = logging.getLogger(__name__)\n\n")
        
        # Configuration
        f.write("# Configuration\n")
        f.write("DATABASE_PATH = \"instance/app.db\"\n")
        f.write("BACKUP_DIR = f\"static/backup_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}\"\n\n")
        
        # Chemins alternatifs
        f.write("# Chemins alternatifs pour rechercher les images\n")
        f.write("ALTERNATIVE_PATHS = [\n")
        f.write("    \"static/uploads/exercises/qcm/\",\n")
        f.write("    \"static/uploads/qcm/\",\n")
        f.write("    \"static/uploads/\",\n")
        f.write("    \"static/uploads/exercises/\"\n")
        f.write("]\n\n")
        
        # Fonction ensure_directory_exists
        f.write("def ensure_directory_exists(directory):\n")
        f.write("    \"\"\"Create directory if it does not exist.\"\"\"\n")
        f.write("    if not os.path.exists(directory):\n")
        f.write("        os.makedirs(directory)\n")
        f.write("        logger.info(f\"Répertoire créé: {directory}\")\n\n")
        
        # Fonction backup_database
        f.write("def backup_database():\n")
        f.write("    \"\"\"Create database backup.\"\"\"\n")
        f.write("    backup_path = f\"instance/app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db\"\n")
        f.write("    shutil.copy2(DATABASE_PATH, backup_path)\n")
        f.write("    logger.info(f\"Base de données sauvegardée: {backup_path}\")\n")
        f.write("    return backup_path\n\n")
        
        # Fonction find_image_in_alternative_paths
        f.write("def find_image_in_alternative_paths(filename):\n")
        f.write("    \"\"\"Search for image in alternative paths.\"\"\"\n")
        f.write("    for path in ALTERNATIVE_PATHS:\n")
        f.write("        full_path = os.path.join(path, filename)\n")
        f.write("        if os.path.exists(full_path):\n")
        f.write("            return full_path\n")
        f.write("    return None\n\n")
        
        # Fonction fix_qcm_images - première partie
        f.write("def fix_qcm_images():\n")
        f.write("    \"\"\"Fix QCM image issues.\"\"\"\n")
        f.write("    print(\"=== Correction des problèmes d'images QCM ===\\n\")\n\n")
        f.write("    # 1. Créer les répertoires nécessaires\n")
        f.write("    ensure_directory_exists(\"static/uploads/exercises/qcm\")\n")
        f.write("    ensure_directory_exists(BACKUP_DIR)\n\n")
        
        # Fonction fix_qcm_images - deuxième partie
        f.write("    # 2. Sauvegarder la base de données\n")
        f.write("    backup_path = backup_database()\n\n")
        f.write("    # 3. Connexion à la base de données\n")
        f.write("    try:\n")
        f.write("        conn = sqlite3.connect(DATABASE_PATH)\n")
        f.write("        cursor = conn.cursor()\n")
        f.write("        logger.info(\"Connexion à la base de données réussie\")\n")
        f.write("    except Exception as e:\n")
        f.write("        logger.error(f\"Erreur de connexion à la base de données: {e}\")\n")
        f.write("        return\n\n")
        
        # Fonction fix_qcm_images - troisième partie
        f.write("    # 4. Récupérer tous les exercices QCM\n")
        f.write("    try:\n")
        f.write("        cursor.execute(\"SELECT id, title, content, image_path FROM exercise WHERE exercise_type = 'qcm'\")\n")
        f.write("        exercises = cursor.fetchall()\n")
        f.write("        logger.info(f\"{len(exercises)} exercices QCM trouvés\")\n")
        f.write("    except Exception as e:\n")
        f.write("        logger.error(f\"Erreur lors de la récupération des exercices QCM: {e}\")\n")
        f.write("        return\n\n")
        
        # Fonction fix_qcm_images - quatrième partie
        f.write("    # 5. Traiter chaque exercice\n")
        f.write("    fixed_count = 0\n")
        f.write("    for exercise_id, title, content_json, db_image_path in exercises:\n")
        f.write("        print(f\"\\nTraitement de l'exercice #{exercise_id}: {title}\")\n\n")
        f.write("        try:\n")
        f.write("            # Déterminer le chemin d'image à utiliser\n")
        f.write("            image_path = db_image_path\n")
        f.write("            source = \"image_path\"\n\n")
        f.write("            if not image_path:\n")
        f.write("                # Vérifier dans le contenu JSON\n")
        f.write("                content = json.loads(content_json) if content_json else {}\n")
        f.write("                image_path = content.get(\"image\", \"\")\n")
        f.write("                source = \"content.image\"\n\n")
        
        # Fonction fix_qcm_images - cinquième partie
        f.write("            if not image_path:\n")
        f.write("                print(f\"  Pas d'image définie pour cet exercice\")\n")
        f.write("                continue\n\n")
        f.write("            print(f\"  Chemin d'image actuel ({source}): {image_path}\")\n\n")
        f.write("            # Extraire le nom du fichier\n")
        f.write("            filename = os.path.basename(image_path)\n\n")
        f.write("            # Vérifier si l'image existe au chemin attendu\n")
        f.write("            expected_path = image_path\n")
        f.write("            if expected_path.startswith(\"/\"):\n")
        f.write("                expected_path = expected_path[1:]\n\n")
        
        # Fonction fix_qcm_images - sixième partie
        f.write("            if os.path.exists(expected_path):\n")
        f.write("                print(f\"  ✅ L'image existe déjà au bon emplacement\")\n")
        f.write("                continue\n\n")
        f.write("            # Rechercher l'image dans les chemins alternatifs\n")
        f.write("            alt_path = find_image_in_alternative_paths(filename)\n\n")
        f.write("            if alt_path:\n")
        f.write("                # Copier l'image vers le bon emplacement\n")
        f.write("                target_path = \"static/uploads/exercises/qcm/\" + filename\n")
        f.write("                shutil.copy2(alt_path, target_path)\n")
        f.write("                print(f\"  ✅ Image copiée de {alt_path} vers {target_path}\")\n\n")
        
        # Fonction fix_qcm_images - septième partie
        f.write("                # Mettre à jour le chemin dans la base de données\n")
        f.write("                new_path = \"/static/uploads/exercises/qcm/\" + filename\n\n")
        f.write("                if source == \"image_path\":\n")
        f.write("                    cursor.execute(\"UPDATE exercise SET image_path = ? WHERE id = ?\", (new_path, exercise_id))\n")
        f.write("                else:\n")
        f.write("                    # Mettre à jour le champ image dans le contenu JSON\n")
        f.write("                    content = json.loads(content_json)\n")
        f.write("                    content[\"image\"] = new_path\n")
        f.write("                    cursor.execute(\"UPDATE exercise SET content = ? WHERE id = ?\", (json.dumps(content), exercise_id))\n\n")
        
        # Fonction fix_qcm_images - huitième partie
        f.write("                conn.commit()\n")
        f.write("                print(f\"  ✅ Chemin d'image mis à jour dans la base de données: {new_path}\")\n")
        f.write("                fixed_count += 1\n")
        f.write("            else:\n")
        f.write("                print(f\"  ❌ Image introuvable dans tous les chemins alternatifs\")\n")
        f.write("        except Exception as e:\n")
        f.write("            print(f\"  ❌ Erreur lors du traitement: {e}\")\n\n")
        
        # Fonction fix_qcm_images - conclusion
        f.write("    # 6. Conclusion\n")
        f.write("    print(\"\\n=== Résumé ===\")\n") # Ajout du guillemet manquant
        f.write("    print(f\"Base de données sauvegardée: {backup_path}\")\n")
        f.write("    print(f\"{fixed_count} exercices QCM corrigés sur {len(exercises)}\")\n")
        f.write("    print(\"Opération terminée.\")\n\n")
        
        # Point d'entrée du script
        f.write("if __name__ == \"__main__\":\n")
        f.write("    fix_qcm_images()\n")

    
    logger.info(f"Script de correction généré: {fix_script_path}")
    return fix_script_path

def generate_report(issues):
    """Generate report of image issues."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"qcm_images_report_{timestamp}.md"
    fix_script_path = None
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Rapport de vérification des images QCM\n\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if not issues:
            f.write("✅ Toutes les images des exercices QCM sont accessibles.\n")
        else:
            f.write(f"⚠️ {len(issues)} images non trouvées:\n\n")
            f.write("| ID | Titre | Chemin d'image | Source | Existe localement | Existe en production |\n")
            f.write("|----|--------------------|---------------|--------|-------------------|---------------------|\n")
            
            for issue in issues:
                f.write(f"| {issue['exercise_id']} | {issue['title'][:20]}... | {issue['image_path']} | {issue['source']} | ")
                f.write(f"{'✅' if issue['exists_locally'] else '❌'} | {'✅' if issue['exists_remotely'] else '❌'} |\n")
            
            f.write("\n## Actions recommandées\n\n")
            fix_script_path = generate_fix_script(issues, timestamp)
            f.write(f"1. Exécuter le script `{fix_script_path}` pour corriger automatiquement les problèmes d'images\n")
            f.write("2. Vérifier manuellement les exercices qui n'ont pas pu être corrigés automatiquement\n")
            f.write("3. Relancer le script de vérification pour confirmer que tous les problèmes sont résolus\n")
    
    logger.info(f"Rapport généré: {report_path}")
    return report_path, fix_script_path

def main():
    """Main function."""
    logger.info("Début de la vérification des images QCM")
    logger.info(f"Fichier de log: {log_file}")
    
    # Vérifier si l'URL de production a été configurée
    if BASE_URL == "https://votre-application-production.com":
        logger.warning("L'URL de production n'a pas été configurée. La vérification distante sera désactivée.")
        logger.warning("Pour activer la vérification distante, modifiez la variable BASE_URL dans le script.")
    
    # Exécuter la vérification
    issues = verify_qcm_images()
    
    # Générer le rapport et le script de correction
    report_path, fix_script_path = generate_report(issues)
    
    # Afficher un résumé final
    if issues:
        logger.warning(f"Vérification terminée avec {len(issues)} problèmes détectés.")
        logger.warning(f"Consultez le rapport {report_path} pour plus de détails.")
        logger.warning(f"Exécutez le script {fix_script_path} pour corriger automatiquement les problèmes.")
    else:
        logger.info("Vérification terminée avec succès. Aucun problème détecté.")
    
    logger.info("Fin de la vérification des images QCM")

if __name__ == "__main__":
    main()
