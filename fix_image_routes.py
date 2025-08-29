"""
Script pour ajouter une route Flask pour récupérer les URLs Cloudinary
et corriger l'affichage des images dans les exercices word_placement et flashcards
"""

import os
import logging
from flask import Flask, request, jsonify, url_for
import cloud_storage
from utils.image_path_manager import ImagePathManager

def register_image_routes(app):
    """
    Enregistre les routes nécessaires pour la gestion des images dans les exercices
    
    Args:
        app: L'application Flask
    """
    # Configuration du logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Route pour récupérer l'URL Cloudinary d'une image
    @app.route('/get_cloudinary_url', methods=['GET'])
    def get_cloudinary_url_route():
        """
        Route pour récupérer l'URL Cloudinary d'une image
        Utilisée par le JavaScript dans les templates flashcards.html
        """
        image_path = request.args.get('image_path')
        if not image_path:
            logger.error("Aucun chemin d'image fourni à /get_cloudinary_url")
            return jsonify({'error': 'Aucun chemin d\'image fourni'}), 400
            
        try:
            # Utiliser la fonction existante pour obtenir l'URL
            url = cloud_storage.get_cloudinary_url(image_path)
            logger.info(f"URL générée pour {image_path}: {url}")
            return jsonify({'url': url})
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'URL pour {image_path}: {str(e)}")
            return jsonify({'error': str(e)}), 500

def fix_templates():
    """
    Fonction pour corriger les templates word_placement.html et flashcards.html
    Cette fonction est appelée manuellement pour appliquer les corrections
    """
    try:
        # Chemin des templates
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'exercise_types')
        
        # Correction du template flashcards.html
        flashcards_path = os.path.join(templates_dir, 'flashcards.html')
        if os.path.exists(flashcards_path):
            with open(flashcards_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Correction 1: Simplifier l'affichage initial de l'image
            content = content.replace(
                """<img src="{{ cloud_storage.get_cloudinary_url(normalize_image_path(content.cards[0].image)) }}" 
                             alt="Image de la carte" class="img-fluid rounded" 
                             style="max-height: 300px;" id="card-image">""",
                """<img src="{{ cloud_storage.get_cloudinary_url(content.cards[0].image) }}" 
                             alt="Image de la carte" class="img-fluid rounded" 
                             style="max-height: 300px;" id="card-image">"""
            )
            
            # Correction 2: Corriger la fonction updateCard() pour utiliser directement cloud_storage.get_cloudinary_url
            content = content.replace(
                """// Mettre à jour l'image
    if (card.image) {
        // Utiliser l'URL Cloudinary via une route dédiée
        cardImage.src = `/get_cloudinary_url?image_path=${encodeURIComponent(card.image)}`;
        cardImageContainer.style.display = 'block';
    } else {
        cardImageContainer.style.display = 'none';
    }""",
                """// Mettre à jour l'image
    if (card.image) {
        // Utiliser l'API pour récupérer l'URL Cloudinary
        fetch(`/get_cloudinary_url?image_path=${encodeURIComponent(card.image)}`)
            .then(response => response.json())
            .then(data => {
                if (data.url) {
                    cardImage.src = data.url;
                    cardImageContainer.style.display = 'block';
                } else {
                    console.error('Erreur: URL non trouvée dans la réponse');
                    cardImageContainer.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Erreur lors de la récupération de l\'URL:', error);
                cardImageContainer.style.display = 'none';
            });
    } else {
        cardImageContainer.style.display = 'none';
    }"""
            )
            
            # Sauvegarder les modifications
            with open(flashcards_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Template flashcards.html corrigé avec succès")
        else:
            print(f"Template flashcards.html introuvable à {flashcards_path}")
            
        # Pas besoin de corriger word_placement.html car il utilise déjà get_exercise_image_url correctement
        
        return True
    except Exception as e:
        print(f"Erreur lors de la correction des templates: {str(e)}")
        return False

if __name__ == "__main__":
    print("Ce script doit être importé dans app.py pour enregistrer les routes")
    print("Exemple d'utilisation:")
    print("from fix_image_routes import register_image_routes")
    print("register_image_routes(app)")
