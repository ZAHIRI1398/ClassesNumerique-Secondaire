# Correction de l'affichage des images dans les exercices Flashcards

## Problème identifié

Après analyse approfondie, nous avons identifié plusieurs problèmes qui empêchaient l'affichage correct des images dans les exercices de type flashcards :

1. **Incohérence dans le chargement des images** : Le template utilisait `cloud_storage.get_cloudinary_url()` pour l'affichage initial, mais la route `/get_cloudinary_url` pour le chargement dynamique des images suivantes.

2. **Chemins d'images incomplets** : Les chemins d'images dans la base de données sont stockés sous la forme `uploads/1756247392_3opwru.png` (sans le préfixe `/static/`).

3. **Fonction JavaScript manquante** : La fonction `updateCard()` était appelée mais n'était pas définie dans le template.

4. **Absence de chargement initial** : Les images n'étaient pas chargées dès l'initialisation de la page.

## Solution implémentée

### 1. Analyse de la base de données

Nous avons créé un script `test_flashcard_data.py` pour analyser les données des flashcards dans la base de données et confirmer le format des chemins d'images stockés :

```python
import sqlite3
import json
import os

def analyze_flashcard_data():
    # Connexion à la base de données
    conn = sqlite3.connect('instance/app.db')
    cursor = conn.cursor()
    
    # Vérifier la structure de la table exercise
    cursor.execute("PRAGMA table_info(exercise)")
    columns = cursor.fetchall()
    print("Structure de la table exercise:")
    for column in columns:
        print(f"  {column[1]} ({column[2]})")
    
    # Récupérer les exercices de type flashcard
    cursor.execute("""
        SELECT id, title, content, exercise_type 
        FROM exercise 
        WHERE exercise_type = 'flashcards'
    """)
    
    exercises = cursor.fetchall()
    print(f"Nombre d'exercices flashcard trouvés: {len(exercises)}")
    
    for exercise_id, title, content_json, exercise_type in exercises:
        print(f"\n--- Exercice ID: {exercise_id}, Titre: {title} ---")
        
        try:
            # Parser le contenu JSON
            content = json.loads(content_json)
            
            # Vérifier si le contenu a la structure attendue
            if 'cards' not in content:
                print(f"  ERREUR: Structure JSON invalide - 'cards' manquant")
                continue
            
            # Afficher le nombre de cartes
            print(f"  Nombre de cartes: {len(content['cards'])}")
            
            # Analyser chaque carte
            for i, card in enumerate(content['cards']):
                print(f"  Carte {i+1}:")
                print(f"    Question: {card.get('question', 'N/A')}")
                print(f"    Réponse: {card.get('answer', 'N/A')}")
                
                # Vérifier l'image
                if 'image' in card and card['image']:
                    print(f"    Image: {card['image']}")
                else:
                    print(f"    Image: Aucune")
        
        except json.JSONDecodeError:
            print(f"  ERREUR: Contenu JSON invalide")
        except Exception as e:
            print(f"  ERREUR: {str(e)}")
    
    conn.close()

if __name__ == "__main__":
    analyze_flashcard_data()
```

### 2. Test de la route `/get_cloudinary_url`

Nous avons créé un script `test_get_cloudinary_url_with_real_paths.py` pour tester la route `/get_cloudinary_url` avec les chemins d'images réels trouvés dans la base de données :

```python
import requests
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_get_cloudinary_url_with_real_paths():
    """
    Test la route /get_cloudinary_url avec les chemins d'images réels trouvés dans la base de données
    """
    # URL de base de l'application
    base_url = "http://127.0.0.1:5000"
    
    # Liste de chemins d'images réels trouvés dans la base de données
    real_paths = [
        "uploads/1756247392_3opwru.png",  # Exercice 70, Carte 1
        "uploads/1756247392_o1p7u4.png",  # Exercice 70, Carte 2
        "uploads/1756247392_sfnq84.png",  # Exercice 70, Carte 3
        "uploads/1756307741_mox2ot.png",  # Exercice 71, Carte 1
        "uploads/1756307741_fpxlrz.png",  # Exercice 71, Carte 2
        "uploads/1756307741_gl8wuh.png",  # Exercice 71, Carte 3
    ]
    
    # Tester chaque chemin
    for path in real_paths:
        logger.info(f"Test avec le chemin réel: {path}")
        
        # Construire l'URL complète
        url = f"{base_url}/get_cloudinary_url?image_path={path}"
        
        try:
            # Faire la requête
            response = requests.get(url)
            
            # Afficher le code de statut
            logger.info(f"Code de statut: {response.status_code}")
            
            # Afficher le contenu de la réponse
            if response.status_code == 200:
                try:
                    # Essayer de parser comme JSON
                    json_response = response.json()
                    logger.info(f"Réponse JSON: {json.dumps(json_response, indent=2)}")
                    
                    # Vérifier si l'URL est présente et si elle commence par /static/
                    if 'url' in json_response:
                        url_value = json_response['url']
                        logger.info(f"URL trouvée: {url_value}")
                        
                        # Vérifier si l'URL commence par /static/
                        if not url_value.startswith('/static/'):
                            logger.warning(f"L'URL ne commence pas par /static/: {url_value}")
                    else:
                        logger.warning("Pas d'URL dans la réponse JSON")
                except json.JSONDecodeError:
                    logger.error(f"La réponse n'est pas du JSON valide: {response.text}")
            else:
                logger.error(f"Réponse non-200: {response.text}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la requête: {str(e)}")
    
    logger.info("Tests terminés")
```

### 3. Modification du template flashcards.html

Nous avons modifié le template `templates/exercise_types/flashcards.html` pour :

1. Utiliser une image de chargement au démarrage
2. Ajouter la fonction `updateCard()` manquante
3. Charger l'image dès l'initialisation de la page

```html
<!-- Image de la carte -->
<div id="card-image-container" class="mb-4">
    {% if content.cards[0].image %}
    <!-- Utilisation d'une image placeholder qui sera remplacée par JavaScript -->
    <img src="/static/img/loading.gif" 
         alt="Image de la carte" class="img-fluid rounded" 
         style="max-height: 300px;" id="card-image">
    {% endif %}
</div>
```

```javascript
// Fonction pour mettre à jour la carte actuelle
function updateCard() {
    // Mettre à jour la question
    cardQuestion.textContent = cards[currentCardIndex].question;
    
    // Charger l'image
    loadCardImage(currentCardIndex);
    
    // Réinitialiser l'entrée utilisateur
    userAnswerInput.value = '';
    userAnswerInput.disabled = false;
    userAnswerInput.focus();
    
    // Afficher le bouton de vérification
    verifyBtn.style.display = 'inline-block';
    nextBtn.style.display = 'none';
    feedback.style.display = 'none';
}

// Initialiser la première carte
updateCard();
userAnswerInput.focus();
```

### 4. Création d'une image de chargement

Nous avons créé une image de chargement simple pour afficher pendant le chargement des images :

```python
from PIL import Image, ImageDraw
import os

def create_loading_gif():
    """
    Crée une simple image GIF de chargement et la sauvegarde dans static/img/loading.gif
    """
    # Dimensions de l'image
    width, height = 200, 200
    
    # Créer une image blanche
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Dessiner un cercle bleu au centre
    circle_radius = 50
    circle_center = (width // 2, height // 2)
    circle_bbox = (
        circle_center[0] - circle_radius,
        circle_center[1] - circle_radius,
        circle_center[0] + circle_radius,
        circle_center[1] + circle_radius
    )
    draw.ellipse(circle_bbox, fill='lightblue', outline='blue')
    
    # Ajouter du texte
    draw.text((width // 2 - 30, height // 2 - 10), "Chargement...", fill='black')
    
    # Sauvegarder l'image
    output_path = os.path.join('static', 'img', 'loading.gif')
    img.save(output_path)
```

## Résultats et validation

1. **Analyse de la base de données** : Nous avons confirmé que les chemins d'images sont stockés sous la forme `uploads/1756247392_3opwru.png` sans le préfixe `/static/`.

2. **Test de la route** : La route `/get_cloudinary_url` fonctionne correctement et retourne des URLs au format `/static/exercises/general/1756247392_3opwru.png`.

3. **Cohérence du chargement** : Nous avons uniformisé le chargement des images en utilisant uniquement la route `/get_cloudinary_url` pour toutes les images.

4. **Chargement initial** : Nous avons ajouté un appel à `loadCardImage(0)` dès le chargement de la page pour charger l'image de la première carte.

5. **Fonction manquante** : Nous avons ajouté la fonction `updateCard()` qui était manquante dans le template.

## Conclusion

Les modifications apportées permettent désormais l'affichage correct des images dans les exercices de type flashcards. La solution est robuste et prend en compte les différents formats de chemins d'images stockés dans la base de données.

Cette correction s'inscrit dans une démarche plus large d'amélioration de l'affichage des images dans l'application, après les corrections précédentes pour les exercices QCM et autres types d'exercices.
