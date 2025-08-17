#!/usr/bin/env python3
"""
Script pour identifier et synchroniser les images manquantes en production Railway
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au path pour les imports
sys.path.append('.')

def check_local_images():
    """Vérifie les images présentes localement"""
    uploads_dir = Path('static/uploads')
    
    if not uploads_dir.exists():
        print("❌ Répertoire static/uploads n'existe pas localement")
        return []
    
    images = list(uploads_dir.glob('*.png')) + list(uploads_dir.glob('*.jpg')) + list(uploads_dir.glob('*.jpeg')) + list(uploads_dir.glob('*.gif'))
    
    print(f"📁 Images locales trouvées: {len(images)}")
    for img in images:
        print(f"  - {img.name}")
    
    return images

def check_database_references():
    """Vérifie les références d'images dans la base de données"""
    try:
        from app import app, db
        from models import Exercise
        
        with app.app_context():
            exercises_with_images = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
            
            print(f"🗄️ Exercices avec images dans la DB: {len(exercises_with_images)}")
            
            image_refs = []
            for ex in exercises_with_images:
                print(f"  - Exercice {ex.id}: {ex.title}")
                print(f"    Image path: {ex.image_path}")
                
                # Extraire le nom de fichier
                if ex.image_path:
                    if '/' in ex.image_path:
                        filename = ex.image_path.split('/')[-1]
                    else:
                        filename = ex.image_path
                    image_refs.append(filename)
                    print(f"    Fichier attendu: {filename}")
                print()
            
            return image_refs
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification DB: {e}")
        return []

def create_missing_images_route():
    """Crée une route Flask pour lister les images manquantes en production"""
    route_code = '''
@app.route('/check-missing-images')
def check_missing_images():
    """Route pour identifier les images manquantes en production Railway"""
    try:
        import os
        from pathlib import Path
        
        result = []
        result.append("<h2>DIAGNOSTIC IMAGES PRODUCTION RAILWAY</h2>")
        
        # 1. Vérifier le répertoire uploads
        uploads_dir = Path('static/uploads')
        result.append(f"<h3>1. Répertoire static/uploads</h3>")
        result.append(f"<p><strong>Existe:</strong> {uploads_dir.exists()}</p>")
        
        if uploads_dir.exists():
            files = list(uploads_dir.glob('*'))
            result.append(f"<p><strong>Fichiers présents:</strong> {len(files)}</p>")
            result.append("<ul>")
            for f in files:
                result.append(f"<li>{f.name}</li>")
            result.append("</ul>")
        
        # 2. Vérifier les références dans la DB
        result.append(f"<h3>2. Exercices avec images dans la base</h3>")
        exercises_with_images = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        result.append(f"<p><strong>Nombre d'exercices avec images:</strong> {len(exercises_with_images)}</p>")
        
        missing_images = []
        for ex in exercises_with_images:
            if ex.image_path:
                filename = ex.image_path.split('/')[-1] if '/' in ex.image_path else ex.image_path
                image_path = uploads_dir / filename
                
                result.append(f"<h4>Exercice {ex.id}: {ex.title}</h4>")
                result.append(f"<p><strong>Image path DB:</strong> {ex.image_path}</p>")
                result.append(f"<p><strong>Fichier attendu:</strong> {filename}</p>")
                result.append(f"<p><strong>Fichier existe:</strong> {image_path.exists()}</p>")
                
                if not image_path.exists():
                    missing_images.append(filename)
                    result.append(f"<p style='color: red;'><strong>❌ MANQUANT</strong></p>")
                else:
                    result.append(f"<p style='color: green;'><strong>✅ OK</strong></p>")
                result.append("<hr>")
        
        # 3. Résumé
        result.append(f"<h3>3. Résumé</h3>")
        result.append(f"<p><strong>Images manquantes:</strong> {len(missing_images)}</p>")
        if missing_images:
            result.append("<ul>")
            for img in missing_images:
                result.append(f"<li style='color: red;'>{img}</li>")
            result.append("</ul>")
        
        return "<br>".join(result)
        
    except Exception as e:
        return f"<h2>❌ Erreur:</h2><p>{str(e)}</p>"
'''
    
    print("📝 Code de route généré pour diagnostic images Railway")
    return route_code

def main():
    print("🔍 DIAGNOSTIC IMAGES LOCALES vs PRODUCTION RAILWAY")
    print("=" * 60)
    
    # Vérifier les images locales
    local_images = check_local_images()
    
    print("\n" + "=" * 60)
    
    # Vérifier les références DB
    db_refs = check_database_references()
    
    print("\n" + "=" * 60)
    
    # Générer la route de diagnostic
    route_code = create_missing_images_route()
    
    print("\n📋 PROCHAINES ÉTAPES:")
    print("1. Ajouter la route /check-missing-images dans app.py")
    print("2. Déployer sur Railway")
    print("3. Exécuter https://web-production-9a047.up.railway.app/check-missing-images")
    print("4. Identifier les images manquantes")
    print("5. Créer une stratégie de synchronisation des images")

if __name__ == "__main__":
    main()
