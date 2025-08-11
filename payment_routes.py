from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from payment_service import payment_service
from models import User, db
import stripe
import os

# Blueprint pour les routes de paiement
payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/subscribe/<subscription_type>')
@login_required
def subscribe(subscription_type):
    """Page de souscription avec choix du type d'abonnement"""
    if subscription_type not in ['teacher', 'school']:
        flash('Type d\'abonnement invalide.', 'error')
        return redirect(url_for('subscription_status'))
    
    # Vérifier si l'utilisateur n'a pas déjà un abonnement actif
    if current_user.subscription_status in ['paid', 'approved']:
        flash('Vous avez déjà un abonnement actif.', 'info')
        return redirect(url_for('dashboard'))
    
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
@login_required
def create_checkout_session():
    """Créer une session de paiement Stripe"""
    try:
        subscription_type = request.form.get('subscription_type')
        
        if subscription_type not in ['teacher', 'school']:
            return jsonify({'error': 'Type d\'abonnement invalide'}), 400
        
        # Créer la session de paiement
        session = payment_service.create_checkout_session(current_user, subscription_type)
        
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
