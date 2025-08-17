#!/usr/bin/env python3
"""
Script pour déboguer la soumission des formulaires pour les exercices fill_in_blanks
et comprendre pourquoi seule la première réponse est comptée correctement
"""

import os
import sys
import re
import json
import logging
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user

# Configuration
LOG_FILE = f'debug_form_submission_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

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

def create_debug_app():
    """Crée une application Flask minimaliste pour déboguer les soumissions de formulaires"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'debug_secret_key'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        # Utilisateur factice pour le débogage
        class FakeUser:
            def __init__(self):
                self.id = 1
                self.is_authenticated = True
                self.is_active = True
                self.is_anonymous = False
                self.role = 'teacher'
            
            def get_id(self):
                return str(self.id)
        
        return FakeUser()
    
    @app.route('/')
    def index():
        return render_template('debug/form_data.html')
    
    @app.route('/debug-form', methods=['POST'])
    def debug_form():
        """Route pour déboguer les données du formulaire"""
        logger.info("=== DONNÉES DU FORMULAIRE REÇUES ===")
        
        # Récupérer toutes les données du formulaire
        form_data = dict(request.form)
        logger.info(f"Données brutes du formulaire: {form_data}")
        
        # Vérifier les champs answer_X
        answer_fields = {}
        for key in form_data:
            if key.startswith('answer_'):
                try:
                    index = int(key.split('_')[1])
                    answer_fields[index] = form_data[key]
                except (ValueError, IndexError):
                    logger.warning(f"Format de champ invalide: {key}")
        
        logger.info(f"Champs de réponse trouvés: {answer_fields}")
        
        # Simuler le traitement des réponses comme dans app.py
        user_answers_list = []
        user_answers_data = {}
        
        # Récupérer les réponses dans l'ordre des indices
        sorted_indices = sorted(answer_fields.keys())
        logger.info(f"Indices triés: {sorted_indices}")
        
        for i in sorted_indices:
            user_answer = answer_fields.get(i, '').strip()
            user_answers_list.append(user_answer)
            user_answers_data[f'answer_{i}'] = user_answer
        
        logger.info(f"Liste des réponses utilisateur: {user_answers_list}")
        logger.info(f"Dictionnaire des réponses utilisateur: {user_answers_data}")
        
        # Simuler le traitement avec des réponses correctes factices
        correct_answers = ["mot1", "mot2", "mot3", "mot4", "mot5"]
        logger.info(f"Réponses correctes (simulation): {correct_answers}")
        
        # Copie des réponses correctes pour éviter de les modifier
        remaining_correct_answers = correct_answers.copy()
        
        # Compter les réponses correctes
        correct_blanks = 0
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
        total_blanks = len(correct_answers)
        score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        
        logger.info(f"Score final: {score}% ({correct_blanks}/{total_blanks})")
        logger.info(f"Détails du feedback: {feedback_details}")
        
        return jsonify({
            'status': 'success',
            'form_data': form_data,
            'answer_fields': answer_fields,
            'user_answers_list': user_answers_list,
            'correct_blanks': correct_blanks,
            'total_blanks': total_blanks,
            'score': score,
            'feedback_details': feedback_details
        })
    
    return app

def create_test_form_template():
    """Crée un template de test pour simuler un exercice fill_in_blanks"""
    os.makedirs('templates/debug', exist_ok=True)
    
    template_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Débogage Formulaire Fill-in-Blanks</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .blank-input {
            width: 120px;
            padding: 5px 10px;
            border: 2px solid #ccc;
            border-radius: 4px;
            margin: 0 5px;
        }
        .word-bank {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .word-item {
            display: inline-block;
            background-color: #007bff;
            color: white;
            padding: 5px 10px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
        }
        .word-item:hover {
            background-color: #0056b3;
        }
        .result-panel {
            display: none;
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        pre {
            background-color: #f1f1f1;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1>Débogage Formulaire Fill-in-Blanks</h1>
        <p class="lead">Cet outil permet de tester la soumission des formulaires pour les exercices de type "texte à trous".</p>
        
        <div class="card mb-4">
            <div class="card-header">
                <h2>Exercice de test</h2>
            </div>
            <div class="card-body">
                <div class="word-bank">
                    <h5>Mots disponibles:</h5>
                    <div class="word-item" onclick="selectWord(this)">mot1</div>
                    <div class="word-item" onclick="selectWord(this)">mot2</div>
                    <div class="word-item" onclick="selectWord(this)">mot3</div>
                    <div class="word-item" onclick="selectWord(this)">mot4</div>
                    <div class="word-item" onclick="selectWord(this)">mot5</div>
                </div>
                
                <form id="fillBlanksForm" method="POST" action="/debug-form">
                    <div class="mb-3">
                        <p>
                            Phrase 1: Le <input type="text" class="blank-input" name="answer_0" required placeholder="____"> est un animal domestique.
                        </p>
                    </div>
                    <div class="mb-3">
                        <p>
                            Phrase 2: La <input type="text" class="blank-input" name="answer_1" required placeholder="____"> est un fruit délicieux.
                        </p>
                    </div>
                    <div class="mb-3">
                        <p>
                            Phrase 3: Le <input type="text" class="blank-input" name="answer_2" required placeholder="____"> est une planète du système solaire.
                        </p>
                    </div>
                    <div class="mb-3">
                        <p>
                            Phrase 4: La <input type="text" class="blank-input" name="answer_3" required placeholder="____"> est un instrument de musique.
                        </p>
                    </div>
                    <div class="mb-3">
                        <p>
                            Phrase 5: Le <input type="text" class="blank-input" name="answer_4" required placeholder="____"> est un moyen de transport.
                        </p>
                    </div>
                    
                    <button type="submit" class="btn btn-primary">Soumettre</button>
                </form>
            </div>
        </div>
        
        <div id="resultPanel" class="result-panel">
            <h3>Résultats de la soumission</h3>
            <div id="resultContent"></div>
        </div>
    </div>
    
    <script>
        // Fonction pour sélectionner un mot et le placer dans le champ actif
        function selectWord(wordElement) {
            const word = wordElement.textContent;
            const inputs = document.querySelectorAll('.blank-input');
            
            // Trouver le premier champ vide
            let emptyInput = null;
            for (const input of inputs) {
                if (!input.value) {
                    emptyInput = input;
                    break;
                }
            }
            
            // Si un champ vide est trouvé, y placer le mot
            if (emptyInput) {
                emptyInput.value = word;
                emptyInput.classList.add('filled');
            }
        }
        
        // Intercepter la soumission du formulaire pour afficher les résultats
        document.getElementById('fillBlanksForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch('/debug-form', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const resultPanel = document.getElementById('resultPanel');
                const resultContent = document.getElementById('resultContent');
                
                // Formater les résultats
                let html = `
                    <div class="alert alert-info">
                        <strong>Score:</strong> ${data.score.toFixed(1)}% (${data.correct_blanks}/${data.total_blanks})
                    </div>
                    
                    <h4>Détails des réponses:</h4>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Champ</th>
                                <th>Réponse</th>
                                <th>Statut</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                for (let i = 0; i < data.feedback_details.length; i++) {
                    const detail = data.feedback_details[i];
                    html += `
                        <tr>
                            <td>answer_${i}</td>
                            <td>${detail.user_answer}</td>
                            <td>
                                ${detail.is_correct 
                                    ? '<span class="badge bg-success">Correct</span>' 
                                    : '<span class="badge bg-danger">Incorrect</span>'}
                            </td>
                        </tr>
                    `;
                }
                
                html += `
                        </tbody>
                    </table>
                    
                    <h4>Données brutes:</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
                
                resultContent.innerHTML = html;
                resultPanel.style.display = 'block';
                
                // Faire défiler jusqu'aux résultats
                resultPanel.scrollIntoView({ behavior: 'smooth' });
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Une erreur est survenue lors de la soumission du formulaire.');
            });
        });
    </script>
</body>
</html>
"""
    
    with open('templates/debug/form_data.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    logger.info("Template de test créé: templates/debug/form_data.html")

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== DÉBOGAGE DE LA SOUMISSION DES FORMULAIRES FILL-IN-BLANKS ===")
    
    # Créer le template de test
    create_test_form_template()
    
    # Créer et lancer l'application Flask
    app = create_debug_app()
    
    logger.info("Démarrage de l'application de débogage sur http://127.0.0.1:5000")
    logger.info("Utilisez Ctrl+C pour arrêter l'application")
    
    app.run(debug=True)

if __name__ == "__main__":
    main()
