# Instructions de déploiement pour la correction du flux d'abonnement

## Modifications apportées

1. **Modification de la requête SQL** pour inclure les écoles avec statuts `pending`, `paid` et `approved`
2. **Correction du format des données** passées au template `select_school.html`
3. **Ajout de logs détaillés** pour faciliter le diagnostic des problèmes

## Étapes de déploiement

### 1. Vérifier les fichiers modifiés

```bash
git status
```

Vous devriez voir les fichiers suivants modifiés :
- `production_code/ClassesNumerique-Secondaire-main/payment_routes.py`
- `RESUME_CORRECTION_FLUX_ABONNEMENT.md`
- `check_subscription_statuses.py` (nouveau)
- `run_check_subscription_statuses.bat` (nouveau)

### 2. Ajouter les fichiers au commit

```bash
git add production_code/ClassesNumerique-Secondaire-main/payment_routes.py
git add RESUME_CORRECTION_FLUX_ABONNEMENT.md
git add check_subscription_statuses.py
git add run_check_subscription_statuses.bat
git add INSTRUCTIONS_DEPLOIEMENT_CORRECTION_FLUX_ABONNEMENT.md
```

### 3. Créer un commit avec un message descriptif

```bash
git commit -m "Correction du flux d'abonnement: inclusion des statuts pending/paid et format des données pour le template"
```

### 4. Pousser les modifications vers le dépôt distant

```bash
git push
```

## Vérification après déploiement

### 1. Exécuter le script de vérification des routes

Avant d'exécuter le script, modifiez le fichier `run_check_routes.bat` pour y mettre l'URL correcte de votre application :

```bash
set PRODUCTION_APP_URL=https://votre-application.up.railway.app
```

Puis exécutez le script :

```bash
run_check_routes.bat
```

### 2. Vérifier les statuts d'abonnement des écoles

Modifiez le fichier `run_check_subscription_statuses.bat` pour y mettre l'URL correcte de votre base de données :

```bash
set PRODUCTION_DATABASE_URL=postgres://user:password@host:port/database
```

Puis exécutez le script :

```bash
run_check_subscription_statuses.bat
```

### 3. Analyser les logs de production

Recherchez les logs avec les préfixes suivants :
- `[SUBSCRIBE_DEBUG]`
- `[SELECT_SCHOOL_DEBUG]`

Vérifiez particulièrement :
- Le nombre d'écoles trouvées
- Les statuts d'abonnement de chaque école
- Le format des données passées au template

### 4. Tester manuellement le flux d'abonnement

1. Accédez à la page `/payment/subscribe/school`
2. Vérifiez que vous êtes bien redirigé vers `/payment/select_school`
3. Vérifiez que les écoles avec abonnement (statuts `pending`, `paid` ou `approved`) sont bien affichées
4. Testez l'association à une école existante

## En cas de problème

Si le problème persiste après déploiement :

1. Vérifiez les logs pour identifier l'erreur
2. Assurez-vous que les modifications ont bien été déployées (vérifiez la date de dernière modification des fichiers)
3. Vérifiez que le format des données dans la base de production correspond à celui attendu
4. Si nécessaire, utilisez le script `check_subscription_statuses.py` pour analyser en détail les statuts d'abonnement
