"""
Script d'intégration pour les correctifs de la route /payment/select-school
Ce script doit être exécuté pour ajouter les blueprints de diagnostic et de correction à l'application Flask
"""
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user
import os
import sys

def integrate_select_school_fix(app):
    """
    Intègre les blueprints de diagnostic et de correction dans l'application Flask
    
    Args:
        app: L'instance de l'application Flask
    """
    try:
        # Importer les blueprints
        from fix_payment_select_school import fix_payment_select_school_bp
        from diagnose_select_school_route import diagnose_select_school_bp
        
        # Enregistrer les blueprints
        app.register_blueprint(fix_payment_select_school_bp)
        app.register_blueprint(diagnose_select_school_bp)
        
        print("✅ Les blueprints de diagnostic et de correction ont été intégrés avec succès!")
        
        # Ajouter une route de redirection pour faciliter l'accès
        @app.route('/fix-select-school')
        def redirect_to_fix():
            if current_user.is_authenticated and current_user.role == 'admin':
                return redirect(url_for('diagnose_select_school.diagnose_select_school_route'))
            else:
                flash('Vous devez être connecté en tant qu\'administrateur pour accéder à cette page.', 'error')
                return redirect(url_for('index'))
        
        print("✅ Route de redirection /fix-select-school ajoutée!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'intégration des blueprints: {str(e)}")
        return False

if __name__ == "__main__":
    # Ce code s'exécute uniquement si le script est exécuté directement
    print("Ce script doit être importé dans app.py pour intégrer les correctifs.")
    print("Exemple d'utilisation:")
    print("```python")
    print("from integrate_select_school_fix import integrate_select_school_fix")
    print("# Après la création de l'application Flask")
    print("integrate_select_school_fix(app)")
    print("```")
