# Documentation de correction du flux d'abonnement en production

## Problème identifié

Le système ne détecte pas correctement les écoles avec abonnement actif en production, ce qui entraîne les problèmes suivants :
- Message "Aucune école avec un abonnement actif n'a été trouvée" alors que des écoles ont un abonnement actif
- Redirection infinie vers la page de paiement lorsqu'un enseignant tente de rejoindre une école
- Impossibilité pour les enseignants de s'associer à une école avec abonnement

## Causes identifiées

1. **Différence de nom d'école** : L'école "École Bruxelles II" est enregistrée comme "Ecole Bruxelles ll" dans la base de données (sans accent et avec des 'l' minuscules au lieu de chiffres romains)
2. **Type d'abonnement incorrect** : Les utilisateurs associés à cette école ont un `subscription_type` défini sur 'trial' au lieu de 'school'
3. **Filtre SQL trop restrictif** : Le code filtre sur `subscription_status.in_(['paid', 'approved'])` alors que seul 'approved' est utilisé en production

## Corrections apportées

### 1. Correction du code de production

Le fichier `payment_routes.py` dans le dossier `production_code/ClassesNumerique-Secondaire-main/` a été modifié pour :
- Filtrer uniquement sur `subscription_status == 'approved'` au lieu de `subscription_status.in_(['paid', 'approved'])`
- Ajouter des logs de débogage pour faciliter le diagnostic
- Afficher toutes les écoles et leurs statuts d'abonnement pour vérification

### 2. Script de mise à jour de la base de données de production

Un script `update_production_database.py` a été créé pour :
- Se connecter à la base de données PostgreSQL de production
- Corriger le nom de l'école de "Ecole Bruxelles ll" à "École Bruxelles II"
- Corriger le type d'abonnement de 'trial' à 'school' pour les utilisateurs concernés
- Vérifier que les corrections ont été appliquées correctement

## Instructions de déploiement

### Étape 1 : Mise à jour du code

1. Connectez-vous au serveur Railway ou à votre plateforme d'hébergement
2. Mettez à jour le fichier `payment_routes.py` avec les modifications apportées :
   - Remplacer le filtre `subscription_status.in_(['paid', 'approved'])` par `subscription_status == 'approved'`
   - Ajouter les logs de débogage comme indiqué dans le fichier modifié

### Étape 2 : Mise à jour de la base de données

1. Installez les dépendances nécessaires :
   ```bash
   pip install psycopg2-binary
   ```

2. Configurez la variable d'environnement `DATABASE_URL` avec l'URL de connexion à votre base de données PostgreSQL :
   ```bash
   # Windows
   set DATABASE_URL=postgresql://username:password@host:port/database
   
   # Linux/Mac
   export DATABASE_URL=postgresql://username:password@host:port/database
   ```

3. Exécutez le script de mise à jour :
   ```bash
   python update_production_database.py
   ```

4. Vérifiez le fichier de log `update_production_database.log` pour confirmer que les modifications ont été appliquées avec succès

### Étape 3 : Vérification

1. Redémarrez l'application Flask pour que les modifications du code prennent effet
2. Connectez-vous en tant qu'enseignant et accédez à la page de sélection d'école
3. Vérifiez que l'école "École Bruxelles II" apparaît dans la liste des écoles avec abonnement actif
4. Essayez de rejoindre cette école et confirmez que le processus fonctionne correctement

## Logs et diagnostics

Le code modifié génère des logs détaillés qui peuvent être utilisés pour diagnostiquer d'éventuels problèmes :

- `[DEBUG_SCHOOL] Toutes les écoles dans la base: ...` - Liste toutes les écoles avec leur statut d'abonnement
- `[DEBUG_SCHOOL] Écoles avec abonnement trouvées: ...` - Liste les écoles qui passent le filtre d'abonnement actif
- `[DEBUG_SCHOOL] Vérification abonnement pour l'école: ...` - Vérifie si une école spécifique a un abonnement actif

## Prévention des problèmes futurs

Pour éviter que ce type de problème ne se reproduise à l'avenir, nous recommandons :

1. **Normalisation des noms d'écoles** :
   - Standardiser la casse (majuscules/minuscules)
   - Gérer correctement les caractères spéciaux et accents
   - Utiliser des chiffres romains cohérents (II au lieu de ll)

2. **Validation des types d'abonnement** :
   - S'assurer que le type d'abonnement est correctement défini lors de la création/modification des utilisateurs
   - Ajouter des vérifications pour éviter les incohérences

3. **Tests automatisés** :
   - Créer des tests qui vérifient spécifiquement la détection des écoles avec abonnement
   - Tester régulièrement le flux complet d'abonnement et d'association d'école

4. **Monitoring** :
   - Mettre en place une surveillance des logs pour détecter les problèmes similaires
   - Créer des alertes en cas d'échec répété de détection d'écoles avec abonnement

## Conclusion

Ces corrections permettent de résoudre le problème de détection des écoles avec abonnement actif en production. Les modifications apportées sont minimales et ciblées pour éviter d'introduire de nouveaux problèmes.

Le script de mise à jour de la base de données est conçu pour être idempotent, ce qui signifie qu'il peut être exécuté plusieurs fois sans effet secondaire indésirable.
