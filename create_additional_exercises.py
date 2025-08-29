from flask import Flask
from models import db, User, Exercise
import json
import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_image(path, text, width=600, height=300, bg_color=(240, 240, 240), text_color=(0, 0, 0)):
    """Crée une image avec du texte pour les exercices"""
    # Vérifier si le répertoire existe, sinon le créer
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Créer une image
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Essayer de charger une police, sinon utiliser la police par défaut
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Ajouter du texte au centre de l'image
    text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (200, 30)
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill=text_color, font=font)
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Image créée: {path}")

with app.app_context():
    # Récupérer l'enseignant existant
    teacher = User.query.filter_by(email='mr.zahiri@gmail.com').first()
    if not teacher:
        print("Erreur: Enseignant non trouvé. Exécutez d'abord init_exercises.py")
        exit(1)
    
    # 1. QCM Multichoix
    qcm_multichoix = Exercise(
        title="Exercice5: Géographie - QCM Multichoix",
        description="Sélectionnez toutes les bonnes réponses pour chaque question.",
        exercise_type="qcm_multichoix",
        image_path="/static/uploads/qcm_multichoix/geography_qcm.png",
        content=json.dumps({
            "image": "/static/uploads/qcm_multichoix/geography_qcm.png",
            "instructions": "Cochez toutes les réponses correctes pour chaque question.",
            "questions": [
                {
                    "text": "Quels pays font partie de l'Union Européenne?",
                    "choices": ["France", "Suisse", "Allemagne", "Royaume-Uni", "Espagne"],
                    "correct_answers": [0, 2, 4]  # France, Allemagne, Espagne
                },
                {
                    "text": "Quelles sont les langues officielles de la Belgique?",
                    "choices": ["Français", "Allemand", "Anglais", "Néerlandais", "Italien"],
                    "correct_answers": [0, 1, 3]  # Français, Allemand, Néerlandais
                },
                {
                    "text": "Quelles villes sont des capitales?",
                    "choices": ["Lyon", "Madrid", "Berlin", "Marseille", "Rome"],
                    "correct_answers": [1, 2, 4]  # Madrid, Berlin, Rome
                }
            ]
        }),
        teacher_id=teacher.id
    )
    db.session.add(qcm_multichoix)
    
    # 2. Mots à placer
    word_placement = Exercise(
        title="Exercice6: Grammaire - Mots à placer",
        description="Placez les mots au bon endroit dans les phrases.",
        exercise_type="word_placement",
        image_path="/static/uploads/word_placement/grammar_placement.png",
        content=json.dumps({
            "image": "/static/uploads/word_placement/grammar_placement.png",
            "instructions": "Faites glisser les mots dans les bonnes phrases.",
            "sentences": [
                "Le chat ___ sur le canapé.",
                "Les enfants ___ dans le jardin.",
                "Nous ___ au cinéma hier soir."
            ],
            "words": ["dort", "jouent", "sommes allés"],
            "answers": [
                {"sentence_index": 0, "word_index": 0},  # dort
                {"sentence_index": 1, "word_index": 1},  # jouent
                {"sentence_index": 2, "word_index": 2}   # sommes allés
            ]
        }),
        teacher_id=teacher.id
    )
    db.session.add(word_placement)
    
    # 3. Souligner un mot
    underline_words = Exercise(
        title="Exercice7: Grammaire - Souligner les mots",
        description="Soulignez les verbes dans les phrases suivantes.",
        exercise_type="underline_words",
        image_path="/static/uploads/underline_words/verbs_underline.png",
        content=json.dumps({
            "image": "/static/uploads/underline_words/verbs_underline.png",
            "instructions": "Soulignez tous les verbes dans les phrases suivantes.",
            "sentences": [
                {"text": "Le chat dort sur le canapé.", "words_to_underline": [2]},
                {"text": "Les enfants jouent dans le jardin.", "words_to_underline": [2]},
                {"text": "Nous mangeons des pommes.", "words_to_underline": [1]}
            ]
        }),
        teacher_id=teacher.id
    )
    db.session.add(underline_words)
    
    # 4. Cartes mémoire
    flashcards = Exercise(
        title="Exercice8: Vocabulaire - Cartes mémoire",
        description="Mémorisez le vocabulaire français-anglais.",
        exercise_type="flashcards",
        image_path="/static/uploads/flashcards/vocabulary_cards.png",
        content=json.dumps({
            "image": "/static/uploads/flashcards/vocabulary_cards.png",
            "instructions": "Cliquez sur une carte pour voir sa traduction.",
            "cards": [
                {"front": "Maison", "back": "House"},
                {"front": "Voiture", "back": "Car"},
                {"front": "École", "back": "School"},
                {"front": "Livre", "back": "Book"},
                {"front": "Ordinateur", "back": "Computer"}
            ]
        }),
        teacher_id=teacher.id
    )
    db.session.add(flashcards)
    
    # Créer les dossiers pour les images si nécessaires
    upload_dirs = [
        os.path.join(app.root_path, 'static', 'uploads', 'qcm_multichoix'),
        os.path.join(app.root_path, 'static', 'uploads', 'word_placement'),
        os.path.join(app.root_path, 'static', 'uploads', 'underline_words'),
        os.path.join(app.root_path, 'static', 'uploads', 'flashcards')
    ]
    
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Créer des images pour chaque exercice
    create_image(
        os.path.join(app.root_path, 'static', 'uploads', 'qcm_multichoix', 'geography_qcm.png'),
        "QCM MULTICHOIX - GÉOGRAPHIE",
        bg_color=(200, 230, 255)
    )
    create_image(
        os.path.join(app.root_path, 'static', 'uploads', 'word_placement', 'grammar_placement.png'),
        "MOTS À PLACER - GRAMMAIRE",
        bg_color=(255, 230, 200)
    )
    create_image(
        os.path.join(app.root_path, 'static', 'uploads', 'underline_words', 'verbs_underline.png'),
        "SOULIGNER LES MOTS - VERBES",
        bg_color=(230, 255, 200)
    )
    create_image(
        os.path.join(app.root_path, 'static', 'uploads', 'flashcards', 'vocabulary_cards.png'),
        "CARTES MÉMOIRE - VOCABULAIRE",
        bg_color=(255, 200, 230)
    )
    
    db.session.commit()
    print("Exercices supplémentaires créés avec succès !")
    print("\nExercices ajoutés :")
    print("- QCM Multichoix: " + qcm_multichoix.image_path)
    print("- Mots à placer: " + word_placement.image_path)
    print("- Souligner les mots: " + underline_words.image_path)
    print("- Cartes mémoire: " + flashcards.image_path)
