#!/usr/bin/env python3
"""
Script pour tester le cas spécifique des exercices fill_in_blanks avec plusieurs blancs dans une même ligne.
Ce script simule une soumission de formulaire avec plusieurs blancs par phrase et vérifie que toutes
les réponses sont correctement récupérées et traitées.
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify

# Configuration
LOG_FILE = f'test_fill_in_blanks_multiple_blanks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

def setup_logging():
    """Configure le système de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def create_test_app():
    """Crée une application Flask de test pour simuler la soumission de formulaire"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.logger.setLevel(logging.INFO)
    
    @app.route('/', methods=['GET'])
    def test_form():
        """Affiche un formulaire de test pour les exercices fill_in_blanks avec plusieurs blancs par ligne"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Fill-in-Blanks avec Multiples Blancs</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .form-control.d-inline-block {
                    width: 150px !important;
                    margin: 0 10px;
                }
            </style>
        </head>
        <body>
            <div class="container mt-5">
                <h1>Test de la correction Fill-in-Blanks avec Multiples Blancs</h1>
                <div class="card">
                    <div class="card-header">
                        <h2>Formulaire de test</h2>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="/submit">
                            <div class="mb-3">
                                <label class="form-label">Phrase 1: Le <input type="text" name="answer_0" class="form-control d-inline-block w-auto"> est un <input type="text" name="answer_1" class="form-control d-inline-block w-auto"> domestique.</label>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Phrase 2: La <input type="text" name="answer_2" class="form-control d-inline-block w-auto"> est un <input type="text" name="answer_3" class="form-control d-inline-block w-auto"> délicieux.</label>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Phrase 3: Le <input type="text" name="answer_4" class="form-control d-inline-block w-auto"> est une <input type="text" name="answer_5" class="form-control d-inline-block w-auto"> du système solaire.</label>
                            </div>
                            
                            <div class="mb-3">
                                <h4>Banque de mots</h4>
                                <div class="d-flex flex-wrap gap-2">
                                    <span class="badge bg-primary p-2">chat</span>
                                    <span class="badge bg-primary p-2">animal</span>
                                    <span class="badge bg-primary p-2">pomme</span>
                                    <span class="badge bg-primary p-2">fruit</span>
                                    <span class="badge bg-primary p-2">mars</span>
                                    <span class="badge bg-primary p-2">planète</span>
                                </div>
                            </div>
                            
                            <button type="submit" class="btn btn-primary">Soumettre</button>
                        </form>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(template)
    
    @app.route('/submit', methods=['POST'])
    def test_submit():
        """Traite la soumission du formulaire de test"""
        logger.info("=== TRAITEMENT DU FORMULAIRE DE TEST AVEC MULTIPLES BLANCS ===")
        logger.info(f"Données du formulaire: {dict(request.form)}")
        
        # Simuler le contexte d'un exercice fill_in_blanks
        class MockExercise:
            def __init__(self):
                self.exercise_type = 'fill_in_blanks'
                self.content = json.dumps({
                    'sentences': [
                        'Le ___ est un ___ domestique.',
                        'La ___ est un ___ délicieux.',
                        'Le ___ est une ___ du système solaire.'
                    ],
                    'words': ['chat', 'animal', 'pomme', 'fruit', 'mars', 'planète']
                })
            
            def get_content(self):
                return json.loads(self.content)
        
        exercise = MockExercise()
        content = exercise.get_content()
        
        # Compter le nombre réel de blancs dans le contenu
        total_blanks_in_content = 0
        
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            logger.info(f"Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            logger.info(f"Format 'text' détecté: {text_blanks} blanks dans text")
        
        logger.info(f"Total blancs trouvés dans le contenu: {total_blanks_in_content}")
        
        # Récupérer les réponses correctes
        correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        logger.info(f"Réponses correctes: {correct_answers}")
        
        # Utiliser le nombre réel de blancs trouvés dans le contenu
        total_blanks = max(total_blanks_in_content, len(correct_answers))
        logger.info(f"Nombre total de blancs: {total_blanks}")
        
        # Initialiser les variables pour le scoring
        correct_blanks = 0
        feedback_details = []
        user_answers_data = {}
        
        # === DÉBUT DU CODE DE RÉCUPÉRATION DES RÉPONSES ===
        logger.info(f"[FILL_IN_BLANKS_DEBUG] Toutes les données du formulaire: {dict(request.form)}")
        
        # Rechercher spécifiquement les champs answer_X
        answer_fields = {}
        for key in request.form:
            if key.startswith('answer_'):
                try:
                    index = int(key.split('_')[1])
                    answer_fields[index] = request.form[key].strip()
                except (ValueError, IndexError):
                    logger.warning(f"[FILL_IN_BLANKS_DEBUG] Format de champ invalide: {key}")
        
        logger.info(f"[FILL_IN_BLANKS_DEBUG] Champs de réponse trouvés: {answer_fields}")
        
        # Récupérer les réponses dans l'ordre des indices
        user_answers_list = []
        user_answers_data = {}
        
        # Utiliser les indices triés pour garantir l'ordre correct
        sorted_indices = sorted(answer_fields.keys())
        logger.info(f"[FILL_IN_BLANKS_DEBUG] Indices triés: {sorted_indices}")
        
        for i in sorted_indices:
            user_answer = answer_fields.get(i, '').strip()
            user_answers_list.append(user_answer)
            user_answers_data[f'answer_{i}'] = user_answer
        # === FIN DU CODE DE RÉCUPÉRATION DES RÉPONSES ===
        
        logger.info(f"Réponses utilisateur: {user_answers_list}")
        
        # Copie des réponses correctes pour éviter de les modifier
        remaining_correct_answers = correct_answers.copy() if correct_answers else []
        
        # Pour chaque réponse de l'utilisateur, vérifier si elle est dans les réponses attendues
        feedback_details = []
        for i, user_answer in enumerate(user_answers_list):
            is_correct = False
            matched_correct_answer = ""
            
            # Vérifier si la réponse est dans la liste des réponses correctes restantes
            for j, correct_answer in enumerate(remaining_correct_answers):
                if user_answer.lower() == correct_answer.lower():
                    is_correct = True
                    matched_correct_answer = correct_answer
                    remaining_correct_answers.pop(j)
                    correct_blanks += 1
                    logger.info(f"Réponse correcte trouvée: '{user_answer}' correspond à '{matched_correct_answer}'")
                    break
            
            if not is_correct:
                logger.info(f"Réponse incorrecte: '{user_answer}'")
            
            feedback_details.append({
                'user_answer': user_answer,
                'is_correct': is_correct,
                'correct_answer': matched_correct_answer if is_correct else "?"
            })
        
        # Calculer le score final
        score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        logger.info(f"Score final: {score}% ({correct_blanks}/{total_blanks})")
        
        # Préparer la réponse
        result_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Résultats du test</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1>Résultats du test avec multiples blancs</h1>
                
                <div class="alert alert-{{ 'success' if score == 100 else 'warning' }}">
                    <h4>Score: {{ score }}% ({{ correct_blanks }}/{{ total_blanks }})</h4>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h2>Détails des réponses</h2>
                    </div>
                    <div class="card-body">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Champ</th>
                                    <th>Réponse</th>
                                    <th>Statut</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for i, detail in enumerate(feedback_details) %}
                                <tr>
                                    <td>answer_{{ i }}</td>
                                    <td>{{ detail.user_answer }}</td>
                                    <td>
                                        {% if detail.is_correct %}
                                        <span class="badge bg-success">Correct</span>
                                        {% else %}
                                        <span class="badge bg-danger">Incorrect</span>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Données brutes</h2>
                    </div>
                    <div class="card-body">
                        <h3>Données du formulaire</h3>
                        <pre>{{ form_data }}</pre>
                        
                        <h3>Réponses utilisateur</h3>
                        <pre>{{ user_answers }}</pre>
                        
                        <h3>Réponses correctes</h3>
                        <pre>{{ correct_answers }}</pre>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="/" class="btn btn-primary">Retour au formulaire</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Rendre le template avec les résultats
        return render_template_string(
            result_template,
            score=score,
            correct_blanks=correct_blanks,
            total_blanks=total_blanks,
            feedback_details=feedback_details,
            enumerate=enumerate,
            form_data=json.dumps(dict(request.form), indent=2),
            user_answers=json.dumps(user_answers_list, indent=2),
            correct_answers=json.dumps(correct_answers, indent=2)
        )
    
    return app

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== TEST DE LA CORRECTION POUR LES EXERCICES AVEC MULTIPLES BLANCS PAR LIGNE ===")
    
    # Créer l'application de test
    app = create_test_app()
    
    if app:
        logger.info("Application de test créée avec succès")
        logger.info("Démarrage de l'application de test sur http://127.0.0.1:5001/")
        logger.info("Utilisez Ctrl+C pour arrêter l'application")
        
        app.run(debug=True, port=5001)
    else:
        logger.error("Impossible de créer l'application de test")
        return False
    
    return True

if __name__ == "__main__":
    logger = setup_logging()
    success = main()
    if not success:
        print("Test terminé avec des erreurs")
        print("Consultez le fichier de log pour plus de détails")
