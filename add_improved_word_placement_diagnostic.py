import os
import sys
import re
import json
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_improved_diagnostic_route():
    """
    Ajoute une route de diagnostic améliorée pour les exercices word_placement
    """
    try:
        # Chemin vers le fichier app.py
        app_path = 'app.py'
        backup_path = f'app.py.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        # Vérifier si le fichier existe
        if not os.path.exists(app_path):
            logger.error(f"Le fichier {app_path} n'existe pas.")
            return False
        
        # Créer une sauvegarde
        with open(app_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        logger.info(f"Sauvegarde créée: {backup_path}")
        
        # Code de la route de diagnostic améliorée
        diagnostic_route = '''
@app.route('/diagnostic/word-placement', methods=['GET'])
@login_required
def diagnostic_word_placement():
    """Route de diagnostic améliorée pour les exercices word_placement"""
    if not current_user.is_admin:
        flash('Accès non autorisé. Seuls les administrateurs peuvent accéder à cette page.', 'error')
        return redirect(url_for('index'))
    
    # Récupérer tous les exercices word_placement
    exercises = Exercise.query.filter_by(exercise_type='word_placement').all()
    
    results = []
    for exercise in exercises:
        try:
            content = exercise.get_content()
            
            # Analyser la structure
            has_sentences = 'sentences' in content
            has_words = 'words' in content
            has_answers = 'answers' in content
            
            # Compter les blancs dans les phrases
            total_blanks_in_sentences = 0
            if has_sentences:
                total_blanks_in_sentences = sum(s.count('___') for s in content['sentences'])
            
            # Compter les réponses
            total_answers = 0
            if has_answers:
                total_answers = len(content['answers'])
            
            # Compter les mots disponibles
            total_words = 0
            if has_words:
                total_words = len(content['words'])
            
            # Vérifier la cohérence
            is_consistent = total_blanks_in_sentences == total_answers
            
            # Récupérer les tentatives pour cet exercice
            attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise.id).order_by(ExerciseAttempt.created_at.desc()).limit(5).all()
            
            attempt_data = []
            for attempt in attempts:
                try:
                    feedback = json.loads(attempt.feedback) if attempt.feedback else []
                    answers = json.loads(attempt.answers) if attempt.answers else {}
                    
                    # Compter les réponses correctes
                    correct_count = sum(1 for item in feedback if item.get('is_correct', False))
                    
                    attempt_data.append({
                        'id': attempt.id,
                        'student_id': attempt.student_id,
                        'score': attempt.score,
                        'correct_count': correct_count,
                        'total_answers': len(feedback),
                        'created_at': attempt.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except Exception as e:
                    attempt_data.append({
                        'id': attempt.id,
                        'error': str(e)
                    })
            
            # Simuler le scoring avec la logique actuelle
            simulated_score = None
            if has_sentences and has_answers:
                # Simuler des réponses toutes correctes
                correct_count = len(content['answers'])
                total_blanks = max(total_blanks_in_sentences, total_answers)
                simulated_score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
            
            results.append({
                'id': exercise.id,
                'title': exercise.title,
                'has_sentences': has_sentences,
                'has_words': has_words,
                'has_answers': has_answers,
                'blanks_in_sentences': total_blanks_in_sentences,
                'answers_count': total_answers,
                'words_count': total_words,
                'is_consistent': is_consistent,
                'simulated_score': simulated_score,
                'attempts': attempt_data,
                'content': content
            })
        except Exception as e:
            results.append({
                'id': exercise.id,
                'title': exercise.title,
                'error': str(e)
            })
    
    # Créer un template HTML pour afficher les résultats
    return render_template('diagnostic/word_placement.html', results=results)

@app.route('/diagnostic/word-placement/test/<int:exercise_id>', methods=['GET'])
@login_required
def test_word_placement_scoring(exercise_id):
    """Route pour tester le scoring d'un exercice word_placement spécifique"""
    if not current_user.is_admin:
        flash('Accès non autorisé. Seuls les administrateurs peuvent accéder à cette page.', 'error')
        return redirect(url_for('index'))
    
    exercise = Exercise.query.get_or_404(exercise_id)
    if exercise.exercise_type != 'word_placement':
        flash('Cet exercice n\\'est pas de type "Mots à placer".', 'error')
        return redirect(url_for('diagnostic_word_placement'))
    
    content = exercise.get_content()
    
    # Vérifier la structure
    if not isinstance(content, dict) or 'sentences' not in content or 'answers' not in content:
        flash('Structure de l\\'exercice invalide.', 'error')
        return redirect(url_for('diagnostic_word_placement'))
    
    sentences = content['sentences']
    correct_answers = content['answers']
    
    # Compter les blancs dans les phrases
    total_blanks_in_sentences = sum(s.count('___') for s in sentences)
    
    # Simuler différentes logiques de scoring
    logic1_total = len(correct_answers)
    logic1_score = 100.0  # Toutes les réponses sont correctes
    
    logic2_total = total_blanks_in_sentences
    logic2_score = (min(len(correct_answers), total_blanks_in_sentences) / total_blanks_in_sentences) * 100 if total_blanks_in_sentences > 0 else 0
    
    logic3_total = max(total_blanks_in_sentences, len(correct_answers))
    logic3_score = (len(correct_answers) / logic3_total) * 100 if logic3_total > 0 else 0
    
    # Créer des données de test pour simuler une soumission
    test_data = {
        'exercise': exercise,
        'content': content,
        'sentences': sentences,
        'correct_answers': correct_answers,
        'total_blanks_in_sentences': total_blanks_in_sentences,
        'total_answers': len(correct_answers),
        'logic1': {
            'description': 'Utiliser uniquement le nombre de réponses',
            'total': logic1_total,
            'score': logic1_score
        },
        'logic2': {
            'description': 'Utiliser uniquement le nombre de blancs',
            'total': logic2_total,
            'score': logic2_score
        },
        'logic3': {
            'description': 'Utiliser le maximum entre blancs et réponses (logique actuelle)',
            'total': logic3_total,
            'score': logic3_score
        }
    }
    
    return render_template('diagnostic/word_placement_test.html', data=test_data)
'''
        
        # Créer les templates nécessaires
        os.makedirs('templates/diagnostic', exist_ok=True)
        
        with open('templates/diagnostic/word_placement.html', 'w', encoding='utf-8') as f:
            f.write('''{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <h1>Diagnostic des exercices "Mots à placer"</h1>
    <p>Nombre d'exercices trouvés: {{ results|length }}</p>
    
    <div class="alert alert-info">
        <h4>Comment interpréter les résultats</h4>
        <p>Cette page analyse tous les exercices de type "Mots à placer" et vérifie la cohérence entre:</p>
        <ul>
            <li>Le nombre de blancs (___) dans les phrases</li>
            <li>Le nombre de réponses attendues</li>
            <li>Le nombre de mots disponibles</li>
        </ul>
        <p>Un exercice est considéré comme <strong>cohérent</strong> si le nombre de blancs est égal au nombre de réponses attendues.</p>
    </div>
    
    <div class="mb-4">
        <h2>Résumé</h2>
        <div class="row">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Exercices cohérents</h5>
                        <p class="card-text display-4">{{ results|selectattr('is_consistent')|list|length }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Exercices incohérents</h5>
                        <p class="card-text display-4">{{ results|rejectattr('is_consistent')|list|length }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Total</h5>
                        <p class="card-text display-4">{{ results|length }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <h2>Détails des exercices</h2>
    <div class="accordion" id="exerciseAccordion">
        {% for result in results %}
        <div class="accordion-item">
            <h2 class="accordion-header" id="heading{{ result.id }}">
                <button class="accordion-button {{ 'collapsed' if result.is_consistent else '' }}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ result.id }}" aria-expanded="{{ 'false' if result.is_consistent else 'true' }}" aria-controls="collapse{{ result.id }}">
                    #{{ result.id }} - {{ result.title }}
                    {% if result.is_consistent %}
                    <span class="badge bg-success ms-2">Cohérent</span>
                    {% else %}
                    <span class="badge bg-danger ms-2">Incohérent</span>
                    {% endif %}
                </button>
            </h2>
            <div id="collapse{{ result.id }}" class="accordion-collapse collapse {{ 'show' if not result.is_consistent else '' }}" aria-labelledby="heading{{ result.id }}" data-bs-parent="#exerciseAccordion">
                <div class="accordion-body">
                    {% if result.error is defined %}
                    <div class="alert alert-danger">
                        Erreur: {{ result.error }}
                    </div>
                    {% else %}
                    <div class="row">
                        <div class="col-md-6">
                            <h4>Structure</h4>
                            <table class="table table-bordered">
                                <tr>
                                    <th>Phrases</th>
                                    <td>{{ 'Oui' if result.has_sentences else 'Non' }}</td>
                                </tr>
                                <tr>
                                    <th>Mots</th>
                                    <td>{{ 'Oui' if result.has_words else 'Non' }}</td>
                                </tr>
                                <tr>
                                    <th>Réponses</th>
                                    <td>{{ 'Oui' if result.has_answers else 'Non' }}</td>
                                </tr>
                                <tr>
                                    <th>Blancs dans phrases</th>
                                    <td>{{ result.blanks_in_sentences }}</td>
                                </tr>
                                <tr>
                                    <th>Nombre de réponses</th>
                                    <td>{{ result.answers_count }}</td>
                                </tr>
                                <tr>
                                    <th>Nombre de mots</th>
                                    <td>{{ result.words_count }}</td>
                                </tr>
                                <tr>
                                    <th>Score simulé (toutes réponses correctes)</th>
                                    <td>{{ result.simulated_score|round(1) if result.simulated_score is not none else 'N/A' }}%</td>
                                </tr>
                            </table>
                            
                            <h4>Actions</h4>
                            <a href="{{ url_for('test_word_placement_scoring', exercise_id=result.id) }}" class="btn btn-primary">Tester le scoring</a>
                            <a href="{{ url_for('edit_exercise', exercise_id=result.id) }}" class="btn btn-secondary">Modifier l'exercice</a>
                        </div>
                        <div class="col-md-6">
                            <h4>Contenu</h4>
                            <div class="card">
                                <div class="card-body">
                                    <h5>Phrases</h5>
                                    {% if result.has_sentences %}
                                    <ol>
                                        {% for sentence in result.content.sentences %}
                                        <li>{{ sentence }}</li>
                                        {% endfor %}
                                    </ol>
                                    {% else %}
                                    <p>Aucune phrase trouvée</p>
                                    {% endif %}
                                    
                                    <h5>Mots</h5>
                                    {% if result.has_words %}
                                    <ul>
                                        {% for word in result.content.words %}
                                        <li>{{ word }}</li>
                                        {% endfor %}
                                    </ul>
                                    {% else %}
                                    <p>Aucun mot trouvé</p>
                                    {% endif %}
                                    
                                    <h5>Réponses</h5>
                                    {% if result.has_answers %}
                                    <ol>
                                        {% for answer in result.content.answers %}
                                        <li>{{ answer }}</li>
                                        {% endfor %}
                                    </ol>
                                    {% else %}
                                    <p>Aucune réponse trouvée</p>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {% if result.attempts %}
                    <h4 class="mt-4">Dernières tentatives</h4>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Étudiant</th>
                                <th>Score</th>
                                <th>Réponses correctes</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for attempt in result.attempts %}
                            <tr>
                                <td>{{ attempt.id }}</td>
                                <td>{{ attempt.student_id }}</td>
                                <td>{{ attempt.score|round(1) }}%</td>
                                <td>{{ attempt.correct_count }}/{{ attempt.total_answers }}</td>
                                <td>{{ attempt.created_at }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <p class="mt-4">Aucune tentative trouvée pour cet exercice.</p>
                    {% endif %}
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <h2 class="mt-4">Logique de scoring actuelle</h2>
    <div class="card">
        <div class="card-body">
            <pre><code>
# Code actuel de scoring pour word_placement:
elif exercise.exercise_type == 'word_placement':
    # ...
    sentences = content['sentences']
    correct_answers = content['answers']
    
    # CORRECTION: Compter le nombre réel de blancs dans les phrases
    total_blanks_in_sentences = sum(s.count('___') for s in sentences)
    total_blanks = max(total_blanks_in_sentences, len(correct_answers))
    
    # ...
    score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
            </code></pre>
        </div>
    </div>
</div>
{% endblock %}''')
        
        with open('templates/diagnostic/word_placement_test.html', 'w', encoding='utf-8') as f:
            f.write('''{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <h1>Test de scoring pour l'exercice "{{ data.exercise.title }}"</h1>
    <p><a href="{{ url_for('diagnostic_word_placement') }}" class="btn btn-secondary">Retour au diagnostic</a></p>
    
    <div class="alert alert-info">
        <h4>Informations sur l'exercice</h4>
        <p>ID: {{ data.exercise.id }}</p>
        <p>Titre: {{ data.exercise.title }}</p>
        <p>Nombre de blancs dans les phrases: {{ data.total_blanks_in_sentences }}</p>
        <p>Nombre de réponses attendues: {{ data.total_answers }}</p>
    </div>
    
    <h2>Contenu de l'exercice</h2>
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">Phrases</div>
                <div class="card-body">
                    <ol>
                        {% for sentence in data.sentences %}
                        <li>{{ sentence }}</li>
                        {% endfor %}
                    </ol>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">Réponses attendues</div>
                <div class="card-body">
                    <ol>
                        {% for answer in data.correct_answers %}
                        <li>{{ answer }}</li>
                        {% endfor %}
                    </ol>
                </div>
            </div>
        </div>
    </div>
    
    <h2 class="mt-4">Simulation de scoring</h2>
    <p>Cette simulation suppose que toutes les réponses sont correctes.</p>
    
    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">Logique 1</div>
                <div class="card-body">
                    <h5>{{ data.logic1.description }}</h5>
                    <p>Total: {{ data.logic1.total }}</p>
                    <p>Score: {{ data.logic1.score|round(1) }}%</p>
                    <p>Formule: {{ data.total_answers }} / {{ data.logic1.total }} * 100</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">Logique 2</div>
                <div class="card-body">
                    <h5>{{ data.logic2.description }}</h5>
                    <p>Total: {{ data.logic2.total }}</p>
                    <p>Score: {{ data.logic2.score|round(1) }}%</p>
                    <p>Formule: {{ min(data.total_answers, data.total_blanks_in_sentences) }} / {{ data.logic2.total }} * 100</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card {{ 'border-success' if data.logic3.score == 100 else '' }}">
                <div class="card-header {{ 'bg-success text-white' if data.logic3.score == 100 else '' }}">Logique 3 (actuelle)</div>
                <div class="card-body">
                    <h5>{{ data.logic3.description }}</h5>
                    <p>Total: {{ data.logic3.total }}</p>
                    <p>Score: {{ data.logic3.score|round(1) }}%</p>
                    <p>Formule: {{ data.total_answers }} / {{ data.logic3.total }} * 100</p>
                </div>
            </div>
        </div>
    </div>
    
    <h2 class="mt-4">Conclusion</h2>
    <div class="alert alert-success">
        <p>La logique actuelle utilise le <strong>maximum</strong> entre le nombre de blancs dans les phrases et le nombre de réponses attendues.</p>
        <p>Cette approche est la plus robuste car elle gère correctement les cas où:</p>
        <ul>
            <li>Il y a plus de blancs que de réponses</li>
            <li>Il y a plus de réponses que de blancs</li>
        </ul>
        <p>Pour cet exercice, le score avec la logique actuelle est de <strong>{{ data.logic3.score|round(1) }}%</strong>.</p>
    </div>
    
    <div class="mt-4">
        <a href="{{ url_for('diagnostic_word_placement') }}" class="btn btn-secondary">Retour au diagnostic</a>
        <a href="{{ url_for('edit_exercise', exercise_id=data.exercise.id) }}" class="btn btn-primary">Modifier l'exercice</a>
    </div>
</div>
{% endblock %}''')
        
        # Trouver un bon endroit pour insérer la route
        # Chercher après la dernière route
        last_route_idx = original_content.rfind('@app.route')
        if last_route_idx != -1:
            # Trouver la fin de cette fonction
            def_start = original_content.find('def', last_route_idx)
            if def_start != -1:
                function_name_end = original_content.find('(', def_start)
                if function_name_end != -1:
                    function_name = original_content[def_start+4:function_name_end].strip()
                    
                    # Trouver la fin de cette fonction
                    next_def = original_content.find('def ', def_start + 4)
                    if next_def != -1:
                        # Insérer la nouvelle route avant la prochaine fonction
                        modified_content = original_content[:next_def] + diagnostic_route + original_content[next_def:]
                        
                        # Écrire le contenu modifié
                        with open(app_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        
                        logger.info("Route de diagnostic améliorée ajoutée avec succès.")
                        return True
        
        # Si nous n'avons pas pu trouver un bon endroit, essayer une autre approche
        # Chercher juste avant la ligne if __name__ == "__main__":
        main_idx = original_content.find('if __name__ == "__main__":')
        if main_idx != -1:
            modified_content = original_content[:main_idx] + diagnostic_route + "\n\n" + original_content[main_idx:]
            
            # Écrire le contenu modifié
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            logger.info("Route de diagnostic améliorée ajoutée avec succès.")
            return True
        
        logger.warning("Impossible de trouver un bon endroit pour insérer la route.")
        return False
    
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de la route de diagnostic: {str(e)}")
        return False

def main():
    """
    Fonction principale
    """
    logger.info("=== AJOUT DE LA ROUTE DE DIAGNOSTIC AMÉLIORÉE POUR WORD_PLACEMENT ===")
    
    success = add_improved_diagnostic_route()
    
    if success:
        logger.info("""
=== ROUTE DE DIAGNOSTIC AMÉLIORÉE AJOUTÉE AVEC SUCCÈS ===

La route de diagnostic améliorée pour les exercices word_placement a été ajoutée.
Pour l'utiliser:
1. Redémarrez l'application Flask
2. Connectez-vous en tant qu'administrateur
3. Accédez à /diagnostic/word-placement

Cette route vous permettra de:
- Voir tous les exercices word_placement avec leurs détails
- Vérifier la cohérence entre les blancs et les réponses
- Tester différentes logiques de scoring
- Visualiser les dernières tentatives des étudiants
- Identifier les exercices problématiques

Les templates ont été créés dans:
- templates/diagnostic/word_placement.html
- templates/diagnostic/word_placement_test.html

Pour déployer cette route en production:
1. Vérifiez que tout fonctionne correctement en local
2. Committez les changements: git commit -am "Ajout route diagnostic améliorée pour word_placement"
3. Poussez vers le dépôt distant: git push

La route sera alors déployée automatiquement sur Railway.
""")
    else:
        logger.error("""
=== ÉCHEC DE L'AJOUT DE LA ROUTE DE DIAGNOSTIC ===

La route de diagnostic n'a pas pu être ajoutée. Vérifiez les messages d'erreur ci-dessus.
""")

if __name__ == "__main__":
    main()
