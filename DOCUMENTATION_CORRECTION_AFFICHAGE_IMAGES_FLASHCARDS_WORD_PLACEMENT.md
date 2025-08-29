# Documentation : Correction de l'affichage des images pour les exercices "Cartes mémoire" et "Mots à placer"

## Problèmes identifiés

Deux types d'exercices présentaient des problèmes d'affichage d'images :

1. **Cartes mémoire (flashcards)** : Les images ne s'affichaient pas correctement lors de la navigation entre les cartes. Le problème était dû à l'absence d'une route backend `/get_cloudinary_url` qui était appelée par le JavaScript pour récupérer les URLs des images Cloudinary.

2. **Mots à placer (word_placement)** : Les images pouvaient ne pas s'afficher correctement selon la façon dont elles étaient référencées dans l'exercice.

3. **Conflit de routes** : Après implémentation de la solution initiale, un conflit de routes a été détecté. La route `/get_cloudinary_url` était définie à la fois dans le fichier principal `app.py` et dans le module `fix_image_display_routes.py`.

## Solution implémentée

### 1. Création d'une route Flask pour `/get_cloudinary_url`

Nous avons créé un module `fix_image_display_routes.py` qui définit une route Flask permettant de récupérer l'URL Cloudinary d'une image à partir de son chemin et la renvoyer au format JSON (contrairement à la version précédente qui effectuait une redirection) :

```python
from flask import Blueprint, request, jsonify
import cloud_storage

def register_image_display_routes(app):
    """
    Enregistre les routes nécessaires pour l'affichage des images
    """
    image_display_bp = Blueprint('image_display', __name__)
    
    @image_display_bp.route('/get_cloudinary_url')
    def get_cloudinary_url():
        """
        Route pour récupérer l'URL Cloudinary d'une image
        Utilisée par le JavaScript des templates pour charger les images dynamiquement
        """
        image_path = request.args.get('image_path', '')
        if not image_path:
            return jsonify({'error': 'Aucun chemin d\'image fourni'}), 400
            
        try:
            url = cloud_storage.get_cloudinary_url(image_path)
            if url:
                return jsonify({'url': url})
            else:
                return jsonify({'error': 'URL non trouvée'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    app.register_blueprint(image_display_bp)
    return image_display_bp
```

### 2. Intégration de la route dans l'application principale

Nous avons modifié `app.py` pour importer et enregistrer cette nouvelle route :

```python
from fix_image_display_routes import register_image_display_routes

# ... autres imports et configuration ...

# Enregistrement des routes pour l'affichage des images
register_image_display_routes(app)
```

### 3. Correction du template flashcards.html

Nous avons corrigé le template `flashcards.html` pour :

1. Simplifier l'affichage initial de l'image en utilisant directement `cloud_storage.get_cloudinary_url`
2. Mettre à jour la fonction JavaScript `updateCard()` pour récupérer l'URL Cloudinary via la nouvelle route `/get_cloudinary_url`

```javascript
function updateCard() {
    // ... code existant ...
    
    // Mise à jour de l'image si elle existe
    if (cards[currentIndex].image) {
        // Récupérer l'URL Cloudinary via l'API
        fetch(`/get_cloudinary_url?image_path=${encodeURIComponent(cards[currentIndex].image)}`)
            .then(response => response.json())
            .then(data => {
                if (data.url) {
                    cardImage.src = data.url;
                    cardImageContainer.style.display = 'block';
                } else {
                    cardImageContainer.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Erreur lors de la récupération de l\'URL de l\'image:', error);
                cardImageContainer.style.display = 'none';
            });
    } else {
        cardImageContainer.style.display = 'none';
    }
    
    // ... code existant ...
}
```

### 4. Vérification du template word_placement.html

Nous avons vérifié que le template `word_placement.html` utilisait correctement la fonction helper `get_exercise_image_url` pour afficher les images, ce qui était déjà le cas. Cette fonction utilise en interne `cloud_storage.get_cloudinary_url` pour résoudre les URLs des images.

## Tests effectués

Pour valider notre solution, nous avons créé :

1. Un script de test `test_word_placement_images.py` qui :
   - Crée des exercices de test avec différentes configurations d'images
   - Fournit des routes pour visualiser ces exercices
   - Permet de tester la génération d'URLs Cloudinary

2. Des templates de test pour visualiser et vérifier l'affichage des images :
   - `test_image_exercises.html` : Affiche les exercices et leurs images
   - `test_get_cloudinary_url.html` : Permet de tester directement la route `/get_cloudinary_url`

## Résultats

Les corrections apportées permettent maintenant :

1. **Pour les cartes mémoire (flashcards)** :
   - L'affichage correct de l'image initiale
   - La mise à jour correcte des images lors de la navigation entre les cartes
   - Une gestion robuste des erreurs (affichage/masquage du conteneur d'image)

2. **Pour les mots à placer (word_placement)** :
   - L'affichage correct des images d'exercice
   - Une résolution cohérente des URLs d'images

## Recommandations

1. **Surveillance** : Surveiller les logs pour détecter d'éventuelles erreurs liées à la génération d'URLs d'images.

2. **Optimisation future** : Envisager de mettre en cache les URLs Cloudinary côté client pour réduire les appels API.

3. **Standardisation** : Standardiser l'utilisation de `get_exercise_image_url` dans tous les templates pour une gestion cohérente des images.

### 5. Correction du conflit de routes

Après avoir implémenté la solution initiale, nous avons détecté un conflit de routes dans l'application :

```
AssertionError: View function mapping is overwriting an existing endpoint function: get_cloudinary_url_route
```

Ce conflit était dû à la présence de deux définitions de la route `/get_cloudinary_url` :

1. Une dans `app.py` qui redirigait vers l'URL Cloudinary
2. Une dans `fix_image_display_routes.py` qui renvoyait l'URL au format JSON

Nous avons résolu ce conflit en supprimant la route définie directement dans `app.py` et en conservant uniquement celle définie dans le module `fix_image_display_routes.py`, qui est plus adaptée à l'utilisation par le JavaScript des templates.

```python
# Dans app.py, nous avons remplacé la définition de route par un commentaire
# @app.route('/get_cloudinary_url')
# def get_cloudinary_url_route():
#     ...

# Route /get_cloudinary_url maintenant gérée par fix_image_display_routes.py
```

## Conclusion

La correction implémentée résout le problème d'affichage des images dans les exercices "cartes mémoire" et "mots à placer" en centralisant la logique de résolution des URLs d'images via une route API dédiée. Cette approche assure une cohérence dans l'affichage des images et une meilleure robustesse face aux différentes façons dont les images peuvent être référencées dans les exercices.

Le conflit de routes a été résolu en supprimant la définition redondante, ce qui permet à l'application de démarrer correctement et de servir les URLs d'images au format JSON, comme attendu par le JavaScript des templates.
