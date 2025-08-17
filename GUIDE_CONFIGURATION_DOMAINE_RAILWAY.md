# Guide de configuration d'un domaine personnalisé pour votre application Railway

Ce guide vous explique comment configurer un domaine personnalisé pour votre application hébergée sur Railway.

## 1. Options d'hébergement de domaine disponibles

Avant de configurer votre domaine sur Railway, vous devez d'abord acheter un nom de domaine. Voici quelques registrars populaires où vous pouvez acheter votre domaine :

- **Namecheap** : Offre des prix compétitifs et un service client de qualité
- **GoDaddy** : L'un des registrars les plus connus avec une large gamme de TLDs
- **OVH** : Registrar français avec de bonnes options pour les domaines européens
- **Google Domains** : Interface simple et intégration avec d'autres services Google
- **Gandi.net** : Registrar français réputé pour sa transparence

Le coût d'un domaine varie généralement entre 10€ et 20€ par an pour les extensions courantes (.com, .fr, .org, etc.).

## 2. Lier votre domaine à votre application Railway

Une fois que vous avez acheté votre domaine, suivez ces étapes pour le configurer sur Railway :

1. **Connectez-vous à votre compte Railway** et accédez à votre projet
2. **Sélectionnez le service** auquel vous souhaitez associer votre domaine (généralement votre service web)
3. **Cliquez sur l'onglet "Settings"** dans le menu de navigation
4. **Faites défiler jusqu'à la section "Domains"**
5. **Cliquez sur "Add Domain"**
6. **Entrez votre nom de domaine** (par exemple, classesnumeriques.fr)
7. **Cliquez sur "Add"**

Railway va maintenant générer les informations DNS nécessaires pour configurer votre domaine.

## 3. Configuration DNS

Après avoir ajouté votre domaine sur Railway, vous devrez configurer les enregistrements DNS chez votre registrar. Railway vous fournira deux types d'informations :

### Option 1 : Configuration CNAME (recommandée)

1. Connectez-vous au panneau de gestion de votre registrar
2. Accédez à la section de gestion DNS
3. Ajoutez un enregistrement CNAME avec :
   - **Nom/Host** : @ ou www (selon que vous voulez configurer le domaine racine ou le sous-domaine www)
   - **Valeur/Target** : l'URL fournie par Railway (généralement quelque chose comme `yourapp.up.railway.app`)
   - **TTL** : Auto ou 3600

### Option 2 : Configuration ALIAS/ANAME (pour domaine racine)

Certains registrars ne permettent pas d'utiliser un CNAME pour le domaine racine. Dans ce cas :

1. Utilisez un enregistrement ALIAS ou ANAME (si disponible)
2. Pointez-le vers l'URL fournie par Railway

### Option 3 : Configuration A Record (alternative)

Si votre registrar ne supporte ni CNAME pour le domaine racine ni ALIAS/ANAME :

1. Ajoutez un enregistrement A avec :
   - **Nom/Host** : @ (pour le domaine racine)
   - **Valeur** : les adresses IP fournies par Railway
   - **TTL** : Auto ou 3600

## 4. Vérification et attente de propagation

1. Une fois les enregistrements DNS configurés, retournez sur Railway
2. Railway vérifiera automatiquement la configuration DNS
3. La propagation DNS peut prendre jusqu'à 48 heures, mais généralement quelques heures suffisent
4. Une fois la vérification réussie, Railway affichera "Active" à côté de votre domaine

## 5. Configuration SSL (HTTPS)

Railway configure automatiquement un certificat SSL pour votre domaine personnalisé. Vous n'avez rien à faire de plus pour activer HTTPS.

## 6. Sous-domaines supplémentaires

Si vous souhaitez configurer plusieurs sous-domaines (par exemple, api.votredomaine.com, admin.votredomaine.com) :

1. Répétez le processus d'ajout de domaine sur Railway pour chaque sous-domaine
2. Configurez les enregistrements CNAME correspondants chez votre registrar

## Dépannage

Si vous rencontrez des problèmes lors de la configuration de votre domaine :

- **Vérifiez que les enregistrements DNS sont correctement configurés** chez votre registrar
- **Utilisez des outils comme [DNSChecker](https://dnschecker.org)** pour vérifier la propagation DNS
- **Attendez au moins 24 heures** pour la propagation complète des DNS
- **Consultez la documentation Railway** pour des informations spécifiques à votre cas

## Coûts associés

- **Achat du domaine** : 10€-20€/an selon l'extension
- **Railway** : La configuration de domaines personnalisés est incluse dans tous les plans Railway, y compris le plan gratuit (avec limitations)

## Ressources supplémentaires

- [Documentation officielle Railway sur les domaines personnalisés](https://docs.railway.app/deploy/exposing-your-app#custom-domains)
- [Guide de dépannage DNS](https://docs.railway.app/troubleshoot/dns-issues)
