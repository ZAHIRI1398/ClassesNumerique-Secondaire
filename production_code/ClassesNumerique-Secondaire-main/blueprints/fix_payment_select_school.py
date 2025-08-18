"""
Script de correction pour la route /payment/select-school qui génère une erreur 500
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import User, db
from sqlalchemy import func
from datetime import datetime

# Blueprint pour la correction
fix_payment_select_school_bp = Blueprint('fix_payment_select_school', __name__, url_prefix='/fix-payment')

@fix_payment_select_school_bp.route('/select-school')
def fix_select_school():
    """
    Version corrigée de la route select_school
    """
    current_app.logger.info(f"[FIX_SELECT_SCHOOL_DEBUG] Accès à la route fix select_school")
    current_app.logger.info(f"[FIX_SELECT_SCHOOL_DEBUG] Utilisateur authentifié: {current_user.is_authenticated}")
    
    # Vérifier que l'utilisateur est un enseignant seulement s'il est connecté
    if current_user.is_authenticated and not current_user.role == 'teacher':
        current_app.logger.warning(f"[FIX_SELECT_SCHOOL_DEBUG] Utilisateur non enseignant: {current_user.role}")
        flash('Cette page est réservée aux enseignants.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Récupérer la liste des écoles ayant un abonnement actif
        schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
            filter(User.school_name != None).\
            filter(User.school_name != '').\
            filter(User.subscription_type == 'school').\
            filter(User.subscription_status == 'approved').\
            group_by(User.school_name).all()
        
        # Ajouter des logs pour le débogage
        current_app.logger.info(f"[FIX_SELECT_SCHOOL_DEBUG] Nombre d'écoles trouvées: {len(schools_with_subscription)}")
        for school, count in schools_with_subscription:
            current_app.logger.info(f"[FIX_SELECT_SCHOOL_DEBUG] École: {school}, Utilisateurs: {count}")
        
        if not schools_with_subscription:
            current_app.logger.warning("[FIX_SELECT_SCHOOL_DEBUG] Aucune école avec abonnement actif trouvée")
            flash('Aucune école avec un abonnement actif n\'a été trouvée. Veuillez procéder au paiement pour un abonnement école.', 'info')
            try:
                return redirect(url_for('payment.subscribe', subscription_type='school'))
            except Exception as e:
                current_app.logger.error(f"[FIX_SELECT_SCHOOL_DEBUG] Erreur lors de la redirection: {str(e)}")
                return redirect(url_for('index'))
        
        # Convertir les tuples en dictionnaires pour le template
        schools_for_template = [{'school_name': school, 'user_count': count} for school, count in schools_with_subscription]
        current_app.logger.info(f"[FIX_SELECT_SCHOOL_DEBUG] Écoles formatées pour le template: {schools_for_template}")
        
        return render_template('payment/select_school.html', schools=schools_for_template)
    
    except Exception as e:
        current_app.logger.error(f"[FIX_SELECT_SCHOOL_DEBUG] Erreur non gérée: {str(e)}")
        flash('Une erreur est survenue lors de la recherche des écoles. Veuillez réessayer plus tard.', 'error')
        return redirect(url_for('index'))

@fix_payment_select_school_bp.route('/join-school', methods=['POST'])
@login_required
def fix_join_school():
    """
    Version corrigée de la route join_school
    """
    # Vérifier que l'utilisateur est un enseignant
    if not current_user.role == 'teacher':
        flash('Cette fonctionnalité est réservée aux enseignants.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Récupérer le nom de l'école sélectionnée
        school_name = request.form.get('school_name')
        if not school_name:
            flash('Veuillez sélectionner une école.', 'error')
            return redirect(url_for('fix_payment_select_school.fix_select_school'))
        
        # Vérifier que l'école a bien un abonnement actif
        school_subscription = User.query.filter(
            User.school_name == school_name,
            User.subscription_type == 'school',
            User.subscription_status == 'approved'
        ).first()
        
        if not school_subscription:
            flash('Cette école n\'a pas d\'abonnement actif.', 'error')
            return redirect(url_for('fix_payment_select_school.fix_select_school'))
        
        # Associer l'enseignant à l'école et activer son abonnement
        current_user.school_name = school_name
        current_user.subscription_status = 'approved'
        current_user.subscription_type = 'school'
        current_user.approval_date = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"Enseignant {current_user.email} associé à l'école {school_name} avec abonnement approuvé")
        flash(f'Vous avez été associé avec succès à l\'école {school_name}. Votre compte a été automatiquement approuvé.', 'success')
        
        return redirect(url_for('index'))
    
    except Exception as e:
        current_app.logger.error(f"[FIX_JOIN_SCHOOL_DEBUG] Erreur non gérée: {str(e)}")
        flash('Une erreur est survenue lors de l\'association à l\'école. Veuillez réessayer plus tard.', 'error')
        return redirect(url_for('index'))
