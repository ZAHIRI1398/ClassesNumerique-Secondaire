import os
import sys

def fix_image_labeling_creation():
    # Chemins possibles vers le fichier app.py
    possible_paths = [
        'app.py',
        'modified_submit.py',
        'production_code/ClassesNumerique-Secondaire-main/app.py',
        '../app.py'
    ]
    
    # Trouver le premier chemin valide
    app_file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            app_file_path = path
            print(f"[OK] Fichier trouve: {path}")
            break
    
    if not app_file_path:
        print("[ERREUR] Aucun fichier d'application trouve.")
        return False
    
    try:
        from fix_image_labeling_creation import fix_image_labeling_exercise_creation
        fix_image_labeling_exercise_creation(app_file_path)
        print("[SUCCES] Correction appliquee avec succes!")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'application de la correction: {e}")
        return False

if __name__ == "__main__":
    print("[INFO] Application de la correction pour l'affichage des images dans les exercices image_labeling...")
    success = fix_image_labeling_creation()
    if success:
        print("[SUCCES] Correction terminee avec succes.")
    else:
        print("[ERREUR] La correction a echoue.")
        sys.exit(1)
    