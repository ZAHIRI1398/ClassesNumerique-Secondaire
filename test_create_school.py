import os
import sys
import sqlite3
from datetime import datetime
from flask import Flask
from models import db, School, User
from config import config

def create_test_school():
    """
    Crée une école de test directement dans la base de données.
    """
    # Créer une application Flask temporaire pour utiliser SQLAlchemy
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    
    with app.app_context():
        try:
            # Vérifier si un utilisateur existe pour être le créateur de l'école
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                print("[ERREUR] Aucun utilisateur administrateur trouvé pour créer l'école.")
                return
            
            # Créer une école de test
            school_name = f"École de Test {datetime.now().strftime('%Y%m%d%H%M%S')}"
            new_school = School(
                name=school_name,
                address="123 Rue de Test",
                postal_code="75000",
                city="Paris",
                country="France",
                created_by=admin_user.id
            )
            
            db.session.add(new_school)
            db.session.commit()
            
            print(f"[OK] École '{school_name}' créée avec succès (ID: {new_school.id}).")
            
            # Associer l'école à l'utilisateur admin
            admin_user.school_id = new_school.id
            db.session.commit()
            
            print(f"[OK] École associée à l'utilisateur {admin_user.name} (ID: {admin_user.id}).")
            
            # Vérifier que l'école a bien été créée
            school = School.query.filter_by(name=school_name).first()
            if school:
                print(f"[OK] Vérification réussie: École '{school.name}' trouvée dans la base de données.")
                print(f"     - ID: {school.id}")
                print(f"     - Adresse: {school.address}")
                print(f"     - Créée par: {school.created_by}")
            else:
                print("[ERREUR] L'école n'a pas été trouvée dans la base de données après création.")
            
            # Vérifier que l'utilisateur est bien associé à l'école
            user = User.query.get(admin_user.id)
            if user.school_id == new_school.id:
                print(f"[OK] Vérification réussie: Utilisateur {user.name} associé à l'école '{school_name}'.")
            else:
                print("[ERREUR] L'utilisateur n'est pas correctement associé à l'école.")
            
            return new_school.id
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERREUR] Erreur lors de la création de l'école: {str(e)}")
            return None

if __name__ == "__main__":
    create_test_school()
