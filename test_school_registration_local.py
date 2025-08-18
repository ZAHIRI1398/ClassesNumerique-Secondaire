"""
Script pour tester localement la solution d'inscription d'école simplifiée
"""

import os
import sys
from flask import Flask, render_template, url_for

# Créer une application Flask minimale pour le test
app = Flask(__name__, 
           template_folder=os.path.abspath('templates'),
           static_folder=os.path.abspath('static'))
app.secret_key = 'test_secret_key'

# Simuler l'authentification pour les tests
class User:
    def __init__(self, is_authenticated=False):
        self.is_authenticated = is_authenticated
        self.name = "Test User"
        self.role = "teacher"
        self.subscription_status = None
    
    @property
    def is_teacher(self):
        return self.role == "teacher"

# Simuler les routes nécessaires
@app.route('/')
def index():
    return "Page d'accueil"

@app.route('/login')
def login():
    return "Page de connexion"

@app.route('/subscription/choice')
def subscription_choice():
    return "Page de choix d'abonnement"

@app.route('/contact')
def contact():
    return "Page de contact"

@app.route('/register/teacher')
def register_teacher():
    return "Page d'inscription enseignant"

@app.route('/payment/select-school')
def select_school():
    return "Page de sélection d'école"

@app.route('/create-checkout-session/<subscription_type>')
def create_checkout_session(subscription_type):
    return f"Création de session de paiement pour {subscription_type}"

# Importer et enregistrer les blueprints
from create_school_button import school_registration_bp
from modify_subscription_flow import subscription_flow_bp

app.register_blueprint(school_registration_bp)
app.register_blueprint(subscription_flow_bp)

# Injecter les variables de contexte
@app.context_processor
def inject_user():
    # Simuler un utilisateur non connecté pour voir le bouton
    return {'current_user': User(is_authenticated=False)}

@app.context_processor
def inject_school_registration_url():
    return {
        'school_registration_url': url_for('school_registration.register_school_simplified')
    }

# Route de test pour afficher le template avec le bouton
@app.route('/test-button')
def test_button():
    return render_template('base_with_school_button.html')

# Route de test pour afficher le formulaire d'inscription
@app.route('/test-form')
def test_form():
    return render_template('auth/register_school_simplified.html')

# Route de test pour afficher la page de choix d'abonnement
@app.route('/test-subscription')
def test_subscription():
    return render_template('subscription/choice_improved.html')

if __name__ == '__main__':
    print("=== Test de la solution d'inscription d'école simplifiée ===")
    print("\nRoutes disponibles pour le test:")
    print("- http://127.0.0.1:5000/test-button - Tester le bouton dans la barre de navigation")
    print("- http://127.0.0.1:5000/test-form - Tester le formulaire d'inscription école")
    print("- http://127.0.0.1:5000/test-subscription - Tester la page de choix d'abonnement")
    print("\nDémarrage du serveur de test...")
    app.run(debug=True)
