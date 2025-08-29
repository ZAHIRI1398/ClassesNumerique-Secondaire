from flask import Flask, render_template_string, jsonify, request
import os
import sys
import shutil
from sqlalchemy import create_engine, text
import json

app = Flask(__name__)

# Chemin vers le répertoire du projet
project_dir = os.path.dirname(os.path.abspath(__file__))

# Configuration de la base de données
db_path = os.path.join(project_dir, 'instance', 'app.db')
db_uri = f'sqlite:///{db_path}'

# Création d'une connexion à la base de données
engine = create_engine(db_uri)

@app.route('/')
def index():
    """Page d'accueil avec liste des exercices QCM Multichoix"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, content, image_path FROM exercise WHERE exercise_type = 'qcm_multichoix'"))
        exercises = []
        for row in result:
            exercises.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'image_path': row[3]
            })
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Diagnostic QCM Multichoix</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .image-container img { max-width: 300px; height: auto; }
            .path-list { font-family: monospace; font-size: 0.8rem; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1>Diagnostic des images QCM Multichoix</h1>
            
            <div class="alert alert-info">
                <h4>Instructions</h4>
                <p>Cette page permet de diagnostiquer et corriger les problèmes d'affichage des images pour les exercices QCM Multichoix.</p>
                <p>Pour chaque exercice, vous pouvez voir l'image actuelle, les chemins alternatifs, et copier l'image vers le bon emplacement si nécessaire.</p>
            </div>
            
            {% if exercises %}
                <h2>{{ exercises|length }} exercice(s) QCM Multichoix trouvé(s)</h2>
                
                {% for exercise in exercises %}
                    <div class="card mb-4">
                        <div class="card-header">
                            <h3>Exercice #{{ exercise.id }}: {{ exercise.title }}</h3>
                        </div>
                        <div class="card-body">
                            <h4>Chemin d'image actuel</h4>
                            <p class="path-list">{{ exercise.image_path }}</p>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h4>Image actuelle</h4>
                                    <div class="image-container">
                                        <img src="{{ exercise.image_path }}?v={{ range(1000, 9999)|random }}" 
                                             alt="Image de l'exercice" 
                                             onerror="this.onerror=null; this.src='/static/images/placeholder-image.png'; this.style.opacity='0.7';">
                                    </div>
                                </div>
                                
                                <div class="col-md-6">
                                    <h4>Chemins alternatifs</h4>
                                    <div id="alt-paths-{{ exercise.id }}" class="path-list">
                                        Chargement des chemins alternatifs...
                                    </div>
                                    
                                    <h4 class="mt-3">Actions</h4>
                                    <form action="/fix-image-path" method="post" class="mb-2">
                                        <input type="hidden" name="exercise_id" value="{{ exercise.id }}">
                                        <button type="submit" class="btn btn-primary">Corriger le chemin d'image</button>
                                    </form>
                                    
                                    <form action="/copy-image" method="post">
                                        <input type="hidden" name="exercise_id" value="{{ exercise.id }}">
                                        <div class="mb-3">
                                            <label for="target_path_{{ exercise.id }}" class="form-label">Copier l'image vers:</label>
                                            <select name="target_path" id="target_path_{{ exercise.id }}" class="form-select">
                                                <option value="/static/uploads/qcm_multichoix/">static/uploads/qcm_multichoix/</option>
                                                <option value="/static/exercises/general/">static/exercises/general/</option>
                                                <option value="/static/exercises/qcm/">static/exercises/qcm/</option>
                                                <option value="/static/uploads/">static/uploads/</option>
                                            </select>
                                        </div>
                                        <button type="submit" class="btn btn-success">Copier l'image</button>
                                    </form>
                                </div>
                            </div>
                            
                            <h4 class="mt-4">Contenu JSON</h4>
                            <pre class="bg-light p-3">{{ exercise.content|tojson(indent=2) }}</pre>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <div class="alert alert-warning">
                    Aucun exercice QCM Multichoix trouvé dans la base de données.
                </div>
            {% endif %}
        </div>
        
        <script>
            // Fonction pour vérifier les chemins alternatifs
            function checkAlternativePaths(exerciseId, originalPath) {
                if (!originalPath) return;
                
                const filename = originalPath.split('/').pop();
                const altPaths = [
                    `/static/exercises/general/${filename}`,
                    `/static/uploads/qcm_multichoix/${filename}`,
                    `/static/uploads/${filename}`,
                    `/static/exercises/qcm/${filename}`,
                    `/static/exercises/${filename}`
                ];
                
                const altPathsContainer = document.getElementById(`alt-paths-${exerciseId}`);
                altPathsContainer.innerHTML = '';
                
                const ul = document.createElement('ul');
                altPathsContainer.appendChild(ul);
                
                altPaths.forEach(path => {
                    const li = document.createElement('li');
                    const img = new Image();
                    img.onload = function() {
                        li.innerHTML = `<span class="text-success">✓</span> ${path} <span class="badge bg-success">Trouvée</span>`;
                    };
                    img.onerror = function() {
                        li.innerHTML = `<span class="text-danger">✗</span> ${path} <span class="badge bg-danger">Non trouvée</span>`;
                    };
                    img.src = `${path}?v=${Math.random()}`;
                    
                    ul.appendChild(li);
                });
            }
            
            // Vérifier les chemins alternatifs pour chaque exercice
            {% for exercise in exercises %}
                checkAlternativePaths({{ exercise.id }}, "{{ exercise.image_path }}");
            {% endfor %}
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html, exercises=exercises)

@app.route('/fix-image-path', methods=['POST'])
def fix_image_path():
    """Corriger le chemin d'image pour un exercice"""
    exercise_id = request.form.get('exercise_id')
    
    if not exercise_id:
        return jsonify({'error': 'ID d\'exercice manquant'}), 400
    
    # Récupérer l'exercice
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, content, image_path FROM exercise WHERE id = :id"), 
                             {"id": exercise_id})
        exercise = None
        for row in result:
            exercise = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'image_path': row[3]
            }
    
    if not exercise:
        return jsonify({'error': 'Exercice non trouvé'}), 404
    
    # Vérifier si l'image existe
    image_path = exercise['image_path']
    if not image_path:
        return jsonify({'error': 'Pas d\'image associée à cet exercice'}), 400
    
    # Extraire le nom du fichier
    filename = os.path.basename(image_path)
    
    # Chercher l'image dans des chemins alternatifs
    alt_paths = [
        os.path.join('static', 'exercises', 'general', filename),
        os.path.join('static', 'uploads', 'qcm_multichoix', filename),
        os.path.join('static', 'uploads', filename),
        os.path.join('static', 'exercises', 'qcm', filename),
        os.path.join('static', 'exercises', filename)
    ]
    
    correct_path = None
    for alt_path in alt_paths:
        full_alt_path = os.path.join(project_dir, alt_path)
        if os.path.exists(full_alt_path):
            correct_path = f"/{alt_path.replace(os.sep, '/')}"
            break
    
    if not correct_path:
        return jsonify({'error': 'Image introuvable dans tous les chemins alternatifs'}), 404
    
    # Mettre à jour le chemin d'image dans la base de données
    try:
        with engine.connect() as conn:
            conn.execute(text("UPDATE exercise SET image_path = :path WHERE id = :id"), 
                        {"path": correct_path, "id": exercise_id})
            conn.commit()
        
        # Mettre à jour le chemin d'image dans le contenu JSON si nécessaire
        try:
            content = json.loads(exercise['content'])
            if 'image' in content:
                content['image'] = correct_path
                
                # Mettre à jour le contenu JSON dans la base de données
                with engine.connect() as conn:
                    conn.execute(text("UPDATE exercise SET content = :content WHERE id = :id"), 
                               {"content": json.dumps(content), "id": exercise_id})
                    conn.commit()
        except json.JSONDecodeError:
            pass
        
        return jsonify({
            'success': True, 
            'message': f'Chemin d\'image mis à jour: {correct_path}',
            'old_path': image_path,
            'new_path': correct_path
        })
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

@app.route('/copy-image', methods=['POST'])
def copy_image():
    """Copier l'image vers un nouvel emplacement"""
    exercise_id = request.form.get('exercise_id')
    target_path = request.form.get('target_path')
    
    if not exercise_id or not target_path:
        return jsonify({'error': 'Paramètres manquants'}), 400
    
    # Récupérer l'exercice
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, content, image_path FROM exercise WHERE id = :id"), 
                             {"id": exercise_id})
        exercise = None
        for row in result:
            exercise = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'image_path': row[3]
            }
    
    if not exercise:
        return jsonify({'error': 'Exercice non trouvé'}), 404
    
    # Vérifier si l'image existe
    image_path = exercise['image_path']
    if not image_path:
        return jsonify({'error': 'Pas d\'image associée à cet exercice'}), 400
    
    # Extraire le nom du fichier
    filename = os.path.basename(image_path)
    
    # Chercher l'image dans des chemins alternatifs
    alt_paths = [
        os.path.join('static', 'exercises', 'general', filename),
        os.path.join('static', 'uploads', 'qcm_multichoix', filename),
        os.path.join('static', 'uploads', filename),
        os.path.join('static', 'exercises', 'qcm', filename),
        os.path.join('static', 'exercises', filename)
    ]
    
    source_path = None
    for alt_path in alt_paths:
        full_alt_path = os.path.join(project_dir, alt_path)
        if os.path.exists(full_alt_path):
            source_path = full_alt_path
            break
    
    if not source_path:
        return jsonify({'error': 'Image source introuvable'}), 404
    
    # Créer le répertoire cible s'il n'existe pas
    target_dir = os.path.join(project_dir, target_path.lstrip('/'))
    os.makedirs(target_dir, exist_ok=True)
    
    # Copier l'image
    target_file = os.path.join(target_dir, filename)
    try:
        shutil.copy2(source_path, target_file)
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la copie: {str(e)}'}), 500
    
    # Mettre à jour le chemin d'image dans la base de données
    new_path = f"{target_path}{filename}"
    try:
        with engine.connect() as conn:
            conn.execute(text("UPDATE exercise SET image_path = :path WHERE id = :id"), 
                        {"path": new_path, "id": exercise_id})
            conn.commit()
        
        # Mettre à jour le chemin d'image dans le contenu JSON si nécessaire
        try:
            content = json.loads(exercise['content'])
            if 'image' in content:
                content['image'] = new_path
                
                # Mettre à jour le contenu JSON dans la base de données
                with engine.connect() as conn:
                    conn.execute(text("UPDATE exercise SET content = :content WHERE id = :id"), 
                               {"content": json.dumps(content), "id": exercise_id})
                    conn.commit()
        except json.JSONDecodeError:
            pass
        
        return jsonify({
            'success': True, 
            'message': f'Image copiée vers {new_path}',
            'old_path': image_path,
            'new_path': new_path
        })
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
