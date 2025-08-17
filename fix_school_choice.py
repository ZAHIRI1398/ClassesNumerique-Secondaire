from flask import Blueprint, jsonify, current_app, render_template, redirect, url_for
from flask_login import login_required
from models import User, db
from functools import wraps

# Blueprint pour les routes de correction
fix_bp = Blueprint('fix', __name__, url_prefix='/fix')

# Décorateur pour vérifier si l'utilisateur est administrateur
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Accès non autorisé. Vous devez être administrateur.'}), 403
        return f(*args, **kwargs)
    return decorated_function

@fix_bp.route('/school-choice', methods=['GET'])
@login_required
@admin_required
def fix_school_choice():
    """Endpoint pour corriger le problème de choix d'école"""
    try:
        # 1. Vérifier les abonnements de type 'Trial' ou 'trial' avant correction
        trial_count_before = User.query.filter(
            User.subscription_type.in_(['Trial', 'trial']),
            User.school_name != None,
            User.school_name != ''
        ).count()
        
        # 2. Mettre à jour les abonnements de type 'Trial' ou 'trial' en 'school'
        updated_users = User.query.filter(
            User.subscription_type.in_(['Trial', 'trial']),
            User.school_name != None,
            User.school_name != ''
        ).update({'subscription_type': 'school'}, synchronize_session=False)
        
        # 3. Vérifier les abonnements avec statut 'pending' ou 'paid' qui devraient être 'approved'
        pending_paid_count_before = User.query.filter(
            User.subscription_type == 'school',
            User.subscription_status.in_(['pending', 'paid']),
            User.school_name != None,
            User.school_name != ''
        ).count()
        
        # 4. Mettre à jour les abonnements avec statut 'pending' ou 'paid' en 'approved'
        updated_statuses = User.query.filter(
            User.subscription_type == 'school',
            User.subscription_status.in_(['pending', 'paid']),
            User.school_name != None,
            User.school_name != ''
        ).update({'subscription_status': 'approved'}, synchronize_session=False)
        
        # 5. Valider les modifications
        db.session.commit()
        
        # 6. Vérifier les écoles éligibles après correction
        eligible_schools = db.session.query(User.school_name).filter(
            User.school_name != None,
            User.school_name != '',
            User.subscription_type == 'school',
            User.subscription_status == 'approved'
        ).distinct().count()
        
        current_app.logger.info(f"[FIX_SCHOOL_CHOICE] Correction des abonnements: {updated_users} utilisateurs mis à jour (Trial -> school)")
        current_app.logger.info(f"[FIX_SCHOOL_CHOICE] Correction des statuts: {updated_statuses} utilisateurs mis à jour (pending/paid -> approved)")
        
        return render_template('fix/school_choice_result.html',
            success=True,
            message=f"Correction réussie: {updated_users} types d'abonnement et {updated_statuses} statuts mis à jour",
            trial_count_before=trial_count_before,
            pending_paid_count_before=pending_paid_count_before,
            updated_users=updated_users,
            updated_statuses=updated_statuses,
            eligible_schools=eligible_schools
        )
        
    except Exception as e:
        current_app.logger.error(f"[FIX_SCHOOL_CHOICE] Erreur lors de la correction: {str(e)}")
        db.session.rollback()
        return render_template('fix/school_choice_result.html',
            success=False,
            error=f"Erreur lors de la correction: {str(e)}"
        ), 500

# Comment enregistrer ce blueprint dans app.py:
# from fix_school_choice import fix_bp
# app.register_blueprint(fix_bp)
