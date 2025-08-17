from flask import Blueprint, jsonify, current_app
from flask_login import login_required
from models import User, db
from functools import wraps

# Blueprint pour les routes d'administration
admin_fix_bp = Blueprint('admin_fix', __name__, url_prefix='/admin/fix')

# Décorateur pour vérifier si l'utilisateur est administrateur
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Accès non autorisé. Vous devez être administrateur.'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_fix_bp.route('/subscriptions', methods=['GET'])
@login_required
@admin_required
def fix_subscriptions():
    """Endpoint pour corriger les abonnements de type 'Trial' en 'school'"""
    try:
        # Compter les abonnements de type 'Trial' ou 'trial' avant correction
        trial_count_before = User.query.filter(
            User.subscription_type.in_(['Trial', 'trial']),
            User.school_name != None,
            User.school_name != ''
        ).count()
        
        # Mettre à jour les abonnements de type 'Trial' ou 'trial' en 'school'
        updated_users = User.query.filter(
            User.subscription_type.in_(['Trial', 'trial']),
            User.school_name != None,
            User.school_name != ''
        ).update({'subscription_type': 'school'}, synchronize_session=False)
        
        # Valider les modifications
        db.session.commit()
        
        # Compter les écoles éligibles après correction
        eligible_schools = db.session.query(User.school_name).filter(
            User.school_name != None,
            User.school_name != '',
            User.subscription_type == 'school',
            User.subscription_status.in_(['pending', 'paid', 'approved'])
        ).distinct().count()
        
        current_app.logger.info(f"[ADMIN_FIX] Correction des abonnements: {updated_users} utilisateurs mis à jour (Trial -> school)")
        
        return jsonify({
            'success': True,
            'message': f"Correction réussie: {updated_users} utilisateurs mis à jour (Trial -> school)",
            'trial_count_before': trial_count_before,
            'updated_users': updated_users,
            'eligible_schools': eligible_schools
        })
        
    except Exception as e:
        current_app.logger.error(f"[ADMIN_FIX] Erreur lors de la correction des abonnements: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f"Erreur lors de la correction des abonnements: {str(e)}"}), 500

# Comment enregistrer ce blueprint dans app.py:
# from admin_fix_subscriptions import admin_fix_bp
# app.register_blueprint(admin_fix_bp)
