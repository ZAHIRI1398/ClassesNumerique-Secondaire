"""
Script de migration des images locales vers Cloudinary
"""

import os
import sys
import json
import time
import argparse
from flask import Flask, current_app
from models import db, Exercise
import cloud_storage
from tabulate import tabulate

def create_app():
    """Crée une instance minimale de l'application Flask pour accéder à la base de données"""
    app = Flask(__name__)
    
    # Charger la configuration depuis config.py
    try:
        app.config.from_pyfile('config.py')
    except:
        print("Erreur: Impossible de charger config.py")
        sys.exit(1)
    
    # Initialiser la base de données
    db.init_app(app)
    
    return app

def migrate_images_to_cloudinary(dry_run=True, batch_size=10, sleep_time=1):
    """
    Migre les images locales vers Cloudinary
    
    Args:
        dry_run: Si True, n'effectue pas réellement la migration
        batch_size: Nombre d'images à migrer par lot
        sleep_time: Temps d'attente entre chaque lot (en secondes)
    """
    app = create_app()
    
    with app.app_context():
        # Configurer Cloudinary
        if not cloud_storage.configure_cloudinary():
            print("Erreur: Impossible de configurer Cloudinary")
            print("Vérifiez vos variables d'environnement CLOUDINARY_*")
            sys.exit(1)
        
        print("✅ Cloudinary configuré avec succès")
        
        # Récupérer tous les exercices avec des images locales
        exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        
        local_images = []
        for ex in exercises:
            if not ex.image_path:
                continue
                
            # Ignorer les URLs Cloudinary et externes
            if 'cloudinary.com' in ex.image_path or ex.image_path.startswith('http'):
                continue
                
            # Extraire le nom du fichier
            filename = ex.image_path.split('/')[-1]
            
            # Construire le chemin local complet
            local_path = os.path.join(current_app.static_folder, 'uploads', filename)
            
            # Vérifier si le fichier existe
            file_exists = os.path.isfile(local_path)
            
            local_images.append({
                'exercise_id': ex.id,
                'title': ex.title,
                'image_path': ex.image_path,
                'local_path': local_path,
                'file_exists': file_exists
            })
        
        print(f"Trouvé {len(local_images)} images locales à migrer vers Cloudinary")
        
        if not local_images:
            print("Aucune image à migrer")
            return
        
        # Afficher un tableau des images à migrer
        table_data = []
        for img in local_images[:10]:  # Limiter à 10 pour l'affichage
            table_data.append([
                img['exercise_id'],
                img['title'][:30] + '...' if len(img['title']) > 30 else img['title'],
                img['image_path'],
                '✅' if img['file_exists'] else '❌'
            ])
        
        print("\nAperçu des images à migrer:")
        print(tabulate(table_data, headers=["ID", "Titre", "Chemin", "Existe"], tablefmt="grid"))
        
        if len(local_images) > 10:
            print(f"... et {len(local_images) - 10} autres images")
        
        if dry_run:
            print("\n⚠️ Mode simulation activé, aucune modification ne sera effectuée")
            print("Pour effectuer la migration réelle, exécutez avec --no-dry-run")
            return
        
        # Confirmer la migration
        if input("\nConfirmer la migration vers Cloudinary ? (o/N) ").lower() != 'o':
            print("Migration annulée")
            return
        
        # Migrer les images par lots
        successful = 0
        failed = 0
        results = []
        
        for i in range(0, len(local_images), batch_size):
            batch = local_images[i:i+batch_size]
            print(f"\nMigration du lot {i//batch_size + 1}/{(len(local_images) + batch_size - 1)//batch_size}...")
            
            for img in batch:
                if not img['file_exists']:
                    print(f"❌ Image manquante: {img['local_path']}")
                    failed += 1
                    results.append({
                        'exercise_id': img['exercise_id'],
                        'status': 'failed',
                        'error': 'Image manquante'
                    })
                    continue
                
                try:
                    # Ouvrir le fichier image
                    with open(img['local_path'], 'rb') as f:
                        # Uploader vers Cloudinary
                        cloudinary_url = cloud_storage.upload_to_cloudinary(f, folder='uploads')
                        
                        if not cloudinary_url:
                            print(f"❌ Échec d'upload pour l'exercice #{img['exercise_id']}")
                            failed += 1
                            results.append({
                                'exercise_id': img['exercise_id'],
                                'status': 'failed',
                                'error': 'Échec d\'upload vers Cloudinary'
                            })
                            continue
                        
                        # Mettre à jour l'exercice avec l'URL Cloudinary
                        exercise = Exercise.query.get(img['exercise_id'])
                        old_path = exercise.image_path
                        exercise.image_path = cloudinary_url
                        db.session.commit()
                        
                        print(f"✅ Exercice #{img['exercise_id']} migré: {old_path} → {cloudinary_url}")
                        successful += 1
                        results.append({
                            'exercise_id': img['exercise_id'],
                            'status': 'success',
                            'old_path': old_path,
                            'new_path': cloudinary_url
                        })
                        
                except Exception as e:
                    print(f"❌ Erreur pour l'exercice #{img['exercise_id']}: {str(e)}")
                    failed += 1
                    results.append({
                        'exercise_id': img['exercise_id'],
                        'status': 'failed',
                        'error': str(e)
                    })
            
            # Attendre entre les lots pour éviter de surcharger l'API Cloudinary
            if i + batch_size < len(local_images):
                print(f"Attente de {sleep_time} secondes avant le prochain lot...")
                time.sleep(sleep_time)
        
        # Afficher un résumé
        print("\n=== Résumé de la migration ===")
        print(f"Total: {len(local_images)} images")
        print(f"Réussies: {successful} images")
        print(f"Échouées: {failed} images")
        
        # Sauvegarder les résultats dans un fichier JSON
        with open('migration_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("\nRésultats détaillés sauvegardés dans migration_results.json")

def upload_to_cloudinary(file, folder='uploads'):
    """
    Upload un fichier vers Cloudinary
    
    Args:
        file: Fichier ouvert en mode binaire
        folder: Dossier de destination sur Cloudinary
        
    Returns:
        str: URL Cloudinary du fichier uploadé ou None en cas d'erreur
    """
    try:
        import cloudinary.uploader
        
        # Upload vers Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto"
        )
        
        return result['secure_url']
    except Exception as e:
        print(f"Erreur lors de l'upload vers Cloudinary: {str(e)}")
        return None

if __name__ == "__main__":
    # Ajouter la fonction upload_to_cloudinary à cloud_storage
    cloud_storage.upload_to_cloudinary = upload_to_cloudinary
    
    parser = argparse.ArgumentParser(description="Migrer les images locales vers Cloudinary")
    parser.add_argument("--no-dry-run", action="store_true", help="Effectuer réellement la migration")
    parser.add_argument("--batch-size", type=int, default=10, help="Nombre d'images à migrer par lot")
    parser.add_argument("--sleep-time", type=int, default=1, help="Temps d'attente entre chaque lot (en secondes)")
    args = parser.parse_args()
    
    migrate_images_to_cloudinary(
        dry_run=not args.no_dry_run,
        batch_size=args.batch_size,
        sleep_time=args.sleep_time
    )
