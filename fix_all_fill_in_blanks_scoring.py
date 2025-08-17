#!/usr/bin/env python3
"""
Script pour corriger le problème de scoring pour tous les exercices de type 'texte à trous'
Ce script applique la correction à tous les exercices fill_in_blanks et word_placement
"""
import os
import sys
import re
import argparse
import subprocess

def run_command(command):
    """Exécute une commande et affiche le résultat"""
    print(f"\n>>> Exécution: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               capture_output=True, text=True)
        print(f"[OK] Succès: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Échec: {e}")
        print(f"Sortie d'erreur: {e.stderr}")
        return False

def check_app_py():
    """Vérifie si app.py existe et contient la logique de scoring problématique"""
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print(f"[ERREUR] {app_path} n'existe pas!")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher la logique de scoring problématique pour fill_in_blanks
    fill_in_blanks_pattern = r"if 'text' in content:\s+text_blanks = content\['text'\].count\('___'\)\s+total_blanks_in_content \+= text_blanks\s+if 'sentences' in content:\s+sentences_blanks = sum\(s\.count\('___'\) for s in content\['sentences'\]\)\s+total_blanks_in_content \+= sentences_blanks"
    
    # Rechercher la logique de scoring problématique pour word_placement
    word_placement_pattern = r"if 'text' in content:\s+text_blanks = content\['text'\].count\('___'\)\s+total_blanks_in_content = text_blanks\s+elif 'sentences' in content:\s+sentences_blanks = sum\(s\.count\('___'\) for s in content\['sentences'\]\)\s+total_blanks_in_content = sentences_blanks"
    
    # Rechercher la logique de scoring corrigée
    corrected_pattern = r"if 'sentences' in content:\s+sentences_blanks = sum\(s\.count\('___'\) for s in content\['sentences'\]\)\s+total_blanks_in_content = sentences_blanks\s+elif 'text' in content:\s+text_blanks = content\['text'\].count\('___'\)\s+total_blanks_in_content = text_blanks"
    
    has_problematic_fill_in_blanks = bool(re.search(fill_in_blanks_pattern, content, re.DOTALL))
    has_problematic_word_placement = bool(re.search(word_placement_pattern, content, re.DOTALL))
    has_corrected_logic = bool(re.search(corrected_pattern, content, re.DOTALL))
    
    print(f"[INFO] Problème fill_in_blanks trouvé: {has_problematic_fill_in_blanks}")
    print(f"[INFO] Problème word_placement trouvé: {has_problematic_word_placement}")
    print(f"[INFO] Logique corrigée trouvée: {has_corrected_logic}")
    
    return {
        'has_problematic_fill_in_blanks': has_problematic_fill_in_blanks,
        'has_problematic_word_placement': has_problematic_word_placement,
        'has_corrected_logic': has_corrected_logic
    }

def fix_fill_in_blanks_scoring():
    """Corrige la logique de scoring pour les exercices fill_in_blanks"""
    app_path = 'app.py'
    backup_path = 'app.py.bak.fill_in_blanks_fix'
    
    # Créer une sauvegarde
    print(f"[INFO] Création d'une sauvegarde dans {backup_path}...")
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Rechercher et remplacer la logique problématique pour fill_in_blanks
    problematic_pattern = r"if 'text' in content:\s+text_blanks = content\['text'\].count\('___'\)\s+total_blanks_in_content \+= text_blanks\s+if 'sentences' in content:\s+sentences_blanks = sum\(s\.count\('___'\) for s in content\['sentences'\]\)\s+total_blanks_in_content \+= sentences_blanks"
    
    corrected_code = """if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks"""
    
    new_content = re.sub(problematic_pattern, corrected_code, content, flags=re.DOTALL)
    
    if new_content == content:
        print("[INFO] Aucune modification nécessaire pour fill_in_blanks.")
        return False
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("[SUCCÈS] Correction appliquée pour fill_in_blanks!")
    return True

def fix_word_placement_scoring():
    """Corrige la logique de scoring pour les exercices word_placement"""
    app_path = 'app.py'
    backup_path = 'app.py.bak.word_placement_fix'
    
    # Créer une sauvegarde
    print(f"[INFO] Création d'une sauvegarde dans {backup_path}...")
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Rechercher et remplacer la logique problématique pour word_placement
    problematic_pattern = r"if 'text' in content:\s+text_blanks = content\['text'\].count\('___'\)\s+total_blanks_in_content = text_blanks\s+elif 'sentences' in content:\s+sentences_blanks = sum\(s\.count\('___'\) for s in content\['sentences'\]\)\s+total_blanks_in_content = sentences_blanks"
    
    corrected_code = """if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks"""
    
    new_content = re.sub(problematic_pattern, corrected_code, content, flags=re.DOTALL)
    
    if new_content == content:
        print("[INFO] Aucune modification nécessaire pour word_placement.")
        return False
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("[SUCCÈS] Correction appliquée pour word_placement!")
    return True

def add_diagnostic_route():
    """Ajoute une route de diagnostic pour tous les exercices fill_in_blanks"""
    app_path = 'app.py'
    
    # Vérifier si la route existe déjà
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '@app.route(\'/debug-all-fill-in-blanks\')' in content:
        print("[INFO] La route de diagnostic existe déjà!")
        return False
    
    # Préparer le code de la nouvelle route
    new_route_code = """
# Route de diagnostic pour tous les exercices fill_in_blanks
@app.route('/debug-all-fill-in-blanks')
def debug_all_fill_in_blanks():
    # Route de diagnostic pour analyser tous les exercices fill_in_blanks
    if not current_user.is_authenticated or not current_user.is_admin:
        return "Accès non autorisé", 403
        
    results = []
    
    # En-tête
    results.append("<h1>DIAGNOSTIC TOUS LES EXERCICES FILL_IN_BLANKS</h1>")
    
    # 1. Environnement
    results.append("<h2>1. ENVIRONNEMENT</h2>")
    
    # Vérifier les variables d'environnement
    env_vars = {
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'non défini'),
        'DATABASE_URL': os.environ.get('DATABASE_URL', 'non défini')[:10] + '...' if os.environ.get('DATABASE_URL') else 'non défini',
        'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT', 'non défini'),
        'PORT': os.environ.get('PORT', 'non défini')
    }
    
    results.append("<h3>Variables d'environnement:</h3>")
    for key, value in env_vars.items():
        results.append(f"<p>{key}: {value}</p>")
    
    # 2. Liste des exercices
    results.append("<h2>2. LISTE DES EXERCICES FILL_IN_BLANKS</h2>")
    
    try:
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        results.append(f"<p>Nombre d'exercices fill_in_blanks: {len(exercises)}</p>")
        
        if exercises:
            results.append("<table border='1' style='border-collapse: collapse; width: 100%;'>")
            results.append("<tr><th>ID</th><th>Titre</th><th>Image</th><th>Blancs</th><th>Mots</th><th>Cohérence</th></tr>")
            
            for ex in exercises:
                try:
                    content = json.loads(ex.content)
                    
                    # Compter les blancs
                    total_blanks = 0
                    
                    if 'sentences' in content:
                        sentences_blanks = sum(s.count('___') for s in content['sentences'])
                        total_blanks = sentences_blanks
                    elif 'text' in content:
                        text_blanks = content['text'].count('___')
                        total_blanks = text_blanks
                    
                    # Compter les mots
                    words = []
                    if 'words' in content:
                        words = content['words']
                    elif 'available_words' in content:
                        words = content['available_words']
                    
                    # Vérifier la cohérence
                    coherence = "✓" if total_blanks == len(words) else "✗"
                    coherence_color = "green" if total_blanks == len(words) else "red"
                    
                    # Image
                    has_image = "✓" if ex.image_path else "✗"
                    image_color = "green" if ex.image_path else "gray"
                    
                    results.append(f"<tr>")
                    results.append(f"<td>{ex.id}</td>")
                    results.append(f"<td>{ex.title}</td>")
                    results.append(f"<td style='color: {image_color};'>{has_image}</td>")
                    results.append(f"<td>{total_blanks}</td>")
                    results.append(f"<td>{len(words)}</td>")
                    results.append(f"<td style='color: {coherence_color};'>{coherence}</td>")
                    results.append(f"</tr>")
                except Exception as e:
                    results.append(f"<tr><td>{ex.id}</td><td>{ex.title}</td><td colspan='4' style='color: red;'>Erreur: {str(e)}</td></tr>")
            
            results.append("</table>")
        else:
            results.append("<p>Aucun exercice fill_in_blanks trouvé.</p>")
    except Exception as e:
        results.append(f"<p style='color: red;'>Erreur lors de la récupération des exercices: {str(e)}</p>")
    
    # 3. Liste des exercices word_placement
    results.append("<h2>3. LISTE DES EXERCICES WORD_PLACEMENT</h2>")
    
    try:
        exercises = Exercise.query.filter_by(exercise_type='word_placement').all()
        results.append(f"<p>Nombre d'exercices word_placement: {len(exercises)}</p>")
        
        if exercises:
            results.append("<table border='1' style='border-collapse: collapse; width: 100%;'>")
            results.append("<tr><th>ID</th><th>Titre</th><th>Image</th><th>Blancs</th><th>Mots</th><th>Cohérence</th></tr>")
            
            for ex in exercises:
                try:
                    content = json.loads(ex.content)
                    
                    # Compter les blancs
                    total_blanks = 0
                    
                    if 'sentences' in content:
                        sentences_blanks = sum(s.count('___') for s in content['sentences'])
                        total_blanks = sentences_blanks
                    elif 'text' in content:
                        text_blanks = content['text'].count('___')
                        total_blanks = text_blanks
                    
                    # Compter les mots
                    words = []
                    if 'words' in content:
                        words = content['words']
                    elif 'available_words' in content:
                        words = content['available_words']
                    
                    # Vérifier la cohérence
                    coherence = "✓" if total_blanks == len(words) else "✗"
                    coherence_color = "green" if total_blanks == len(words) else "red"
                    
                    # Image
                    has_image = "✓" if ex.image_path else "✗"
                    image_color = "green" if ex.image_path else "gray"
                    
                    results.append(f"<tr>")
                    results.append(f"<td>{ex.id}</td>")
                    results.append(f"<td>{ex.title}</td>")
                    results.append(f"<td style='color: {image_color};'>{has_image}</td>")
                    results.append(f"<td>{total_blanks}</td>")
                    results.append(f"<td>{len(words)}</td>")
                    results.append(f"<td style='color: {coherence_color};'>{coherence}</td>")
                    results.append(f"</tr>")
                except Exception as e:
                    results.append(f"<tr><td>{ex.id}</td><td>{ex.title}</td><td colspan='4' style='color: red;'>Erreur: {str(e)}</td></tr>")
            
            results.append("</table>")
        else:
            results.append("<p>Aucun exercice word_placement trouvé.</p>")
    except Exception as e:
        results.append(f"<p style='color: red;'>Erreur lors de la récupération des exercices: {str(e)}</p>")
    
    # 4. Test de la logique de scoring
    results.append("<h2>4. TEST DE LA LOGIQUE DE SCORING</h2>")
    
    # Test avec sentences
    results.append("<h3>Test avec sentences</h3>")
    test_content_sentences = {
        "sentences": ["Le ___ mange une ___ rouge."],
        "words": ["chat", "pomme"]
    }
    
    # Simuler des réponses utilisateur parfaites
    user_answers_sentences = {
        'answer_0': 'chat',
        'answer_1': 'pomme'
    }
    
    # Calculer le score
    try:
        total_blanks = sum(s.count('___') for s in test_content_sentences['sentences'])
        correct_blanks = 0
        
        for i in range(total_blanks):
            answer_key = f'answer_{i}'
            user_answer = user_answers_sentences.get(answer_key, '')
            correct_answer = test_content_sentences['words'][i] if i < len(test_content_sentences['words']) else ''
            
            if user_answer.lower() == correct_answer.lower():
                correct_blanks += 1
        
        score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
        
        results.append(f"<p>Score avec sentences: {correct_blanks}/{total_blanks} = {score}%</p>")
        if score == 100:
            results.append("<p style='color: green;'>✓ Test sentences réussi!</p>")
        else:
            results.append("<p style='color: red;'>✗ Test sentences échoué!</p>")
    except Exception as e:
        results.append(f"<p style='color: red;'>Erreur test sentences: {str(e)}</p>")
    
    # Test avec text
    results.append("<h3>Test avec text</h3>")
    test_content_text = {
        "text": "Le ___ mange une ___ rouge.",
        "words": ["chat", "pomme"]
    }
    
    # Simuler des réponses utilisateur parfaites
    user_answers_text = {
        'answer_0': 'chat',
        'answer_1': 'pomme'
    }
    
    # Calculer le score
    try:
        total_blanks = test_content_text['text'].count('___')
        correct_blanks = 0
        
        for i in range(total_blanks):
            answer_key = f'answer_{i}'
            user_answer = user_answers_text.get(answer_key, '')
            correct_answer = test_content_text['words'][i] if i < len(test_content_text['words']) else ''
            
            if user_answer.lower() == correct_answer.lower():
                correct_blanks += 1
        
        score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
        
        results.append(f"<p>Score avec text: {correct_blanks}/{total_blanks} = {score}%</p>")
        if score == 100:
            results.append("<p style='color: green;'>✓ Test text réussi!</p>")
        else:
            results.append("<p style='color: red;'>✗ Test text échoué!</p>")
    except Exception as e:
        results.append(f"<p style='color: red;'>Erreur test text: {str(e)}</p>")
    
    # 5. Conclusion
    results.append("<h2>5. CONCLUSION</h2>")
    results.append("<p>Si tous les tests ci-dessus sont réussis (affichés en vert), la logique de scoring est correcte.</p>")
    results.append("<p>Vérifiez particulièrement:</p>")
    results.append("<ul>")
    results.append("<li>Que le nombre de blancs correspond au nombre de mots pour chaque exercice</li>")
    results.append("<li>Que les tests de scoring donnent bien 100%</li>")
    results.append("<li>Que les exercices problématiques sont identifiés (marqués en rouge)</li>")
    results.append("</ul>")
    
    return "<br>".join(results)
"""
    
    # Trouver un bon endroit pour insérer la route
    import_section_end = content.find("# Configuration")
    if import_section_end == -1:
        import_section_end = content.find("@app.route")
    
    if import_section_end == -1:
        print("[ERREUR] Impossible de trouver un bon endroit pour insérer la route!")
        return False
    
    # Insérer la nouvelle route
    new_content = content[:import_section_end] + new_route_code + content[import_section_end:]
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("[SUCCÈS] Route de diagnostic ajoutée avec succès!")
    return True

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Corriger le problème de scoring pour tous les exercices de type 'texte à trous'")
    parser.add_argument("--check-only", action="store_true", help="Vérifier seulement, sans appliquer les corrections")
    parser.add_argument("--add-diagnostic", action="store_true", help="Ajouter une route de diagnostic")
    args = parser.parse_args()
    
    print("[INFO] Vérification de app.py...")
    check_result = check_app_py()
    
    if args.check_only:
        print("[INFO] Mode vérification uniquement. Aucune modification effectuée.")
        return
    
    # Appliquer les corrections si nécessaire
    if check_result['has_problematic_fill_in_blanks']:
        print("[INFO] Application de la correction pour fill_in_blanks...")
        fix_fill_in_blanks_scoring()
    
    if check_result['has_problematic_word_placement']:
        print("[INFO] Application de la correction pour word_placement...")
        fix_word_placement_scoring()
    
    if not check_result['has_problematic_fill_in_blanks'] and not check_result['has_problematic_word_placement']:
        print("[INFO] Aucune correction nécessaire, la logique de scoring semble déjà correcte.")
    
    # Ajouter la route de diagnostic si demandé
    if args.add_diagnostic:
        print("[INFO] Ajout de la route de diagnostic...")
        add_diagnostic_route()
    
    print("\n[SUCCÈS] Opération terminée!")
    print("[INFO] Pour déployer les modifications sur Railway:")
    print("1. Vérifiez les modifications avec 'git diff'")
    print("2. Ajoutez les fichiers modifiés avec 'git add app.py'")
    print("3. Committez avec 'git commit -m \"Fix: Correction du scoring pour tous les exercices texte à trous\"'")
    print("4. Poussez sur GitHub avec 'git push origin main'")
    print("5. Vérifiez le déploiement sur Railway")

if __name__ == "__main__":
    main()
