"""
Script de test pour vérifier la fonctionnalité d'affichage des images lors de l'édition d'exercices.
Ce script permet de tester localement les corrections apportées au problème d'affichage des images.
"""

import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Exercise, User
import cloud_storage
from fix_image_paths import register_image_sync_routes

# Configuration de l'application de test
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_image_display.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['TESTING'] = True

# Initialisation de la base de données
db.init_app(app)

# Enregistrement des routes de synchronisation d'images
register_image_sync_routes(app)

@app.route('/')
def index():
    """Page d'accueil du test"""
    exercises = Exercise.query.all()
    return render_template('test_image_display.html', exercises=exercises)

@app.route('/test/create-sample-exercises')
def create_sample_exercises():
    """Crée des exercices de test avec différentes configurations d'images"""
    try:
        # Créer un utilisateur de test si nécessaire
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(
                email='test@example.com',
                username='testuser',
                role='teacher'
            )
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
        
        # Cas 1: Exercice avec image_path mais sans content['image']
        exercise1 = Exercise(
            title="Test 1 - image_path uniquement",
            description="Exercice avec image_path mais sans content['image']",
            subject="Test",
            exercise_type="qcm",
            teacher_id=user.id,
            image_path="/static/uploads/test1.png",
            content=json.dumps({
                "questions": [
                    {"text": "Question de test", "choices": ["Option 1", "Option 2"], "correct_answer": 0}
                ]
            })
        )
        
        # Cas 2: Exercice avec content['image'] mais sans image_path
        exercise2 = Exercise(
            title="Test 2 - content['image'] uniquement",
            description="Exercice avec content['image'] mais sans image_path",
            subject="Test",
            exercise_type="qcm",
            teacher_id=user.id,
            image_path=None,
            content=json.dumps({
                "image": "/static/uploads/test2.png",
                "questions": [
                    {"text": "Question de test", "choices": ["Option 1", "Option 2"], "correct_answer": 0}
                ]
            })
        )
        
        # Cas 3: Exercice avec image_path et content['image'] identiques
        exercise3 = Exercise(
            title="Test 3 - Les deux identiques",
            description="Exercice avec image_path et content['image'] identiques",
            subject="Test",
            exercise_type="qcm",
            teacher_id=user.id,
            image_path="/static/uploads/test3.png",
            content=json.dumps({
                "image": "/static/uploads/test3.png",
                "questions": [
                    {"text": "Question de test", "choices": ["Option 1", "Option 2"], "correct_answer": 0}
                ]
            })
        )
        
        # Cas 4: Exercice avec image_path et content['image'] différents
        exercise4 = Exercise(
            title="Test 4 - image_path et content['image'] différents",
            description="Exercice avec image_path et content['image'] différents",
            subject="Test",
            exercise_type="qcm",
            teacher_id=user.id,
            image_path="/static/uploads/test4a.png",
            content=json.dumps({
                "image": "/static/uploads/test4b.png",
                "questions": [
                    {"text": "Question de test", "choices": ["Option 1", "Option 2"], "correct_answer": 0}
                ]
            })
        )
        
        # Cas 5: Exercice sans image
        exercise5 = Exercise(
            title="Test 5 - Sans image",
            description="Exercice sans image",
            subject="Test",
            exercise_type="qcm",
            teacher_id=user.id,
            image_path=None,
            content=json.dumps({
                "questions": [
                    {"text": "Question de test", "choices": ["Option 1", "Option 2"], "correct_answer": 0}
                ]
            })
        )
        
        # Ajouter les exercices à la base de données
        db.session.add_all([exercise1, exercise2, exercise3, exercise4, exercise5])
        db.session.commit()
        
        # Créer des images de test si elles n'existent pas
        uploads_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        for i in range(1, 5):
            # Créer des images SVG simples pour les tests
            for suffix in ['', 'a', 'b']:
                filename = f"test{i}{suffix}.png"
                filepath = os.path.join(uploads_dir, filename)
                if not os.path.exists(filepath):
                    with open(filepath, 'w') as f:
                        f.write(f"""<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
                            <rect width="100%" height="100%" fill="#f0f0f0"/>
                            <text x="200" y="100" font-family="Arial" font-size="24" text-anchor="middle" fill="#333">
                                Test Image {i}{suffix}
                            </text>
                        </svg>""")
        
        return "Exercices de test créés avec succès!"
    except Exception as e:
        return f"Erreur lors de la création des exercices de test: {str(e)}"

@app.route('/test/run-fix')
def run_fix():
    """Exécute la correction des chemins d'images"""
    return redirect(url_for('image_sync.fix_edit_image_display'))

@app.route('/test/check-consistency')
def check_consistency():
    """Vérifie la cohérence des chemins d'images"""
    return redirect(url_for('image_sync.check_image_consistency'))

@app.route('/test/edit/<int:exercise_id>', methods=['GET', 'POST'])
def test_edit_exercise(exercise_id):
    """Simule l'édition d'un exercice pour tester l'affichage des images"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if request.method == 'POST':
        # Simuler la mise à jour de l'exercice
        exercise.title = request.form.get('title', exercise.title)
        exercise.description = request.form.get('description', exercise.description)
        
        # Gestion de l'image
        if 'exercise_image' in request.files:
            file = request.files['exercise_image']
            if file and file.filename != '':
                # Simuler l'upload d'image
                filename = f"uploaded_{exercise_id}.png"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Créer une image SVG simple
                with open(filepath, 'w') as f:
                    f.write(f"""<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="100%" fill="#e0f0e0"/>
                        <text x="200" y="100" font-family="Arial" font-size="24" text-anchor="middle" fill="#333">
                            Uploaded Image for Exercise {exercise_id}
                        </text>
                    </svg>""")
                
                # Mettre à jour l'exercice
                image_url = f"/static/uploads/{filename}"
                exercise.image_path = image_url
                
                # Mettre à jour le contenu
                content = json.loads(exercise.content) if exercise.content else {}
                content['image'] = image_url
                exercise.content = json.dumps(content)
        
        # Gestion de la suppression d'image
        if 'remove_exercise_image' in request.form and request.form['remove_exercise_image'] == 'true':
            # Supprimer l'image
            exercise.image_path = None
            
            # Mettre à jour le contenu
            content = json.loads(exercise.content) if exercise.content else {}
            if 'image' in content:
                del content['image']
            exercise.content = json.dumps(content)
        
        db.session.commit()
        flash('Exercice mis à jour avec succès!', 'success')
        return redirect(url_for('index'))
    
    # Afficher le formulaire d'édition
    content = json.loads(exercise.content) if exercise.content else {}
    return render_template('test_edit_exercise.html', exercise=exercise, content=content)

@app.route('/test/view/<int:exercise_id>')
def view_exercise(exercise_id):
    """Affiche un exercice pour vérifier l'affichage des images"""
    exercise = Exercise.query.get_or_404(exercise_id)
    content = json.loads(exercise.content) if exercise.content else {}
    return render_template('test_view_exercise.html', exercise=exercise, content=content)

@app.route('/test/reset-db')
def reset_db():
    """Réinitialise la base de données de test"""
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if os.path.exists(db_path):
        os.remove(db_path)
    
    with app.app_context():
        db.create_all()
    
    return "Base de données réinitialisée!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
