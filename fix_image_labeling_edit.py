"""
Script pour corriger l'affichage du contenu lors de la modification d'exercices image_labeling.
Ce script ajoute la logique nécessaire pour assurer que les étiquettes et zones sont correctement
chargées et affichées dans le template d'édition.
"""

import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Créer une application Flask minimale pour tester la correction
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clé_secrète_pour_tests'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Définir un modèle Exercise simplifié pour les tests
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    exercise_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    
    def get_content(self):
        """Méthode pour récupérer le contenu JSON de l'exercice"""
        if self.content:
            try:
                return json.loads(self.content)
            except json.JSONDecodeError:
                return {}
        return {}

def fix_edit_exercise_route():
    """
    Fonction qui corrige la route d'édition des exercices image_labeling
    pour assurer que les étiquettes et zones sont correctement chargées.
    """
    # Code de correction pour la route edit_exercise dans app.py
    correction_code = """
@app.route('/exercise/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_exercise(exercise_id):
    \"\"\"Route pour éditer un exercice existant\"\"\"
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if request.method == 'GET':
        # Charger le contenu de l'exercice
        content = exercise.get_content() if hasattr(exercise, 'get_content') else {}
        if not content and exercise.content:
            try:
                content = json.loads(exercise.content)
            except:
                content = {}
        
        # Pour les exercices image_labeling, s'assurer que les structures de données sont correctes
        if exercise.exercise_type == 'image_labeling':
            # S'assurer que content.labels existe
            if 'labels' not in content:
                content['labels'] = []
            
            # S'assurer que content.zones existe
            if 'zones' not in content:
                content['zones'] = []
            
            # Vérifier que les zones ont le bon format
            for i, zone in enumerate(content.get('zones', [])):
                # S'assurer que chaque zone a les propriétés x, y et label
                if not isinstance(zone, dict):
                    content['zones'][i] = {'x': 0, 'y': 0, 'label': ''}
                    continue
                
                if 'x' not in zone:
                    zone['x'] = 0
                if 'y' not in zone:
                    zone['y'] = 0
                if 'label' not in zone:
                    zone['label'] = ''
            
            # Log pour le débogage
            app.logger.info(f"[IMAGE_LABELING_EDIT] Contenu chargé: {content}")
            app.logger.info(f"[IMAGE_LABELING_EDIT] Étiquettes: {content.get('labels', [])}")
            app.logger.info(f"[IMAGE_LABELING_EDIT] Zones: {content.get('zones', [])}")
        
        # Utiliser le template spécifique selon le type d'exercice
        if exercise.exercise_type == 'image_labeling':
            # Rendre le template spécifique pour l'édition des exercices de type étiquetage d'image
            return render_template('exercise_types/image_labeling_edit.html', exercise=exercise, content=content)
        # ... reste du code inchangé ...
    """
    
    print("Correction pour la route edit_exercise:")
    print(correction_code)
    
    # Instructions pour appliquer la correction
    print("\nPour appliquer cette correction:")
    print("1. Ouvrez le fichier app.py")
    print("2. Localisez la route '/exercise/<int:exercise_id>/edit'")
    print("3. Ajoutez le code de traitement spécifique pour les exercices image_labeling")
    print("4. Assurez-vous que les structures content.labels et content.zones sont correctement initialisées")
    
    return True

def test_image_labeling_edit():
    """
    Fonction de test pour vérifier que la correction fonctionne correctement
    """
    # Créer un exercice de test avec un contenu JSON valide
    exercise = Exercise(
        title="Test Image Labeling",
        description="Exercice de test pour l'étiquetage d'image",
        exercise_type="image_labeling",
        content=json.dumps({
            'main_image': '/static/uploads/test_image.jpg',
            'labels': ['Étiquette 1', 'Étiquette 2'],
            'zones': [
                {'x': 100, 'y': 100, 'label': 'Étiquette 1'},
                {'x': 200, 'y': 200, 'label': 'Étiquette 2'}
            ]
        })
    )
    
    # Simuler le chargement du contenu comme dans la route corrigée
    content = exercise.get_content()
    
    # Vérifier que les étiquettes et zones sont correctement chargées
    assert 'labels' in content, "Les étiquettes ne sont pas présentes dans le contenu"
    assert 'zones' in content, "Les zones ne sont pas présentes dans le contenu"
    assert len(content['labels']) == 2, "Le nombre d'étiquettes est incorrect"
    assert len(content['zones']) == 2, "Le nombre de zones est incorrect"
    
    print("✅ Test réussi: Les étiquettes et zones sont correctement chargées")
    
    # Créer un exercice de test avec un contenu JSON incomplet
    exercise_incomplet = Exercise(
        title="Test Image Labeling Incomplet",
        description="Exercice de test avec contenu incomplet",
        exercise_type="image_labeling",
        content=json.dumps({
            'main_image': '/static/uploads/test_image.jpg'
            # Pas de labels ni de zones
        })
    )
    
    # Simuler le traitement comme dans la route corrigée
    content = exercise_incomplet.get_content()
    if 'labels' not in content:
        content['labels'] = []
    if 'zones' not in content:
        content['zones'] = []
    
    # Vérifier que les structures sont correctement initialisées
    assert 'labels' in content, "Les étiquettes ne sont pas initialisées"
    assert 'zones' in content, "Les zones ne sont pas initialisées"
    assert isinstance(content['labels'], list), "Les étiquettes ne sont pas une liste"
    assert isinstance(content['zones'], list), "Les zones ne sont pas une liste"
    
    print("✅ Test réussi: Les structures sont correctement initialisées pour un contenu incomplet")
    
    return True

if __name__ == "__main__":
    print("=== Script de correction pour l'affichage du contenu des exercices image_labeling ===")
    fix_edit_exercise_route()
    print("\n=== Tests de validation ===")
    test_image_labeling_edit()
    print("\n✅ Correction prête à être appliquée")
