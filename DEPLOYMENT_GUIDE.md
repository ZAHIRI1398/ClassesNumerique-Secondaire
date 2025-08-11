# 🚀 Guide de Déploiement - Classe Numérique Secondaire

## 📋 Prérequis

### 1. Comptes nécessaires
- [x] Compte GitHub (déjà configuré)
- [ ] Compte Railway : https://railway.app
- [ ] Compte Stripe : https://dashboard.stripe.com

### 2. Configuration Stripe
1. Créer un compte Stripe
2. Obtenir les clés API :
   - Clé publique : `pk_test_...` (test) ou `pk_live_...` (production)
   - Clé secrète : `sk_test_...` (test) ou `sk_live_...` (production)
3. Configurer un webhook pour : `https://votre-domaine.com/payment/webhook`

## 🌐 Déploiement sur Railway

### Étape 1 : Préparation
```bash
# Vérifier que tous les fichiers sont prêts
git add .
git commit -m "Préparation déploiement production avec Stripe"
git push origin main
```

### Étape 2 : Configuration Railway
1. Aller sur https://railway.app
2. Se connecter avec GitHub
3. Cliquer "New Project" → "Deploy from GitHub repo"
4. Sélectionner le repository `ClassesNumerique-Secondaire`

### Étape 3 : Variables d'environnement
Dans Railway, aller dans Settings → Variables et ajouter :

```env
# Configuration Flask
SECRET_KEY=votre-clé-secrète-ultra-sécurisée-ici
FLASK_ENV=production

# Base de données (automatique avec Railway PostgreSQL)
DATABASE_URL=postgresql://... (fournie automatiquement)

# Configuration Stripe
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Configuration email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-app

# Configuration application
ADMIN_EMAIL=admin@classesnumeriques.com
```

### Étape 4 : Ajouter PostgreSQL
1. Dans Railway, cliquer "Add Service" → "Database" → "PostgreSQL"
2. La variable `DATABASE_URL` sera automatiquement configurée

### Étape 5 : Déploiement
1. Railway détecte automatiquement le `Procfile`
2. Le déploiement se lance automatiquement
3. Attendre la fin du build (5-10 minutes)

## 🔧 Configuration post-déploiement

### 1. Initialiser la base de données
```python
# Se connecter au shell Railway ou exécuter :
python -c "from app import app, db; db.create_all()"
```

### 2. Créer le compte administrateur
```python
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        username='admin',
        email='admin@classesnumeriques.com',
        name='Administrateur',
        role='admin',
        subscription_status='approved'
    )
    admin.set_password('MotDePasseSecurise123!')
    db.session.add(admin)
    db.session.commit()
    print("Compte admin créé avec succès!")
```

### 3. Configurer le webhook Stripe
1. Dans Stripe Dashboard → Webhooks
2. Ajouter endpoint : `https://votre-domaine.railway.app/payment/webhook`
3. Événements à écouter : `checkout.session.completed`
4. Copier le secret webhook dans les variables Railway

## 🎯 Tests de production

### 1. Test de l'application
- [ ] Accès à l'URL Railway
- [ ] Connexion admin
- [ ] Création d'un compte enseignant
- [ ] Test du paiement (mode test Stripe)

### 2. Test du paiement
- [ ] Processus de souscription
- [ ] Redirection vers Stripe
- [ ] Paiement test (carte 4242 4242 4242 4242)
- [ ] Retour et validation
- [ ] Webhook reçu et traité

## 💰 Coûts estimés

### Railway (mensuel)
- Application web : ~5$
- PostgreSQL : ~5$
- **Total : ~10$/mois**

### Stripe
- 1.4% + 0.25€ par transaction (Europe)
- Exemple : 40€ → 0.81€ de frais

### Domaine (optionnel)
- .com : ~10€/an
- .fr : ~8€/an

## 🔒 Sécurité

### Variables sensibles
- ✅ SECRET_KEY : généré aléatoirement
- ✅ Clés Stripe : en variables d'environnement
- ✅ Mots de passe : hashés en base
- ✅ HTTPS : automatique avec Railway

### Recommandations
- Changer le mot de passe admin par défaut
- Activer l'authentification 2FA sur Stripe
- Surveiller les logs d'erreur
- Sauvegardes automatiques de la base

## 📞 Support

### En cas de problème
1. Vérifier les logs Railway
2. Tester les variables d'environnement
3. Vérifier la configuration Stripe
4. Contacter le support technique

### Logs utiles
```bash
# Dans Railway, onglet "Logs"
# Filtrer par "ERROR" ou "payment"
```

## 🚀 Mise en production

### Checklist finale
- [ ] Tests complets en local
- [ ] Variables d'environnement configurées
- [ ] Base de données initialisée
- [ ] Compte admin créé
- [ ] Webhook Stripe configuré
- [ ] Tests de paiement validés
- [ ] Domaine configuré (optionnel)
- [ ] Monitoring en place

**🎉 Votre plateforme est prête pour la production !**
