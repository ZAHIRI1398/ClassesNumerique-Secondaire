#!/usr/bin/env python3
"""
Script pour tester l'affichage des mots dans les exercices fill_in_blanks avec plusieurs blancs par ligne.
Ce script simule l'affichage des mots dans l'interface et vérifie que tous les mots sont correctement affichés.
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify

# Configuration
LOG_FILE = f'test_fill_in_blanks_display_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

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
    """Crée une application Flask de test pour simuler l'affichage des mots"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.logger.setLevel(logging.INFO)
    
    @app.route('/', methods=['GET'])
    def test_display():
        """Affiche une page de test pour vérifier l'affichage des mots"""
        # Simuler différents formats de contenu JSON
        test_cases = [
            {
                'name': 'Format sentences avec 2 mots',
                'content': {
                    'sentences': ['Le ___ est un animal.', 'La ___ est rouge.'],
                    'words': ['chat', 'pomme']
                }
            },
            {
                'name': 'Format sentences avec plusieurs blancs par ligne',
                'content': {
                    'sentences': ['Le ___ est un ___ domestique.', 'La ___ est un ___ délicieux.'],
                    'words': ['chat', 'animal', 'pomme', 'fruit']
                }
            },
            {
                'name': 'Format text avec plusieurs blancs',
                'content': {
                    'text': 'Le ___ est un ___ domestique. La ___ est un ___ délicieux.',
                    'words': ['chat', 'animal', 'pomme', 'fruit']
                }
            },
            {
                'name': 'Format mixte (sentences + text)',
                'content': {
                    'sentences': ['Le ___ est un ___ domestique.'],
                    'text': 'La ___ est un ___ délicieux.',
                    'words': ['chat', 'animal', 'pomme', 'fruit']
                }
            },
            {
                'name': 'Format avec available_words au lieu de words',
                'content': {
                    'sentences': ['Le ___ est un ___ domestique.'],
                    'available_words': ['chat', 'animal']
                }
            }
        ]
        
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test d'affichage des mots</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .word-bank {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 0.25rem;
                    padding: 1rem;
                    margin-bottom: 1rem;
                }
                .draggable-word {
                    margin-right: 0.5rem;
                    margin-bottom: 0.5rem;
                }
                .test-case {
                    border: 1px solid #dee2e6;
                    border-radius: 0.25rem;
                    padding: 1rem;
                    margin-bottom: 1rem;
                }
                .debug-info {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 0.25rem;
                    padding: 1rem;
                    margin-top: 1rem;
                    font-family: monospace;
                    white-space: pre-wrap;
                }
            </style>
        </head>
        <body>
            <div class="container mt-4">
                <h1>Test d'affichage des mots dans les exercices fill_in_blanks</h1>
                <p class="lead">Ce test vérifie que tous les mots sont correctement affichés dans l'interface.</p>
                
                {% for test_case in test_cases %}
                <div class="test-case">
                    <h3>{{ test_case.name }}</h3>
                    
                    <div class="mb-3">
                        <h4>Contenu JSON</h4>
                        <div class="debug-info">{{ test_case.content | tojson(indent=2) }}</div>
                    </div>
                    
                    <div class="mb-3">
                        <h4>Banque de mots (version originale)</h4>
                        <div class="word-bank" id="word-bank-original-{{ loop.index }}">
                            {% set words = test_case.content.get('words', test_case.content.get('available_words', [])) %}
                            {% for word in words %}
                                <button type="button" class="btn btn-primary draggable-word" data-word="{{ word }}">{{ word }}</button>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <h4>Banque de mots (après mélange JavaScript)</h4>
                        <div class="word-bank" id="word-bank-shuffled-{{ loop.index }}">
                            <!-- Sera rempli par JavaScript -->
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <h4>Phrases avec blancs</h4>
                        {% if test_case.content.get('sentences') %}
                            {% for sentence in test_case.content.get('sentences', []) %}
                                <div class="mb-2">{{ sentence | replace('___', '<span class="badge bg-secondary">____</span>') | safe }}</div>
                            {% endfor %}
                        {% endif %}
                        
                        {% if test_case.content.get('text') %}
                            <div class="mb-2">{{ test_case.content.get('text', '') | replace('___', '<span class="badge bg-secondary">____</span>') | safe }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <h4>Informations de débogage</h4>
                        <div class="debug-info" id="debug-info-{{ loop.index }}">
                            Nombre de blancs: {{ (test_case.content.get('sentences', []) | join('') ~ test_case.content.get('text', '')).count('___') }}
                            Nombre de mots: {{ test_case.content.get('words', test_case.content.get('available_words', [])) | length }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Pour chaque cas de test
                {% for test_case in test_cases %}
                (function(index) {
                    const originalBank = document.getElementById('word-bank-original-' + index);
                    const shuffledBank = document.getElementById('word-bank-shuffled-' + index);
                    const debugInfo = document.getElementById('debug-info-' + index);
                    
                    if (originalBank && shuffledBank) {
                        // Récupérer tous les mots de la banque originale
                        const words = Array.from(originalBank.querySelectorAll('.draggable-word'));
                        
                        // Fonction de mélange Fisher-Yates
                        function shuffleArray(array) {
                            const shuffled = [...array];
                            for (let i = shuffled.length - 1; i > 0; i--) {
                                const j = Math.floor(Math.random() * (i + 1));
                                [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
                            }
                            return shuffled;
                        }
                        
                        // Mélanger les mots
                        const shuffledWords = shuffleArray(words);
                        
                        // Ajouter des informations de débogage
                        debugInfo.textContent += '\n\nMots originaux: ' + words.map(w => w.textContent).join(', ');
                        debugInfo.textContent += '\nMots mélangés: ' + shuffledWords.map(w => w.textContent).join(', ');
                        
                        // Vider la banque de mots mélangés et réinsérer dans l'ordre mélangé
                        shuffledBank.innerHTML = '';
                        shuffledWords.forEach(word => {
                            const button = document.createElement('button');
                            button.type = 'button';
                            button.className = 'btn btn-primary draggable-word';
                            button.textContent = word.textContent;
                            button.setAttribute('data-word', word.getAttribute('data-word'));
                            shuffledBank.appendChild(button);
                        });
                        
                        // Vérifier si tous les mots sont présents
                        const originalWordCount = words.length;
                        const shuffledWordCount = shuffledBank.querySelectorAll('.draggable-word').length;
                        
                        if (originalWordCount === shuffledWordCount) {
                            debugInfo.textContent += '\n\nVérification: OK - Tous les mots sont présents (' + shuffledWordCount + '/' + originalWordCount + ')';
                        } else {
                            debugInfo.textContent += '\n\nVérification: ERREUR - Certains mots sont manquants (' + shuffledWordCount + '/' + originalWordCount + ')';
                        }
                    }
                })({{ loop.index }});
                {% endfor %}
            });
            </script>
        </body>
        </html>
        """
        
        return render_template_string(template, test_cases=test_cases)
    
    return app

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== TEST D'AFFICHAGE DES MOTS DANS LES EXERCICES FILL_IN_BLANKS ===")
    
    # Créer l'application de test
    app = create_test_app()
    
    if app:
        logger.info("Application de test créée avec succès")
        logger.info("Démarrage de l'application de test sur http://127.0.0.1:5002/")
        logger.info("Utilisez Ctrl+C pour arrêter l'application")
        
        app.run(debug=True, port=5002)
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
