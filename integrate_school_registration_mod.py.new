from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from models import db, School, User

def integrate_school_registration_mod(app):
    """
    Intègre le module de simplification d'inscription des écoles à l'application Flask.
    Cette fonction crée un blueprint pour gérer les routes d'inscription simplifiée.
    """
    # Création du blueprint
    school_registration_mod = Blueprint('school_registration_mod', __name__)
    
    @school_registration_mod.route('/register-school-simplified', methods=['GET', 'POST'])
    @login_required
    def register_school_simplified():
        """
        Route pour l'inscription simplifiée d'une école pour les utilisateurs déjà connectés.
        Cette route ne demande que le nom de l'école.
        """
        if request.method == 'POST':
            school_name = request.form.get('school_name')
            
            if not school_name:
                flash('Le nom de l\'école est requis.', 'danger')
                return render_template('auth/register_school_simplified.html')
            
            # Vérifier si l'école existe déjà
            existing_school = School.query.filter_by(name=school_name).first()
            if existing_school:
                flash('Cette école existe déjà.', 'warning')
                return render_template('auth/register_school_simplified.html')
            
            try:
                # Créer la nouvelle école
                new_school = School(
                    name=school_name,
                    created_by=current_user.id
                )
                db.session.add(new_school)
                db.session.commit()
                
                # Mettre à jour l'utilisateur avec l'ID de l'école
                current_user.school_id = new_school.id
                db.session.commit()
                
                flash('École créée avec succès!', 'success')
                # Rediriger vers le tableau de bord approprié selon le rôle
                if current_user.role == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                elif current_user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('index'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Erreur lors de la création de l'école: {str(e)}")
                flash('Une erreur est survenue lors de la création de l\'école.', 'danger')
                return render_template('auth/register_school_simplified.html')
        
        return render_template('auth/register_school_simplified.html')
    
    @school_registration_mod.route('/register-school-connected', methods=['GET', 'POST'])
    @login_required
    def register_school_connected():
        """
        Route alternative pour l'inscription d'une école pour les utilisateurs déjà connectés.
        Cette route utilise le formulaire complet mais pré-remplit les informations de l'utilisateur.
        """
        if request.method == 'POST':
            school_name = request.form.get('school_name')
            address = request.form.get('address')
            postal_code = request.form.get('postal_code')
            city = request.form.get('city')
            country = request.form.get('country')
            
            if not all([school_name, address, postal_code, city, country]):
                flash('Tous les champs sont requis.', 'danger')
                return render_template('auth/register_school_connected.html')
            
            # Vérifier si l'école existe déjà
            existing_school = School.query.filter_by(name=school_name).first()
            if existing_school:
                flash('Cette école existe déjà.', 'warning')
                return render_template('auth/register_school_connected.html')
            
            try:
                # Créer la nouvelle école
                new_school = School(
                    name=school_name,
                    address=address,
                    postal_code=postal_code,
                    city=city,
                    country=country,
                    created_by=current_user.id
                )
                db.session.add(new_school)
                db.session.commit()
                
                # Mettre à jour l'utilisateur avec l'ID de l'école
                current_user.school_id = new_school.id
                db.session.commit()
                
                flash('École créée avec succès!', 'success')
                # Rediriger vers le tableau de bord approprié selon le rôle
                if current_user.role == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                elif current_user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('index'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Erreur lors de la création de l'école: {str(e)}")
                flash('Une erreur est survenue lors de la création de l\'école.', 'danger')
                return render_template('auth/register_school_connected.html')
        
        return render_template('auth/register_school_connected.html')
    
    # Enregistrer le blueprint dans l'application
    app.register_blueprint(school_registration_mod)
    
    return app
