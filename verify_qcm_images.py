import os
import sys
import json
from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connexion directe à la base de données
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def verify_qcm_images():
    """
    Verifie les chemins d'images pour les exercices QCM dans la base de donnees.
    Identifie les problemes potentiels et suggere des corrections.
    """
    print("=== VERIFICATION DES IMAGES QCM ===")
    
    # Recuperer tous les exercices QCM
    query = text("SELECT id, title, exercise_type, image_path, content FROM exercise WHERE exercise_type = 'qcm'")
    result = db_session.execute(query)
    exercises = result.fetchall()
    
    print(f"Nombre d'exercices QCM trouves: {len(exercises)}")
    
    issues_found = 0
    for exercise in exercises:
        exercise_id = exercise[0]
        title = exercise[1]
        image_path = exercise[3]
        content_json = exercise[4]
        
        print(f"\n--- Exercice #{exercise_id}: {title} ---")
        
        # Analyser le contenu JSON
        try:
            content = json.loads(content_json) if content_json else {}
        except json.JSONDecodeError:
            print(f"ERREUR: Contenu JSON invalide pour l'exercice #{exercise_id}")
            issues_found += 1
            continue
        
        # Vérifier si l'image existe dans le contenu
        content_image = content.get('image')
        
        # Afficher les chemins d'image
        print(f"exercise.image_path: {image_path}")
        print(f"content.image: {content_image}")
        
        # Vérifier les problèmes potentiels
        issues = []
        
        # 1. Vérifier si les chemins d'image sont définis
        if not image_path and not content_image:
            issues.append("Aucun chemin d'image defini (ni dans exercise.image_path, ni dans content.image)")
        
        # 2. Vérifier si les chemins commencent par /static/
        if image_path and not image_path.startswith('/static/'):
            issues.append(f"Le chemin exercise.image_path ne commence pas par '/static/': {image_path}")
        
        if content_image and not content_image.startswith('/static/'):
            issues.append(f"Le chemin content.image ne commence pas par '/static/': {content_image}")
        
        # 3. Vérifier si les chemins sont cohérents entre eux
        if image_path and content_image and image_path != content_image:
            issues.append(f"Incoherence entre exercise.image_path et content.image")
        
        # 4. Vérifier si le fichier image existe physiquement
        if content_image:
            file_path = os.path.join(app.root_path, content_image.lstrip('/'))
            if not os.path.exists(file_path):
                issues.append(f"Le fichier image n'existe pas: {file_path}")
        
        # Afficher les problèmes trouvés
        if issues:
            print("PROBLEMES DETECTES:")
            for issue in issues:
                print(f"  - {issue}")
            issues_found += 1
        else:
            print("[OK] Aucun probleme detecte")
    
    print(f"\n=== RESUME ===")
    print(f"Exercices QCM verifies: {len(exercises)}")
    print(f"Exercices avec problemes: {issues_found}")
    
    return issues_found

def suggest_fixes():
    """
    Suggere des corrections pour les problemes d'images QCM courants
    """
    print("\n=== SUGGESTIONS DE CORRECTION ===")
    print("Pour corriger les problemes d'images QCM, vous pouvez:")
    
    print("\n1. Normaliser tous les chemins d'images:")
    print("   - Assurez-vous que tous les chemins commencent par '/static/'")
    print("   - Utilisez le format '/static/uploads/qcm/nom_fichier.png'")
    
    print("\n2. Synchroniser exercise.image_path et content.image:")
    print("   - Mettez à jour content.image pour qu'il corresponde à exercise.image_path")
    print("   - Ou utilisez uniquement content.image dans les templates")
    
    print("\n3. Vérifier l'existence des fichiers images:")
    print("   - Créez les images manquantes dans le dossier static/uploads/qcm/")
    print("   - Ou corrigez les chemins pour pointer vers des images existantes")
    
    print("\n4. Utiliser le script de correction automatique:")
    print("   - Exécutez fix_all_image_paths.py pour corriger automatiquement les chemins")
    print("   - Ou utilisez la route web /fix-all-image-paths (admin uniquement)")

if __name__ == "__main__":
    # Définir le chemin racine de l'application
    app.root_path = os.path.dirname(os.path.abspath(__file__))
    
    # Vérifier les images QCM
    issues_found = verify_qcm_images()
    
    # Si des problèmes ont été trouvés, suggérer des corrections
    if issues_found > 0:
        suggest_fixes()
    else:
        print("\nTous les exercices QCM ont des images correctement configurees!")
    
    # Fermer la session de base de données
    db_session.remove()
