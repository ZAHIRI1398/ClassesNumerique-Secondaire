# Documentation : Vérification et correction des images QCM en production

## Contexte

Les exercices de type QCM dans l'application peuvent contenir des images qui sont stockées dans différents répertoires. Au fil du temps, certaines images ont pu être déplacées, renommées ou supprimées, ce qui peut entraîner des problèmes d'affichage. Cette documentation décrit la solution mise en place pour vérifier et corriger les problèmes d'images QCM en production.

## Solution implémentée

### 1. Script de vérification des images QCM

Le script `verify_qcm_images_production_fixed.py` permet de vérifier que toutes les images des exercices QCM sont accessibles, tant localement qu'en production. Il génère un rapport détaillé des problèmes détectés et un script de correction automatique.

#### Fonctionnalités principales

- **Vérification locale et distante** : Le script vérifie si les images existent localement et sur le serveur de production.
- **Recherche dans les chemins alternatifs** : Si une image n'est pas trouvée à son emplacement principal, le script recherche dans plusieurs chemins alternatifs.
- **Génération de rapport** : Un rapport au format Markdown est généré avec la liste des problèmes détectés.
- **Génération de script de correction** : Un script Python est automatiquement généré pour corriger les problèmes détectés.
- **Journalisation détaillée** : Toutes les actions sont enregistrées dans un fichier de log horodaté.

### 2. Script de correction automatique

Le script de correction généré automatiquement permet de :

- Copier les images manquantes depuis les chemins alternatifs vers le répertoire standard `/static/uploads/exercises/qcm/`.
- Mettre à jour les chemins d'images dans la base de données.
- Sauvegarder la base de données avant toute modification.
- Générer un rapport détaillé des actions effectuées.

## Comment utiliser les scripts

### Vérification des images QCM

1. Exécuter le script de vérification :
   ```bash
   python verify_qcm_images_production_fixed.py
   ```

2. Consulter le rapport généré (`qcm_images_report_YYYYMMDD_HHMMSS.md`) pour voir les problèmes détectés.

3. Consulter le fichier de log (`qcm_images_verification_YYYYMMDD_HHMMSS.log`) pour plus de détails sur l'exécution du script.

### Correction automatique des problèmes

1. Exécuter le script de correction généré automatiquement :
   ```bash
   python fix_qcm_images_YYYYMMDD_HHMMSS.py
   ```

2. Vérifier les résultats de la correction dans la console.

3. Relancer le script de vérification pour confirmer que tous les problèmes ont été résolus.

## Configuration du script de vérification

Avant d'exécuter le script de vérification en production, vous devez configurer l'URL de base de l'application :

1. Ouvrir le fichier `verify_qcm_images_production_fixed.py`.
2. Modifier la variable `BASE_URL` pour qu'elle pointe vers l'URL de votre application en production :
   ```python
   # URL de base de l'application en production
   BASE_URL = 'https://votre-application-production.com'  # À remplacer par l'URL réelle
   ```

## Structure des chemins d'images

Le script gère plusieurs formats de chemins d'images :

1. **Chemin absolu** : `/static/uploads/exercises/qcm/image.png`
2. **Chemin relatif** : `static/uploads/exercises/qcm/image.png`
3. **Chemin alternatif** : 
   - `static/uploads/qcm/image.png`
   - `static/uploads/image.png`
   - `static/uploads/exercises/image.png`

## Résolution des problèmes courants

### Images non trouvées (404)

Causes possibles :
- L'image a été déplacée vers un autre répertoire.
- L'image a été renommée.
- L'image a été supprimée.

Solution :
1. Exécuter le script de vérification pour identifier les images manquantes.
2. Exécuter le script de correction généré pour copier les images depuis les chemins alternatifs.
3. Si l'image n'est pas trouvée dans les chemins alternatifs, la recréer ou la télécharger à nouveau.

### Chemins d'images incorrects dans la base de données

Causes possibles :
- Le chemin a été modifié manuellement.
- L'image a été déplacée sans mettre à jour la base de données.

Solution :
1. Exécuter le script de correction pour mettre à jour les chemins dans la base de données.
2. Vérifier que les chemins sont au format standard `/static/uploads/exercises/qcm/image.png`.

## Bonnes pratiques pour éviter les problèmes d'images

1. **Utiliser le répertoire standard** : Toujours stocker les images QCM dans le répertoire `/static/uploads/exercises/qcm/`.
2. **Nommer les images de manière unique** : Utiliser un préfixe ou un timestamp pour éviter les conflits de noms.
3. **Mettre à jour la base de données** : Si une image est déplacée ou renommée, mettre à jour le chemin dans la base de données.
4. **Exécuter régulièrement le script de vérification** : Pour détecter et corriger les problèmes avant qu'ils n'affectent les utilisateurs.

## Conclusion

Cette solution permet de vérifier et corriger automatiquement les problèmes d'images QCM en production. Elle garantit que toutes les images sont accessibles et correctement référencées dans la base de données, améliorant ainsi l'expérience utilisateur et la fiabilité de l'application.
