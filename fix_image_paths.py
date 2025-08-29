from flask import Blueprint, current_app, render_template_string, jsonify, request, redirect, url_for, flash
import os
import json
from pathlib import Path
from models import Exercise, db
import cloud_storage

# Création du blueprint pour les routes de synchronisation et correction d'images
image_sync_bp = Blueprint('image_sync', __name__, url_prefix='/image-sync')

@image_sync_bp.route('/sync-image-paths')
def sync_image_paths():
    """Synchronise les chemins d'images entre exercise.image_path et content.main_image"""
    try:
        # Récupérer tous les exercices avec des images
        exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        
        results = {
            'total': len(exercises),
            'updated': 0,
            'already_synced': 0,
            'errors': 0,
            'details': []
        }
        
        for ex in exercises:
            try:
                # Récupérer le contenu JSON
                content = ex.get_content()
                if not content:
                    content = {}
                
                # Vérifier si l'exercice a un chemin d'image
                if ex.image_path:
                    # Normaliser le chemin avec get_cloudinary_url
                    normalized_path = cloud_storage.get_cloudinary_url(ex.image_path)
                    
                    # Vérifier si content.main_image existe et est différent
                    if 'main_image' not in content or content['main_image'] != normalized_path:
                        # Sauvegarder l'ancienne valeur pour le rapport
                        old_value = content.get('main_image', 'None')
                        
                        # Mettre à jour content.main_image
                        content['main_image'] = normalized_path
                        ex.set_content(content)
                        
                        # Sauvegarder les modifications
                        db.session.commit()
                        
                        results['updated'] += 1
                        results['details'].append({
                            'exercise_id': ex.id,
                            'title': ex.title,
                            'old_main_image': old_value,
                            'new_main_image': normalized_path,
                            'image_path': ex.image_path,
                            'status': 'updated'
                        })
                    else:
                        results['already_synced'] += 1
                        results['details'].append({
                            'exercise_id': ex.id,
                            'title': ex.title,
                            'main_image': content.get('main_image'),
                            'image_path': ex.image_path,
                            'status': 'already_synced'
                        })
            except Exception as e:
                current_app.logger.error(f"[SYNC_IMAGE_PATHS] Erreur pour l'exercice {ex.id}: {str(e)}")
                results['errors'] += 1
                results['details'].append({
                    'exercise_id': ex.id,
                    'title': ex.title,
                    'error': str(e),
                    'status': 'error'
                })
        
        # Générer un rapport HTML
        html_report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Synchronisation des chemins d'images</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .status-ok { color: green; }
                .status-updated { color: blue; }
                .status-error { color: red; }
            </style>
        </head>
        <body>
            <div class="container mt-4">
                <h1>Synchronisation des chemins d'images</h1>
                
                <div class="mb-4">
                    <h2>Résumé</h2>
                    <ul>
                        <li>Total d'exercices traités: {{ results.total }}</li>
                        <li>Exercices mis à jour: {{ results.updated }}</li>
                        <li>Exercices déjà synchronisés: {{ results.already_synced }}</li>
                        <li>Erreurs: {{ results.errors }}</li>
                    </ul>
                </div>
                
                <h2>Détails</h2>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Titre</th>
                            <th>Image Path</th>
                            <th>Main Image (avant)</th>
                            <th>Main Image (après)</th>
                            <th>Statut</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for detail in results.details %}
                        <tr>
                            <td>{{ detail.exercise_id }}</td>
                            <td>{{ detail.title }}</td>
                            <td><code>{{ detail.image_path }}</code></td>
                            <td>
                                {% if detail.status == 'updated' %}
                                <code>{{ detail.old_main_image }}</code>
                                {% else %}
                                <code>{{ detail.main_image }}</code>
                                {% endif %}
                            </td>
                            <td>
                                {% if detail.status == 'updated' %}
                                <code>{{ detail.new_main_image }}</code>
                                {% else %}
                                <code>{{ detail.main_image }}</code>
                                {% endif %}
                            </td>
                            <td class="status-{{ detail.status }}">
                                {{ detail.status }}
                                {% if detail.error %}
                                <br><small>{{ detail.error }}</small>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_report, results=results)
        
    except Exception as e:
        current_app.logger.error(f"[SYNC_IMAGE_PATHS] Erreur générale: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_sync_bp.route('/fix-template-paths')
def fix_template_paths():
    """Vérifie et corrige les chemins d'images dans les templates"""
    try:
        templates_dir = os.path.join(current_app.root_path, 'templates', 'exercise_types')
        
        results = {
            'checked': [],
            'fixed': [],
            'errors': []
        }
        
        # Liste des templates à vérifier
        templates = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
        
        for template_name in templates:
            template_path = os.path.join(templates_dir, template_name)
            try:
                with open(template_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Vérifier si le template utilise url_for('static', filename='uploads/...')
                if "url_for('static', filename='uploads/" in content or 'url_for("static", filename="uploads/' in content:
                    # Remplacer par cloud_storage.get_cloudinary_url
                    new_content = content.replace("url_for('static', filename='uploads/", "cloud_storage.get_cloudinary_url(")
                    new_content = new_content.replace('url_for("static", filename="uploads/', 'cloud_storage.get_cloudinary_url(')
                    new_content = new_content.replace("')", "')")
                    new_content = new_content.replace('")', '")')
                    
                    # Sauvegarder le fichier modifié
                    with open(template_path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    
                    results['fixed'].append({
                        'template': template_name,
                        'path': template_path,
                        'status': 'fixed'
                    })
                else:
                    results['checked'].append({
                        'template': template_name,
                        'path': template_path,
                        'status': 'ok'
                    })
            except Exception as e:
                results['errors'].append({
                    'template': template_name,
                    'path': template_path,
                    'error': str(e),
                    'status': 'error'
                })
        
        # Générer un rapport HTML
        html_report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Correction des chemins dans les templates</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .status-ok { color: green; }
                .status-fixed { color: blue; }
                .status-error { color: red; }
            </style>
        </head>
        <body>
            <div class="container mt-4">
                <h1>Correction des chemins dans les templates</h1>
                
                <div class="mb-4">
                    <h2>Résumé</h2>
                    <ul>
                        <li>Templates vérifiés: {{ results.checked|length + results.fixed|length }}</li>
                        <li>Templates corrigés: {{ results.fixed|length }}</li>
                        <li>Erreurs: {{ results.errors|length }}</li>
                    </ul>
                </div>
                
                <h2>Templates corrigés</h2>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Template</th>
                            <th>Chemin</th>
                            <th>Statut</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in results.fixed %}
                        <tr>
                            <td>{{ item.template }}</td>
                            <td><code>{{ item.path }}</code></td>
                            <td class="status-fixed">{{ item.status }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <h2>Templates vérifiés (déjà corrects)</h2>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Template</th>
                            <th>Chemin</th>
                            <th>Statut</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in results.checked %}
                        <tr>
                            <td>{{ item.template }}</td>
                            <td><code>{{ item.path }}</code></td>
                            <td class="status-ok">{{ item.status }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                {% if results.errors %}
                <h2>Erreurs</h2>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Template</th>
                            <th>Chemin</th>
                            <th>Erreur</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in results.errors %}
                        <tr>
                            <td>{{ item.template }}</td>
                            <td><code>{{ item.path }}</code></td>
                            <td class="status-error">{{ item.error }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_report, results=results)
        
    except Exception as e:
        current_app.logger.error(f"[FIX_TEMPLATE_PATHS] Erreur générale: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_sync_bp.route('/check-image-consistency')
def check_image_consistency():
    """Vérifie la cohérence entre exercise.image_path et content.main_image"""
    try:
        # Récupérer tous les exercices
        exercises = Exercise.query.all()
        
        results = {
            'total': len(exercises),
            'consistent': 0,
            'inconsistent': 0,
            'no_image': 0,
            'details': []
        }
        
        for ex in exercises:
            try:
                # Récupérer le contenu JSON
                content = ex.get_content()
                
                # Cas 1: Pas d'image du tout
                if not ex.image_path and (not content or 'main_image' not in content or not content['main_image']):
                    results['no_image'] += 1
                    continue
                
                # Cas 2: Image dans exercise.image_path mais pas dans content.main_image
                if ex.image_path and (not content or 'main_image' not in content or not content['main_image']):
                    results['inconsistent'] += 1
                    results['details'].append({
                        'exercise_id': ex.id,
                        'title': ex.title,
                        'image_path': ex.image_path,
                        'main_image': None,
                        'status': 'missing_main_image'
                    })
                    continue
                
                # Cas 3: Image dans content.main_image mais pas dans exercise.image_path
                if (not ex.image_path or ex.image_path == '') and content and 'main_image' in content and content['main_image']:
                    results['inconsistent'] += 1
                    results['details'].append({
                        'exercise_id': ex.id,
                        'title': ex.title,
                        'image_path': None,
                        'main_image': content['main_image'],
                        'status': 'missing_image_path'
                    })
                    continue
                
                # Cas 4: Les deux sont présents mais différents
                if ex.image_path and content and 'main_image' in content and content['main_image']:
                    # Normaliser les deux chemins pour comparaison
                    normalized_image_path = cloud_storage.get_cloudinary_url(ex.image_path)
                    normalized_main_image = cloud_storage.get_cloudinary_url(content['main_image'])
                    
                    if normalized_image_path != normalized_main_image:
                        results['inconsistent'] += 1
                        results['details'].append({
                            'exercise_id': ex.id,
                            'title': ex.title,
                            'image_path': ex.image_path,
                            'normalized_image_path': normalized_image_path,
                            'main_image': content['main_image'],
                            'normalized_main_image': normalized_main_image,
                            'status': 'different_paths'
                        })
                    else:
                        results['consistent'] += 1
                else:
                    # Cas 5: Les deux sont présents et identiques
                    results['consistent'] += 1
                
            except Exception as e:
                current_app.logger.error(f"[CHECK_IMAGE_CONSISTENCY] Erreur pour l'exercice {ex.id}: {str(e)}")
                results['details'].append({
                    'exercise_id': ex.id,
                    'title': ex.title,
                    'error': str(e),
                    'status': 'error'
                })
        
        # Générer un rapport HTML
        html_report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cohérence des chemins d'images</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .status-ok { color: green; }
                .status-warning { color: orange; }
                .status-error { color: red; }
            </style>
        </head>
        <body>
            <div class="container mt-4">
                <h1>Cohérence des chemins d'images</h1>
                
                <div class="mb-4">
                    <h2>Résumé</h2>
                    <ul>
                        <li>Total d'exercices: {{ results.total }}</li>
                        <li>Exercices cohérents: {{ results.consistent }}</li>
                        <li>Exercices incohérents: {{ results.inconsistent }}</li>
                        <li>Exercices sans image: {{ results.no_image }}</li>
                    </ul>
                </div>
                
                <h2>Détails des incohérences</h2>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Titre</th>
                            <th>Image Path</th>
                            <th>Main Image</th>
                            <th>Problème</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for detail in results.details %}
                        <tr>
                            <td>{{ detail.exercise_id }}</td>
                            <td>{{ detail.title }}</td>
                            <td>
                                {% if detail.image_path %}
                                <code>{{ detail.image_path }}</code>
                                {% if detail.normalized_image_path %}
                                <br><small>Normalisé: {{ detail.normalized_image_path }}</small>
                                {% endif %}
                                {% else %}
                                <span class="text-danger">Manquant</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if detail.main_image %}
                                <code>{{ detail.main_image }}</code>
                                {% if detail.normalized_main_image %}
                                <br><small>Normalisé: {{ detail.normalized_main_image }}</small>
                                {% endif %}
                                {% else %}
                                <span class="text-danger">Manquant</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if detail.status == 'missing_main_image' %}
                                <span class="status-warning">Main Image manquant</span>
                                {% elif detail.status == 'missing_image_path' %}
                                <span class="status-warning">Image Path manquant</span>
                                {% elif detail.status == 'different_paths' %}
                                <span class="status-warning">Chemins différents</span>
                                {% elif detail.status == 'error' %}
                                <span class="status-error">Erreur: {{ detail.error }}</span>
                                {% endif %}
                            </td>
                            <td>
                                <a href="{{ url_for('image_sync.fix_single_exercise', exercise_id=detail.exercise_id) }}" class="btn btn-sm btn-primary">Corriger</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_report, results=results)
        
    except Exception as e:
        current_app.logger.error(f"[CHECK_IMAGE_CONSISTENCY] Erreur générale: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_sync_bp.route('/fix-single-exercise/<int:exercise_id>')
def fix_single_exercise(exercise_id):
    """Corrige la cohérence des chemins d'images pour un exercice spécifique"""
    try:
        # Récupérer l'exercice
        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Récupérer le contenu JSON
        content = exercise.get_content() or {}
        
        # Déterminer la source de vérité
        # Priorité à exercise.image_path s'il existe
        if exercise.image_path:
            # Normaliser le chemin
            normalized_path = cloud_storage.get_cloudinary_url(exercise.image_path)
            
            # Mettre à jour content.main_image
            content['main_image'] = normalized_path
            exercise.set_content(content)
            
            message = f"Mise à jour de content.main_image avec {normalized_path}"
        elif content and 'main_image' in content and content['main_image']:
            # Si seulement content.main_image existe, l'utiliser comme source
            normalized_path = cloud_storage.get_cloudinary_url(content['main_image'])
            
            # Mettre à jour exercise.image_path
            exercise.image_path = normalized_path
            
            # S'assurer que content.main_image est également normalisé
            content['main_image'] = normalized_path
            exercise.set_content(content)
            
            message = f"Mise à jour de exercise.image_path avec {normalized_path}"
        else:
            # Aucune image disponible
            message = "Aucune image disponible pour cet exercice"
        
        # Sauvegarder les modifications
        db.session.commit()
        
        return jsonify({
            'success': True,
            'exercise_id': exercise.id,
            'title': exercise.title,
            'image_path': exercise.image_path,
            'main_image': content.get('main_image'),
            'message': message
        })
        
    except Exception as e:
        current_app.logger.error(f"[FIX_SINGLE_EXERCISE] Erreur pour l'exercice {exercise_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_sync_bp.route('/create-simple-placeholders')
def create_simple_placeholders():
    """Crée des images placeholder SVG simples pour les images manquantes (sans dépendance à Pillow)"""
    try:
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
                
            # Créer une image SVG placeholder
            svg_content = f"""<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="#f0f0f0"/>
                <rect x="20" y="20" width="760" height="560" stroke="#cccccc" stroke-width="2" fill="none"/>
                <text x="400" y="250" font-family="Arial" font-size="30" text-anchor="middle" fill="#666666">Image placeholder</text>
                <text x="400" y="300" font-family="Arial" font-size="24" text-anchor="middle" fill="#666666">Exercice #{ex.id}: {ex.title}</text>
                <text x="400" y="350" font-family="Arial" font-size="18" text-anchor="middle" fill="#666666">Fichier: {filename}</text>
            </svg>"""
            
            # Sauvegarder l'image SVG
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
                
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
        current_app.logger.error(f"[CREATE_SIMPLE_PLACEHOLDERS] Erreur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_sync_bp.route('/fix-edit-image-display')
def fix_edit_image_display():
    """Corrige le problème d'affichage des images lors de l'édition d'exercices
    en s'assurant que exercise.image_path est toujours synchronisé avec content['image'] ou content['main_image']"""
    try:
        # Récupérer tous les exercices
        exercises = Exercise.query.all()
        
        results = {
            'total': len(exercises),
            'updated': 0,
            'already_synced': 0,
            'no_image': 0,
            'errors': 0,
            'details': []
        }
        
        for ex in exercises:
            try:
                # Récupérer le contenu JSON
                content = ex.get_content() or {}
                
                # Cas 1: Pas d'image du tout
                if not ex.image_path and not content.get('image') and not content.get('main_image'):
                    results['no_image'] += 1
                    continue
                
                # Cas 2: Image dans exercise.image_path mais pas dans content
                if ex.image_path and not content.get('image') and not content.get('main_image'):
                    # Mettre à jour content avec l'image de exercise.image_path
                    normalized_path = cloud_storage.get_cloudinary_url(ex.image_path)
                    content['main_image'] = normalized_path
                    ex.set_content(content)
                    
                    results['updated'] += 1
                    results['details'].append({
                        'exercise_id': ex.id,
                        'title': ex.title,
                        'action': 'Ajout de main_image dans content',
                        'image_path': ex.image_path,
                        'main_image': normalized_path,
                        'status': 'updated'
                    })
                    continue
                
                # Cas 3: Image dans content mais pas dans exercise.image_path
                image_in_content = content.get('image') or content.get('main_image')
                if image_in_content and not ex.image_path:
                    # Mettre à jour exercise.image_path avec l'image de content
                    normalized_path = cloud_storage.get_cloudinary_url(image_in_content)
                    ex.image_path = normalized_path
                    
                    # S'assurer que main_image est défini et cohérent
                    content['main_image'] = normalized_path
                    ex.set_content(content)
                    
                    results['updated'] += 1
                    results['details'].append({
                        'exercise_id': ex.id,
                        'title': ex.title,
                        'action': 'Ajout de image_path depuis content',
                        'image_path': normalized_path,
                        'main_image': normalized_path,
                        'status': 'updated'
                    })
                    continue
                
                # Cas 4: Les deux sont présents mais différents
                if ex.image_path and image_in_content:
                    # Normaliser les deux chemins pour comparaison
                    normalized_image_path = cloud_storage.get_cloudinary_url(ex.image_path)
                    normalized_content_image = cloud_storage.get_cloudinary_url(image_in_content)
                    
                    if normalized_image_path != normalized_content_image:
                        # Priorité à exercise.image_path
                        content['main_image'] = normalized_image_path
                        ex.set_content(content)
                        
                        results['updated'] += 1
                        results['details'].append({
                            'exercise_id': ex.id,
                            'title': ex.title,
                            'action': 'Synchronisation des chemins différents',
                            'image_path': ex.image_path,
                            'old_main_image': normalized_content_image,
                            'new_main_image': normalized_image_path,
                            'status': 'updated'
                        })
                    else:
                        results['already_synced'] += 1
                else:
                    # Cas 5: Les deux sont présents et identiques
                    results['already_synced'] += 1
                
            except Exception as e:
                current_app.logger.error(f"[FIX_EDIT_IMAGE_DISPLAY] Erreur pour l'exercice {ex.id}: {str(e)}")
                results['errors'] += 1
                results['details'].append({
                    'exercise_id': ex.id,
                    'title': ex.title,
                    'error': str(e),
                    'status': 'error'
                })
        
        # Sauvegarder toutes les modifications
        db.session.commit()
        
        # Générer un rapport HTML
        html_report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Correction de l'affichage des images en édition</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .status-ok { color: green; }
                .status-updated { color: blue; }
                .status-error { color: red; }
            </style>
        </head>
        <body>
            <div class="container mt-4">
                <h1>Correction de l'affichage des images en édition</h1>
                
                <div class="mb-4">
                    <h2>Résumé</h2>
                    <ul>
                        <li>Total d'exercices: {{ results.total }}</li>
                        <li>Exercices mis à jour: {{ results.updated }}</li>
                        <li>Exercices déjà synchronisés: {{ results.already_synced }}</li>
                        <li>Exercices sans image: {{ results.no_image }}</li>
                        <li>Erreurs: {{ results.errors }}</li>
                    </ul>
                </div>
                
                <h2>Détails des mises à jour</h2>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Titre</th>
                            <th>Action</th>
                            <th>Image Path</th>
                            <th>Main Image</th>
                            <th>Statut</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for detail in results.details %}
                        <tr>
                            <td>{{ detail.exercise_id }}</td>
                            <td>{{ detail.title }}</td>
                            <td>{{ detail.action }}</td>
                            <td>
                                <code>{{ detail.image_path }}</code>
                            </td>
                            <td>
                                {% if detail.old_main_image %}
                                <code>{{ detail.old_main_image }}</code> → <code>{{ detail.new_main_image }}</code>
                                {% else %}
                                <code>{{ detail.main_image }}</code>
                                {% endif %}
                            </td>
                            <td class="status-{{ detail.status }}">
                                {{ detail.status }}
                                {% if detail.error %}
                                <br><small>{{ detail.error }}</small>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="mt-4">
                    <a href="{{ url_for('image_sync.check_image_consistency') }}" class="btn btn-primary">Vérifier la cohérence des images</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_report, results=results)
        
    except Exception as e:
        current_app.logger.error(f"[FIX_EDIT_IMAGE_DISPLAY] Erreur générale: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_sync_bp.route('/fix-image-labeling')
def fix_image_labeling():
    """Corrige l'incohérence entre exercise.image_path et content['main_image'] pour les exercices de type image_labeling"""
    try:
        # Récupérer tous les exercices de type image_labeling
        exercises = Exercise.query.filter_by(exercise_type='image_labeling').all()
        
        results = {
            'total': len(exercises),
            'updated': 0,
            'already_synced': 0,
            'no_image': 0,
            'errors': 0,
            'details': []
        }
        
        for ex in exercises:
            try:
                # Récupérer le contenu JSON
                try:
                    content = json.loads(ex.content) if ex.content else {}
                except:
                    content = {}
                
                if not isinstance(content, dict):
                    content = {}
                
                # Cas 1: content['main_image'] existe mais pas exercise.image_path
                if content.get('main_image') and not ex.image_path:
                    # Normaliser le chemin de l'image
                    normalized_path = normalize_image_path(content['main_image'])
                    
                    # Mettre à jour exercise.image_path
                    ex.image_path = normalized_path
                    
                    # Mettre à jour content['main_image'] avec le chemin normalisé
                    content['main_image'] = normalized_path
                    ex.content = json.dumps(content)
                    
                    results['updated'] += 1
                    results['details'].append({
                        'exercise_id': ex.id,
                        'title': ex.title,
                        'action': 'Ajout de exercise.image_path',
                        'image_path': normalized_path,
                        'old_main_image': content.get('main_image'),
                        'new_main_image': normalized_path,
                        'status': 'updated'
                    })
                
                # Cas 2: exercise.image_path existe mais pas content['main_image']
                elif ex.image_path and not content.get('main_image'):
                    # Normaliser le chemin de l'image
                    normalized_path = normalize_image_path(ex.image_path)
                    
                    # Mettre à jour content['main_image']
                    content['main_image'] = normalized_path
                    ex.content = json.dumps(content)
                    
                    # Mettre à jour exercise.image_path avec le chemin normalisé
                    ex.image_path = normalized_path
                    
                    results['updated'] += 1
                    results['details'].append({
                        'exercise_id': ex.id,
                        'title': ex.title,
                        'action': 'Ajout de content[main_image]',
                        'image_path': normalized_path,
                        'old_main_image': None,
                        'new_main_image': normalized_path,
                        'status': 'updated'
                    })
                
                # Cas 3: Les deux existent mais sont différents
                elif ex.image_path and content.get('main_image') and ex.image_path != content['main_image']:
                    # Normaliser le chemin de l'image (priorité à content['main_image'])
                    normalized_path = normalize_image_path(content['main_image'])
                    
                    # Mettre à jour exercise.image_path
                    ex.image_path = normalized_path
                    
                    # Mettre à jour content['main_image'] avec le chemin normalisé
                    content['main_image'] = normalized_path
                    ex.content = json.dumps(content)
                    
                    results['updated'] += 1
                    results['details'].append({
                        'exercise_id': ex.id,
                        'title': ex.title,
                        'action': 'Synchronisation des chemins',
                        'image_path': normalized_path,
                        'old_main_image': content.get('main_image'),
                        'new_main_image': normalized_path,
                        'status': 'updated'
                    })
                
                # Cas 4: Aucune image
                elif not ex.image_path and not content.get('main_image'):
                    results['no_image'] += 1
                
                # Cas 5: Les deux sont présents et identiques
                else:
                    results['already_synced'] += 1
                    results['details'].append({
                        'exercise_id': ex.id,
                        'title': ex.title,
                        'action': 'Déjà synchronisé',
                        'image_path': ex.image_path,
                        'main_image': content.get('main_image'),
                        'status': 'ok'
                    })
            
            except Exception as e:
                current_app.logger.error(f"[FIX_IMAGE_LABELING] Erreur pour l'exercice {ex.id}: {str(e)}")
                results['errors'] += 1
                results['details'].append({
                    'exercise_id': ex.id,
                    'title': ex.title,
                    'error': str(e),
                    'status': 'error'
                })
        
        # Sauvegarder toutes les modifications
        db.session.commit()
        
        # Générer un rapport HTML
        html_report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Correction des exercices d'étiquetage d'image</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .status-ok { color: green; }
                .status-updated { color: blue; }
                .status-error { color: red; }
            </style>
        </head>
        <body>
            <div class="container mt-4">
                <h1>Correction des exercices d'étiquetage d'image</h1>
                
                <div class="mb-4">
                    <h2>Résumé</h2>
                    <ul>
                        <li>Total d'exercices: {{ results.total }}</li>
                        <li>Exercices mis à jour: {{ results.updated }}</li>
                        <li>Exercices déjà synchronisés: {{ results.already_synced }}</li>
                        <li>Exercices sans image: {{ results.no_image }}</li>
                        <li>Erreurs: {{ results.errors }}</li>
                    </ul>
                </div>
                
                <h2>Détails des mises à jour</h2>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Titre</th>
                            <th>Action</th>
                            <th>Image Path</th>
                            <th>Main Image</th>
                            <th>Statut</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for detail in results.details %}
                        <tr>
                            <td>{{ detail.exercise_id }}</td>
                            <td>{{ detail.title }}</td>
                            <td>{{ detail.action }}</td>
                            <td>
                                <code>{{ detail.image_path }}</code>
                            </td>
                            <td>
                                {% if detail.old_main_image %}
                                <code>{{ detail.old_main_image }}</code> → <code>{{ detail.new_main_image }}</code>
                                {% else %}
                                <code>{{ detail.main_image }}</code>
                                {% endif %}
                            </td>
                            <td class="status-{{ detail.status }}">
                                {{ detail.status }}
                                {% if detail.error %}
                                <br><small>{{ detail.error }}</small>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="mt-4">
                    <a href="{{ url_for('image_sync.check_image_consistency') }}" class="btn btn-primary">Vérifier la cohérence des images</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_report, results=results)
        
    except Exception as e:
        current_app.logger.error(f"[FIX_IMAGE_LABELING] Erreur générale: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Fonction pour normaliser les chemins d'image
def normalize_image_path(path):
    """Normalise le chemin d'image pour assurer la cohérence"""
    if not path:
        return None
    
    # Si c'est déjà un chemin relatif commençant par /static/
    if path.startswith('/static/'):
        return path
    
    # Si c'est un chemin relatif sans /static/
    if not path.startswith('/'):
        # Si c'est un chemin d'image pour les exercices d'étiquetage
        if 'exercises/image_labeling/' in path or path.startswith('exercises/image_labeling/'):
            return f'/static/uploads/{path}'
        
        # Si c'est un chemin d'image standard pour les exercices
        if 'exercises/' in path or path.startswith('exercises/'):
            return f'/static/uploads/{path}'
    
    return path

# Fonction pour intégrer le blueprint dans l'application
def register_image_sync_routes(app):
    # Vérifier si le blueprint est déjà enregistré
    if 'image_sync' not in app.blueprints:
        app.register_blueprint(image_sync_bp, url_prefix='/image-sync')
        app.logger.info("Routes de synchronisation et correction d'images enregistrées")
    else:
        app.logger.info("Routes de synchronisation d'images déjà enregistrées")
