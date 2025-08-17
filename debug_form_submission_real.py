import json
import sys
from flask import Flask, request, render_template_string
from app import app, db, Exercise, User, current_user
from flask_login import login_user

def debug_form_submission_real():
    """
    Crée une page HTML pour tester la soumission du formulaire de l'exercice à texte à trous
    et afficher les détails du traitement des réponses avec un formulaire réel.
    """
    with app.app_context():
        # Récupérer un utilisateur pour le test
        user = User.query.filter_by(role='student').first()
        if user:
            login_user(user)
            print(f"Connecté en tant que: {user.username} (ID: {user.id}, Rôle: {user.role})")
        
        # Récupérer l'exercice à texte à trous
        exercise_id = 7
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            return "Exercice non trouvé"
        
        # Charger le contenu de l'exercice
        content = json.loads(exercise.content)
        
        # Compter les blancs dans le contenu
        total_blanks_in_content = 0
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            print(f"Nombre de blancs dans 'sentences': {sentences_blanks}")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            print(f"Nombre de blancs dans 'text': {text_blanks}")
        
        # Récupérer les réponses correctes
        correct_answers = content.get('words', []) or content.get('available_words', [])
        print(f"Réponses correctes: {correct_answers}")
        print(f"Nombre de réponses correctes: {len(correct_answers)}")
        
        # Créer un formulaire HTML pour tester la soumission
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debug Fill-in-Blanks (Real Form)</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .debug-section { margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; }
                .form-section { background-color: #f0f0f0; }
                .results-section { background-color: #e0f0e0; }
                .error { color: red; }
                .success { color: green; }
                pre { background-color: #f5f5f5; padding: 10px; overflow: auto; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .blank-input {
                    border: 2px dashed #cbd5e0;
                    border-radius: 8px;
                    background: rgba(102, 126, 234, 0.05);
                    padding: 8px 12px;
                    min-width: 100px;
                    text-align: center;
                    font-weight: 600;
                    color: #2d3748;
                }
            </style>
        </head>
        <body>
            <h1>Débogage de l'exercice à texte à trous (ID: {{ exercise.id }})</h1>
            
            <div class="debug-section">
                <h2>Informations sur l'exercice</h2>
                <p><strong>Titre:</strong> {{ exercise.title }}</p>
                <p><strong>Type:</strong> {{ exercise.exercise_type }}</p>
                <p><strong>Contenu:</strong></p>
                <pre>{{ content_json }}</pre>
            </div>
            
            <div class="debug-section form-section">
                <h2>Formulaire de test (EXACT COMME DANS L'APPLICATION)</h2>
                <p>Ce formulaire est une copie exacte du formulaire utilisé dans l'application.</p>
                
                <form method="POST" action="/debug-form-submit-real">
                    <input type="hidden" name="exercise_id" value="{{ exercise.id }}">
                    
                    {% set blank_counter = [0] %}
                    
                    {% if content.sentences %}
                        {% for sentence in content.sentences %}
                            <div class="mb-4 sentence-container">
                                <div class="sentence-text">
                                    {% set parts = sentence.split('___') %}
                                    {% for part in parts %}
                                        {{ part }}
                                        {% if not loop.last %}
                                            <input type="text" 
                                                   class="blank-input d-inline-block mx-1" 
                                                   name="answer_{{ blank_counter[0] }}" 
                                                   required 
                                                   placeholder="____"
                                                   value="{{ correct_answers[blank_counter[0]] }}"
                                                   style="width: auto; min-width: 80px; max-width: 150px;">
                                            {% if blank_counter.append(blank_counter.pop() + 1) %}{% endif %}
                                        {% endif %}
                                    {% endfor %}
                                </div>
                            </div>
                        {% endfor %}
                    {% elif content.text %}
                        <div class="mb-4 sentence-container">
                            <div class="sentence-text">
                                {% set parts = content.text.split('___') %}
                                {% for part in parts %}
                                    {{ part }}
                                    {% if not loop.last %}
                                        <input type="text" 
                                               class="blank-input d-inline-block mx-1" 
                                               name="answer_{{ blank_counter[0] }}" 
                                               required 
                                               placeholder="____"
                                               value="{{ correct_answers[blank_counter[0]] }}"
                                               style="width: auto; min-width: 80px; max-width: 150px;">
                                        {% if blank_counter.append(blank_counter.pop() + 1) %}{% endif %}
                                    {% endif %}
                                {% endfor %}
                            </div>
                        </div>
                    {% endif %}
                    
                    <button type="submit" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
                        Soumettre mes réponses
                    </button>
                </form>
            </div>
            
            <div class="debug-section">
                <h2>Formulaire de test (VERSION SIMPLIFIÉE)</h2>
                <p>Ce formulaire est une version simplifiée pour tester directement les champs.</p>
                
                <form method="POST" action="/debug-form-submit-simple">
                    <input type="hidden" name="exercise_id" value="{{ exercise.id }}">
                    
                    {% for i in range(max_blanks) %}
                        <div style="margin-bottom: 10px;">
                            <label for="simple_answer_{{ i }}">Réponse {{ i }}:</label>
                            <input type="text" id="simple_answer_{{ i }}" name="answer_{{ i }}" value="{{ correct_answers[i] if i < correct_answers|length else '' }}">
                        </div>
                    {% endfor %}
                    
                    <button type="submit" style="background-color: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
                        Soumettre (version simple)
                    </button>
                </form>
            </div>
            
            {% if results %}
            <div class="debug-section results-section">
                <h2>Résultats du traitement</h2>
                
                <p><strong>Score:</strong> {{ results['score'] }}%</p>
                <p><strong>Réponses correctes:</strong> {{ results['correct_blanks'] }}/{{ results['total_blanks'] }}</p>
                
                <h3>Détails par réponse:</h3>
                <table>
                    <tr>
                        <th>Index</th>
                        <th>Réponse utilisateur</th>
                        <th>Réponse correcte</th>
                        <th>Résultat</th>
                    </tr>
                    {% for detail in results['details'] %}
                    <tr>
                        <td>{{ detail['blank_index'] }}</td>
                        <td>{{ detail['user_answer'] }}</td>
                        <td>{{ detail['correct_answer'] }}</td>
                        <td class="{{ 'success' if detail['is_correct'] else 'error' }}">
                            {{ 'Correct' if detail['is_correct'] else detail['status'] }}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
                
                <h3>Données brutes du formulaire:</h3>
                <pre>{{ form_data }}</pre>
                
                <h3>Résultats complets:</h3>
                <pre>{{ results_json }}</pre>
            </div>
            {% endif %}
            
            <div class="debug-section">
                <h2>Analyse du problème</h2>
                <p>Si vous obtenez un score de 20% (1/5) malgré des réponses correctes, vérifiez:</p>
                <ol>
                    <li>Le format des réponses dans le formulaire (name="answer_0", name="answer_1", etc.)</li>
                    <li>La comparaison des réponses (sensibilité à la casse, espaces)</li>
                    <li>Le comptage des blancs dans le contenu</li>
                    <li>La soumission du formulaire (tous les champs sont-ils envoyés?)</li>
                </ol>
            </div>
        </body>
        </html>
        """
        
        # Ajouter la route pour le traitement du formulaire (version réelle)
        @app.route('/debug-form-submit-real', methods=['POST'])
        def debug_form_submit_real():
            exercise_id = request.form.get('exercise_id')
            exercise = Exercise.query.get(exercise_id)
            
            if not exercise:
                return "Exercice non trouvé"
            
            content = json.loads(exercise.content)
            
            # Afficher toutes les données du formulaire pour le débogage
            print("Données du formulaire (RÉEL):", dict(request.form))
            
            # Compter les blancs dans le contenu
            total_blanks_in_content = 0
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
            
            # Récupérer les réponses correctes
            correct_answers = content.get('words', []) or content.get('available_words', [])
            total_blanks = max(total_blanks_in_content, len(correct_answers))
            
            # Traiter les réponses utilisateur
            correct_blanks = 0
            feedback_details = []
            user_answers_data = {}
            
            # Vérifier chaque blanc individuellement
            for i in range(total_blanks):
                # Récupérer la réponse de l'utilisateur pour ce blanc
                user_answer = request.form.get(f'answer_{i}', '').strip()
                
                # Récupérer la réponse correcte correspondante
                correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                
                print(f"Blanc {i}:")
                print(f"  - Réponse utilisateur: '{user_answer}'")
                print(f"  - Réponse correcte: '{correct_answer}'")
                
                # Vérifier si la réponse est correcte (insensible à la casse)
                is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
                if is_correct:
                    correct_blanks += 1
                    print(f"  - CORRECT")
                else:
                    print(f"  - INCORRECT")
                
                # Créer le feedback pour ce blanc
                feedback_details.append({
                    'blank_index': i,
                    'user_answer': user_answer or '',
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}'
                })
                
                # Sauvegarder les réponses utilisateur
                user_answers_data[f'answer_{i}'] = user_answer
            
            # Calculer le score final
            score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
            
            print(f"Score final: {score}% ({correct_blanks}/{total_blanks})")
            
            results = {
                'score': score,
                'correct_blanks': correct_blanks,
                'total_blanks': total_blanks,
                'details': feedback_details
            }
            
            # Rendre le template avec les résultats
            return render_template_string(
                html_template,
                exercise=exercise,
                content=content,
                content_json=json.dumps(content, indent=2, ensure_ascii=False),
                max_blanks=total_blanks,
                correct_answers=correct_answers,
                results=results,
                results_json=json.dumps(results, indent=2, ensure_ascii=False),
                form_data=json.dumps(dict(request.form), indent=2, ensure_ascii=False)
            )
        
        # Ajouter la route pour le traitement du formulaire (version simple)
        @app.route('/debug-form-submit-simple', methods=['POST'])
        def debug_form_submit_simple():
            exercise_id = request.form.get('exercise_id')
            exercise = Exercise.query.get(exercise_id)
            
            if not exercise:
                return "Exercice non trouvé"
            
            content = json.loads(exercise.content)
            
            # Afficher toutes les données du formulaire pour le débogage
            print("Données du formulaire (SIMPLE):", dict(request.form))
            
            # Compter les blancs dans le contenu
            total_blanks_in_content = 0
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
            
            # Récupérer les réponses correctes
            correct_answers = content.get('words', []) or content.get('available_words', [])
            total_blanks = max(total_blanks_in_content, len(correct_answers))
            
            # Traiter les réponses utilisateur
            correct_blanks = 0
            feedback_details = []
            user_answers_data = {}
            
            # Vérifier chaque blanc individuellement
            for i in range(total_blanks):
                # Récupérer la réponse de l'utilisateur pour ce blanc
                user_answer = request.form.get(f'answer_{i}', '').strip()
                
                # Récupérer la réponse correcte correspondante
                correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                
                print(f"Blanc {i}:")
                print(f"  - Réponse utilisateur: '{user_answer}'")
                print(f"  - Réponse correcte: '{correct_answer}'")
                
                # Vérifier si la réponse est correcte (insensible à la casse)
                is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
                if is_correct:
                    correct_blanks += 1
                    print(f"  - CORRECT")
                else:
                    print(f"  - INCORRECT")
                
                # Créer le feedback pour ce blanc
                feedback_details.append({
                    'blank_index': i,
                    'user_answer': user_answer or '',
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}'
                })
                
                # Sauvegarder les réponses utilisateur
                user_answers_data[f'answer_{i}'] = user_answer
            
            # Calculer le score final
            score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
            
            print(f"Score final: {score}% ({correct_blanks}/{total_blanks})")
            
            results = {
                'score': score,
                'correct_blanks': correct_blanks,
                'total_blanks': total_blanks,
                'details': feedback_details
            }
            
            # Rendre le template avec les résultats
            return render_template_string(
                html_template,
                exercise=exercise,
                content=content,
                content_json=json.dumps(content, indent=2, ensure_ascii=False),
                max_blanks=total_blanks,
                correct_answers=correct_answers,
                results=results,
                results_json=json.dumps(results, indent=2, ensure_ascii=False),
                form_data=json.dumps(dict(request.form), indent=2, ensure_ascii=False)
            )
        
        # Rendre le template initial
        return render_template_string(
            html_template,
            exercise=exercise,
            content=content,
            content_json=json.dumps(content, indent=2, ensure_ascii=False),
            max_blanks=max(total_blanks_in_content, len(correct_answers)),
            correct_answers=correct_answers,
            results=None,
            results_json=None,
            form_data=None
        )

# Ajouter la route pour la page de débogage
@app.route('/debug-form-real')
def debug_form_real_route():
    return debug_form_submission_real()

if __name__ == "__main__":
    # Exécuter l'application Flask en mode debug
    app.run(debug=True)
    print("Accédez à http://127.0.0.1:5000/debug-form-real pour déboguer l'exercice à texte à trous")
