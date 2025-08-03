from models import db, Exercise, User
from app import app
import json
from traceback import format_exc
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

def create_test_exercise():
    try:
        print('Initialisation de la base de données...')
        with app.app_context():
            db.create_all()
            print('Base de données initialisée.')
        
        with app.app_context():
            try:
                # Supprimer tous les utilisateurs test existants
                User.query.filter_by(username='test').delete()
                User.query.filter_by(email='test@example.com').delete()
                db.session.commit()
                print('Anciens utilisateurs test supprimés')
                
                # Créer le nouvel utilisateur test
                print('Création de l\'utilisateur test...')
                user = User(
                    username='test',
                    email='test@example.com',
                    name='Test User',
                    password_hash=generate_password_hash('test'),
                    role='teacher'
                )
                db.session.add(user)
                db.session.commit()
                print(f'Utilisateur test créé avec ID: {user.id}')
            except IntegrityError:
                db.session.rollback()
                print('Erreur: Impossible de créer l\'utilisateur test (contrainte unique)')
                return
            
            print('Vérification des exercices existants...')
            existing = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
            print(f'Nombre d\'exercices existants: {len(existing)}')
            
            # Créer un exercice de test
            content = {
                'sentences': [
                    'Le ___ est bleu.',
                    'La ___ est rouge.'
                ],
                'words': [
                    'ciel',
                    'voiture'
                ]
            }
            
            print('Création de l\'exercice...')
            exercise = Exercise(
                title='Test Texte à Trous',
                exercise_type='fill_in_blanks',
                content=json.dumps(content),
                teacher_id=user.id  # Utiliser l'ID de l'utilisateur test
            )
            
            db.session.add(exercise)
            print('Sauvegarde dans la base de données...')
            db.session.commit()
            print(f'Exercice créé avec ID: {exercise.id}')
            
    except Exception as e:
        print(f'Erreur: {str(e)}')
        print('Détails:')
        print(format_exc())

if __name__ == '__main__':
    create_test_exercise()
