from flask import Blueprint, current_app, render_template_string, jsonify
import os
import json
from pathlib import Path
from models import Exercise

# Création du blueprint pour les routes de diagnostic et correction d'images
image_fix_bp = Blueprint('image_fix_display', __name__, url_prefix='/image-fix')

@image_fix_bp.route('/fix-uploads-directory')
def fix_uploads_directory():
    """Crée le répertoire static/uploads s'il n'existe pas en production"""
    try:
        # Chemin vers le répertoire static/uploads
        uploads_dir = os.path.join(current_app.static_folder, 'uploads')
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Vérifier si le répertoire existe maintenant
        exists = os.path.isdir(uploads_dir)
        
        return jsonify({
            'success': exists,
            'path': uploads_dir,
            'exists': exists,
            'message': f"Répertoire {'créé' if exists else 'non créé'}: {uploads_dir}"
        })
    except Exception as e:
        current_app.logger.error(f"[FIX_UPLOADS_DIR] Erreur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_fix_bp.route('/check-image-paths')
def check_image_paths():
    """Vérifie tous les chemins d'images dans la base de données et leur accessibilité"""
    try:
        # Récupérer tous les exercices avec des images
        exercises_with_images = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        
        results = []
        for ex in exercises_with_images:
            if not ex.image_path:
                continue
                
            # Analyser le chemin d'image
            image_path = ex.image_path
            
            # Vérifier si c'est une URL Cloudinary
            is_cloudinary = 'cloudinary.com' in image_path
            
            # Pour les chemins locaux, vérifier si le fichier existe
            file_exists = False
            local_path = None
            
            if not is_cloudinary and not image_path.startswith('http'):
                # Extraire le nom du fichier
                filename = image_path.split('/')[-1]
                
                # Construire le chemin local complet
                local_path = os.path.join(current_app.static_folder, 'uploads', filename)
                
                # Vérifier si le fichier existe
                file_exists = os.path.isfile(local_path)
            
            # Ajouter les résultats
            results.append({
                'exercise_id': ex.id,
                'title': ex.title,
                'image_path': image_path,
                'is_cloudinary': is_cloudinary,
                'local_path': local_path,
                'file_exists': file_exists,
                'normalized_path': f"/static/uploads/{image_path.split('/')[-1]}" if not is_cloudinary else image_path
            })
        
        # Générer un rapport HTML
        html_report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Diagnostic des chemins d'images</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .status-ok { color: green; }
                .status-error { color: red; }
            </style>
        </head>
        <body>
            <div class="container mt-4">
                <h1>Diagnostic des chemins d'images</h1>
                <p>Nombre d'exercices avec images: {{ results|length }}</p>
                
                <div class="mb-4">
                    <h2>Résumé</h2>
                    <ul>
                        <li>Images Cloudinary: {{ cloudinary_count }}</li>
                        <li>Images locales: {{ local_count }}</li>
                        <li>Images locales manquantes: {{ missing_count }}</li>
                    </ul>
                </div>
                
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Titre</th>
                            <th>Chemin d'image</th>
                            <th>Type</th>
                            <th>Statut</th>
                            <th>Chemin normalisé</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for result in results %}
                        <tr>
                            <td>{{ result.exercise_id }}</td>
                            <td>{{ result.title }}</td>
                            <td><code>{{ result.image_path }}</code></td>
                            <td>{{ 'Cloudinary' if result.is_cloudinary else 'Local' }}</td>
                            <td class="{{ 'status-ok' if result.is_cloudinary or result.file_exists else 'status-error' }}">
                                {{ 'OK' if result.is_cloudinary or result.file_exists else 'Manquant' }}
                            </td>
                            <td><code>{{ result.normalized_path }}</code></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        # Compter les différents types d'images
        cloudinary_count = sum(1 for r in results if r['is_cloudinary'])
        local_count = sum(1 for r in results if not r['is_cloudinary'])
        missing_count = sum(1 for r in results if not r['is_cloudinary'] and not r['file_exists'])
        
        return render_template_string(
            html_report, 
            results=results,
            cloudinary_count=cloudinary_count,
            local_count=local_count,
            missing_count=missing_count
        )
        
    except Exception as e:
        current_app.logger.error(f"[CHECK_IMAGE_PATHS] Erreur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_fix_bp.route('/create-placeholder-images')
def create_placeholder_images():
    """Crée des images placeholder pour les images manquantes"""
    try:
        # Vérifier si Pillow est installé
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            return jsonify({
                'success': False,
                'error': "Pillow n'est pas installé. Exécutez 'pip install Pillow'"
            }), 500
            
        # Récupérer tous les exercices avec des images
        exercises_with_images = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        
        # Chemin vers le répertoire static/uploads
        uploads_dir = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        created_images = []
        for ex in exercises_with_images:
            if not ex.image_path:
                continue
                
            # Ignorer les URLs Cloudinary
            if 'cloudinary.com' in ex.image_path or ex.image_path.startswith('http'):
                continue
                
            # Extraire le nom du fichier
            filename = ex.image_path.split('/')[-1]
            
            # Construire le chemin local complet
            local_path = os.path.join(uploads_dir, filename)
            
            # Vérifier si le fichier existe déjà
            if os.path.isfile(local_path):
                continue
                
            # Créer une image placeholder
            img = Image.new('RGB', (800, 600), color=(240, 240, 240))
            d = ImageDraw.Draw(img)
            
            # Dessiner un cadre
            d.rectangle([(20, 20), (780, 580)], outline=(200, 200, 200), width=2)
            
            # Ajouter du texte
            try:
                # Essayer d'utiliser une police système
                font = ImageFont.truetype("arial.ttf", 30)
            except:
                # Fallback sur la police par défaut
                font = ImageFont.load_default()
                
            # Texte d'information
            d.text((400, 250), f"Image placeholder", fill=(100, 100, 100), font=font, anchor="mm")
            d.text((400, 300), f"Exercice #{ex.id}: {ex.title}", fill=(100, 100, 100), font=font, anchor="mm")
            d.text((400, 350), f"Fichier: {filename}", fill=(100, 100, 100), font=font, anchor="mm")
            
            # Sauvegarder l'image
            img.save(local_path)
            created_images.append({
                'exercise_id': ex.id,
                'title': ex.title,
                'filename': filename,
                'path': local_path
            })
            
        return jsonify({
            'success': True,
            'created_count': len(created_images),
            'created_images': created_images
        })
        
    except Exception as e:
        current_app.logger.error(f"[CREATE_PLACEHOLDER_IMAGES] Erreur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Fonction pour intégrer le blueprint dans l'application
def register_image_fix_routes(app):
    # Vérifier si le blueprint est déjà enregistré
    if 'image_fix_display' not in [bp.name for bp in app.blueprints.values()]:
        app.register_blueprint(image_fix_bp)
        app.logger.info("Routes de diagnostic et correction d'images enregistrées")
    else:
        app.logger.info("Routes de diagnostic d'images déjà enregistrées")
