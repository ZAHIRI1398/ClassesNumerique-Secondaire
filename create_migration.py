import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Assurez-vous que le répertoire parent est dans le chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db

# Créer une application Flask minimale pour la migration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser l'extension de base de données
db.init_app(app)

# Initialiser Flask-Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':
    print("Configuration de migration prête.")
    print("Pour créer une migration, exécutez:")
    print("flask db migrate -m 'add_school_table_and_relationship'")
    print("Pour appliquer la migration, exécutez:")
    print("flask db upgrade")
