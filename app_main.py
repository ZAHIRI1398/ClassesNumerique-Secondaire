"""
Point d'entrée principal pour l'application Flask avec contexte d'application correctement configuré.
Ce fichier importe app.py et exécute l'application avec le contexte approprié.
"""
import os
from app import app, db

# Configuration de l'application
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('Tables de base de donnees creees avec succes')
        except Exception as e:
            app.logger.error(f'Erreur lors de l\'initialisation de la base: {str(e)}')
    
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
