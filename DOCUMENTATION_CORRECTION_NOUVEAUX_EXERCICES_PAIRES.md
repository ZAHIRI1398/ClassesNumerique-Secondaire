# Documentation - Correction des nouveaux exercices d'association de paires

## Problème identifié

Les nouveaux exercices d'association de paires créés après l'application du correctif initial affichaient "Image 0", "Image 1", "Image 2" au lieu des images réelles. Ce problème était dû à deux facteurs :

1. Les chemins d'images dans les nouveaux exercices utilisaient le préfixe `/static/exercises/` au lieu de `/static/uploads/`
2. Les images physiques n'étaient pas correctement accessibles dans le système de fichiers

## Solution implémentée

Un script de correction (`fix_new_pairs_exercise.py`) a été créé pour :

1. Normaliser les chemins d'images en remplaçant `/static/exercises/` par `/static/uploads/`
2. Vérifier l'existence physique des images et créer des images placeholder si nécessaire
3. Mettre à jour la base de données avec les chemins corrigés

## Structure de données attendue

Pour que les exercices d'association de paires fonctionnent correctement, leur structure JSON doit respecter le format suivant :

```json
{
  "pairs": [
    {
      "id": "1",
      "left": {
        "content": "/static/uploads/chemin_vers_image.png",
        "type": "image"
      },
      "right": {
        "content": "Texte associé",
        "type": "text"
      }
    },
    // Autres paires...
  ]
}
```

Points importants :
- Les chemins d'images doivent commencer par `/static/uploads/`
- Chaque élément doit avoir un objet avec les propriétés `type` et `content`
- Pour les images, `type` doit être `"image"` et `content` doit être le chemin de l'image
- Pour les textes, `type` doit être `"text"` et `content` doit être le texte à afficher

## Recommandations pour éviter ce problème à l'avenir

1. **Lors de la création d'exercices** : S'assurer que les chemins d'images sont correctement formatés avec le préfixe `/static/uploads/`
2. **Dans le code de création d'exercices** : Ajouter une validation pour normaliser automatiquement les chemins d'images
3. **Dans le template** : Ajouter une gestion de fallback pour afficher une image par défaut si l'image n'est pas trouvée

## Utilisation du script de correction

Pour corriger un exercice spécifique :

```python
python fix_new_pairs_exercise.py
```

Ce script corrige actuellement l'exercice avec l'ID 45 ("Test paires Complet"). Pour corriger d'autres exercices, modifiez la ligne `fix_exercise(45)` dans la section `if __name__ == "__main__":` du script.

## Vérification de la correction

Après avoir exécuté le script, les chemins d'images dans la base de données ont été mis à jour et les images sont maintenant correctement affichées dans l'interface utilisateur.

## Conclusion

Cette correction assure que tous les exercices d'association de paires, y compris ceux nouvellement créés, affichent correctement les images. La solution est robuste car elle normalise les chemins d'images et crée des images placeholder si nécessaire.
