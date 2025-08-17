from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import User, db
from sqlalchemy import func
from functools import wraps

# Blueprint pour la correction du problème de sélection d'école
fix_select_school_bp = Blueprint('fix_select_school', __name__, url_prefix='/fix')

# Décorateur pour vérifier si l'utilisateur est administrateur
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Accès non autorisé. Vous devez être administrateur.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@fix_select_school_bp.route('/select-school-route', methods=['GET'])
@admin_required
def fix_select_school_route():
    """
    Route de diagnostic et correction pour la route /payment/select-school
    """
    try:
        # Récupérer la liste des écoles ayant un abonnement actif
        schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
            filter(User.school_name != None).\
            filter(User.school_name != '').\
            filter(User.subscription_type == 'school').\
            filter(User.subscription_status == 'approved').\
            group_by(User.school_name).all()
        
        # Convertir les tuples en dictionnaires pour le template
        schools_for_template = [{'school_name': school, 'user_count': count} for school, count in schools_with_subscription]
        
        # Vérifier si le template existe
        try:
            render_template('payment/select_school.html', schools=schools_for_template)
            template_exists = True
        except Exception as e:
            template_exists = False
            template_error = str(e)
        
        # Vérifier les tokens CSRF
        csrf_enabled = current_app.config.get('WTF_CSRF_ENABLED', False)
        
        return render_template('fix_select_school.html', 
                              schools=schools_for_template,
                              template_exists=template_exists,
                              template_error=template_error if not template_exists else None,
                              csrf_enabled=csrf_enabled)
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors du diagnostic de la route select-school: {str(e)}")
        return render_template('fix_select_school.html', 
                              error=str(e),
                              schools=[],
                              template_exists=False,
                              csrf_enabled=False)

@fix_select_school_bp.route('/apply-select-school-fix', methods=['POST'])
@admin_required
def apply_select_school_fix():
    """
    Appliquer la correction pour la route /payment/select-school
    """
    try:
        # Vérifier si le token CSRF est activé dans la configuration
        if not current_app.config.get('WTF_CSRF_ENABLED', False):
            current_app.config['WTF_CSRF_ENABLED'] = True
            current_app.logger.info("CSRF protection activée")
            
        # Vérifier si le template existe et est accessible
        try:
            render_template('payment/select_school.html', schools=[])
            template_ok = True
        except Exception as e:
            template_ok = False
            
        # Résultats de la correction
        results = {
            'csrf_enabled': current_app.config.get('WTF_CSRF_ENABLED', False),
            'template_ok': template_ok
        }
        
        flash('Correction appliquée avec succès pour la route select-school.', 'success')
        return render_template('fix_select_school_result.html', results=results)
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'application de la correction: {str(e)}")
        flash(f'Erreur lors de l\'application de la correction: {str(e)}', 'error')
        return redirect(url_for('fix_select_school.fix_select_school_route'))
