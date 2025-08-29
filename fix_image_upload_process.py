#!/usr/bin/env python3
"""
Script pour corriger le processus d'upload d'images et éviter les fichiers de 0 bytes
"""

import os
import sys
import shutil
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Exercise
from app import app

def create_image_upload_fix():
    """Créer un patch pour corriger le processus d'upload d'images"""
    
    patch_content = '''
def safe_file_save(file, filepath):
    """Sauvegarder un fichier de manière sécurisée avec vérification de taille"""
    try:
        # Créer le répertoire parent s'il n'existe pas
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Sauvegarder le fichier
        file.save(filepath)
        
        # Vérifier que le fichier a été sauvegardé correctement
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            current_app.logger.info(f"[UPLOAD_SUCCESS] Fichier sauvegardé: {filepath} ({os.path.getsize(filepath)} bytes)")
            return True
        else:
            current_app.logger.error(f"[UPLOAD_ERROR] Fichier vide ou non sauvegardé: {filepath}")
            # Supprimer le fichier vide s'il existe
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
    except Exception as e:
        current_app.logger.error(f"[UPLOAD_ERROR] Erreur lors de la sauvegarde: {str(e)}")
        return False

def generate_consistent_image_path(filename):
    """Générer un chemin d'image cohérent"""
    return f'/static/uploads/{filename}'
'''
    
    return patch_content

def fix_existing_zero_byte_files():
    """Identifier et supprimer les fichiers de 0 bytes"""
    
    print("=== NETTOYAGE DES FICHIERS VIDES ===\n")
    
    uploads_dir = Path("static/uploads")
    removed_files = []
    
    for file_path in uploads_dir.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size == 0 and file_path.name != '.gitkeep':
            try:
                file_path.unlink()
                removed_files.append(str(file_path))
                print(f"Supprimé: {file_path}")
            except Exception as e:
                print(f"Erreur suppression {file_path}: {e}")
    
    print(f"\nTotal fichiers vides supprimés: {len(removed_files)}")
    return removed_files

def create_upload_test_page():
    """Créer une page de test pour l'upload d'images"""
    
    test_page_content = '''
@app.route('/test_upload', methods=['GET', 'POST'])
def test_upload():
    """Page de test pour l'upload d'images"""
    if request.method == 'POST':
        if 'test_image' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        file = request.files['test_image']
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = generate_unique_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Utiliser la fonction sécurisée
            if safe_file_save(file, filepath):
                image_path = f'/static/uploads/{filename}'
                flash(f'Image uploadée avec succès: {image_path}', 'success')
                return render_template('test_upload.html', uploaded_image=image_path)
            else:
                flash('Erreur lors de l\\'upload de l\\'image', 'error')
        else:
            flash('Type de fichier non autorisé', 'error')
    
    return render_template('test_upload.html')
'''
    
    # Créer le template de test
    template_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Test Upload Images</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h2>Test Upload Images</h2>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST" enctype="multipart/form-data" class="mb-4">
            <div class="mb-3">
                <label for="test_image" class="form-label">Sélectionner une image</label>
                <input type="file" class="form-control" id="test_image" name="test_image" accept="image/*" required>
            </div>
            <button type="submit" class="btn btn-primary">Upload Test</button>
        </form>
        
        {% if uploaded_image %}
        <div class="card">
            <div class="card-header">
                <h5>Image uploadée</h5>
            </div>
            <div class="card-body">
                <img src="{{ uploaded_image }}" class="img-fluid" style="max-width: 500px;">
                <p class="mt-2"><strong>Chemin:</strong> {{ uploaded_image }}</p>
            </div>
        </div>
        {% endif %}
        
        <a href="{{ url_for('index') }}" class="btn btn-secondary mt-3">Retour</a>
    </div>
</body>
</html>
'''
    
    # Sauvegarder le template
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)
    
    with open(template_dir / "test_upload.html", "w", encoding="utf-8") as f:
        f.write(template_content)
    
    return test_page_content, template_content

def main():
    """Fonction principale"""
    
    print("CORRECTION DU PROCESSUS D'UPLOAD D'IMAGES\n")
    
    # 1. Nettoyer les fichiers vides
    removed = fix_existing_zero_byte_files()
    
    # 2. Créer le patch pour l'upload sécurisé
    patch = create_image_upload_fix()
    
    # 3. Créer la page de test
    test_route, test_template = create_upload_test_page()
    
    print("\n=== SOLUTIONS CRÉÉES ===")
    print("1. Fichiers vides supprimés")
    print("2. Fonction safe_file_save() créée")
    print("3. Page de test d'upload créée (/test_upload)")
    
    print("\n=== ACTIONS REQUISES ===")
    print("1. Ajouter la fonction safe_file_save() dans app.py")
    print("2. Remplacer tous les file.save() par safe_file_save()")
    print("3. Utiliser generate_consistent_image_path() pour les chemins")
    print("4. Tester l'upload avec /test_upload")
    
    # Sauvegarder les patches dans des fichiers
    with open("upload_patch.py", "w", encoding="utf-8") as f:
        f.write(patch)
    
    with open("test_upload_route.py", "w", encoding="utf-8") as f:
        f.write(test_route)
    
    print("\nFichiers créés:")
    print("- upload_patch.py (fonctions à ajouter)")
    print("- test_upload_route.py (route de test)")
    print("- templates/test_upload.html (template de test)")

if __name__ == "__main__":
    main()
