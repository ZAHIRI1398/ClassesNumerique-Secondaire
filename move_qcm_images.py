import os
import sqlite3
import shutil
from datetime import datetime

# Configuration
DATABASE_PATH = 'instance/app.db'
QCM_UPLOAD_DIR = 'static/uploads/qcm'
EXERCISES_QCM_DIR = 'static/uploads/exercises/qcm'
BACKUP_DIR = f'static/backup_images_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

def ensure_directory_exists(directory):
    """Crée le répertoire s'il n'existe pas"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[INFO] Répertoire créé: {directory}")

def backup_database():
    """Crée une sauvegarde de la base de données"""
    backup_path = f"instance/app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DATABASE_PATH, backup_path)
    print(f"[INFO] Base de données sauvegardée: {backup_path}")
    return backup_path

def move_qcm_images():
    """
    Script pour déplacer les images QCM vers les bons répertoires
    et mettre à jour les chemins dans la base de données
    """
    print("=== Déplacement des images QCM vers les bons répertoires ===")
    
    # 1. Créer les répertoires nécessaires
    ensure_directory_exists(EXERCISES_QCM_DIR)
    ensure_directory_exists(BACKUP_DIR)
    
    # 2. Sauvegarder la base de données
    backup_path = backup_database()
    
    # 3. Connexion à la base de données
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        print("[INFO] Connexion à la base de données réussie")
    except Exception as e:
        print(f"[ERREUR] Erreur de connexion à la base de données: {e}")
        return
    
    # 4. Récupération des exercices QCM
    try:
        cursor.execute("SELECT id, title, image_path FROM exercise WHERE exercise_type = 'qcm'")
        qcm_exercises = cursor.fetchall()
        print(f"[INFO] {len(qcm_exercises)} exercices QCM trouvés")
        
        if not qcm_exercises:
            print("[ATTENTION] Aucun exercice QCM trouvé dans la base de données")
            return
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la récupération des exercices QCM: {e}")
        return
    
    # 5. Traitement des exercices QCM
    updates_count = 0
    for exercise_id, title, image_path in qcm_exercises:
        print(f"\nTraitement de l'exercice #{exercise_id}: {title}")
        print(f"  Chemin d'image actuel: {image_path}")
        
        # Vérifier si le chemin est défini
        if not image_path:
            print(f"  [ATTENTION] Pas de chemin d'image défini pour l'exercice #{exercise_id}")
            continue
        
        # Extraire le nom du fichier
        filename = os.path.basename(image_path)
        
        # Définir le nouveau chemin
        new_path = f"/static/uploads/exercises/qcm/{filename}"
        
        # Vérifier si le fichier existe physiquement
        source_paths = [
            image_path.replace('/static/', 'static/'),  # Chemin actuel sans le préfixe /static/
            f"static/uploads/qcm/{filename}",           # Dossier QCM
            f"static/uploads/{filename}",               # Dossier uploads général
            f"static/uploads/exercises/{filename}"      # Dossier exercises général
        ]
        
        source_path = None
        for path in source_paths:
            if os.path.exists(path):
                source_path = path
                print(f"  [INFO] Fichier image trouvé: {path}")
                break
        
        if not source_path:
            print(f"  [ERREUR] Fichier image non trouvé dans aucun chemin")
            continue
        
        # Créer le chemin de destination
        dest_path = f"static/uploads/exercises/qcm/{filename}"
        
        # Copier l'image vers le bon répertoire
        try:
            # Ne pas copier si le fichier est déjà au bon endroit
            if source_path != dest_path:
                shutil.copy2(source_path, dest_path)
                print(f"  [INFO] Image copiée de {source_path} vers {dest_path}")
            else:
                print(f"  [INFO] L'image est déjà au bon endroit: {dest_path}")
        except Exception as e:
            print(f"  [ERREUR] Erreur lors de la copie de l'image: {e}")
            continue
        
        # Mettre à jour le chemin dans la base de données
        try:
            if image_path != new_path:
                cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", (new_path, exercise_id))
                conn.commit()
                print(f"  [INFO] Chemin d'image mis à jour dans la base de données: {new_path}")
                updates_count += 1
            else:
                print(f"  [INFO] Le chemin d'image est déjà correct dans la base de données")
        except Exception as e:
            print(f"  [ERREUR] Erreur lors de la mise à jour du chemin d'image: {e}")
    
    # 6. Déplacer les images orphelines du dossier QCM vers le dossier de sauvegarde
    if os.path.exists(QCM_UPLOAD_DIR):
        qcm_images = os.listdir(QCM_UPLOAD_DIR)
        moved_count = 0
        
        for img in qcm_images:
            # Vérifier si l'image est utilisée par un exercice
            cursor.execute("SELECT COUNT(*) FROM exercise WHERE image_path LIKE ?", (f"%{img}%",))
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Image orpheline, la déplacer vers le dossier de sauvegarde
                try:
                    source = os.path.join(QCM_UPLOAD_DIR, img)
                    dest = os.path.join(BACKUP_DIR, img)
                    shutil.move(source, dest)
                    moved_count += 1
                    print(f"  [INFO] Image orpheline déplacée vers la sauvegarde: {img}")
                except Exception as e:
                    print(f"  [ERREUR] Erreur lors du déplacement de l'image orpheline {img}: {e}")
        
        print(f"\n[INFO] {moved_count} images orphelines déplacées vers {BACKUP_DIR}")
    
    # 7. Conclusion
    print("\n=== Résumé ===")
    print(f"Base de données sauvegardée: {backup_path}")
    print(f"{updates_count} chemins d'images mis à jour dans la base de données")
    print(f"Les images sont maintenant correctement organisées dans {EXERCISES_QCM_DIR}")
    print("Opération terminée avec succès.")

if __name__ == "__main__":
    move_qcm_images()
