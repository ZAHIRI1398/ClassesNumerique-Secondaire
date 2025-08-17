#!/usr/bin/env python3
"""
Solution définitive pour corriger tous les problèmes de scoring des exercices fill_in_blanks et word_placement
Ce script combine toutes les corrections précédentes et s'assure que tous les exercices sont correctement traités
"""
import os
import sys
import json
import argparse
import subprocess
import re
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

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

def connect_to_db():
    """Établit une connexion à la base de données"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("[ERREUR] Variable d'environnement DATABASE_URL non définie!")
        return None
    
    try:
        engine = create_engine(database_url)
        connection = engine.connect()
        print("[INFO] Connexion à la base de données établie avec succès!")
        return connection
    except Exception as e:
        print(f"[ERREUR] Impossible de se connecter à la base de données: {e}")
        return None

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

def fix_all_exercises_in_db(connection):
    """Corrige tous les exercices fill_in_blanks et word_placement dans la base de données"""
    try:
        print("\n[INFO] Correction de tous les exercices fill_in_blanks et word_placement dans la base de données...")
        
        # Récupérer tous les exercices fill_in_blanks
        result = connection.execute(text("SELECT id, title, exercise_type, content FROM exercise WHERE exercise_type IN ('fill_in_blanks', 'word_placement')"))
        exercises = result.fetchall()
        
        if not exercises:
            print("[INFO] Aucun exercice fill_in_blanks ou word_placement trouvé.")
            return True
        
        print(f"[INFO] {len(exercises)} exercice(s) trouvé(s):")
        
        fixed_count = 0
        for ex in exercises:
            print(f"\n[INFO] Traitement de l'exercice '{ex.title}' (ID: {ex.id}, Type: {ex.exercise_type})...")
            try:
                content = json.loads(ex.content)
                
                # Compter les blancs dans le contenu
                total_blanks_in_content = 0
                
                if 'sentences' in content:
                    sentences_blanks = sum(s.count('___') for s in content['sentences'])
                    total_blanks_in_content = sentences_blanks
                    print(f"[INFO] Format 'sentences' détecté: {sentences_blanks} blancs")
                elif 'text' in content:
                    text_blanks = content['text'].count('___')
                    total_blanks_in_content = text_blanks
                    print(f"[INFO] Format 'text' détecté: {text_blanks} blancs")
                
                # Récupérer les réponses correctes (peut être 'words' ou 'available_words')
                correct_answers = content.get('words', [])
                if not correct_answers:
                    correct_answers = content.get('available_words', [])
                
                if not correct_answers:
                    print(f"[ALERTE] Aucune réponse correcte trouvée pour l'exercice {ex.id}!")
                    continue
                
                print(f"[INFO] {len(correct_answers)} réponses correctes trouvées")
                
                # Vérifier la cohérence et corriger si nécessaire
                needs_fixing = False
                
                # Si les réponses sont dans available_words mais pas dans words, c'est un problème
                if not content.get('words') and content.get('available_words'):
                    content['words'] = content['available_words']
                    needs_fixing = True
                    print("[INFO] Correction: Copie des réponses de 'available_words' vers 'words'")
                
                # Vérifier la cohérence entre le nombre de blancs et le nombre de réponses
                if total_blanks_in_content != len(correct_answers):
                    print(f"[ALERTE] Incohérence détectée: {total_blanks_in_content} blancs mais {len(correct_answers)} réponses!")
                    
                    # Si le nombre de blancs est supérieur au nombre de réponses, ajouter des réponses vides
                    if total_blanks_in_content > len(correct_answers):
                        for i in range(len(correct_answers), total_blanks_in_content):
                            correct_answers.append("")
                        content['words'] = correct_answers
                        needs_fixing = True
                        print(f"[INFO] Correction: Ajout de {total_blanks_in_content - len(correct_answers)} réponses vides")
                    
                    # Si le nombre de réponses est supérieur au nombre de blancs, supprimer les réponses en trop
                    elif len(correct_answers) > total_blanks_in_content:
                        content['words'] = correct_answers[:total_blanks_in_content]
                        needs_fixing = True
                        print(f"[INFO] Correction: Suppression de {len(correct_answers) - total_blanks_in_content} réponses en trop")
                
                if needs_fixing:
                    # Mettre à jour l'exercice dans la base de données
                    new_content = json.dumps(content, ensure_ascii=False)
                    connection.execute(
                        text("UPDATE exercise SET content = :content WHERE id = :id"),
                        {"content": new_content, "id": ex.id}
                    )
                    connection.commit()
                    print(f"[SUCCÈS] Exercice '{ex.title}' (ID: {ex.id}) corrigé avec succès!")
                    fixed_count += 1
                else:
                    print(f"[INFO] Aucune correction nécessaire pour l'exercice '{ex.title}' (ID: {ex.id}).")
            
            except Exception as e:
                print(f"[ERREUR] Erreur lors du traitement de l'exercice {ex.id}: {e}")
                continue
        
        print(f"\n[INFO] {fixed_count}/{len(exercises)} exercice(s) corrigé(s).")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la correction des exercices: {e}")
        return False

def add_form_data_debug_route():
    """Ajoute une route de diagnostic pour les données de formulaire"""
    app_path = 'app.py'
    template_path = 'templates/debug/form_data.html'
    
    # Vérifier si la route existe déjà
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '@app.route(\'/debug-form-data\')' in content:
        print("[INFO] La route de diagnostic pour les données de formulaire existe déjà!")
        return False
    
    # Créer le répertoire templates/debug s'il n'existe pas
    os.makedirs('templates/debug', exist_ok=True)
    
    # Créer le template
    template_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test de formulaire</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        form { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        label { display: block; margin: 10px 0 5px; }
        input { padding: 8px; width: 300px; }
        button { margin-top: 20px; padding: 10px 15px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        pre { background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Test de formulaire</h1>
    
    <form method="POST" action="/debug-form-data">
        <h2>Formulaire de test</h2>
        <p>Ce formulaire simule un exercice avec plusieurs champs de réponse.</p>
        
        <label for="answer_0">Réponse 1:</label>
        <input type="text" id="answer_0" name="answer_0" value="test_mot_1">
        
        <label for="answer_1">Réponse 2:</label>
        <input type="text" id="answer_1" name="answer_1" value="test_mot_2">
        
        <label for="answer_2">Réponse 3:</label>
        <input type="text" id="answer_2" name="answer_2" value="test_mot_3">
        
        <label for="answer_3">Réponse 4:</label>
        <input type="text" id="answer_3" name="answer_3" value="test_mot_4">
        
        <label for="answer_4">Réponse 5:</label>
        <input type="text" id="answer_4" name="answer_4" value="test_mot_5">
        
        <button type="submit">Soumettre</button>
    </form>
    
    {% if form_data %}
    <h2>Données reçues:</h2>
    <pre>{{ form_data | tojson(indent=2) }}</pre>
    {% endif %}
</body>
</html>"""
    
    # Écrire le template
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    # Préparer le code de la nouvelle route
    new_route_code = """
# Route de diagnostic pour les données de formulaire
@app.route('/debug-form-data', methods=['GET', 'POST'])
def debug_form_data():
    # Route de diagnostic pour analyser les données de formulaire
    if not current_user.is_authenticated or not current_user.is_admin:
        return "Accès non autorisé", 403
        
    form_data = None
    
    if request.method == 'POST':
        # Récupérer toutes les données du formulaire
        form_data = {
            'form_data': dict(request.form),
            'answer_fields': {k: v for k, v in request.form.items() if k.startswith('answer_')},
            'answer_count': len([k for k in request.form.keys() if k.startswith('answer_')])
        }
        
        # Journaliser les données pour analyse
        app.logger.info(f"[DEBUG_FORM_DATA] Données de formulaire reçues: {form_data}")
        print(f"[DEBUG_FORM_DATA] Données de formulaire reçues: {form_data}")
    
    return render_template('debug/form_data.html', form_data=form_data)
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
    
    print("[SUCCÈS] Route de diagnostic pour les données de formulaire ajoutée avec succès!")
    return True

def deploy_changes():
    """Déploie les modifications sur Railway"""
    print("\n[INFO] Déploiement des modifications sur Railway...")
    
    # Ajouter les fichiers modifiés
    if not run_command("git add app.py templates/debug/form_data.html"):
        return False
    
    # Committer les modifications
    if not run_command("git commit -m \"Fix: Solution définitive pour le scoring des exercices fill_in_blanks et word_placement\""):
        return False
    
    # Pousser sur GitHub
    if not run_command("git push origin main"):
        return False
    
    print("[SUCCÈS] Modifications déployées avec succès sur Railway!")
    return True

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Solution définitive pour corriger tous les problèmes de scoring des exercices fill_in_blanks et word_placement")
    parser.add_argument("--check-only", action="store_true", help="Vérifier seulement, sans appliquer les corrections")
    parser.add_argument("--fix-app", action="store_true", help="Corriger la logique de scoring dans app.py")
    parser.add_argument("--fix-db", action="store_true", help="Corriger les exercices dans la base de données")
    parser.add_argument("--add-debug-route", action="store_true", help="Ajouter une route de diagnostic pour les données de formulaire")
    parser.add_argument("--deploy", action="store_true", help="Déployer les modifications sur Railway")
    parser.add_argument("--all", action="store_true", help="Appliquer toutes les corrections")
    args = parser.parse_args()
    
    # Si --all est spécifié, activer toutes les options
    if args.all:
        args.fix_app = True
        args.fix_db = True
        args.add_debug_route = True
        args.deploy = True
    
    # Si aucune option n'est spécifiée, afficher l'aide
    if not (args.check_only or args.fix_app or args.fix_db or args.add_debug_route or args.deploy):
        parser.print_help()
        return
    
    # Vérifier app.py
    print("[INFO] Vérification de app.py...")
    check_result = check_app_py()
    
    if args.check_only:
        print("[INFO] Mode vérification uniquement. Aucune modification effectuée.")
        return
    
    # Corriger app.py si nécessaire
    if args.fix_app:
        if check_result['has_problematic_fill_in_blanks']:
            print("[INFO] Application de la correction pour fill_in_blanks...")
            fix_fill_in_blanks_scoring()
        
        if check_result['has_problematic_word_placement']:
            print("[INFO] Application de la correction pour word_placement...")
            fix_word_placement_scoring()
        
        if not check_result['has_problematic_fill_in_blanks'] and not check_result['has_problematic_word_placement']:
            print("[INFO] Aucune correction nécessaire pour app.py, la logique de scoring semble déjà correcte.")
    
    # Corriger les exercices dans la base de données
    if args.fix_db:
        print("[INFO] Connexion à la base de données...")
        connection = connect_to_db()
        if connection:
            try:
                fix_all_exercises_in_db(connection)
            finally:
                connection.close()
                print("[INFO] Connexion à la base de données fermée.")
    
    # Ajouter la route de diagnostic
    if args.add_debug_route:
        print("[INFO] Ajout de la route de diagnostic pour les données de formulaire...")
        add_form_data_debug_route()
    
    # Déployer les modifications
    if args.deploy:
        print("[INFO] Déploiement des modifications...")
        deploy_changes()
    
    print("\n[SUCCÈS] Opération terminée!")

if __name__ == "__main__":
    main()
