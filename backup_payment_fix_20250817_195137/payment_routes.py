from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from payment_service import PaymentService
from models import User, db
import stripe
import os
from datetime import datetime

# Blueprint pour les routes de paiement
payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/subscribe/<subscription_type>')
def subscribe(subscription_type):
    """Page de souscription avec choix du type d'abonnement"""
    # Récupérer le paramètre from_select_school pour éviter la boucle de redirection
    from_select_school = request.args.get('from_select_school', 'false') == 'true'
    
    if subscription_type not in ['teacher', 'school']:
        flash('Type d\'abonnement invalide.', 'error')
        return redirect(url_for('subscription_choice'))
    
    # Vérifier si l'utilisateur est connecté et a déjà un abonnement actif
    if current_user.is_authenticated and current_user.subscription_status == 'approved':
        flash('Vous avez déjà un abonnement actif.', 'info')
        return redirect(url_for('index'))
    
    # Si l'utilisateur choisit l'abonnement école et est déjà associé à une école
    if current_user.is_authenticated and subscription_type == 'school' and current_user.school_name:
        # Rechercher si un autre utilisateur de la même école a déjà un abonnement actif
        from models import User
        school_subscription = User.query.filter(
            User.school_name == current_user.school_name,
            User.subscription_type == 'school',
            User.subscription_status == 'approved'
        ).first()
        
        if school_subscription:
            # L'école a déjà un abonnement actif, approuver automatiquement cet utilisateur
            current_app.logger.info(f"Approbation automatique pour {current_user.email} car l'école {current_user.school_name} a déjà payé")
            current_user.subscription_status = 'approved'
            current_user.subscription_type = 'school'
            current_user.approval_date = datetime.utcnow()
            db.session.commit()
            
            flash(f'Votre école {current_user.school_name} a déjà un abonnement actif. Votre compte a été automatiquement approuvé.', 'success')
            return redirect(url_for('index'))
    
    # Si l'utilisateur est un enseignant et choisit l'abonnement école, rediriger vers la sélection d'école
    # Mais seulement s'il ne vient pas déjà de la page de sélection d'école (évite la boucle infinie)
    if current_user.is_authenticated and subscription_type == 'school' and current_user.role == 'teacher' and not from_select_school:
        return redirect(url_for('payment.select_school'))
    
    # Déterminer le prix
    if subscription_type == 'teacher':
        price = 40
        description = "Accès complet pour un enseignant"
    else:  # school
        price = 80
        description = "Accès complet pour une école"
    
    return render_template('payment/subscribe.html', 
                         subscription_type=subscription_type,
                         price=price,
                         description=description)

@payment_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Créer une session de paiement Stripe"""
    try:
        subscription_type = request.form.get('subscription_type')
        
        if subscription_type not in ['teacher', 'school']:
            return jsonify({'error': 'Type d\'abonnement invalide'}), 400
        
        # Pour les utilisateurs non connectés, créer une session temporaire
        user = current_user if current_user.is_authenticated else None
        
        # Créer la session de paiement
        session = PaymentService.create_checkout_session(subscription_type, user)
        
        return jsonify({'checkout_url': session.url})
        
    except Exception as e:
        current_app.logger.error(f"Erreur création session: {str(e)}")
        return jsonify({'error': 'Erreur lors de la création de la session de paiement'}), 500

@payment_bp.route('/success')
@login_required
def payment_success():
    """Page de confirmation de paiement réussi"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Session de paiement invalide.', 'error')
        return redirect(url_for('subscription_status'))
    
    # Vérifier le paiement
    session = payment_service.verify_payment(session_id)
    
    if not session or session.payment_status != 'paid':
        flash('Paiement non confirmé. Veuillez contacter le support.', 'error')
        return redirect(url_for('subscription_status'))
    
    # Traiter le paiement réussi
    if payment_service.handle_successful_payment(session):
        flash('Paiement réussi ! Votre abonnement est en attente de validation par un administrateur.', 'success')
    else:
        flash('Erreur lors du traitement du paiement. Veuillez contacter le support.', 'error')
    
    return render_template('payment/success.html', session=session)

@payment_bp.route('/simulate-checkout')
def simulate_checkout():
    """Page de simulation de paiement pour les tests"""
    session_id = request.args.get('session_id')
    subscription_type = request.args.get('type')
    amount = request.args.get('amount', '4000')
    
    if not session_id or not subscription_type:
        flash('Paramètres de simulation invalides.', 'error')
        return redirect(url_for('subscription_choice'))
    
    # Convertir le montant en euros
    price_euros = int(amount) / 100
    
    return render_template('payment/simulate_checkout.html', 
                         session_id=session_id,
                         subscription_type=subscription_type,
                         amount=amount,
                         price_euros=price_euros)

@payment_bp.route('/simulate-payment', methods=['POST'])
def simulate_payment():
    """Traiter le paiement simulé"""
    session_id = request.form.get('session_id')
    action = request.form.get('action')  # 'success' ou 'cancel'
    
    if action == 'success':
        # Simuler un paiement réussi
        flash('🎉 Paiement simulé réussi ! Redirection vers la page de succès...', 'success')
        return redirect(url_for('payment.payment_success', session_id=session_id))
    else:
        # Simuler une annulation
        flash('❌ Paiement simulé annulé.', 'info')
        return redirect(url_for('payment.payment_cancel'))

@payment_bp.route('/cancel')
@login_required
def payment_cancel():
    """Page d'annulation de paiement"""
    flash('Paiement annulé. Vous pouvez réessayer à tout moment.', 'info')
    return render_template('payment/cancel.html')

@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Webhook Stripe pour traiter les événements de paiement"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    if payment_service.handle_webhook(payload, sig_header):
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error'}), 400

@payment_bp.route('/status')
@login_required
def payment_status():
    """Page de statut du paiement et de l'abonnement"""
    return render_template('payment/status.html', user=current_user)

# Route pour l'ancienne URL (compatibilité)
@payment_bp.route('/process_payment', methods=['POST'])
@login_required
def process_payment_redirect():
    """Redirection vers la nouvelle logique de paiement"""
    subscription_type = request.form.get('subscription_type', 'teacher')
    return redirect(url_for('payment.subscribe', subscription_type=subscription_type))

@payment_bp.route('/select_school')
@login_required
def select_school():
    """Page de sélection d'une école déjà abonnée"""
    # Vérifier que l'utilisateur est un enseignant
    if not current_user.role == 'teacher':
        flash('Cette page est réservée aux enseignants.', 'error')
        return redirect(url_for('index'))
    
    # Récupérer la liste des écoles ayant un abonnement actif
    from models import User
    from sqlalchemy import func
    
    current_app.logger.debug("=== DÉBUT REQUÊTE ÉCOLES AVEC ABONNEMENT ===")
    
    # Vérifier toutes les écoles dans la base de données avec leurs statuts et types d'abonnement
    all_schools_details = db.session.query(User.school_name, User.subscription_status, User.subscription_type).\
        filter(User.school_name != None).\
        filter(User.school_name != '').distinct().all()
    
    current_app.logger.debug(f"Toutes les écoles dans la base avec détails: {all_schools_details}")
    
    # Afficher les écoles avec leurs statuts d'abonnement de manière plus lisible
    for school in all_schools_details:
        current_app.logger.debug(f"École: {school.school_name}, Statut: {school.subscription_status}, Type: {school.subscription_type}")
        
    all_schools = db.session.query(User.school_name, User.subscription_status).\
        filter(User.school_name != None).\
        filter(User.school_name != '').distinct().all()
    
    current_app.logger.debug(f"Toutes les écoles dans la base: {all_schools}")
    
    # Trouver toutes les écoles avec au moins un utilisateur ayant un abonnement actif
    schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
        filter(User.school_name != None).\
        filter(User.school_name != '').\
        filter(User.subscription_type == 'school').\
        filter(User.subscription_status == 'approved').\
        group_by(User.school_name).all()
    
    current_app.logger.debug(f"Écoles avec abonnement trouvées: {schools_with_subscription}")
    
    # Si aucune école n'est trouvée
    if not schools_with_subscription:
        current_app.logger.warning("Aucune école avec abonnement actif n'a été trouvée")
        flash('Aucune école avec un abonnement actif n\'a été trouvée. Veuillez procéder au paiement pour un abonnement école.', 'info')
        return redirect(url_for('payment.subscribe', subscription_type='school', from_select_school='true'))
    
    current_app.logger.info(f"Écoles avec abonnement trouvées: {[school.school_name for school in schools_with_subscription]}")
    current_app.logger.debug("=== FIN REQUÊTE ÉCOLES AVEC ABONNEMENT ===")
    
    return render_template('payment/select_school.html', schools=schools_with_subscription)

@payment_bp.route('/join_school', methods=['POST'])
@login_required
def join_school():
    """Associer un enseignant à une école déjà abonnée"""
    current_app.logger.debug("=== DÉBUT ROUTE JOIN_SCHOOL ===")
    current_app.logger.debug(f"Méthode: {request.method}")
    current_app.logger.debug(f"Headers: {dict(request.headers)}")
    current_app.logger.debug(f"Form data: {dict(request.form)}")
    current_app.logger.debug(f"CSRF token présent: {'csrf_token' in request.form}")
    
    # Vérifier que l'utilisateur est un enseignant
    if not current_user.role == 'teacher':
        current_app.logger.warning(f"Accès refusé: l'utilisateur {current_user.email} n'est pas un enseignant")
        flash('Cette fonctionnalité est réservée aux enseignants.', 'error')
        return redirect(url_for('index'))
    
    # Récupérer le nom de l'école sélectionnée
    school_name = request.form.get('school_name')
    current_app.logger.debug(f"École sélectionnée: {school_name}")
    
    if not school_name:
        current_app.logger.warning("Aucune école sélectionnée")
        flash('Veuillez sélectionner une école.', 'error')
        return redirect(url_for('payment.select_school'))
    
    # Vérifier que l'école a bien un abonnement actif
    from models import User
    try:
        current_app.logger.debug(f"Recherche d'un abonnement actif pour l'école: {school_name}")
        
        # Vérifier tous les utilisateurs associés à cette école et leurs statuts d'abonnement
        all_school_users = User.query.filter(
            User.school_name == school_name
        ).all()
        
        current_app.logger.debug(f"Nombre d'utilisateurs associés à l'école {school_name}: {len(all_school_users)}")
        
        for user in all_school_users:
            current_app.logger.debug(f"Utilisateur: {user.email}, Rôle: {user.role}, Type d'abonnement: {user.subscription_type}, Statut: {user.subscription_status}")
        
        # Recherche spécifique pour un abonnement école actif
        school_subscription = User.query.filter(
            User.school_name == school_name,
            User.subscription_type == 'school',
            User.subscription_status == 'approved'
        ).first()
        
        current_app.logger.debug(f"Résultat de la recherche d'abonnement actif: {school_subscription is not None}")
        if school_subscription:
            current_app.logger.debug(f"Détails de l'abonnement trouvé: Utilisateur {school_subscription.email}, Type: {school_subscription.subscription_type}, Statut: {school_subscription.subscription_status}")
        else:
            current_app.logger.debug(f"Aucun abonnement actif trouvé pour l'école {school_name}. Vérification des critères de recherche.")
            # Vérifier s'il y a des utilisateurs avec un abonnement école mais un statut différent
            other_status = User.query.filter(
                User.school_name == school_name,
                User.subscription_type == 'school',
                User.subscription_status != 'approved'
            ).all()
            
            if other_status:
                for user in other_status:
                    current_app.logger.debug(f"Utilisateur avec abonnement école mais statut non approuvé: {user.email}, Statut: {user.subscription_status}")
            else:
                current_app.logger.debug(f"Aucun utilisateur avec abonnement école trouvé pour {school_name}")
        
        
        if not school_subscription:
            current_app.logger.warning(f"École sans abonnement actif: {school_name}")
            flash('Cette école n\'a pas d\'abonnement actif.', 'error')
            return redirect(url_for('payment.select_school'))
        
        # Associer l'enseignant à l'école et activer son abonnement
        current_app.logger.debug(f"Association de l'enseignant {current_user.email} à l'école {school_name}")
        current_user.school_name = school_name
        current_user.subscription_status = 'approved'
        current_user.subscription_type = 'school'
        current_user.approval_date = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"Enseignant {current_user.email} associé avec succès à l'école {school_name} avec abonnement approuvé")
        flash(f'Vous avez été associé avec succès à l\'école {school_name}. Votre compte a été automatiquement approuvé.', 'success')
        
        return redirect(url_for('index'))
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'association à l'école: {str(e)}")
        flash('Une erreur est survenue lors de l\'association à l\'école. Veuillez réessayer.', 'error')
        return redirect(url_for('payment.select_school'))
    
    finally:
        current_app.logger.debug("=== FIN ROUTE JOIN_SCHOOL ===")
