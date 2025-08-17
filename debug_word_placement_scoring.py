import os
import sys
import json
import sqlite3
from flask import Flask
import logging
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Créer une application Flask minimale pour les tests
app = Flask(__name__)
app.logger = logger

def analyze_local_word_placement_exercises():
    """
    Analyse les exercices word_placement en local
    """
    try:
        # Connexion à la base de données locale
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # Récupérer tous les exercices word_placement
        cursor.execute("SELECT id, title, content FROM exercise WHERE exercise_type = 'word_placement'")
        exercises = cursor.fetchall()
        
        if not exercises:
            logger.warning("Aucun exercice word_placement trouvé dans la base de données locale.")
            return
        
        logger.info(f"Nombre d'exercices word_placement trouvés: {len(exercises)}")
        
        for exercise in exercises:
            exercise_id, title, content_str = exercise
            try:
                content = json.loads(content_str)
                logger.info(f"\n=== Exercice: {title} (ID: {exercise_id}) ===")
                
                # Analyser la structure
                if not isinstance(content, dict):
                    logger.warning(f"Contenu invalide pour l'exercice {exercise_id}: {content}")
                    continue
                
                # Vérifier les clés importantes
                has_sentences = 'sentences' in content
                has_words = 'words' in content
                has_answers = 'answers' in content
                
                logger.info(f"Structure: sentences={has_sentences}, words={has_words}, answers={has_answers}")
                
                # Analyser les phrases et les blancs
                if has_sentences:
                    sentences = content['sentences']
                    total_blanks = sum(s.count('___') for s in sentences)
                    logger.info(f"Phrases: {len(sentences)}")
                    logger.info(f"Blancs dans les phrases: {total_blanks}")
                    
                    # Afficher les phrases
                    for i, sentence in enumerate(sentences):
                        logger.info(f"  Phrase {i+1}: {sentence}")
                        logger.info(f"    Blancs: {sentence.count('___')}")
                
                # Analyser les mots disponibles
                if has_words:
                    words = content['words']
                    logger.info(f"Mots disponibles: {len(words)}")
                    logger.info(f"  Mots: {words}")
                
                # Analyser les réponses attendues
                if has_answers:
                    answers = content['answers']
                    logger.info(f"Réponses attendues: {len(answers)}")
                    logger.info(f"  Réponses: {answers}")
                    
                    # Vérifier la cohérence
                    if has_sentences:
                        blanks_count = sum(s.count('___') for s in sentences)
                        if len(answers) != blanks_count:
                            logger.warning(f"⚠️ Incohérence: {blanks_count} blancs mais {len(answers)} réponses")
                        else:
                            logger.info(f"✅ Cohérence: {blanks_count} blancs et {len(answers)} réponses")
                
                # Simuler le scoring
                simulate_scoring(content)
                
            except json.JSONDecodeError:
                logger.error(f"Erreur de décodage JSON pour l'exercice {exercise_id}")
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de l'exercice {exercise_id}: {str(e)}")
        
        conn.close()
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des exercices: {str(e)}")

def simulate_scoring(content):
    """
    Simule le scoring d'un exercice word_placement
    """
    try:
        if 'sentences' not in content or 'answers' not in content:
            logger.warning("Impossible de simuler le scoring: structure incomplète")
            return
        
        sentences = content['sentences']
        correct_answers = content['answers']
        
        # Méthode 1: Compter les blancs dans les phrases
        total_blanks_in_sentences = sum(s.count('___') for s in sentences)
        
        # Méthode 2: Utiliser le nombre de réponses
        total_answers = len(correct_answers)
        
        # Méthode 3: Prendre le maximum des deux
        total_blanks_max = max(total_blanks_in_sentences, total_answers)
        
        logger.info("\n=== Simulation de scoring ===")
        logger.info(f"Méthode 1 (blancs dans phrases): {total_blanks_in_sentences} blancs")
        logger.info(f"Méthode 2 (nombre de réponses): {total_answers} réponses")
        logger.info(f"Méthode 3 (maximum des deux): {total_blanks_max}")
        
        # Simuler différents scénarios
        
        # Scénario 1: Toutes les réponses sont correctes
        correct_count = total_answers
        
        # Calcul du score avec différentes méthodes
        score1 = (correct_count / total_blanks_in_sentences) * 100 if total_blanks_in_sentences > 0 else 0
        score2 = (correct_count / total_answers) * 100 if total_answers > 0 else 0
        score3 = (correct_count / total_blanks_max) * 100 if total_blanks_max > 0 else 0
        
        logger.info("\n=== Scores simulés (toutes réponses correctes) ===")
        logger.info(f"Score avec méthode 1: {score1:.1f}% ({correct_count}/{total_blanks_in_sentences})")
        logger.info(f"Score avec méthode 2: {score2:.1f}% ({correct_count}/{total_answers})")
        logger.info(f"Score avec méthode 3: {score3:.1f}% ({correct_count}/{total_blanks_max})")
        
        # Scénario 2: La moitié des réponses sont correctes
        half_correct = total_answers // 2
        
        # Calcul du score avec différentes méthodes
        score1 = (half_correct / total_blanks_in_sentences) * 100 if total_blanks_in_sentences > 0 else 0
        score2 = (half_correct / total_answers) * 100 if total_answers > 0 else 0
        score3 = (half_correct / total_blanks_max) * 100 if total_blanks_max > 0 else 0
        
        logger.info("\n=== Scores simulés (moitié des réponses correctes) ===")
        logger.info(f"Score avec méthode 1: {score1:.1f}% ({half_correct}/{total_blanks_in_sentences})")
        logger.info(f"Score avec méthode 2: {score2:.1f}% ({half_correct}/{total_answers})")
        logger.info(f"Score avec méthode 3: {score3:.1f}% ({half_correct}/{total_blanks_max})")
        
    except Exception as e:
        logger.error(f"Erreur lors de la simulation de scoring: {str(e)}")

def analyze_app_py_scoring_logic():
    """
    Analyse la logique de scoring dans app.py
    """
    try:
        app_path = 'app.py'
        
        if not os.path.exists(app_path):
            logger.error(f"Le fichier {app_path} n'existe pas.")
            return
        
        logger.info("\n=== Analyse de la logique de scoring dans app.py ===")
        
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher la section de scoring pour word_placement
        word_placement_section = None
        if "exercise.exercise_type == 'word_placement'" in content:
            start_idx = content.find("exercise.exercise_type == 'word_placement'")
            if start_idx != -1:
                # Trouver le début du bloc
                block_start = content.rfind("elif", 0, start_idx)
                if block_start != -1:
                    # Trouver la fin du bloc (prochain elif ou else)
                    next_elif = content.find("elif", start_idx + 10)
                    next_else = content.find("else:", start_idx + 10)
                    
                    end_idx = next_elif if next_elif != -1 else next_else
                    if end_idx == -1:
                        end_idx = len(content)
                    
                    word_placement_section = content[block_start:end_idx].strip()
        
        if word_placement_section:
            logger.info("Code de scoring pour word_placement trouvé:")
            
            # Analyser les lignes importantes
            lines = word_placement_section.split('\n')
            scoring_lines = []
            
            for i, line in enumerate(lines):
                if "total_blanks" in line or "correct_count" in line or "score" in line:
                    scoring_lines.append(f"{i+1}: {line.strip()}")
            
            logger.info("\nLignes de scoring importantes:")
            for line in scoring_lines:
                logger.info(line)
            
            # Vérifier la méthode de calcul du score
            if "total_blanks = len(correct_answers)" in word_placement_section:
                logger.info("\n⚠️ Méthode de calcul du score: Utilise le nombre de réponses comme total_blanks")
                logger.info("Cette méthode peut être incorrecte si le nombre de blancs dans les phrases est différent.")
            elif "total_blanks_in_sentences = sum(s.count('___') for s in sentences)" in word_placement_section:
                logger.info("\n✅ Méthode de calcul du score: Compte les blancs dans les phrases")
                logger.info("Cette méthode est plus précise.")
            else:
                logger.info("\n❓ Méthode de calcul du score: Non identifiée clairement")
        else:
            logger.warning("Section de scoring pour word_placement non trouvée dans app.py")
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de app.py: {str(e)}")

def compare_with_production():
    """
    Compare la logique locale avec la production en utilisant une route de diagnostic
    """
    try:
        # URL de production (à adapter selon votre environnement)
        production_url = input("Entrez l'URL de production (ex: https://votre-app.up.railway.app): ")
        
        if not production_url:
            logger.warning("URL de production non fournie, comparaison ignorée.")
            return
        
        # Vérifier si l'URL est valide
        if not production_url.startswith(('http://', 'https://')):
            production_url = 'https://' + production_url
        
        logger.info(f"\n=== Comparaison avec la production ({production_url}) ===")
        
        # Tenter de se connecter à la route de diagnostic
        diagnostic_url = f"{production_url}/diagnostic-word-placement"
        
        try:
            response = requests.get(diagnostic_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Route de diagnostic accessible en production")
                logger.info(f"Réponse: {response.text[:500]}...")
            else:
                logger.warning(f"⚠️ Route de diagnostic inaccessible (code {response.status_code})")
                logger.info("Création d'une route de diagnostic recommandée.")
        except requests.RequestException:
            logger.warning("⚠️ Impossible de se connecter à la route de diagnostic")
            logger.info("Création d'une route de diagnostic recommandée.")
    
    except Exception as e:
        logger.error(f"Erreur lors de la comparaison avec la production: {str(e)}")

def create_diagnostic_route():
    """
    Crée un script pour ajouter une route de diagnostic
    """
    try:
        script_path = 'add_word_placement_diagnostic_route.py'
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("""import os
import sys
import json
import logging
from flask import Flask, jsonify, render_template_string

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_diagnostic_route():
    \"\"\"
    Ajoute une route de diagnostic pour les exercices word_placement
    \"\"\"
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
        diagnostic_route = \"\"\"
@app.route('/diagnostic-word-placement')
@login_required
def diagnostic_word_placement():
    \"\"\"Route de diagnostic pour les exercices word_placement\"\"\"
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
    html_template = \"\"\"
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
    \"\"\"
    
    return render_template_string(html_template, results=results)
\"\"\"
        
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
    \"\"\"
    Fonction principale
    \"\"\"
    logger.info("=== AJOUT DE LA ROUTE DE DIAGNOSTIC WORD_PLACEMENT ===")
    
    success = add_diagnostic_route()
    
    if success:
        logger.info(\"\"\"
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
\"\"\")
    else:
        logger.error(\"\"\"
=== ÉCHEC DE L'AJOUT DE LA ROUTE DE DIAGNOSTIC ===

La route de diagnostic n'a pas pu être ajoutée. Vérifiez les messages d'erreur ci-dessus.
\"\"\")

if __name__ == "__main__":
    main()
""")
        
        logger.info(f"Script de création de route de diagnostic créé: {script_path}")
        logger.info("Exécutez ce script pour ajouter une route de diagnostic à votre application.")
    
    except Exception as e:
        logger.error(f"Erreur lors de la création du script de diagnostic: {str(e)}")

def main():
    """
    Fonction principale
    """
    logger.info("=== DIAGNOSTIC DU SCORING WORD_PLACEMENT ===")
    
    # Analyser les exercices word_placement en local
    analyze_local_word_placement_exercises()
    
    # Analyser la logique de scoring dans app.py
    analyze_app_py_scoring_logic()
    
    # Comparer avec la production
    compare_with_production()
    
    # Créer un script pour ajouter une route de diagnostic
    create_diagnostic_route()
    
    logger.info("""
=== DIAGNOSTIC TERMINÉ ===

Ce diagnostic a analysé:
1. Les exercices word_placement dans la base de données locale
2. La logique de scoring dans app.py
3. La comparaison avec la production (si URL fournie)

Un script pour ajouter une route de diagnostic a été créé: add_word_placement_diagnostic_route.py

Prochaines étapes recommandées:
1. Exécutez le script add_word_placement_diagnostic_route.py pour ajouter la route de diagnostic
2. Redémarrez l'application Flask
3. Accédez à /diagnostic-word-placement pour voir les résultats détaillés
4. Exécutez fix_word_placement_scoring.py pour appliquer la correction
""")

if __name__ == "__main__":
    main()
