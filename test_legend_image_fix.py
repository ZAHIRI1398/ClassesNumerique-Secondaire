"""
Script de test pour valider la solution de correction des chemins d'images dans les exercices de type légende.
Ce script simule différents cas problématiques et vérifie que la correction fonctionne correctement.
"""

import os
import sys
import json
import shutil
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import tempfile
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_legend_image_fix')

class TestLegendImageFix(unittest.TestCase):
    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Créer une application Flask de test
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Utiliser une base de données SQLite en mémoire
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialiser la base de données
        self.db = SQLAlchemy(self.app)
        
        # Définir le modèle Exercise
        class Exercise(self.db.Model):
            __tablename__ = 'exercise'
            
            id = self.db.Column(self.db.Integer, primary_key=True)
            title = self.db.Column(self.db.String(255), nullable=False)
            exercise_type = self.db.Column(self.db.String(50), nullable=False)
            content = self.db.Column(self.db.Text)
            image_path = self.db.Column(self.db.String(255))
            
            def get_content(self):
                if self.content:
                    try:
                        return json.loads(self.content)
                    except json.JSONDecodeError:
                        return {}
                return {}
        
        self.Exercise = Exercise
        
        # Créer les tables
        with self.app.app_context():
            self.db.create_all()
            
            # Créer un répertoire temporaire pour les images
            self.static_dir = tempfile.mkdtemp()
            self.uploads_dir = os.path.join(self.static_dir, 'uploads')
            self.legend_dir = os.path.join(self.uploads_dir, 'legend')
            os.makedirs(self.legend_dir, exist_ok=True)
            
            # Créer quelques images de test
            self.create_test_image(os.path.join(self.uploads_dir, 'test1.jpg'))
            self.create_test_image(os.path.join(self.uploads_dir, 'test2.jpg'))
            self.create_test_image(os.path.join(self.legend_dir, 'test3.jpg'))
            
            # Créer des exercices de test avec différents problèmes
            self.create_test_exercises()
    
    def create_test_image(self, path):
        """Crée une image de test vide"""
        with open(path, 'wb') as f:
            f.write(b'TEST IMAGE CONTENT')
    
    def create_test_exercises(self):
        """Crée des exercices de test avec différents problèmes de chemins d'images"""
        with self.app.app_context():
            # Cas 1: Aucune image définie
            exercise1 = self.Exercise(
                title="Test 1 - Aucune image",
                exercise_type="legend",
                content=json.dumps({"instructions": "Instructions de test"})
            )
            
            # Cas 2: Seulement main_image est défini
            exercise2 = self.Exercise(
                title="Test 2 - Seulement main_image",
                exercise_type="legend",
                content=json.dumps({
                    "instructions": "Instructions de test",
                    "main_image": "uploads/test1.jpg"
                })
            )
            
            # Cas 3: Seulement image_path est défini
            exercise3 = self.Exercise(
                title="Test 3 - Seulement image_path",
                exercise_type="legend",
                content=json.dumps({"instructions": "Instructions de test"}),
                image_path="uploads/test2.jpg"
            )
            
            # Cas 4: Les deux sont définis mais différents
            exercise4 = self.Exercise(
                title="Test 4 - Chemins différents",
                exercise_type="legend",
                content=json.dumps({
                    "instructions": "Instructions de test",
                    "main_image": "uploads/test1.jpg"
                }),
                image_path="uploads/test2.jpg"
            )
            
            # Cas 5: Les deux sont définis et identiques mais pas au format normalisé
            exercise5 = self.Exercise(
                title="Test 5 - Chemins identiques non normalisés",
                exercise_type="legend",
                content=json.dumps({
                    "instructions": "Instructions de test",
                    "main_image": "uploads/legend/test3.jpg"
                }),
                image_path="uploads/legend/test3.jpg"
            )
            
            # Cas 6: Les deux sont définis et déjà normalisés
            exercise6 = self.Exercise(
                title="Test 6 - Chemins déjà normalisés",
                exercise_type="legend",
                content=json.dumps({
                    "instructions": "Instructions de test",
                    "main_image": "/static/uploads/legend/test3.jpg"
                }),
                image_path="/static/uploads/legend/test3.jpg"
            )
            
            self.db.session.add_all([exercise1, exercise2, exercise3, exercise4, exercise5, exercise6])
            self.db.session.commit()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        # S'assurer que la session est fermée avant de supprimer le fichier
        with self.app.app_context():
            self.db.session.close()
            self.db.engine.dispose()
        
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path)
        except PermissionError:
            print(f"Impossible de supprimer {self.db_path} - fichier en cours d'utilisation")
        
        shutil.rmtree(self.static_dir)
    
    def normalize_path(self, path):
        """Normalise un chemin d'image pour le rendre compatible avec Flask"""
        if not path:
            return None
        
        # Nettoyer les chemins
        path = path.replace('\\', '/')
        
        # Extraire le nom du fichier
        filename = os.path.basename(path)
        
        # Construire le chemin normalisé
        if 'legend' in path.lower():
            normalized_path = f"/static/uploads/legend/{filename}"
        else:
            normalized_path = f"/static/uploads/{filename}"
        
        return normalized_path
    
    def fix_legend_image_paths(self):
        """Fonction de correction des chemins d'images pour les tests"""
        with self.app.app_context():
            # Récupérer tous les exercices de type légende
            legend_exercises = self.Exercise.query.filter_by(exercise_type='legend').all()
            logger.info(f"Trouvé {len(legend_exercises)} exercices de type légende")
            
            fixed_count = 0
            for exercise in legend_exercises:
                logger.info(f"Traitement de l'exercice #{exercise.id}: {exercise.title}")
                
                content = exercise.get_content()
                main_image = content.get('main_image')
                image_path = exercise.image_path
                
                # Cas 1: Aucune image définie
                if not main_image and not image_path:
                    logger.warning(f"Exercice #{exercise.id}: Aucune image définie, ignoré")
                    continue
                
                # Cas 2: Seulement main_image est défini
                if main_image and not image_path:
                    normalized_path = self.normalize_path(main_image)
                    exercise.image_path = normalized_path
                    content['main_image'] = normalized_path
                    exercise.content = json.dumps(content)
                    logger.info(f"Exercice #{exercise.id}: image_path défini à partir de main_image: {normalized_path}")
                    fixed_count += 1
                
                # Cas 3: Seulement image_path est défini
                elif not main_image and image_path:
                    normalized_path = self.normalize_path(image_path)
                    exercise.image_path = normalized_path
                    content['main_image'] = normalized_path
                    exercise.content = json.dumps(content)
                    logger.info(f"Exercice #{exercise.id}: main_image défini à partir de image_path: {normalized_path}")
                    fixed_count += 1
                
                # Cas 4: Les deux sont définis mais différents
                elif main_image != image_path:
                    # Préférer main_image car c'est celui utilisé dans le template
                    normalized_path = self.normalize_path(main_image)
                    exercise.image_path = normalized_path
                    content['main_image'] = normalized_path
                    exercise.content = json.dumps(content)
                    logger.info(f"Exercice #{exercise.id}: Synchronisation des chemins: {normalized_path}")
                    fixed_count += 1
                
                # Cas 5: Les deux sont définis et identiques mais pas au format normalisé
                elif main_image == image_path:
                    normalized_path = self.normalize_path(main_image)
                    if normalized_path != main_image:
                        exercise.image_path = normalized_path
                        content['main_image'] = normalized_path
                        exercise.content = json.dumps(content)
                        logger.info(f"Exercice #{exercise.id}: Normalisation des chemins: {normalized_path}")
                        fixed_count += 1
            
            # Sauvegarder les modifications
            if fixed_count > 0:
                try:
                    self.db.session.commit()
                    logger.info(f"Modifications sauvegardées en base de données: {fixed_count} exercices corrigés")
                except Exception as e:
                    self.db.session.rollback()
                    logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            else:
                logger.info("Aucune correction nécessaire")
            
            return fixed_count
    
    def test_fix_legend_image_paths(self):
        """Teste la correction des chemins d'images"""
        # Exécuter la correction
        fixed_count = self.fix_legend_image_paths()
        
        # Vérifier que 4 exercices ont été corrigés (tous sauf le cas 1 qui n'a pas d'image et le cas 6 qui est déjà correct)
        self.assertEqual(fixed_count, 4)
        
        # Vérifier que les exercices ont été correctement corrigés
        with self.app.app_context():
            # Cas 1: Aucune image définie - ne devrait pas être modifié
            exercise1 = self.Exercise.query.filter_by(title="Test 1 - Aucune image").first()
            self.assertIsNone(exercise1.image_path)
            self.assertNotIn('main_image', exercise1.get_content())
            
            # Cas 2: Seulement main_image est défini - image_path devrait être défini et normalisé
            exercise2 = self.Exercise.query.filter_by(title="Test 2 - Seulement main_image").first()
            self.assertEqual(exercise2.image_path, "/static/uploads/test1.jpg")
            self.assertEqual(exercise2.get_content()['main_image'], "/static/uploads/test1.jpg")
            
            # Cas 3: Seulement image_path est défini - main_image devrait être défini et normalisé
            exercise3 = self.Exercise.query.filter_by(title="Test 3 - Seulement image_path").first()
            self.assertEqual(exercise3.image_path, "/static/uploads/test2.jpg")
            self.assertEqual(exercise3.get_content()['main_image'], "/static/uploads/test2.jpg")
            
            # Cas 4: Les deux sont définis mais différents - les deux devraient être synchronisés sur main_image
            exercise4 = self.Exercise.query.filter_by(title="Test 4 - Chemins différents").first()
            self.assertEqual(exercise4.image_path, "/static/uploads/test1.jpg")
            self.assertEqual(exercise4.get_content()['main_image'], "/static/uploads/test1.jpg")
            
            # Cas 5: Les deux sont définis et identiques mais pas au format normalisé - les deux devraient être normalisés
            exercise5 = self.Exercise.query.filter_by(title="Test 5 - Chemins identiques non normalisés").first()
            self.assertEqual(exercise5.image_path, "/static/uploads/legend/test3.jpg")
            self.assertEqual(exercise5.get_content()['main_image'], "/static/uploads/legend/test3.jpg")
            
            # Cas 6: Les deux sont définis et déjà normalisés - ne devrait pas être modifié
            exercise6 = self.Exercise.query.filter_by(title="Test 6 - Chemins déjà normalisés").first()
            self.assertEqual(exercise6.image_path, "/static/uploads/legend/test3.jpg")
            self.assertEqual(exercise6.get_content()['main_image'], "/static/uploads/legend/test3.jpg")

if __name__ == '__main__':
    unittest.main()
