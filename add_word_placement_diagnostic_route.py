import os
import sys
import json
import logging
from flask import Flask, jsonify, render_template_string

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_diagnostic_route():
    """
    Ajoute une route de diagnostic pour les exercices word_placement
    """
    try:
        # Chemin vers le fichier app.py
        app_path = 'app.py'
        backup_path = 'app.py.bak.diagnostic'
        
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
        
        # Code de la route de diagnostic
        diagnostic_route = """
@app.route('/diagnostic-word-placement')
@login_required
def diagnostic_word_placement():
    """Route de diagnostic pour les exercices word_placement"""
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('index'))
    
    # Récupérer tous les exercices word_placement
    exercises = Exercise.query.filter_by(exercise_type='word_placement').all()
    
    results = []
    for exercise in exercises:
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
        
        # Vérifier la cohérence
        is_consistent = total_blanks_in_sentences == total_answers
        
        results.append({
            'id': exercise.id,
            'title': exercise.title,
            'has_sentences': has_sentences,
            'has_words': has_words,
            'has_answers': has_answers,
            'blanks_in_sentences': total_blanks_in_sentences,
            'answers_count': total_answers,
            'is_consistent': is_consistent
        })
    
    # Créer un template HTML simple pour afficher les résultats
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Diagnostic Word Placement</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .success { color: green; }
            .warning { color: red; }
        </style>
    </head>
    <body>
        <h1>Diagnostic des exercices "Mots à placer"</h1>
        <p>Nombre d'exercices trouvés: {{ results|length }}</p>
        
        <h2>Résultats</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Titre</th>
                <th>Phrases</th>
                <th>Mots</th>
                <th>Réponses</th>
                <th>Blancs dans phrases</th>
                <th>Nombre de réponses</th>
                <th>Cohérence</th>
            </tr>
            {% for result in results %}
            <tr>
                <td>{{ result.id }}</td>
                <td>{{ result.title }}</td>
                <td>{{ 'Oui' if result.has_sentences else 'Non' }}</td>
                <td>{{ 'Oui' if result.has_words else 'Non' }}</td>
                <td>{{ 'Oui' if result.has_answers else 'Non' }}</td>
                <td>{{ result.blanks_in_sentences }}</td>
                <td>{{ result.answers_count }}</td>
                <td class="{{ 'success' if result.is_consistent else 'warning' }}">
                    {{ 'Oui' if result.is_consistent else 'Non' }}
                </td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>Logique de scoring</h2>
        <pre>
# Code actuel de scoring:
elif exercise.exercise_type == 'word_placement':
    # ...
    sentences = content['sentences']
    correct_answers = content['answers']
    total_blanks = len(correct_answers)  # <-- Utilise le nombre de réponses
    # ...
    score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
        </pre>
        
        <h3>Recommandation</h3>
        <pre>
# Code recommandé:
elif exercise.exercise_type == 'word_placement':
    # ...
    sentences = content['sentences']
    correct_answers = content['answers']
    
    # Compter le nombre réel de blancs dans les phrases
    total_blanks_in_sentences = sum(s.count('___') for s in sentences)
    total_blanks = max(total_blanks_in_sentences, len(correct_answers))
    # ...
    score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
        </pre>
    </body>
    </html>
    """
    
    return render_template_string(html_template, results=results)
"""
        
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
                        
                        logger.info("Route de diagnostic ajoutée avec succès.")
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
    logger.info("=== AJOUT DE LA ROUTE DE DIAGNOSTIC WORD_PLACEMENT ===")
    
    success = add_diagnostic_route()
    
    if success:
        logger.info("""
=== ROUTE DE DIAGNOSTIC AJOUTÉE AVEC SUCCÈS ===

La route de diagnostic pour les exercices word_placement a été ajoutée.
Pour l'utiliser:
1. Redémarrez l'application Flask
2. Connectez-vous en tant qu'administrateur
3. Accédez à /diagnostic-word-placement

Cette route vous permettra de:
- Voir tous les exercices word_placement
- Vérifier la cohérence entre les blancs et les réponses
- Comprendre la logique de scoring actuelle
- Appliquer la correction recommandée

Pour déployer cette route en production:
1. Vérifiez que tout fonctionne correctement en local
2. Committez les changements: git commit -am "Ajout route diagnostic pour word_placement"
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
