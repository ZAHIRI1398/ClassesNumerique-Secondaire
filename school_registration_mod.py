from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from models import School, User, db

# Création du blueprint
school_registration_mod = Blueprint('school_registration_mod', __name__)

@school_registration_mod.route('/register-school-simplified', methods=['GET', 'POST'])
@login_required
def register_school_simplified():
    """
    Route pour l'inscription simplifiée d'une école.
    Cette route est utilisée pour les utilisateurs déjà connectés.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        postal_code = request.form.get('postal_code')
        country = request.form.get('country')
        
        if not all([name, address, city, postal_code, country]):
            flash('Tous les champs sont obligatoires.', 'danger')
            return render_template('auth/register_school_simplified.html')
        
        # Création de l'école
        school = School(
            name=name,
            address=address,
            city=city,
            postal_code=postal_code,
            country=country
        )
        
        try:
            db.session.add(school)
            db.session.commit()
            
            # Association de l'utilisateur à l'école
            current_user.school_id = school.id
            db.session.commit()
            
            flash('École créée avec succès!', 'success')
            current_app.logger.info(f"École '{name}' créée avec succès par {current_user.email}")
            
            # Redirection vers la page d'accueil ou le tableau de bord
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la création de l'école: {str(e)}")
            flash('Une erreur est survenue lors de la création de l\'école.', 'danger')
    
    return render_template('auth/register_school_simplified.html')

@school_registration_mod.route('/register-school-connected', methods=['GET', 'POST'])
@login_required
def register_school_connected():
    """
    Route pour l'inscription d'une école pour un utilisateur déjà connecté.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        postal_code = request.form.get('postal_code')
        country = request.form.get('country')
        
        if not all([name, address, city, postal_code, country]):
            flash('Tous les champs sont obligatoires.', 'danger')
            return render_template('auth/register_school_connected.html')
        
        # Création de l'école
        school = School(
            name=name,
            address=address,
            city=city,
            postal_code=postal_code,
            country=country
        )
        
        try:
            db.session.add(school)
            db.session.commit()
            
            # Association de l'utilisateur à l'école
            current_user.school_id = school.id
            db.session.commit()
            
            flash('École créée avec succès!', 'success')
            current_app.logger.info(f"École '{name}' créée avec succès par {current_user.email}")
            
            # Redirection vers la page d'accueil ou le tableau de bord
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la création de l'école: {str(e)}")
            flash('Une erreur est survenue lors de la création de l\'école.', 'danger')
    
    return render_template('auth/register_school_connected.html')

def init_app(app):
    """
    Initialise le module d'inscription d'école dans l'application Flask.
    """
    app.register_blueprint(school_registration_mod)
    app.logger.info("Module d'inscription d'école initialisé avec succès.")
