#!/usr/bin/env python3
"""
Script pour ajouter une route de diagnostic à app.py
"""

import os
import re

def add_diagnostic_route():
    """Ajoute une route de diagnostic à app.py"""
    app_path = 'app.py'
    
    # Vérifier que le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: {app_path} n'existe pas!")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la route existe déjà
    if '@app.route(\'/diagnostic-fill-in-blanks\')' in content:
        print("La route de diagnostic existe déjà!")
        return True
    
    # Importer le code de diagnostic
    with open('diagnostic_fill_in_blanks_railway.py', 'r', encoding='utf-8') as f:
        diagnostic_code = f.read()
    
    # Extraire les fonctions nécessaires
    import_pattern = r'import os.*?import platform'
    imports = re.search(import_pattern, diagnostic_code, re.DOTALL)
    
    test_function_pattern = r'def test_fill_in_blanks_scoring\(.*?\):.*?return results'
    test_function = re.search(test_function_pattern, diagnostic_code, re.DOTALL)
    
    system_info_pattern = r'def get_system_info\(\):.*?return info'
    system_info_function = re.search(system_info_pattern, diagnostic_code, re.DOTALL)
    
    # Préparer le code de la nouvelle route
    new_route_code = f"""
# Route de diagnostic pour fill_in_blanks sur Railway
{imports.group(0) if imports else ''}

{system_info_function.group(0) if system_info_function else ''}

{test_function.group(0) if test_function else ''}

@app.route('/diagnostic-fill-in-blanks')
def diagnostic_fill_in_blanks():
    \"\"\"Route de diagnostic pour vérifier les problèmes fill_in_blanks sur Railway\"\"\"
    if not current_user.is_authenticated or not current_user.is_admin:
        return "Accès non autorisé", 403
        
    results = []
    
    # 1. Vérifier l'environnement
    results.append("<h1>DIAGNOSTIC FILL_IN_BLANKS RAILWAY</h1>")
    results.append("<h2>1. ENVIRONNEMENT</h2>")
    
    # Vérifier les variables d'environnement
    env_vars = {{
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'non défini'),
        'DATABASE_URL': os.environ.get('DATABASE_URL', 'non défini')[:10] + '...' if os.environ.get('DATABASE_URL') else 'non défini',
        'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT', 'non défini'),
        'PORT': os.environ.get('PORT', 'non défini')
    }}
    
    results.append("<h3>Variables d'environnement:</h3>")
    for key, value in env_vars.items():
        results.append(f"<p>{{key}}: {{value}}</p>")
    
    # 2. Vérifier les dossiers d'uploads
    results.append("<h2>2. DOSSIERS UPLOADS</h2>")
    
    static_dir = os.path.join(os.getcwd(), 'static')
    uploads_dir = os.path.join(static_dir, 'uploads')
    
    results.append(f"<p>Dossier static: {{static_dir}} - Existe: {{os.path.exists(static_dir)}}</p>")
    results.append(f"<p>Dossier uploads: {{uploads_dir}} - Existe: {{os.path.exists(uploads_dir)}}</p>")
    
    # Créer uploads si nécessaire
    if not os.path.exists(uploads_dir):
        try:
            os.makedirs(uploads_dir, exist_ok=True)
            # Créer .gitkeep
            gitkeep_path = os.path.join(uploads_dir, ".gitkeep")
            with open(gitkeep_path, 'w') as f:
                f.write("# Dossier uploads pour les images des exercices\\n")
            results.append("<p style='color: green;'>✓ Dossier uploads créé avec .gitkeep</p>")
        except Exception as e:
            results.append(f"<p style='color: red;'>✗ Erreur création uploads: {{e}}</p>")
    else:
        try:
            files = os.listdir(uploads_dir)
            results.append(f"<p style='color: green;'>✓ Dossier uploads existe ({{len(files)}} fichiers)</p>")
            
            # Lister quelques fichiers
            if files:
                results.append("<ul>")
                for f in files[:5]:
                    results.append(f"<li>{{f}}</li>")
                if len(files) > 5:
                    results.append(f"<li>... et {{len(files) - 5}} autres</li>")
                results.append("</ul>")
        except Exception as e:
            results.append(f"<p style='color: red;'>✗ Erreur listage uploads: {{e}}</p>")
    
    # 3. Vérifier les exercices fill_in_blanks
    results.append("<h2>3. EXERCICES FILL_IN_BLANKS</h2>")
    
    try:
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        results.append(f"<p>Nombre d'exercices: {{len(exercises)}}</p>")
        
        if exercises:
            # Prendre le premier exercice pour analyse
            ex = exercises[0]
            results.append(f"<h3>Analyse de l'exercice {{ex.id}}: {{ex.title}}</h3>")
            
            # Image
            if ex.image_path:
                results.append(f"<p>Image path: {{ex.image_path}}</p>")
                # Vérifier si l'image existe
                image_path = os.path.join(uploads_dir, os.path.basename(ex.image_path))
                if os.path.exists(image_path):
                    results.append(f"<p style='color: green;'>✓ Image existe: {{image_path}}</p>")
                else:
                    results.append(f"<p style='color: red;'>✗ Image manquante: {{image_path}}</p>")
            
            # Contenu
            content = json.loads(ex.content)
            results.append(f"<p>Format JSON: {{list(content.keys())}}</p>")
            
            # Compter les blancs
            total_blanks = 0
            
            if 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks += text_blanks
                results.append(f"<p>Text: {{content['text']}}</p>")
                results.append(f"<p>Blancs dans text: {{text_blanks}}</p>")
            
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks += sentences_blanks
                results.append(f"<p>Sentences: {{content['sentences']}}</p>")
                results.append(f"<p>Blancs dans sentences: {{sentences_blanks}}</p>")
            
            # Mots
            words = content.get('words', [])
            if not words:
                words = content.get('available_words', [])
            
            results.append(f"<p>Words: {{words}} (count: {{len(words)}})</p>")
            
            # Vérifier la cohérence
            if total_blanks != len(words):
                results.append(f"<p style='color: red;'>✗ Incohérence: {{total_blanks}} blancs mais {{len(words)}} mots!</p>")
            else:
                results.append(f"<p style='color: green;'>✓ Cohérence: {{total_blanks}} blancs = {{len(words)}} mots</p>")
    
    except Exception as e:
        results.append(f"<p style='color: red;'>✗ Erreur analyse exercices: {{e}}</p>")
    
    # 4. Test de la logique de scoring
    results.append("<h2>4. TEST LOGIQUE SCORING</h2>")
    
    try:
        # Simuler un exercice avec notre logique corrigée
        test_content = {{
            "sentences": ["Le ___ mange une ___ rouge."],
            "words": ["chat", "pomme"]
        }}
        
        # Test 1: Toutes réponses correctes
        results.append("<h3>Test 1: Toutes réponses correctes</h3>")
        
        # Simuler des réponses utilisateur parfaites
        user_answers = {{
            'answer_0': 'chat',
            'answer_1': 'pomme'
        }}
        
        # Utiliser notre fonction de test
        test_results = test_fill_in_blanks_scoring(test_content, user_answers)
        
        if test_results["success"]:
            results.append(f"<p>Score: {{test_results['correct_count']}}/{{test_results['total_blanks']}} = {{test_results['score']}}%</p>")
            
            # Détails par blanc
            results.append("<ul>")
            for detail in test_results["blank_details"]:
                if detail["is_correct"]:
                    results.append(f"<li style='color: green;'>Blanc {{detail['blank_index']}}: '{{detail['user_answer']}}' = '{{detail['correct_answer']}}' ✓</li>")
                else:
                    results.append(f"<li style='color: red;'>Blanc {{detail['blank_index']}}: '{{detail['user_answer']}}' ≠ '{{detail['correct_answer']}}' ✗</li>")
            results.append("</ul>")
        else:
            results.append(f"<p style='color: red;'>Erreur test: {{test_results['error']}}</p>")
        
        # Test 2: Réponses partielles
        results.append("<h3>Test 2: Réponses partielles</h3>")
        
        # Simuler des réponses utilisateur partielles
        user_answers_partial = {{
            'answer_0': 'chat',
            'answer_1': 'banane'  # Incorrect
        }}
        
        # Utiliser notre fonction de test
        test_results_partial = test_fill_in_blanks_scoring(test_content, user_answers_partial)
        
        if test_results_partial["success"]:
            results.append(f"<p>Score: {{test_results_partial['correct_count']}}/{{test_results_partial['total_blanks']}} = {{test_results_partial['score']}}%</p>")
            
            # Détails par blanc
            results.append("<ul>")
            for detail in test_results_partial["blank_details"]:
                if detail["is_correct"]:
                    results.append(f"<li style='color: green;'>Blanc {{detail['blank_index']}}: '{{detail['user_answer']}}' = '{{detail['correct_answer']}}' ✓</li>")
                else:
                    results.append(f"<li style='color: red;'>Blanc {{detail['blank_index']}}: '{{detail['user_answer']}}' ≠ '{{detail['correct_answer']}}' ✗</li>")
            results.append("</ul>")
        else:
            results.append(f"<p style='color: red;'>Erreur test: {{test_results_partial['error']}}</p>")
        
    except Exception as e:
        results.append(f"<p style='color: red;'>✗ Erreur test scoring: {{e}}</p>")
    
    # 5. Conclusion
    results.append("<h2>5. CONCLUSION</h2>")
    results.append("<p>Si tous les tests ci-dessus sont réussis (affichés en vert), la logique de scoring est correcte.</p>")
    results.append("<p>Vérifiez particulièrement:</p>")
    results.append("<ul>")
    results.append("<li>Que le dossier uploads existe</li>")
    results.append("<li>Que les images sont présentes</li>")
    results.append("<li>Que le nombre de blancs correspond au nombre de mots</li>")
    results.append("<li>Que le test de scoring partiel donne bien 50%</li>")
    results.append("</ul>")
    
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
    temp_path = 'app_with_diagnostic.py'
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Route de diagnostic ajoutée avec succès dans {temp_path}!")
    print("Pour appliquer les modifications, exécutez:")
    print(f"copy {temp_path} {app_path}")
    
    return True

if __name__ == '__main__':
    add_diagnostic_route()
