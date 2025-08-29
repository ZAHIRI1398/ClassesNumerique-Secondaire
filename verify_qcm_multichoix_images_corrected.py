import os
import json
import sqlite3
import logging
import requests
import datetime
from urllib.parse import urljoin

# Configuration du logging
log_file = f'qcm_multichoix_images_verification_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file, encoding='utf-8'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Chemin de la base de données
DB_PATH = 'instance/app.db'

# URL de base de l'application en production
BASE_URL = 'https://votre-application-production.com'  # À remplacer par l'URL réelle

# Chemins alternatifs pour rechercher les images QCM Multichoix
ALTERNATIVE_PATHS = [
    'static/exercises/qcm_multichoix/',
    'static/uploads/qcm_multichoix/',
    'static/uploads/exercises/qcm_multichoix/',
    'static/uploads/',
    'static/exercises/'
]

def check_image_exists_locally(image_path):
    """Vérifie si l'image existe localement dans le chemin principal ou les chemins alternatifs."""
    # Supprimer le slash initial si présent
    if image_path.startswith('/'):
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
    """Vérifie si l'image existe sur le serveur distant."""
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

def verify_qcm_multichoix_images():
    """Vérifie que toutes les images des exercices QCM Multichoix sont accessibles."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices QCM Multichoix avec leur titre
        cursor.execute("SELECT id, title, content, image_path FROM exercise WHERE exercise_type = 'qcm_multichoix'")
        exercises = cursor.fetchall()
        
        logger.info(f"Vérification de {len(exercises)} exercices QCM Multichoix")
        
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
                    image_path = content.get('image', '')
                    source = "content.image"
                
                if image_path:
                    # Vérifier si l'image existe localement
                    exists_locally, local_path = check_image_exists_locally(image_path)
                    
                    # Vérifier si l'image existe sur le serveur distant
                    exists_remotely, remote_url = False, None
                    if BASE_URL != 'https://votre-application-production.com':
                        exists_remotely, remote_url = check_image_exists_remotely(image_path)
                    
                    if not exists_locally and not exists_remotely:
                        issues.append({
                            'exercise_id': exercise_id,
                            'title': title,
                            'image_path': image_path,
                            'source': source,
                            'exists_locally': exists_locally,
                            'local_path': local_path,
                            'exists_remotely': exists_remotely,
                            'remote_url': remote_url
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
            logger.warning(f"{len(issues)} images non trouvées sur {len(exercises)} exercices QCM Multichoix")
            for issue in issues:
                logger.warning(f"  - Exercice #{issue['exercise_id']} ({issue['title']}): {issue['image_path']}")
        else:
            logger.info(f"Toutes les images des {len(exercises)} exercices QCM Multichoix sont accessibles")
        
        return issues
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des images QCM Multichoix: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def generate_report(issues):
    """Génère un rapport des problèmes d'images."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f'qcm_multichoix_images_report_{timestamp}.md'
    fix_script_path = f'fix_qcm_multichoix_images_{timestamp}.py'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Rapport de vérification des images QCM Multichoix\n\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if not issues:
            f.write("✅ Toutes les images des exercices QCM Multichoix sont accessibles.\n")
        else:
            f.write(f"⚠️ {len(issues)} images non trouvées:\n\n")
            f.write("| ID | Titre | Chemin d'image | Source | Existe localement | Existe en production |\n")
            f.write("|----|--------------------|---------------|--------|-------------------|---------------------|\n")
            
            for issue in issues:
                f.write(f"| {issue['exercise_id']} | {issue['title'][:20]}... | {issue['image_path']} | {issue['source']} | ")
                f.write(f"{'✅' if issue['exists_locally'] else '❌'} | {'✅' if issue['exists_remotely'] else '❌'} |\n")
            
            f.write("\n## Actions recommandées\n\n")
            f.write(f"1. Exécuter le script `{fix_script_path}` pour corriger automatiquement les problèmes d'images\n")
            f.write("2. Vérifier manuellement les exercices qui n'ont pas pu être corrigés automatiquement\n")
            f.write("3. Relancer le script de vérification pour confirmer que tous les problèmes sont résolus\n")
    
    # Générer un script de correction automatique
    with open(fix_script_path, 'w', encoding='utf-8') as f:
        # Imports et configuration
        f.write("""import os
import json
import sqlite3
import shutil
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DATABASE_PATH = 'instance/app.db'
BACKUP_DIR = f'static/backup_images_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

# Chemins alternatifs pour rechercher les images QCM Multichoix
ALTERNATIVE_PATHS = [
    'static/exercises/qcm_multichoix/',
    'static/uploads/qcm_multichoix/',
    'static/uploads/exercises/qcm_multichoix/',
    'static/uploads/',
    'static/exercises/'
]

def ensure_directory_exists(directory):
    # Crée le répertoire s'il n'existe pas
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Répertoire créé: {directory}")

def backup_database():
    # Crée une sauvegarde de la base de données
    backup_path = f"instance/app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DATABASE_PATH, backup_path)
    logger.info(f"Base de données sauvegardée: {backup_path}")
    return backup_path

def find_image_in_alternative_paths(filename):
    # Recherche l'image dans les chemins alternatifs
    for path in ALTERNATIVE_PATHS:
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path):
            return full_path
    return None

def fix_qcm_multichoix_images():
    # Corrige les problèmes d'images QCM Multichoix
    print("=== Correction des problèmes d'images QCM Multichoix ===\\n")
    
    # 1. Créer les répertoires nécessaires
    ensure_directory_exists('static/exercises/qcm_multichoix')
    ensure_directory_exists('static/uploads/qcm_multichoix')
    ensure_directory_exists(BACKUP_DIR)
    
    # 2. Sauvegarder la base de données
    backup_path = backup_database()
    
    # 3. Connexion à la base de données
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        logger.info("Connexion à la base de données réussie")
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        return
    
    # 4. Récupérer tous les exercices QCM Multichoix
    try:
        cursor.execute("SELECT id, title, content, image_path FROM exercise WHERE exercise_type = 'qcm_multichoix'")
        exercises = cursor.fetchall()
        logger.info(f"{len(exercises)} exercices QCM Multichoix trouvés")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des exercices QCM Multichoix: {e}")
        return
    
    # 5. Traiter chaque exercice
    fixed_count = 0
    for exercise_id, title, content_json, db_image_path in exercises:
        print(f"\\nTraitement de l'exercice #{exercise_id}: {title}")
        
        try:
            # Déterminer le chemin d'image à utiliser
            image_path = db_image_path
            source = "image_path"
            
            if not image_path:
                # Vérifier dans le contenu JSON
                content = json.loads(content_json) if content_json else {}
                image_path = content.get('image', '')
                source = "content.image"
            
            if not image_path:
                print(f"  Pas d'image définie pour cet exercice")
                continue
            
            print(f"  Chemin d'image actuel ({source}): {image_path}")
            
            # Extraire le nom du fichier
            filename = os.path.basename(image_path)
            
            # Vérifier si l'image existe au chemin attendu
            expected_path = image_path
            if expected_path.startswith('/'):
                expected_path = expected_path[1:]
            
            if os.path.exists(expected_path):
                print(f"  ✅ L'image existe déjà au bon emplacement")
                continue
            
            # Rechercher l'image dans les chemins alternatifs
            alt_path = find_image_in_alternative_paths(filename)
            
            if alt_path:
                # Copier l'image vers le bon emplacement
                target_path = 'static/uploads/qcm_multichoix/' + filename
                shutil.copy2(alt_path, target_path)
                print(f"  ✅ Image copiée de {alt_path} vers {target_path}")
                
                # Mettre à jour le chemin dans la base de données
                new_path = '/static/uploads/qcm_multichoix/' + filename
                
                if source == "image_path":
                    cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", (new_path, exercise_id))
                else:
                    # Mettre à jour le champ image dans le contenu JSON
                    content = json.loads(content_json)
                    content['image'] = new_path
                    cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (json.dumps(content), exercise_id))
                
                conn.commit()
                print(f"  ✅ Chemin d'image mis à jour dans la base de données: {new_path}")
                fixed_count += 1
            else:
                print(f"  ❌ Image introuvable dans tous les chemins alternatifs")
        except Exception as e:
            print(f"  ❌ Erreur lors du traitement: {e}")
    
    # 6. Conclusion
    print("\\n=== Résumé ===")
    print(f"Base de données sauvegardée: {backup_path}")
    print(f"{fixed_count} exercices QCM Multichoix corrigés sur {len(exercises)}")
    print("Opération terminée.")

if __name__ == "__main__":
    fix_qcm_multichoix_images()
""")
    
    logger.info(f"Rapport généré: {report_path}")
    logger.info(f"Script de correction généré: {fix_script_path}")
    return report_path, fix_script_path

def main():
    """Fonction principale."""
    logger.info("Début de la vérification des images QCM Multichoix")
    logger.info(f"Fichier de log: {log_file}")
    
    # Vérifier si l'URL de production a été configurée
    if BASE_URL == 'https://votre-application-production.com':
        logger.warning("L'URL de production n'a pas été configurée. La vérification distante sera désactivée.")
        logger.warning("Pour activer la vérification distante, modifiez la variable BASE_URL dans le script.")
    
    # Exécuter la vérification
    issues = verify_qcm_multichoix_images()
    
    # Générer le rapport et le script de correction
    report_path, fix_script_path = generate_report(issues)
    
    # Afficher un résumé final
    if issues:
        logger.warning(f"Vérification terminée avec {len(issues)} problèmes détectés.")
        logger.warning(f"Consultez le rapport {report_path} pour plus de détails.")
        logger.warning(f"Exécutez le script {fix_script_path} pour corriger automatiquement les problèmes.")
    else:
        logger.info("Vérification terminée avec succès. Aucun problème détecté.")
    
    logger.info("Fin de la vérification des images QCM Multichoix")

if __name__ == "__main__":
    main()
