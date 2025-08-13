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
    
    @staticmethod
    def create_checkout_session(subscription_type, user=None):
        try:
            # Mode simulation si pas de clé Stripe configurée
            stripe_key = os.getenv('STRIPE_SECRET_KEY')
            if not stripe_key:
                print("[SIMULATION MODE] Pas de clé Stripe - simulation du paiement")
                return PaymentService._create_simulation_session(subscription_type, user)
            
            # Déterminer le prix selon le type d'abonnement
            if subscription_type == 'teacher':
                price_amount = int(os.getenv('TEACHER_SUBSCRIPTION_PRICE', 4000))  # 40€ en centimes
                description = 'Abonnement Enseignant - Accès complet'
            elif subscription_type == 'school':
                price_amount = int(os.getenv('SCHOOL_SUBSCRIPTION_PRICE', 8000))  # 80€ en centimes
                description = 'Abonnement École - Accès complet'
            else:
                raise ValueError("Type d'abonnement invalide")
            
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
            
            # Créer la session de paiement
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
                success_url=url_for('payment.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('payment.payment_cancel', _external=True),
                metadata=metadata
            )
            
            return session
            
        except Exception as e:
            current_app.logger.error(f"Erreur création session Stripe: {str(e)}")
            raise
    
    @staticmethod
    def _create_simulation_session(subscription_type, user=None):
        """Créer une session de paiement simulée pour les tests"""
        import uuid
        
        # Déterminer le prix selon le type d'abonnement
        if subscription_type == 'teacher':
            price_amount = 4000  # 40€ en centimes
            description = 'Abonnement Enseignant - Accès complet'
        elif subscription_type == 'school':
            price_amount = 8000  # 80€ en centimes
            description = 'Abonnement École - Accès complet'
        else:
            raise ValueError("Type d'abonnement invalide")
        
        # Créer un objet session simulé
        class SimulatedSession:
            def __init__(self):
                self.id = f"cs_test_{uuid.uuid4().hex[:24]}"
                self.url = f"http://127.0.0.1:5000/payment/simulate-checkout?session_id={self.id}&type={subscription_type}&amount={price_amount}"
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
        print(f"[SIMULATION] Session créée: {session.id}")
        print(f"[SIMULATION] URL de paiement: {session.url}")
        
        return session
    
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
