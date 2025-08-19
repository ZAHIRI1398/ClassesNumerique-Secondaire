from flask import render_template
from flask_login import login_required, current_user

def register_test_planning_route(app):
    """
    Enregistre une route de test pour la planification annuelle
    """
    @app.route('/test-planning')
    @login_required
    def test_planning():
        """Page de test pour l'intégration de la planification annuelle"""
        if not current_user.is_teacher:
            return render_template('test_planning.html', message="Vous devez être connecté en tant qu'enseignant pour accéder à cette page.")
        
        return render_template('test_planning.html')
