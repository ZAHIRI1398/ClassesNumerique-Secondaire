import stripe
import os
from flask import current_app, url_for
from models import User, db
import logging

class PaymentService:
    """Service de gestion des paiements Stripe"""
    
    def __init__(self):
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        self.webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    def create_checkout_session(self, user, subscription_type):
        """Créer une session de paiement Stripe"""
        try:
            # Déterminer le prix selon le type d'abonnement
            if subscription_type == 'teacher':
                price_amount = current_app.config.get('TEACHER_SUBSCRIPTION_PRICE', 4000)  # 40€
                description = "Abonnement Enseignant - Classe Numérique Secondaire"
            elif subscription_type == 'school':
                price_amount = current_app.config.get('SCHOOL_SUBSCRIPTION_PRICE', 8000)  # 80€
                description = "Abonnement École - Classe Numérique Secondaire"
            else:
                raise ValueError("Type d'abonnement invalide")
            
            # Créer la session de paiement
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': description,
                            'description': f'Accès complet à la plateforme pour {user.name or user.email}',
                        },
                        'unit_amount': price_amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('payment_cancel', _external=True),
                metadata={
                    'user_id': str(user.id),
                    'subscription_type': subscription_type,
                    'user_email': user.email
                }
            )
            
            return session
            
        except Exception as e:
            current_app.logger.error(f"Erreur création session Stripe: {str(e)}")
            raise
    
    def verify_payment(self, session_id):
        """Vérifier le statut d'un paiement"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except Exception as e:
            current_app.logger.error(f"Erreur vérification paiement: {str(e)}")
            return None
    
    def handle_successful_payment(self, session):
        """Traiter un paiement réussi"""
        try:
            user_id = int(session.metadata.get('user_id'))
            subscription_type = session.metadata.get('subscription_type')
            
            user = User.query.get(user_id)
            if not user:
                current_app.logger.error(f"Utilisateur {user_id} non trouvé pour le paiement")
                return False
            
            # Mettre à jour le statut de l'utilisateur
            user.subscription_status = 'paid'
            user.subscription_type = subscription_type
            user.payment_session_id = session.id
            user.payment_amount = session.amount_total / 100  # Convertir centimes en euros
            
            db.session.commit()
            
            current_app.logger.info(f"Paiement réussi pour l'utilisateur {user.email}: {session.amount_total/100}€")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erreur traitement paiement réussi: {str(e)}")
            db.session.rollback()
            return False
    
    def handle_webhook(self, payload, sig_header):
        """Traiter les webhooks Stripe"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                self.handle_successful_payment(session)
            
            return True
            
        except ValueError as e:
            current_app.logger.error(f"Payload webhook invalide: {str(e)}")
            return False
        except stripe.error.SignatureVerificationError as e:
            current_app.logger.error(f"Signature webhook invalide: {str(e)}")
            return False
        except Exception as e:
            current_app.logger.error(f"Erreur webhook: {str(e)}")
            return False

# Instance globale du service
payment_service = PaymentService()
