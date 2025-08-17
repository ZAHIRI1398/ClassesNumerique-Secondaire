#!/usr/bin/env python3
"""
Script pour ajouter une route de diagnostic spécifique pour l'exercice 'Les coordonnées'
"""

import os
import re

def add_coordonnees_diagnostic_route():
    """Ajoute une route de diagnostic spécifique pour l'exercice 'Les coordonnées' à app.py"""
    app_path = 'app.py'
    
    # Vérifier que le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: {app_path} n'existe pas!")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la route existe déjà
    if '@app.route(\'/debug-coordonnees\')' in content:
        print("La route de diagnostic pour 'Les coordonnées' existe déjà!")
        return True
    
    # Préparer le code de la nouvelle route
    new_route_code = """
# Route de diagnostic spécifique pour l'exercice 'Les coordonnées'
@app.route('/debug-coordonnees')
def debug_coordonnees():
    """Route de diagnostic pour analyser l'exercice 'Les coordonnées'"""
    if not current_user.is_authenticated or not current_user.is_admin:
        return "Accès non autorisé", 403
        
    results = []
    
    # En-tête
    results.append("<h1>DIAGNOSTIC EXERCICE 'LES COORDONNÉES'</h1>")
    
    # 1. Recherche de l'exercice
    results.append("<h2>1. RECHERCHE DE L'EXERCICE</h2>")
    
    try:
        # Rechercher par titre exact
        exercise = Exercise.query.filter_by(title="Les coordonnées").first()
        
        if not exercise:
            # Rechercher avec titre partiel
            exercise = Exercise.query.filter(Exercise.title.like("%coordonnées%")).first()
        
        if not exercise:
            # Rechercher par type d'exercice
            exercises = Exercise.query.filter_by(exercise_type="fill_in_blanks").all()
            results.append(f"<p>Aucun exercice 'Les coordonnées' trouvé. {len(exercises)} exercices de type fill_in_blanks disponibles:</p>")
            
            results.append("<ul>")
            for ex in exercises:
                results.append(f"<li>ID: {ex.id} - Titre: {ex.title}</li>")
            results.append("</ul>")
            
            return "<br>".join(results)
        
        # Exercice trouvé
        results.append(f"<p style='color: green;'>✓ Exercice trouvé: ID={exercise.id}, Titre='{exercise.title}', Type='{exercise.exercise_type}'</p>")
        
        # 2. Analyse du contenu
        results.append("<h2>2. ANALYSE DU CONTENU</h2>")
        
        content = json.loads(exercise.content)
        results.append(f"<p>Clés JSON: {list(content.keys())}</p>")
        
        # 3. Analyse des blancs
        results.append("<h2>3. ANALYSE DES BLANCS</h2>")
        
        total_blanks_in_content = 0
        
        # Compter les blancs dans sentences (prioritaire)
        if 'sentences' in content:
            sentences = content['sentences']
            results.append(f"<p>Sentences: {sentences}</p>")
            
            sentences_blanks = sum(s.count('___') for s in sentences)
            total_blanks_in_content = sentences_blanks
            results.append(f"<p>Nombre de blancs dans sentences: {sentences_blanks}</p>")
        
        # Compter les blancs dans text (fallback)
        elif 'text' in content:
            text = content['text']
            results.append(f"<p>Text: {text}</p>")
            
            text_blanks = text.count('___')
            total_blanks_in_content = text_blanks
            results.append(f"<p>Nombre de blancs dans text: {text_blanks}</p>")
        
        # 4. Analyse des mots/réponses
        results.append("<h2>4. ANALYSE DES MOTS/RÉPONSES</h2>")
        
        words = []
        if 'words' in content:
            words = content['words']
            results.append(f"<p>Words: {words}</p>")
        elif 'available_words' in content:
            words = content['available_words']
            results.append(f"<p>Available words: {words}</p>")
        
        # Vérifier la cohérence
        if total_blanks_in_content != len(words):
            results.append(f"<p style='color: red;'>✗ INCOHÉRENCE: {total_blanks_in_content} blancs mais {len(words)} mots!</p>")
        else:
            results.append(f"<p style='color: green;'>✓ Cohérence: {total_blanks_in_content} blancs = {len(words)} mots</p>")
        
        # 5. Analyse de l'image
        results.append("<h2>5. ANALYSE DE L'IMAGE</h2>")
        
        if exercise.image_path:
            results.append(f"<p>Image path: {exercise.image_path}</p>")
            
            # Vérifier si l'image existe
            image_filename = os.path.basename(exercise.image_path)
            image_path = os.path.join('static', 'uploads', image_filename)
            
            if os.path.exists(image_path):
                results.append(f"<p style='color: green;'>✓ Image existe: {image_path}</p>")
                results.append(f"<img src='/static/uploads/{image_filename}' style='max-width: 300px; border: 1px solid #ccc;'>")
            else:
                results.append(f"<p style='color: red;'>✗ Image manquante: {image_path}</p>")
                
                # Créer une image placeholder si nécessaire
                try:
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    with open(image_path, 'w') as f:
                        f.write('''<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
                            <rect width="300" height="200" fill="#f0f0f0"/>
                            <text x="150" y="100" font-family="Arial" font-size="16" text-anchor="middle">Image placeholder</text>
                        </svg>''')
                    results.append("<p style='color: orange;'>⚠️ Image placeholder créée</p>")
                    results.append(f"<img src='/static/uploads/{image_filename}' style='max-width: 300px; border: 1px solid #ccc;'>")
                except Exception as e:
                    results.append(f"<p style='color: red;'>✗ Erreur création placeholder: {e}</p>")
        else:
            results.append("<p>Aucune image associée à cet exercice</p>")
        
        # 6. Analyse des tentatives récentes
        results.append("<h2>6. ANALYSE DES TENTATIVES RÉCENTES</h2>")
        
        try:
            attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise.id).order_by(ExerciseAttempt.timestamp.desc()).limit(5).all()
            
            if attempts:
                results.append(f"<p>{len(attempts)} tentatives récentes trouvées:</p>")
                results.append("<table border='1' style='border-collapse: collapse; width: 100%;'>")
                results.append("<tr><th>ID</th><th>Utilisateur</th><th>Score</th><th>Date</th><th>Réponses</th></tr>")
                
                for attempt in attempts:
                    user = User.query.get(attempt.user_id)
                    username = user.username if user else f"User {attempt.user_id}"
                    
                    # Analyser les réponses
                    answers = {}
                    try:
                        answers_data = json.loads(attempt.answers) if attempt.answers else {}
                        for key, value in answers_data.items():
                            if key.startswith('answer_'):
                                answers[key] = value
                    except:
                        answers = {"error": "Impossible de parser les réponses"}
                    
                    results.append(f"<tr>")
                    results.append(f"<td>{attempt.id}</td>")
                    results.append(f"<td>{username}</td>")
                    results.append(f"<td>{attempt.score}%</td>")
                    results.append(f"<td>{attempt.timestamp}</td>")
                    results.append(f"<td>{answers}</td>")
                    results.append(f"</tr>")
                
                results.append("</table>")
            else:
                results.append("<p>Aucune tentative récente pour cet exercice</p>")
        except Exception as e:
            results.append(f"<p style='color: red;'>✗ Erreur analyse tentatives: {e}</p>")
        
        # 7. Simulation de scoring
        results.append("<h2>7. SIMULATION DE SCORING</h2>")
        
        try:
            # Simuler une soumission parfaite
            perfect_answers = {}
            for i, word in enumerate(words):
                perfect_answers[f'answer_{i}'] = word
            
            # Calculer le score
            total_blanks = total_blanks_in_content
            correct_blanks = 0
            blank_details = []
            
            for i in range(total_blanks):
                answer_key = f'answer_{i}'
                user_answer = perfect_answers.get(answer_key, '')
                correct_answer = words[i] if i < len(words) else ''
                
                is_correct = user_answer.lower() == correct_answer.lower()
                if is_correct:
                    correct_blanks += 1
                
                blank_details.append({
                    'blank_index': i,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct
                })
            
            score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
            
            results.append(f"<p>Score simulé: {correct_blanks}/{total_blanks} = {score}%</p>")
            
            # Détails par blanc
            results.append("<ul>")
            for detail in blank_details:
                if detail["is_correct"]:
                    results.append(f"<li style='color: green;'>Blanc {detail['blank_index']}: '{detail['user_answer']}' = '{detail['correct_answer']}' ✓</li>")
                else:
                    results.append(f"<li style='color: red;'>Blanc {detail['blank_index']}: '{detail['user_answer']}' ≠ '{detail['correct_answer']}' ✗</li>")
            results.append("</ul>")
            
            # Simuler une soumission partielle (50% correct)
            if total_blanks >= 2:
                results.append("<h3>Simulation avec 50% de réponses correctes</h3>")
                
                partial_answers = {}
                for i, word in enumerate(words):
                    if i < total_blanks // 2:
                        partial_answers[f'answer_{i}'] = word
                    else:
                        partial_answers[f'answer_{i}'] = "INCORRECT"
                
                # Calculer le score
                correct_blanks = 0
                blank_details = []
                
                for i in range(total_blanks):
                    answer_key = f'answer_{i}'
                    user_answer = partial_answers.get(answer_key, '')
                    correct_answer = words[i] if i < len(words) else ''
                    
                    is_correct = user_answer.lower() == correct_answer.lower()
                    if is_correct:
                        correct_blanks += 1
                    
                    blank_details.append({
                        'blank_index': i,
                        'user_answer': user_answer,
                        'correct_answer': correct_answer,
                        'is_correct': is_correct
                    })
                
                score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
                
                results.append(f"<p>Score simulé: {correct_blanks}/{total_blanks} = {score}%</p>")
                
                # Détails par blanc
                results.append("<ul>")
                for detail in blank_details:
                    if detail["is_correct"]:
                        results.append(f"<li style='color: green;'>Blanc {detail['blank_index']}: '{detail['user_answer']}' = '{detail['correct_answer']}' ✓</li>")
                    else:
                        results.append(f"<li style='color: red;'>Blanc {detail['blank_index']}: '{detail['user_answer']}' ≠ '{detail['correct_answer']}' ✗</li>")
                results.append("</ul>")
        
        except Exception as e:
            results.append(f"<p style='color: red;'>✗ Erreur simulation scoring: {e}</p>")
        
        # 8. Recommandations
        results.append("<h2>8. RECOMMANDATIONS</h2>")
        
        if total_blanks_in_content != len(words):
            results.append("<p style='color: red;'>⚠️ PROBLÈME CRITIQUE: Le nombre de blancs ne correspond pas au nombre de mots!</p>")
            results.append("<p>Recommandation: Vérifier et corriger le contenu de l'exercice pour assurer la cohérence.</p>")
        
        if 'sentences' not in content and 'text' not in content:
            results.append("<p style='color: red;'>⚠️ PROBLÈME CRITIQUE: Ni 'sentences' ni 'text' n'est présent dans le contenu!</p>")
            results.append("<p>Recommandation: Vérifier et corriger le format du contenu JSON.</p>")
        
        if not words:
            results.append("<p style='color: red;'>⚠️ PROBLÈME CRITIQUE: Aucun mot/réponse trouvé!</p>")
            results.append("<p>Recommandation: Vérifier et corriger le contenu de l'exercice.</p>")
        
        if exercise.image_path and not os.path.exists(os.path.join('static', 'uploads', os.path.basename(exercise.image_path))):
            results.append("<p style='color: orange;'>⚠️ Image manquante: Un placeholder a été créé, mais l'image originale devrait être restaurée.</p>")
        
        results.append("<p>Pour corriger les problèmes de scoring:</p>")
        results.append("<ol>")
        results.append("<li>Vérifier que la logique de comptage des blancs est correcte (priorité à 'sentences' sur 'text')</li>")
        results.append("<li>Vérifier que la comparaison des réponses est insensible à la casse</li>")
        results.append("<li>Vérifier que le calcul du score est correct: (correct_blanks / total_blanks) * 100</li>")
        results.append("</ol>")
    
    except Exception as e:
        results.append(f"<p style='color: red;'>✗ Erreur générale: {e}</p>")
    
    return "<br>".join(results)
"""
    
    # Trouver un bon endroit pour insérer la route
    # Chercher après les imports mais avant les routes
    import_section_end = content.find("# Configuration")
    if import_section_end == -1:
        import_section_end = content.find("@app.route")
    
    if import_section_end == -1:
        print("Impossible de trouver un bon endroit pour insérer la route!")
        return False
    
    # Insérer la nouvelle route
    new_content = content[:import_section_end] + new_route_code + content[import_section_end:]
    
    # Écrire le contenu modifié dans un fichier temporaire
    temp_path = 'app_with_coordonnees_diagnostic.py'
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Route de diagnostic pour 'Les coordonnées' ajoutée avec succès dans {temp_path}!")
    print("Pour appliquer les modifications, exécutez:")
    print(f"copy {temp_path} {app_path}")
    
    return True

if __name__ == '__main__':
    add_coordonnees_diagnostic_route()
