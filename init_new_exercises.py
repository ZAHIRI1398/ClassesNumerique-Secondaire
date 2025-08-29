from app import app, db
from models import User, Exercise
import json
import os
import shutil
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_new_exercises():
    """
    Initialise la base de données avec de nouveaux exercices variés
    en utilisant l'application Flask existante.
    """
    with app.app_context():
        try:
            # Vérifier si l'utilisateur enseignant existe déjà
            teacher = User.query.filter_by(email="mr.zahiri@gmail.com").first()
            if not teacher:
                teacher = User(
                    username="Mr ZAHIRI",
                    email="mr.zahiri@gmail.com",
                    name="Ahmed ZAHIRI",
                    role="teacher"
                )
                teacher.set_password("password123")
                db.session.add(teacher)
                db.session.commit()
                logger.info("Utilisateur enseignant créé")
            else:
                logger.info("Utilisateur enseignant existant trouvé")

            # 1. Exercice à trous sur la grammaire française
            fill_blanks_grammar = Exercise(
                title="Grammaire - Les articles",
                description="Complétez les phrases avec l'article correct (le, la, l', les, un, une, des).",
                exercise_type="fill_in_blanks",
                image_path="/static/uploads/fill_in_blanks/grammar_articles.png",
                content=json.dumps({
                    "sentences": [
                        {"text": "J'ai acheté _____ livre intéressant.", "answer": "un"},
                        {"text": "_____ soleil brille aujourd'hui.", "answer": "Le"},
                        {"text": "Elle a mangé _____ pommes ce matin.", "answer": "des"},
                        {"text": "_____ école est fermée pendant les vacances.", "answer": "L'"},
                        {"text": "Nous avons visité _____ musée célèbre.", "answer": "un"}
                    ],
                    "available_words": ["le", "la", "l'", "les", "un", "une", "des"]
                }),
                teacher_id=teacher.id
            )
            db.session.add(fill_blanks_grammar)

            # 2. QCM sur les sciences
            qcm_science = Exercise(
                title="Sciences - Le système solaire",
                description="Choisissez la bonne réponse pour chaque question sur le système solaire.",
                exercise_type="qcm",
                image_path="/static/uploads/qcm/solar_system.png",
                content=json.dumps({
                    "questions": [
                        {
                            "text": "Quelle est la planète la plus proche du Soleil ?",
                            "choices": ["Vénus", "Mercure", "Mars"],
                            "correct_answer": 1
                        },
                        {
                            "text": "Combien de planètes compte notre système solaire ?",
                            "choices": ["7", "8", "9"],
                            "correct_answer": 1
                        },
                        {
                            "text": "Quelle est la plus grande planète du système solaire ?",
                            "choices": ["Saturne", "Jupiter", "Neptune"],
                            "correct_answer": 1
                        }
                    ]
                }),
                teacher_id=teacher.id
            )
            db.session.add(qcm_science)

            # 3. Exercice d'appariement sur le vocabulaire anglais
            pairs_english = Exercise(
                title="Anglais - Vocabulaire de base",
                description="Associez chaque mot français à sa traduction anglaise.",
                exercise_type="pairs",
                image_path="/static/uploads/pairs/english_vocabulary.png",
                content=json.dumps({
                    "left_items": ["maison", "chat", "école", "livre", "arbre"],
                    "right_items": ["house", "cat", "school", "book", "tree"],
                    "correct_pairs": [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]]
                }),
                teacher_id=teacher.id
            )
            db.session.add(pairs_english)

            # 4. Exercice de glisser-déposer sur l'histoire
            drag_drop_history = Exercise(
                title="Histoire - Chronologie des événements",
                description="Placez ces événements historiques dans l'ordre chronologique.",
                exercise_type="drag_and_drop",
                image_path="/static/uploads/drag_drop/history_timeline.png",
                content=json.dumps({
                    "draggable_items": [
                        "Révolution française (1789)",
                        "Première Guerre mondiale (1914-1918)",
                        "Chute du mur de Berlin (1989)",
                        "Découverte de l'Amérique (1492)",
                        "Seconde Guerre mondiale (1939-1945)"
                    ],
                    "drop_zones": [
                        "Premier événement",
                        "Deuxième événement",
                        "Troisième événement",
                        "Quatrième événement",
                        "Cinquième événement"
                    ],
                    "correct_order": [3, 0, 1, 4, 2]
                }),
                teacher_id=teacher.id
            )
            db.session.add(drag_drop_history)

            # 5. Exercice de légende d'image (mode classique)
            legend_exercise = Exercise(
                title="Géographie - Carte de France",
                description="Placez les noms des villes principales sur la carte de France.",
                exercise_type="legend",
                image_path="/static/uploads/legend/france_map.png",
                content=json.dumps({
                    "mode": "classic",
                    "instructions": "Placez les noms des villes sur la carte de France.",
                    "main_image": "/static/uploads/legend/france_map.png",
                    "elements": ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille"],
                    "zones": [
                        {"id": 1, "x": 250, "y": 150, "name": "Paris"},
                        {"id": 2, "x": 300, "y": 250, "name": "Lyon"},
                        {"id": 3, "x": 300, "y": 350, "name": "Marseille"},
                        {"id": 4, "x": 150, "y": 300, "name": "Bordeaux"},
                        {"id": 5, "x": 250, "y": 80, "name": "Lille"}
                    ]
                }),
                teacher_id=teacher.id
            )
            db.session.add(legend_exercise)

            # 6. Exercice de placement de mots
            word_placement = Exercise(
                title="Français - Phrases à compléter",
                description="Placez les mots au bon endroit dans les phrases.",
                exercise_type="word_placement",
                image_path="/static/uploads/word_placement/french_sentences.png",
                content=json.dumps({
                    "sentences": [
                        "Le chat ___ sur le tapis.",
                        "Les enfants ___ dans le parc.",
                        "Elle ___ un livre intéressant."
                    ],
                    "words": ["dort", "jouent", "lit"],
                    "answers": ["dort", "jouent", "lit"]
                }),
                teacher_id=teacher.id
            )
            db.session.add(word_placement)

            # 7. Exercice d'étiquetage d'image
            image_labeling = Exercise(
                title="Biologie - Le corps humain",
                description="Identifiez les différentes parties du corps humain.",
                exercise_type="image_labeling",
                image_path="/static/uploads/image_labeling/human_body.png",
                content=json.dumps({
                    "image": "/static/uploads/image_labeling/human_body.png",
                    "labels": [
                        {"x": 250, "y": 50, "text": "Tête"},
                        {"x": 250, "y": 150, "text": "Thorax"},
                        {"x": 250, "y": 250, "text": "Abdomen"},
                        {"x": 150, "y": 200, "text": "Bras"},
                        {"x": 250, "y": 350, "text": "Jambe"}
                    ]
                }),
                teacher_id=teacher.id
            )
            db.session.add(image_labeling)

            # Créer les dossiers pour les images si nécessaires
            upload_dirs = [
                os.path.join(app.root_path, 'static', 'uploads', 'qcm'),
                os.path.join(app.root_path, 'static', 'uploads', 'fill_in_blanks'),
                os.path.join(app.root_path, 'static', 'uploads', 'pairs'),
                os.path.join(app.root_path, 'static', 'uploads', 'drag_drop'),
                os.path.join(app.root_path, 'static', 'uploads', 'legend'),
                os.path.join(app.root_path, 'static', 'uploads', 'word_placement'),
                os.path.join(app.root_path, 'static', 'uploads', 'image_labeling')
            ]
            
            for directory in upload_dirs:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Dossier créé ou vérifié: {directory}")
            
            # Créer des images de test pour chaque exercice
            def create_test_image(path, text):
                # Vérifier si l'image existe déjà
                if not os.path.exists(path):
                    # Copier une image existante ou créer une image vide
                    sample_path = os.path.join(app.root_path, 'static', 'exercise_images', 'sample.png')
                    if os.path.exists(sample_path):
                        shutil.copy(sample_path, path)
                        logger.info(f"Image créée: {path}")
                    else:
                        # Créer un fichier texte simple comme placeholder
                        with open(path, 'w') as f:
                            f.write(f"Placeholder pour {text} - {datetime.now()}")
                        logger.info(f"Placeholder créé: {path}")
            
            # Créer les images pour chaque exercice
            create_test_image(os.path.join(app.root_path, 'static', 'uploads', 'qcm', 'solar_system.png'), "QCM Système Solaire")
            create_test_image(os.path.join(app.root_path, 'static', 'uploads', 'fill_in_blanks', 'grammar_articles.png'), "Grammaire Articles")
            create_test_image(os.path.join(app.root_path, 'static', 'uploads', 'pairs', 'english_vocabulary.png'), "Vocabulaire Anglais")
            create_test_image(os.path.join(app.root_path, 'static', 'uploads', 'drag_drop', 'history_timeline.png'), "Chronologie Histoire")
            create_test_image(os.path.join(app.root_path, 'static', 'uploads', 'legend', 'france_map.png'), "Carte de France")
            create_test_image(os.path.join(app.root_path, 'static', 'uploads', 'word_placement', 'french_sentences.png'), "Phrases Françaises")
            create_test_image(os.path.join(app.root_path, 'static', 'uploads', 'image_labeling', 'human_body.png'), "Corps Humain")
            
            # Valider les changements
            db.session.commit()
            logger.info("Nouveaux exercices créés avec succès !")
            print("Nouveaux exercices créés avec succès !")
            print("\nIdentifiants de connexion enseignant :")
            print("Email : mr.zahiri@gmail.com")
            print("Password : password123")
            print("\nExercices créés :")
            print("1. Grammaire - Les articles (fill_in_blanks)")
            print("2. Sciences - Le système solaire (qcm)")
            print("3. Anglais - Vocabulaire de base (pairs)")
            print("4. Histoire - Chronologie des événements (drag_and_drop)")
            print("5. Géographie - Carte de France (legend)")
            print("6. Français - Phrases à compléter (word_placement)")
            print("7. Biologie - Le corps humain (image_labeling)")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création des exercices : {str(e)}")
            print(f"Erreur lors de la création des exercices : {str(e)}")
            return False

if __name__ == "__main__":
    init_new_exercises()
