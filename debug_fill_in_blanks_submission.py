import json
from flask import Flask, request, render_template_string
from app import app, db, Exercise

def debug_form_submission():
    """
    Crée une page HTML pour tester la soumission du formulaire de l'exercice à texte à trous
    et afficher les détails du traitement des réponses.
    """
    with app.app_context():
        # Récupérer l'exercice à texte à trous
        exercise_id = 7
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            return "Exercice non trouvé"
        
        # Charger le contenu de l'exercice
        content = json.loads(exercise.content)
        
        # Créer un formulaire HTML pour tester la soumission
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debug Fill-in-Blanks</title>
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
                <h2>Formulaire de test</h2>
                <form method="POST" action="/debug-fill-in-blanks-submit">
                    <input type="hidden" name="exercise_id" value="{{ exercise.id }}">
                    
                    {% if 'sentences' in content %}
                        <p><strong>Phrases:</strong></p>
                        {% for sentence in content['sentences'] %}
                            <p>{{ sentence }}</p>
                        {% endfor %}
                    {% elif 'text' in content %}
                        <p><strong>Texte:</strong></p>
                        <p>{{ content['text'] }}</p>
                    {% endif %}
                    
                    <p><strong>Mots disponibles:</strong> 
                    {% if 'words' in content %}
                        {{ content['words']|join(', ') }}
                    {% elif 'available_words' in content %}
                        {{ content['available_words']|join(', ') }}
                    {% endif %}
                    </p>
                    
                    <p><strong>Réponses:</strong></p>
                    {% for i in range(max_blanks) %}
                        <div style="margin-bottom: 10px;">
                            <label for="answer_{{ i }}">Réponse {{ i }}:</label>
                            <input type="text" id="answer_{{ i }}" name="answer_{{ i }}" value="{{ correct_answers[i] if i < correct_answers|length else '' }}">
                        </div>
                    {% endfor %}
                    
                    <button type="submit">Soumettre</button>
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
                
                <h3>Données brutes:</h3>
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
                </ol>
            </div>
        </body>
        </html>
        """
        
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
        normalized_correct_answers = []
        for answer in correct_answers:
            if isinstance(answer, dict) and 'word' in answer:
                normalized_correct_answers.append(answer['word'])
            else:
                normalized_correct_answers.append(answer)
        
        correct_answers = normalized_correct_answers
        max_blanks = max(total_blanks_in_content, len(correct_answers))
        
        # Ajouter la route pour le traitement du formulaire
        @app.route('/debug-fill-in-blanks-submit', methods=['POST'])
        def debug_fill_in_blanks_submit():
            exercise_id = request.form.get('exercise_id')
            exercise = Exercise.query.get(exercise_id)
            
            if not exercise:
                return "Exercice non trouvé"
            
            content = json.loads(exercise.content)
            
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
            normalized_correct_answers = []
            for answer in correct_answers:
                if isinstance(answer, dict) and 'word' in answer:
                    normalized_correct_answers.append(answer['word'])
                else:
                    normalized_correct_answers.append(answer)
            
            correct_answers = normalized_correct_answers
            total_blanks = max(total_blanks_in_content, len(correct_answers))
            
            # Traiter les réponses utilisateur
            correct_blanks = 0
            feedback_details = []
            user_answers_data = {}
            
            # Afficher toutes les données du formulaire pour le débogage
            print("Données du formulaire:", dict(request.form))
            
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
            score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
            
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
                max_blanks=max_blanks,
                correct_answers=correct_answers,
                results=results,
                results_json=json.dumps(results, indent=2, ensure_ascii=False)
            )
        
        # Rendre le template initial
        return render_template_string(
            html_template,
            exercise=exercise,
            content=content,
            content_json=json.dumps(content, indent=2, ensure_ascii=False),
            max_blanks=max_blanks,
            correct_answers=correct_answers,
            results=None,
            results_json=None
        )

# Ajouter la route pour la page de débogage
@app.route('/debug-fill-in-blanks')
def debug_fill_in_blanks_route():
    return debug_form_submission()

if __name__ == "__main__":
    # Exécuter l'application Flask en mode debug
    app.run(debug=True)
    print("Accédez à http://127.0.0.1:5000/debug-fill-in-blanks pour déboguer l'exercice à texte à trous")
