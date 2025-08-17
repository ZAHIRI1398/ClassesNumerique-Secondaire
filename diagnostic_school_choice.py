from flask import Blueprint, jsonify, current_app, render_template
from flask_login import login_required
from models import User, db
from functools import wraps
from sqlalchemy import func, text

# Blueprint pour les routes de diagnostic
diagnostic_bp = Blueprint('diagnostic', __name__, url_prefix='/diagnostic')

# Décorateur pour vérifier si l'utilisateur est administrateur
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Accès non autorisé. Vous devez être administrateur.'}), 403
        return f(*args, **kwargs)
    return decorated_function

@diagnostic_bp.route('/school-choice', methods=['GET'])
@login_required
@admin_required
def school_choice():
    """Endpoint pour diagnostiquer le problème de choix d'école"""
    try:
        # 1. Vérifier tous les types d'abonnement dans la base de données
        subscription_types = db.session.query(
            User.subscription_type,
            func.count(User.id).label('count')
        ).group_by(User.subscription_type).all()
        
        subscription_types_result = [
            {'type': type_info[0] or 'None', 'count': type_info[1]}
            for type_info in subscription_types
        ]
        
        current_app.logger.info(f"[DIAGNOSTIC] Types d'abonnement: {subscription_types_result}")
        
        # 2. Vérifier tous les statuts d'abonnement dans la base de données
        subscription_statuses = db.session.query(
            User.subscription_status,
            func.count(User.id).label('count')
        ).group_by(User.subscription_status).all()
        
        subscription_statuses_result = [
            {'status': status_info[0] or 'None', 'count': status_info[1]}
            for status_info in subscription_statuses
        ]
        
        current_app.logger.info(f"[DIAGNOSTIC] Statuts d'abonnement: {subscription_statuses_result}")
        
        # 3. Vérifier les écoles avec abonnement de type 'school'
        schools_with_school_subscription = db.session.query(
            User.school_name,
            func.count(User.id).label('count')
        ).filter(
            User.school_name != None,
            User.school_name != '',
            User.subscription_type == 'school'
        ).group_by(User.school_name).all()
        
        schools_with_school_result = [
            {'school_name': school_info[0], 'count': school_info[1]}
            for school_info in schools_with_school_subscription
        ]
        
        current_app.logger.info(f"[DIAGNOSTIC] Écoles avec abonnement 'school': {schools_with_school_result}")
        
        # 4. Vérifier les écoles avec abonnement de type 'Trial' ou 'trial'
        schools_with_trial_subscription = db.session.query(
            User.school_name,
            func.count(User.id).label('count')
        ).filter(
            User.school_name != None,
            User.school_name != '',
            User.subscription_type.in_(['Trial', 'trial'])
        ).group_by(User.school_name).all()
        
        schools_with_trial_result = [
            {'school_name': school_info[0], 'count': school_info[1]}
            for school_info in schools_with_trial_subscription
        ]
        
        current_app.logger.info(f"[DIAGNOSTIC] Écoles avec abonnement 'Trial' ou 'trial': {schools_with_trial_result}")
        
        # 5. Simuler la requête de sélection d'école
        schools_with_subscription = db.session.query(
            User.school_name,
            func.count(User.id).label('user_count')
        ).filter(
            User.school_name != None,
            User.school_name != '',
            User.subscription_type.in_(['school', 'Trial', 'trial']),
            User.subscription_status.in_(['pending', 'paid', 'approved'])
        ).group_by(User.school_name).all()
        
        # 6. Obtenir des informations détaillées sur chaque école
        schools_with_subscription_details = []
        schools_with_mixed_types = []
        schools_with_mixed_statuses = []
        
        for school_info in schools_with_subscription:
            school_name = school_info[0]
            user_count = school_info[1]
            
            # Types d'abonnement pour cette école
            school_subscription_types = db.session.query(
                User.subscription_type,
                func.count(User.id).label('count')
            ).filter(
                User.school_name == school_name
            ).group_by(User.subscription_type).all()
            
            school_subscription_types_result = [
                {'type': type_info[0] or 'None', 'count': type_info[1]}
                for type_info in school_subscription_types
            ]
            
            # Statuts d'abonnement pour cette école
            school_subscription_statuses = db.session.query(
                User.subscription_status,
                func.count(User.id).label('count')
            ).filter(
                User.school_name == school_name
            ).group_by(User.subscription_status).all()
            
            school_subscription_statuses_result = [
                {'status': status_info[0] or 'None', 'count': status_info[1]}
                for status_info in school_subscription_statuses
            ]
            
            # Ajouter les détails de l'école
            schools_with_subscription_details.append({
                'school_name': school_name,
                'user_count': user_count,
                'subscription_types': school_subscription_types_result,
                'subscription_statuses': school_subscription_statuses_result
            })
            
            # Vérifier les incohérences
            types = [t['type'] for t in school_subscription_types_result]
            statuses = [s['status'] for s in school_subscription_statuses_result]
            
            if len(types) > 1 and any(t in ['Trial', 'trial'] for t in types):
                schools_with_mixed_types.append({
                    'school_name': school_name,
                    'types': types
                })
                
            if len(statuses) > 1 and any(s in ['pending', 'paid'] for s in statuses):
                schools_with_mixed_statuses.append({
                    'school_name': school_name,
                    'statuses': statuses
                })
        
        current_app.logger.info(f"[DIAGNOSTIC] Écoles avec abonnement (requête de sélection): {schools_with_subscription_details}")
        
        # 7. Vérifier les écoles avec abonnement approuvé
        schools_with_approved_subscription = db.session.query(
            User.school_name,
            func.count(User.id).label('count')
        ).filter(
            User.school_name != None,
            User.school_name != '',
            User.subscription_type.in_(['school', 'Trial', 'trial']),
            User.subscription_status == 'approved'
        ).group_by(User.school_name).all()
        
        schools_with_approved_result = [
            {'school_name': school_info[0], 'count': school_info[1]}
            for school_info in schools_with_approved_subscription
        ]
        
        current_app.logger.info(f"[DIAGNOSTIC] Écoles avec abonnement approuvé: {schools_with_approved_result}")
        
        # Rendu du template avec les données
        return render_template('diagnostic/school_choice.html',
                              subscription_types=subscription_types_result,
                              subscription_statuses=subscription_statuses_result,
                              schools_with_subscription=schools_with_subscription_details,
                              schools_with_mixed_types=schools_with_mixed_types,
                              schools_with_mixed_statuses=schools_with_mixed_statuses)
                              
        # Version API JSON si nécessaire
        # return jsonify({
        #     'subscription_types': subscription_types_result,
        #     'subscription_statuses': subscription_statuses_result,
        #     'schools_with_school_subscription': schools_with_school_result,
        #     'schools_with_trial_subscription': schools_with_trial_result,
        #     'schools_with_subscription': schools_with_subscription_details,
        #     'schools_with_approved_subscription': schools_with_approved_result,
        #     'schools_with_mixed_types': schools_with_mixed_types,
        #     'schools_with_mixed_statuses': schools_with_mixed_statuses
        # })

    except Exception as e:
        current_app.logger.error(f"[DIAGNOSTIC] Erreur lors du diagnostic: {str(e)}")
        return jsonify({'error': f"Erreur lors du diagnostic: {str(e)}"}), 500

# Comment enregistrer ce blueprint dans app.py:
# from diagnostic_school_choice import diagnostic_bp
# app.register_blueprint(diagnostic_bp)
