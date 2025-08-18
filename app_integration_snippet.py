
# Ajoutez ces lignes à votre app.py après l'initialisation des extensions
# et l'intégration du module d'inscription d'école

# Intégration du module de paiement d'école
from school_payment_integration import integrate_school_payment
integrate_school_payment(app)
