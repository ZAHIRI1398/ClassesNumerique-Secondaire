"""
Script de test pour vérifier que la correction des chemins d'images dans les exercices image_labeling
fonctionne correctement.

Ce script:
1. Crée un exercice image_labeling de test
2. Vérifie que le chemin d'image commence par '/static/'
3. Vérifie que exercise.image_path est synchronisé avec content['main_image']
4. Affiche un rapport détaillé des résultats
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy

# Créer une application Flask minimale pour le test
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Définir le modèle Exercise pour le test
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    exercise_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f"<Exercise {self.id}: {self.title}>"

def run_test():
    """Exécute le test de vérification des chemins d'images"""
    print("\n=== TEST DE VÉRIFICATION DES CHEMINS D'IMAGES DANS LES EXERCICES IMAGE_LABELING ===\n")
    
    with app.app_context():
        # 1. Récupérer tous les exercices de type image_labeling
        exercises = Exercise.query.filter_by(exercise_type='image_labeling').all()
        
        if not exercises:
            print("Aucun exercice image_labeling trouvé dans la base de données.")
            print("Créez d'abord un exercice image_labeling pour tester la correction.")
            return False
        
        print(f"Nombre d'exercices image_labeling trouvés: {len(exercises)}")
        print("\nAnalyse des chemins d'images...\n")
        
        results = []
        
        # 2. Analyser chaque exercice
        for exercise in exercises:
            result = {
                'id': exercise.id,
                'title': exercise.title,
                'image_path': exercise.image_path,
                'content_main_image': None,
                'path_normalized': False,
                'paths_synchronized': False
            }
            
            # Extraire main_image du contenu JSON
            try:
                content = json.loads(exercise.content)
                if 'main_image' in content:
                    result['content_main_image'] = content['main_image']
                    
                    # Vérifier si le chemin commence par '/static/'
                    if result['content_main_image'].startswith('/static/'):
                        result['path_normalized'] = True
                    
                    # Vérifier si exercise.image_path est synchronisé avec content['main_image']
                    if result['image_path'] == result['content_main_image']:
                        result['paths_synchronized'] = True
            except:
                result['content_main_image'] = "ERROR: Impossible de décoder le JSON"
            
            results.append(result)
        
        # 3. Afficher les résultats
        print("=== RÉSULTATS DE L'ANALYSE ===\n")
        
        all_normalized = True
        all_synchronized = True
        
        for result in results:
            print(f"Exercice ID: {result['id']}")
            print(f"Titre: {result['title']}")
            print(f"exercise.image_path: {result['image_path']}")
            print(f"content['main_image']: {result['content_main_image']}")
            print(f"Chemin normalisé: {'✓' if result['path_normalized'] else '✗'}")
            print(f"Chemins synchronisés: {'✓' if result['paths_synchronized'] else '✗'}")
            print("-" * 50)
            
            if not result['path_normalized']:
                all_normalized = False
            if not result['paths_synchronized']:
                all_synchronized = False
        
        # 4. Résumé final
        print("\n=== RÉSUMÉ ===\n")
        print(f"Tous les chemins sont normalisés: {'✓' if all_normalized else '✗'}")
        print(f"Tous les chemins sont synchronisés: {'✓' if all_synchronized else '✗'}")
        
        if all_normalized and all_synchronized:
            print("\n✅ SUCCÈS: La correction des chemins d'images fonctionne correctement!")
            return True
        else:
            print("\n❌ ÉCHEC: Certains chemins d'images ne sont pas correctement normalisés ou synchronisés.")
            print("Vérifiez les détails ci-dessus et assurez-vous que la correction a été appliquée.")
            return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
