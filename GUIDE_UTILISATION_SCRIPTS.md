# Guide d'utilisation des scripts

Ce document explique comment utiliser les différents scripts créés pour la correction du scoring insensible à l'ordre des réponses dans les exercices de type "fill_in_blanks".

## 1. Script de déploiement

### `deploy_order_insensitive_scoring.py`

Ce script automatise le processus de déploiement de la correction vers Railway.

**Utilisation :**
```bash
python deploy_order_insensitive_scoring.py
```

**Fonctionnalités :**
- Vérifie que tous les fichiers nécessaires existent
- Vérifie le statut git du projet
- Ajoute les fichiers modifiés au staging
- Crée un commit avec un message descriptif
- Demande confirmation avant de pousser vers Railway
- Affiche des instructions pour vérifier l'application après déploiement

**Prérequis :**
- Git doit être installé et configuré
- Le dépôt Railway doit être configuré comme remote

## 2. Scripts de test

### `test_comprehensive_order_insensitive.py`

Ce script teste de manière exhaustive la correction du scoring insensible à l'ordre avec différents scénarios.

**Utilisation :**
```bash
python test_comprehensive_order_insensitive.py
```

**Fonctionnalités :**
- Vérifie la logique de scoring avec des exemples simples
- Récupère tous les exercices de type "fill_in_blanks" de la base de données
- Teste chaque exercice avec différentes combinaisons d'ordre des réponses
- Génère un résumé des tests

**Prérequis :**
- Accès à la base de données `app.db`
- Au moins un exercice de type "fill_in_blanks" dans la base de données

### `check_exercise_compatibility.py`

Ce script vérifie la compatibilité de la modification avec les autres types d'exercices.

**Utilisation :**
```bash
python check_exercise_compatibility.py
```

**Fonctionnalités :**
- Analyse le fichier `app.py` pour identifier les types d'exercices
- Vérifie quels types d'exercices utilisent une logique similaire
- Génère un rapport de compatibilité

**Prérequis :**
- Accès au fichier `app.py`
- Accès à la base de données `app.db`

### `verify_post_deployment.py`

Ce script vérifie le bon fonctionnement de l'application après déploiement.

**Utilisation :**
```bash
python verify_post_deployment.py --url https://classesnumeriques.up.railway.app --username votre_nom --password votre_mot_de_passe
```

**Arguments :**
- `--url` : URL de l'application déployée (par défaut : https://classesnumeriques.up.railway.app)
- `--username` : Nom d'utilisateur pour la connexion
- `--password` : Mot de passe pour la connexion

**Fonctionnalités :**
- Vérifie si le site est accessible
- Tente de se connecter à l'application
- Recherche un exercice de type "fill_in_blanks"
- Teste la soumission d'un exercice avec des réponses dans un ordre différent
- Génère un rapport de vérification

**Prérequis :**
- Connexion Internet
- Compte utilisateur valide sur l'application
- Module Python `requests` installé

## 3. Ordre d'utilisation recommandé

Pour une utilisation optimale, suivez cet ordre :

1. **Avant déploiement :**
   - Exécuter `test_comprehensive_order_insensitive.py` pour vérifier que la correction fonctionne
   - Exécuter `check_exercise_compatibility.py` pour s'assurer que la modification n'affecte pas d'autres types d'exercices

2. **Déploiement :**
   - Exécuter `deploy_order_insensitive_scoring.py` pour déployer la correction

3. **Après déploiement :**
   - Exécuter `verify_post_deployment.py` pour vérifier que tout fonctionne correctement en production

## 4. Résolution des problèmes courants

### Problème : Le script de déploiement échoue avec une erreur git

**Solution :**
- Vérifiez que git est correctement installé et configuré
- Vérifiez que vous avez les droits d'accès au dépôt Railway
- Vérifiez que les fichiers `app.py` et `DOCUMENTATION_ORDER_INSENSITIVE_SCORING.md` existent

### Problème : Les tests échouent

**Solution :**
- Vérifiez que la base de données `app.db` est accessible
- Vérifiez que la logique de scoring a été correctement modifiée dans `app.py`
- Vérifiez qu'il existe des exercices de type "fill_in_blanks" dans la base de données

### Problème : La vérification post-déploiement échoue

**Solution :**
- Vérifiez que l'application est accessible à l'URL spécifiée
- Vérifiez que vos identifiants de connexion sont corrects
- Vérifiez que l'exercice de test existe et est de type "fill_in_blanks"
- Consultez les logs de l'application pour détecter d'éventuelles erreurs

## 5. Documentation supplémentaire

Pour plus d'informations, consultez les fichiers suivants :

- `DOCUMENTATION_ORDER_INSENSITIVE_SCORING.md` - Documentation détaillée de la correction
- `RESUME_MODIFICATIONS_SCORING_INSENSIBLE_ORDRE.md` - Résumé des modifications effectuées
