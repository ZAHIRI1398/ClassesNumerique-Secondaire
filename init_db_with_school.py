#!/usr/bin/env python3
"""
Script pour initialiser la base de données avec la colonne school_name
"""

import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer sans démarrer le serveur
os.environ['FLASK_ENV'] = 'development'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Class, Exercise, ExerciseAttempt

def init_database_with_school():
    """Initialiser la base de données avec toutes les tables"""
    
    # Créer une app Flask minimale
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-key'
    
    # Créer le dossier instance s'il n'existe pas
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print("Dossier instance cree")
    
    # Initialiser la base de données
    db.init_app(app)
    
    with app.app_context():
        try:
            # Créer toutes les tables
            print("Creation des tables...")
            db.create_all()
            
            # Vérifier que les tables ont été créées
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            print("Tables creees:", tables)
            
            # Vérifier la structure de la table User
            if 'user' in tables:
                result = db.session.execute(text("PRAGMA table_info(user)"))
                columns = [row[1] for row in result.fetchall()]
                print("Colonnes dans User:", columns)
                
                if 'school_name' in columns:
                    print("Colonne school_name presente!")
                else:
                    print("ATTENTION: Colonne school_name manquante!")
            
            # Compter les utilisateurs existants
            user_count = User.query.count()
            print(f"Utilisateurs existants: {user_count}")
            
            print("Base de donnees initialisee avec succes!")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation: {e}")
            return False

if __name__ == "__main__":
    print("Initialisation de la base de donnees avec school_name...")
    success = init_database_with_school()
    
    if success:
        print("Initialisation terminee avec succes!")
    else:
        print("Echec de l'initialisation.")
