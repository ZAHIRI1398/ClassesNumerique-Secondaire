#!/usr/bin/env python3
"""
Script pour créer une base de données propre avec Flask-SQLAlchemy
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configuration Flask minimale
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key'

# Initialiser SQLAlchemy
db = SQLAlchemy(app)

# Définir le modèle User avec school_name
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='student')
    school_name = db.Column(db.String(200))  # COLONNE ÉCOLE
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Colonnes d'abonnement
    subscription_status = db.Column(db.String(20), default='pending')
    subscription_type = db.Column(db.String(20))
    subscription_amount = db.Column(db.Float)
    payment_date = db.Column(db.DateTime)
    payment_reference = db.Column(db.String(100))
    payment_session_id = db.Column(db.String(200))
    payment_amount = db.Column(db.Float)
    approval_date = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    subscription_expires = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    notes = db.Column(db.Text)

# Autres modèles simplifiés
class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    exercise_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class ExerciseAttempt(db.Model):
    __tablename__ = 'exercise_attempt'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    score = db.Column(db.Float)
    completed_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    answers = db.Column(db.Text)

# Table d'association
student_class_association = db.Table('student_class_association',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True)
)

def create_clean_database():
    """Créer une base de données propre"""
    
    # Créer le dossier instance
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"Dossier instance cree: {instance_dir}")
    
    with app.app_context():
        try:
            print("Creation des tables avec SQLAlchemy...")
            
            # Supprimer toutes les tables existantes
            db.drop_all()
            print("Anciennes tables supprimees")
            
            # Créer toutes les tables
            db.create_all()
            print("Nouvelles tables creees")
            
            # Vérifier la structure
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            # Vérifier la table User
            user_columns = inspector.get_columns('user')
            column_names = [col['name'] for col in user_columns]
            
            print(f"Colonnes User: {column_names}")
            
            if 'school_name' in column_names:
                print("✅ Colonne school_name presente!")
            else:
                print("❌ Colonne school_name manquante!")
                return False
            
            # Test d'insertion
            print("Test d'insertion...")
            test_user = User(
                username='test',
                email='test@example.com',
                name='Test User',
                role='teacher',
                school_name='École Test'
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            # Test de lecture
            user = User.query.filter_by(email='test@example.com').first()
            if user and user.school_name == 'École Test':
                print("✅ Test lecture/ecriture OK!")
                
                # Supprimer le test
                db.session.delete(user)
                db.session.commit()
            else:
                print("❌ Test lecture/ecriture ECHEC!")
                return False
            
            print("Base de donnees creee avec succes!")
            return True
            
        except Exception as e:
            print(f"Erreur: {e}")
            return False

if __name__ == "__main__":
    print("=== CREATION BASE DE DONNEES PROPRE ===")
    success = create_clean_database()
    
    if success:
        print("=== BASE CREEE AVEC SUCCES ===")
        print("Vous pouvez maintenant demarrer Flask avec: python app.py")
    else:
        print("=== ECHEC CREATION BASE ===")
