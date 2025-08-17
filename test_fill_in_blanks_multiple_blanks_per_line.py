#!/usr/bin/env python3
"""
Test spécifique pour le problème de scoring avec plusieurs blancs sur une même ligne
"""

import json
from flask import Flask, request, render_template_string, session
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)
app.secret_key = 'test_key'

# Template HTML simulant le formulaire de fill_in_blanks avec plusieurs blancs par ligne
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Fill in Blanks - Multiple Blanks Per Line</title>
</head>
<body>
    <h1>Test Fill in Blanks - Multiple Blanks Per Line</h1>
    
    <form method="POST" action="/submit">
        <div>
            <p>Phrase 1: Le <input type="text" name="answer_0" value="{{ answers.get('answer_0', '') }}"> mange une <input type="text" name="answer_1" value="{{ answers.get('answer_1', '') }}"> rouge.</p>
            <p>Phrase 2: La <input type="text" name="answer_2" value="{{ answers.get('answer_2', '') }}"> vole vers son <input type="text" name="answer_3" value="{{ answers.get('answer_3', '') }}">.</p>
        </div>
        <button type="submit">Soumettre</button>
    </form>
    
    {% if score is not none %}
    <div>
        <h2>Résultats</h2>
        <p>Score: {{ score }}%</p>
        <p>Réponses correctes: {{ correct_blanks }}/{{ total_blanks }}</p>
        <h3>Détails:</h3>
        <ul>
            {% for detail in feedback %}
            <li>Blank {{ detail.blank_index }}: 
                {% if detail.is_correct %}
                <span style="color: green;">Correct</span>
                {% else %}
                <span style="color: red;">Incorrect - Attendu: {{ detail.correct_answer }}, Réponse: {{ detail.user_answer }}</span>
                {% endif %}
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
</body>
</html>
"""

# Exemple d'exercice avec plusieurs blancs par ligne
mock_exercise = {
    "sentences": [
        "Le ___ mange une ___ rouge.",  # 2 blancs sur la même ligne
        "La ___ vole vers son ___."     # 2 blancs sur la même ligne
    ],
    "words": ["chat", "pomme", "oiseau", "nid"]
}

@app.route('/', methods=['GET'])
def index():
    """Page d'accueil avec formulaire"""
    return render_template_string(TEMPLATE, answers={}, score=None, correct_blanks=None, total_blanks=None, feedback=[])

@app.route('/submit', methods=['POST'])
def submit():
    """Traitement de la soumission du formulaire"""
    print("\n=== TRAITEMENT DE LA SOUMISSION ===")
    print(f"Données du formulaire: {request.form}")
    
    # Récupérer le contenu de l'exercice
    content = mock_exercise
    print(f"Contenu de l'exercice: {content}")
    
    # Compter le nombre de blancs dans le contenu
    total_blanks_in_content = 0
    
    if 'sentences' in content:
        # Compter les blancs dans chaque phrase
        for idx, sentence in enumerate(content['sentences']):
            blanks_in_sentence = sentence.count('___')
            print(f"Phrase {idx}: '{sentence}' contient {blanks_in_sentence} blancs")
            total_blanks_in_content += blanks_in_sentence
    
    print(f"Total des blancs dans le contenu: {total_blanks_in_content}")
    
    # Récupérer les réponses correctes
    correct_answers = content.get('words', [])
    if not correct_answers:
        correct_answers = content.get('available_words', [])
    
    print(f"Réponses correctes: {correct_answers}")
    
    # Vérifier la cohérence entre le nombre de blancs et le nombre de réponses
    total_blanks = max(total_blanks_in_content, len(correct_answers))
    print(f"Nombre total de blancs à évaluer: {total_blanks}")
    
    # Récupérer et traiter les réponses de l'utilisateur
    correct_blanks = 0
    feedback_details = []
    
    # Fonction auxiliaire pour déterminer la phrase et l'indice du blanc dans cette phrase
    def get_blank_location(global_blank_index, sentences):
        """Détermine à quelle phrase et à quel indice dans cette phrase correspond un indice global de blanc"""
        blank_count = 0
        for idx, sentence in enumerate(sentences):
            blanks_in_sentence = sentence.count('___')
            if blank_count <= global_blank_index < blank_count + blanks_in_sentence:
                # Calculer l'indice local du blanc dans cette phrase
                local_blank_index = global_blank_index - blank_count
                return idx, local_blank_index
            blank_count += blanks_in_sentence
        return -1, -1
    
    # Vérifier d'abord que tous les champs de réponse sont présents
    answer_fields = {}
    for key in request.form:
        if key.startswith('answer_'):
            try:
                index = int(key.split('_')[1])
                answer_fields[index] = request.form[key].strip()
            except (ValueError, IndexError):
                print(f"Format de champ invalide: {key}")
    
    print(f"Champs de réponse trouvés: {answer_fields}")
    print(f"Nombre de réponses: {len(answer_fields)} / {total_blanks} attendues")
    
    # Traiter chaque blanc
    for i in range(total_blanks):
        # Récupérer la réponse de l'utilisateur pour ce blanc
        user_answer = answer_fields.get(i, '').strip()
        
        # Récupérer la réponse correcte correspondante
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        print(f"Blank {i}:")
        print(f"  - Réponse étudiant (answer_{i}): {user_answer}")
        print(f"  - Réponse attendue: {correct_answer}")
        
        # Vérifier si la réponse est correcte (insensible à la casse)
        is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
        if is_correct:
            correct_blanks += 1
        
        # Déterminer l'index de la phrase à laquelle appartient ce blanc
        sentence_index = -1
        local_blank_index = -1
        if 'sentences' in content:
            sentence_index, local_blank_index = get_blank_location(i, content['sentences'])
            print(f"  - Appartient à la phrase {sentence_index}, position {local_blank_index}")
        
        feedback_details.append({
            'blank_index': i,
            'user_answer': user_answer or '',
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}',
            'sentence_index': sentence_index
        })
    
    # Calculer le score final
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    print(f"\n=== RÉSULTAT FINAL ===")
    print(f"Score: {correct_blanks}/{total_blanks} = {score}%")
    
    # Retourner le template avec les résultats
    return render_template_string(
        TEMPLATE, 
        answers=request.form,
        score=round(score),
        correct_blanks=correct_blanks,
        total_blanks=total_blanks,
        feedback=feedback_details
    )

if __name__ == '__main__':
    print("Démarrage du serveur de test pour fill_in_blanks avec plusieurs blancs par ligne")
    print("Accédez à http://127.0.0.1:5000/ pour tester")
    app.run(debug=True)
