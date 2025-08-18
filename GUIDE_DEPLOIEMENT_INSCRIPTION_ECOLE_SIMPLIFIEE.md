# Guide de déploiement : Simplification de l'inscription des écoles

## Préparation au déploiement

1. **Vérifier que tous les fichiers sont en place**
   - Template `register_school_connected.html` dans `templates/auth/`
   - Module `school_registration_mod.py` dans `blueprints/`
   - Script d'intégration `integrate_school_registration_mod.py` à la racine

2. **Vérifier l'intégration dans app.py**
   ```python
   from integrate_school_registration_mod import integrate_school_registration_mod
   integrate_school_registration_mod(app)
   ```

3. **Exécuter le test pour confirmer que tout fonctionne**
   ```
   python test_school_registration_mod.py
   ```

## Déploiement sur Railway

1. **Commiter les changements**
   ```
   git add .
   git commit -m "Simplification du processus d'inscription des écoles"
   git push
   ```

2. **Déployer sur Railway**
   - Se connecter à Railway
   - Accéder au projet ClassesNumerique-Secondaire
   - Déclencher un nouveau déploiement depuis l'interface

3. **Vérifier le déploiement**
   - Attendre que le déploiement soit terminé
   - Accéder à l'URL de l'application
   - Tester le formulaire d'inscription école en étant connecté et déconnecté

## Vérification post-déploiement

1. **Tester en tant qu'utilisateur non connecté**
   - Accéder à `/register/school`
   - Vérifier que le formulaire complet s'affiche (nom, email, mot de passe, école)
   - Remplir le formulaire et soumettre
   - Vérifier la redirection vers le flux d'abonnement

2. **Tester en tant qu'utilisateur connecté**
   - Se connecter avec un compte existant
   - Accéder à `/register/school`
   - Vérifier que seul le champ "Nom de l'établissement" s'affiche
   - Remplir le formulaire et soumettre
   - Vérifier que l'école est associée au compte existant
   - Vérifier la redirection vers le flux d'abonnement

3. **Vérifier dans la base de données**
   - Confirmer que les utilisateurs ont bien le champ `school_name` rempli
   - Confirmer que le type d'abonnement est correctement défini

## Résolution des problèmes courants

1. **Erreur 500 lors de l'accès à la route**
   - Vérifier les logs de l'application
   - S'assurer que les importations sont correctes
   - Vérifier que le template existe au bon emplacement

2. **Problème d'importation des modèles**
   - Utiliser des importations absolues (`from models import User, db`)
   - Éviter les importations relatives (`from .models import User, db`)

3. **Conflit de blueprints**
   - Vérifier que les noms des blueprints sont uniques
   - Utiliser l'option `name=` pour fournir un nom unique si nécessaire

## Contact en cas de problème

Si vous rencontrez des problèmes lors du déploiement, contactez l'équipe technique à support@classenumerique.com
