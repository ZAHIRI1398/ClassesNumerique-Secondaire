# Instructions pour démarrer l'application principale

Ce document explique comment démarrer correctement l'application principale Classes Numériques après avoir effectué des tests avec les scripts de diagnostic.

## Problème identifié

Lors de l'exécution de la commande `flask run` ou `python -m flask run`, l'application qui démarre peut être un script de test plutôt que l'application principale, en fonction de la variable d'environnement `FLASK_APP` ou du dernier script Python exécuté.

## Solution

### Option 1 : Spécifier explicitement l'application principale

```bash
# Sous Windows (PowerShell)
$env:FLASK_APP = "app.py"
flask run

# Sous Windows (CMD)
set FLASK_APP=app.py
flask run
```

### Option 2 : Exécuter directement le fichier app.py

```bash
python app.py
```

Cette méthode est plus directe et évite les problèmes liés à la variable d'environnement `FLASK_APP`.

## Vérification

Pour vérifier que vous avez bien démarré l'application principale et non un script de test :

1. L'URL de base devrait afficher la page d'accueil de Classes Numériques et non une page de test
2. Les routes standard comme `/login`, `/register`, etc. devraient être accessibles
3. La console devrait afficher le message de démarrage standard de l'application principale

## Arrêter les scripts de test en cours d'exécution

Si un script de test est déjà en cours d'exécution, vous devez l'arrêter avant de démarrer l'application principale :

1. Localisez le terminal où le script est en cours d'exécution
2. Appuyez sur `Ctrl+C` pour arrêter le serveur Flask
3. Vérifiez qu'aucun autre processus Python n'utilise le port 5000 (port par défaut de Flask)

## Ports utilisés

- Application principale : port 5000 (par défaut)
- Scripts de test : ports variés (généralement 5001, 5002, etc.)

Si vous rencontrez une erreur indiquant que le port est déjà utilisé, vous pouvez spécifier un port différent :

```bash
flask run --port=5050
```

ou

```bash
python app.py --port=5050
```

## Résolution des problèmes courants

### Le script de test démarre au lieu de l'application principale

Cela peut se produire si la variable d'environnement `FLASK_APP` pointe vers un script de test. Utilisez l'option 1 ou 2 ci-dessus pour résoudre ce problème.

### Erreur "No module named 'app'"

Assurez-vous que vous êtes dans le répertoire racine du projet avant d'exécuter les commandes.

### Erreur "Address already in use"

Un autre processus utilise déjà le port. Utilisez un port différent comme indiqué ci-dessus ou arrêtez le processus qui utilise le port.
