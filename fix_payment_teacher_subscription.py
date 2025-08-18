"""
Script de correction pour le problème de paiement des abonnements enseignants sans école.
Ce script corrige l'erreur "Erreur lors de la création de la session de paiement" qui apparaît
lorsqu'un enseignant tente de souscrire à un abonnement individuel.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
import stripe
import os
from datetime import datetime
import traceback

# Blueprint pour la correction
fix_payment_bp = Blueprint('fix_payment', __name__, url_prefix='/fix_payment')

@fix_payment_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Version corrigée de la création de session de paiement"""
    try:
        current_app.logger.info("[FIX_PAYMENT] Début de la création de session de paiement")
        subscription_type = request.form.get('subscription_type')
        
        current_app.logger.info(f"[FIX_PAYMENT] Type d'abonnement: {subscription_type}")
        
        if subscription_type not in ['teacher', 'school']:
            current_app.logger.error(f"[FIX_PAYMENT] Type d'abonnement invalide: {subscription_type}")
            return jsonify({'error': 'Type d\'abonnement invalide'}), 400
        
        # Pour les utilisateurs non connectés, créer une session temporaire
        user = current_user if current_user.is_authenticated else None
        current_app.logger.info(f"[FIX_PAYMENT] Utilisateur authentifié: {user is not None}")
        
        # Déterminer le prix selon le type d'abonnement
        if subscription_type == 'teacher':
            price_amount = int(os.getenv('TEACHER_SUBSCRIPTION_PRICE', 4000))  # 40€ en centimes
            description = 'Abonnement Enseignant - Accès complet'
        elif subscription_type == 'school':
            price_amount = int(os.getenv('SCHOOL_SUBSCRIPTION_PRICE', 8000))  # 80€ en centimes
            description = 'Abonnement École - Accès complet'
        else:
            raise ValueError("Type d'abonnement invalide")
        
        current_app.logger.info(f"[FIX_PAYMENT] Prix: {price_amount/100}€, Description: {description}")
        
        # Préparer les métadonnées selon l'état de connexion de l'utilisateur
        if user and user.is_authenticated:
            # Utilisateur connecté
            user_description = f'Accès complet à la plateforme pour {user.name or user.email}'
            metadata = {
                'user_id': str(user.id),
                'subscription_type': subscription_type,
                'user_email': user.email
            }
        else:
            # Utilisateur non connecté - session temporaire
            user_description = 'Accès complet à la plateforme éducative'
            metadata = {
                'subscription_type': subscription_type,
                'guest_payment': 'true'
            }
        
        current_app.logger.info(f"[FIX_PAYMENT] Métadonnées: {metadata}")
        
        # Vérifier si la clé Stripe est configurée
        stripe_key = os.getenv('STRIPE_SECRET_KEY')
        if not stripe_key:
            current_app.logger.warning("[FIX_PAYMENT] Pas de clé Stripe - simulation du paiement")
            # Créer une session de simulation
            import uuid
            
            class SimulatedSession:
                def __init__(self):
                    self.id = f"cs_test_{uuid.uuid4().hex[:24]}"
                    self.url = f"{request.host_url.rstrip('/')}/payment/simulate-checkout?session_id={self.id}&type={subscription_type}&amount={price_amount}"
                    self.payment_status = "unpaid"
                    self.amount_total = price_amount
                    self.metadata = {
                        'subscription_type': subscription_type,
                        'simulation': 'true'
                    }
                    if user and hasattr(user, 'id'):
                        self.metadata['user_id'] = str(user.id)
                        self.metadata['user_email'] = getattr(user, 'email', '')
                    else:
                        self.metadata['guest_payment'] = 'true'
            
            session = SimulatedSession()
            current_app.logger.info(f"[FIX_PAYMENT] Session simulée créée: {session.id}")
            current_app.logger.info(f"[FIX_PAYMENT] URL de paiement simulé: {session.url}")
            
            return jsonify({'checkout_url': session.url})
        
        # Configurer Stripe avec la clé API
        stripe.api_key = stripe_key
        
        # Créer la session de paiement
        success_url = url_for('payment.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = url_for('payment.payment_cancel', _external=True)
        
        current_app.logger.info(f"[FIX_PAYMENT] URL de succès: {success_url}")
        current_app.logger.info(f"[FIX_PAYMENT] URL d'annulation: {cancel_url}")
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': description,
                        'description': user_description,
                    },
                    'unit_amount': price_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        current_app.logger.info(f"[FIX_PAYMENT] Session Stripe créée avec succès: {session.id}")
        return jsonify({'checkout_url': session.url})
        
    except Exception as e:
        current_app.logger.error(f"[FIX_PAYMENT] Erreur création session: {str(e)}")
        current_app.logger.error(f"[FIX_PAYMENT] Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erreur lors de la création de la session de paiement', 'details': str(e)}), 500

def register_blueprint(app):
    """Enregistre le blueprint de correction dans l'application Flask"""
    app.register_blueprint(fix_payment_bp)
    current_app.logger.info("[FIX_PAYMENT] Blueprint de correction enregistré")
    return True
