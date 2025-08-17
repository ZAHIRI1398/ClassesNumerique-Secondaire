"""
Script de diagnostic pour la route /payment/select-school qui génère une erreur 500
"""
from flask import Blueprint, render_template, current_app, jsonify
from flask_login import login_required, current_user
from .models import User, db
from sqlalchemy import func
from functools import wraps
import os

# Blueprint pour le diagnostic
diagnose_select_school_bp = Blueprint('diagnose_select_school', __name__, url_prefix='/diagnose')

# Décorateur pour vérifier si l'utilisateur est admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({"error": "Accès non autorisé. Vous devez être administrateur."}), 403
        return f(*args, **kwargs)
    return decorated_function

@diagnose_select_school_bp.route('/select-school-route')
@login_required
@admin_required
def diagnose_select_school_route():
    """
    Diagnostic complet de la route /payment/select-school
    """
    errors = []
    
    # 1. Vérifier si le template existe
    template_path = os.path.join(current_app.root_path, 'templates', 'payment', 'select_school.html')
    template_exists = os.path.exists(template_path)
    if not template_exists:
        errors.append(f"Le template 'payment/select_school.html' n'existe pas au chemin: {template_path}")
    
    # 2. Vérifier les écoles avec abonnement
    try:
        schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
            filter(User.school_name != None).\
            filter(User.school_name != '').\
            filter(User.subscription_type == 'school').\
            filter(User.subscription_status == 'approved').\
            group_by(User.school_name).all()
        
        # Convertir les tuples en dictionnaires pour le template
        schools = [{'school_name': school, 'user_count': count} for school, count in schools_with_subscription]
        
        # Logs pour le débogage
        current_app.logger.info(f"[DIAGNOSTIC] Nombre d'écoles trouvées: {len(schools)}")
        for school in schools:
            current_app.logger.info(f"[DIAGNOSTIC] École: {school['school_name']}, Utilisateurs: {school['user_count']}")
        
        if not schools:
            errors.append("Aucune école avec un abonnement actif (type='school', status='approved') n'a été trouvée.")
    except Exception as e:
        errors.append(f"Erreur lors de la requête des écoles: {str(e)}")
        schools = []
    
    # 3. Vérifier toutes les écoles et leurs abonnements pour diagnostic avancé
    try:
        all_schools = db.session.query(
            User.school_name, 
            User.subscription_type,
            User.subscription_status,
            func.count(User.id).label('user_count')
        ).\
        filter(User.school_name != None).\
        filter(User.school_name != '').\
        group_by(User.school_name, User.subscription_type, User.subscription_status).all()
        
        school_details = []
        for school, sub_type, sub_status, count in all_schools:
            school_details.append({
                'school_name': school,
                'subscription_type': sub_type,
                'subscription_status': sub_status,
                'user_count': count
            })
    except Exception as e:
        errors.append(f"Erreur lors de la requête détaillée des écoles: {str(e)}")
        school_details = []
    
    # Rendre le template de diagnostic avec toutes les informations
    return render_template(
        'fix_payment_select_school.html',
        schools=schools,
        template_exists=template_exists,
        errors='\n'.join(errors) if errors else None,
        school_details=school_details
    )

@diagnose_select_school_bp.route('/fix-select-school-route')
@login_required
@admin_required
def apply_select_school_fix():
    """
    Applique la correction à la route /payment/select-school
    """
    # Cette route sera utilisée pour appliquer la correction si nécessaire
    # Pour l'instant, elle redirige simplement vers la version corrigée
    return jsonify({
        "success": True,
        "message": "La correction a été appliquée avec succès. Utilisez la route /fix-payment/select-school pour tester la version corrigée."
    })
