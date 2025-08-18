import os
import sys
from datetime import datetime

# Assurez-vous que le répertoire parent est dans le chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_migrate import Migrate
from models import db, School, User

# Créer une application Flask minimale pour la migration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser l'extension de base de données
db.init_app(app)

# Initialiser Flask-Migrate
migrate = Migrate(app, db)

def create_migration():
    """Crée une migration pour ajouter la table School et la colonne school_id à User"""
    with app.app_context():
        # Vérifier si la table school existe déjà
        if not db.engine.dialect.has_table(db.engine, 'school'):
            print("Création de la migration pour la table 'school'...")
            # La migration sera créée automatiquement par Flask-Migrate
        else:
            print("La table 'school' existe déjà.")
        
        print("Migration prête à être appliquée.")
        print("Exécutez les commandes suivantes pour appliquer la migration:")
        print("flask db migrate -m 'add_school_table_and_relationship'")
        print("flask db upgrade")

if __name__ == '__main__':
    create_migration()
