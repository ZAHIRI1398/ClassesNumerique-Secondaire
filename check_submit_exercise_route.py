#!/usr/bin/env python3
"""
Script pour vérifier la route de soumission des exercices fill_in_blanks
et identifier pourquoi seule la première réponse est comptée correctement
"""

import os
import sys
import re
import shutil
import logging
from datetime import datetime

# Configuration
APP_PY_PATH = 'app.py'
BACKUP_PATH = f'app.py.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
LOG_FILE = f'check_submit_exercise_route_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

def setup_logging():
    """Configure le système de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def backup_file(file_path, backup_path):
    """Crée une sauvegarde du fichier"""
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Sauvegarde créée: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
        return False

def find_submit_exercise_route():
    """Trouve et analyse la route de soumission des exercices"""
    try:
        with open(APP_PY_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        logger.info("Recherche de la route de soumission des exercices...")
        
        # Rechercher le pattern de la route de soumission des exercices
        submit_route_pattern = re.compile(r'@app\.route\([\'"]\/submit_exercise[\'"].*?\n.*?def submit_exercise\(\):.*?return redirect', re.DOTALL)
        submit_route_match = submit_route_pattern.search(content)
        
        if not submit_route_match:
            # Essayer avec un autre pattern pour la route
            submit_route_pattern = re.compile(r'@app\.route\([\'"]\/exercise/submit[\'"].*?\n.*?def submit_exercise\(\):.*?return redirect', re.DOTALL)
            submit_route_match = submit_route_pattern.search(content)
            
            if not submit_route_match:
                # Essayer avec un autre pattern pour la route
                submit_route_pattern = re.compile(r'@app\.route\([\'"]\/exercise/submit_answer[\'"].*?\n.*?def submit_answer\(\):.*?return redirect', re.DOTALL)
                submit_route_match = submit_route_pattern.search(content)
                
                if not submit_route_match:
                    # Essayer avec un autre pattern pour la route
                    submit_route_pattern = re.compile(r'@app\.route\([\'"]\/exercise/submit_answer/.*?\n.*?def submit_answer\(.*?\):.*?return redirect', re.DOTALL)
                    submit_route_match = submit_route_pattern.search(content)
                    
                    if not submit_route_match:
                        # Rechercher toutes les routes qui contiennent "submit" ou "answer"
                        all_routes_pattern = re.compile(r'@app\.route\([\'"]\/.*?(submit|answer).*?[\'"].*?\n.*?def .*?\(.*?\):.*?return', re.DOTALL)
                        all_routes_matches = all_routes_pattern.findall(content)
                        
                        if all_routes_matches:
                            logger.info(f"Routes potentielles trouvées: {len(all_routes_matches)}")
                            for i, route_match in enumerate(all_routes_matches[:5]):  # Limiter à 5 pour éviter un log trop verbeux
                                logger.info(f"Route potentielle {i+1}: {route_match[:200]}...")
                        else:
                            logger.error("Aucune route de soumission des exercices trouvée.")
                            return False
        
        if submit_route_match:
            submit_route = submit_route_match.group(0)
            logger.info("Route de soumission des exercices trouvée.")
            
            # Extraire le nom de la fonction
            function_name_pattern = re.compile(r'def\s+(\w+)\s*\(')
            function_name_match = function_name_pattern.search(submit_route)
            
            if function_name_match:
                function_name = function_name_match.group(1)
                logger.info(f"Nom de la fonction de soumission: {function_name}")
            
            # Rechercher le code spécifique aux exercices fill_in_blanks
            fill_in_blanks_pattern = re.compile(r'if\s+exercise\.exercise_type\s*==\s*[\'"]fill_in_blanks[\'"].*?(?=elif|else|return)', re.DOTALL)
            fill_in_blanks_match = fill_in_blanks_pattern.search(submit_route)
            
            if fill_in_blanks_match:
                fill_in_blanks_code = fill_in_blanks_match.group(0)
                logger.info("Code spécifique aux exercices fill_in_blanks trouvé.")
                
                # Analyser le code de récupération des réponses utilisateur
                analyze_user_answers_code(fill_in_blanks_code)
                
                # Analyser le code de comparaison des réponses
                analyze_comparison_code(fill_in_blanks_code)
                
                # Analyser le code de calcul du score
                analyze_score_calculation(fill_in_blanks_code)
                
                return True
            else:
                logger.error("Code spécifique aux exercices fill_in_blanks non trouvé.")
                
                # Rechercher toute mention de fill_in_blanks dans la route
                if "fill_in_blanks" in submit_route:
                    logger.info("Mentions de 'fill_in_blanks' trouvées dans la route:")
                    lines = submit_route.split('\n')
                    for i, line in enumerate(lines):
                        if "fill_in_blanks" in line:
                            logger.info(f"Ligne {i+1}: {line.strip()}")
                
                return False
        else:
            logger.error("Route de soumission des exercices non trouvée.")
            return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de la route: {e}")
        return False

def analyze_user_answers_code(code):
    """Analyse le code de récupération des réponses utilisateur"""
    try:
        # Rechercher le code de récupération des réponses utilisateur
        user_answers_pattern = re.compile(r'user_answers_list\s*=\s*\[\].*?for\s+i\s+in\s+range\(.*?\):.*?user_answer\s*=\s*request\.form\.get\(.*?\).*?user_answers_list\.append\(user_answer\)', re.DOTALL)
        user_answers_match = user_answers_pattern.search(code)
        
        if not user_answers_match:
            logger.error("Code de récupération des réponses utilisateur non trouvé.")
            
            # Rechercher des fragments du code
            if "user_answers_list" in code:
                logger.info("Mention de 'user_answers_list' trouvée.")
                
                # Extraire les lignes pertinentes
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if "user_answers_list" in line:
                        start_line = max(0, i-2)
                        end_line = min(len(lines), i+5)
                        logger.info("Contexte de 'user_answers_list':")
                        for j in range(start_line, end_line):
                            logger.info(f"  {lines[j].strip()}")
            
            if "request.form.get" in code:
                logger.info("Mention de 'request.form.get' trouvée.")
                
                # Extraire les lignes pertinentes
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if "request.form.get" in line:
                        start_line = max(0, i-2)
                        end_line = min(len(lines), i+3)
                        logger.info("Contexte de 'request.form.get':")
                        for j in range(start_line, end_line):
                            logger.info(f"  {lines[j].strip()}")
            
            return False
        
        user_answers_code = user_answers_match.group(0)
        logger.info("Code de récupération des réponses utilisateur trouvé:")
        logger.info(user_answers_code)
        
        # Vérifier comment les réponses sont récupérées
        if "answer_{i}" in user_answers_code or "answer_' + str(i)" in user_answers_code or "f'answer_{i}'" in user_answers_code:
            logger.info("Le code utilise correctement un index dynamique pour récupérer les réponses.")
        else:
            logger.warning("Le code pourrait ne pas utiliser un index dynamique pour récupérer les réponses.")
        
        # Vérifier si le code gère les valeurs manquantes
        if ".get(" in user_answers_code and ", '')" in user_answers_code:
            logger.info("Le code gère correctement les valeurs manquantes avec une valeur par défaut.")
        else:
            logger.warning("Le code pourrait ne pas gérer correctement les valeurs manquantes.")
        
        # Vérifier si le code nettoie les réponses
        if ".strip()" in user_answers_code:
            logger.info("Le code nettoie correctement les réponses avec strip().")
        else:
            logger.warning("Le code pourrait ne pas nettoyer les réponses avec strip().")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du code de récupération des réponses: {e}")
        return False

def analyze_comparison_code(code):
    """Analyse le code de comparaison des réponses"""
    try:
        # Rechercher le code de comparaison des réponses
        comparison_pattern = re.compile(r'remaining_correct_answers\s*=\s*correct_answers\.copy\(\).*?for\s+user_answer\s+in\s+user_answers_list:.*?if\s+user_answer\.lower\(\)\s*==\s*correct_answer\.lower\(\):', re.DOTALL)
        comparison_match = comparison_pattern.search(code)
        
        if not comparison_match:
            logger.error("Code de comparaison des réponses non trouvé.")
            
            # Rechercher des fragments du code
            if "correct_answers" in code:
                logger.info("Mention de 'correct_answers' trouvée.")
                
                # Extraire les lignes pertinentes
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if "correct_answers" in line:
                        start_line = max(0, i-2)
                        end_line = min(len(lines), i+5)
                        logger.info("Contexte de 'correct_answers':")
                        for j in range(start_line, end_line):
                            logger.info(f"  {lines[j].strip()}")
            
            return False
        
        comparison_code = comparison_match.group(0)
        logger.info("Code de comparaison des réponses trouvé:")
        logger.info(comparison_code)
        
        # Vérifier si le code utilise la logique insensible à l'ordre
        if "remaining_correct_answers" in comparison_code and "copy()" in comparison_code:
            logger.info("Le code utilise la logique insensible à l'ordre avec une copie des réponses correctes.")
        else:
            logger.warning("Le code pourrait ne pas utiliser la logique insensible à l'ordre.")
        
        # Vérifier si le code est insensible à la casse
        if ".lower()" in comparison_code:
            logger.info("Le code est insensible à la casse avec .lower().")
        else:
            logger.warning("Le code pourrait ne pas être insensible à la casse.")
        
        # Vérifier si le code gère correctement le comptage des réponses correctes
        if "correct_blanks += 1" in comparison_code:
            logger.info("Le code incrémente correctement le compteur de réponses correctes.")
        else:
            logger.warning("Le code pourrait ne pas incrémenter correctement le compteur de réponses correctes.")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du code de comparaison des réponses: {e}")
        return False

def analyze_score_calculation(code):
    """Analyse le code de calcul du score"""
    try:
        # Rechercher le code de calcul du score
        score_pattern = re.compile(r'score\s*=\s*\(correct_blanks\s*\/\s*total_blanks\)\s*\*\s*100')
        score_match = score_pattern.search(code)
        
        if not score_match:
            logger.error("Code de calcul du score non trouvé.")
            
            # Rechercher des fragments du code
            if "score" in code:
                logger.info("Mention de 'score' trouvée.")
                
                # Extraire les lignes pertinentes
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if "score" in line and "=" in line:
                        start_line = max(0, i-2)
                        end_line = min(len(lines), i+3)
                        logger.info("Contexte de 'score':")
                        for j in range(start_line, end_line):
                            logger.info(f"  {lines[j].strip()}")
            
            return False
        
        score_code = score_match.group(0)
        logger.info("Code de calcul du score trouvé:")
        logger.info(score_code)
        
        # Vérifier si le code utilise le bon nombre de blancs
        total_blanks_pattern = re.compile(r'total_blanks\s*=\s*max\(total_blanks_in_content,\s*len\(correct_answers\)\)')
        total_blanks_match = total_blanks_pattern.search(code)
        
        if total_blanks_match:
            logger.info("Le code utilise correctement max(total_blanks_in_content, len(correct_answers)) pour calculer total_blanks.")
        else:
            logger.warning("Le code pourrait ne pas calculer correctement le nombre total de blancs.")
            
            # Rechercher comment total_blanks est calculé
            if "total_blanks" in code:
                logger.info("Recherche de la définition de 'total_blanks':")
                
                # Extraire les lignes pertinentes
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if "total_blanks" in line and "=" in line:
                        start_line = max(0, i-2)
                        end_line = min(len(lines), i+3)
                        logger.info("Contexte de 'total_blanks':")
                        for j in range(start_line, end_line):
                            logger.info(f"  {lines[j].strip()}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du code de calcul du score: {e}")
        return False

def analyze_form_submission():
    """Analyse la soumission du formulaire dans les templates"""
    try:
        template_dir = os.path.join('templates')
        fill_in_blanks_templates = []
        
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'fill_in_blanks' in content or 'texte à trous' in content.lower():
                            fill_in_blanks_templates.append(file_path)
        
        if not fill_in_blanks_templates:
            logger.error("Aucun template pour les exercices fill_in_blanks trouvé.")
            return False
        
        logger.info(f"Templates pour les exercices fill_in_blanks trouvés: {len(fill_in_blanks_templates)}")
        
        for template_path in fill_in_blanks_templates:
            logger.info(f"Analyse du template: {template_path}")
            
            with open(template_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            # Rechercher les formulaires de soumission
            form_pattern = re.compile(r'<form[^>]*action=[\'"][^\'"]*/(?:submit_exercise|exercise/submit|exercise/submit_answer)[\'"][^>]*>.*?</form>', re.DOTALL)
            form_match = form_pattern.search(content)
            
            if not form_match:
                logger.warning(f"Formulaire de soumission non trouvé dans {template_path}.")
                continue
            
            form_code = form_match.group(0)
            logger.info(f"Formulaire de soumission trouvé dans {template_path}.")
            
            # Rechercher les champs input pour les réponses
            input_pattern = re.compile(r'<input[^>]*name=[\'"]answer_\d+[\'"][^>]*>')
            input_matches = input_pattern.findall(form_code)
            
            if not input_matches:
                logger.warning(f"Aucun champ input pour les réponses trouvé dans le formulaire de {template_path}.")
                continue
            
            logger.info(f"Champs input pour les réponses trouvés dans {template_path}: {len(input_matches)}")
            
            # Vérifier si les champs input ont des attributs name corrects
            for i, input_match in enumerate(input_matches[:5]):  # Limiter à 5 pour éviter un log trop verbeux
                logger.info(f"Champ input {i+1}: {input_match}")
            
            # Vérifier s'il y a du JavaScript qui pourrait interférer
            if '<script' in content:
                logger.info(f"Le template {template_path} contient du JavaScript qui pourrait affecter la soumission du formulaire.")
                
                # Rechercher du JavaScript qui manipule les champs du formulaire
                js_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL)
                js_matches = js_pattern.findall(content)
                
                for js_match in js_matches:
                    if 'answer_' in js_match:
                        logger.warning(f"Le JavaScript dans {template_path} manipule les champs de réponse, ce qui pourrait causer des problèmes.")
                        logger.info(f"JavaScript suspect: {js_match[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de la soumission du formulaire: {e}")
        return False

def add_debug_code():
    """Ajoute du code de débogage pour la route de soumission des exercices"""
    try:
        with open(APP_PY_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        logger.info("Ajout de code de débogage pour la route de soumission des exercices...")
        
        # Rechercher le pattern de la route de soumission des exercices
        submit_route_pattern = re.compile(r'(@app\.route\([\'"]\/.*?submit.*?[\'"].*?\n.*?def .*?\(.*?\):.*?)(?=@app\.route|\n\n\n|if __name__)', re.DOTALL)
        submit_route_match = submit_route_pattern.search(content)
        
        if not submit_route_match:
            logger.error("Route de soumission des exercices non trouvée.")
            return False
        
        submit_route = submit_route_match.group(1)
        
        # Rechercher le code spécifique aux exercices fill_in_blanks
        fill_in_blanks_pattern = re.compile(r'(if\s+exercise\.exercise_type\s*==\s*[\'"]fill_in_blanks[\'"].*?)(?=elif|else|return)', re.DOTALL)
        fill_in_blanks_match = fill_in_blanks_pattern.search(submit_route)
        
        if not fill_in_blanks_match:
            logger.error("Code spécifique aux exercices fill_in_blanks non trouvé.")
            return False
        
        fill_in_blanks_code = fill_in_blanks_match.group(1)
        
        # Ajouter du code de débogage pour les réponses utilisateur
        user_answers_pattern = re.compile(r'(user_answers_list\s*=\s*\[\].*?for\s+i\s+in\s+range\(.*?\):.*?user_answer\s*=\s*request\.form\.get\(.*?\).*?user_answers_list\.append\(user_answer\))', re.DOTALL)
        user_answers_match = user_answers_pattern.search(fill_in_blanks_code)
        
        if not user_answers_match:
            logger.error("Code de récupération des réponses utilisateur non trouvé.")
            return False
        
        original_code = user_answers_match.group(1)
        
        # Ajouter du logging
        debug_code = original_code + '\n        app.logger.debug(f"[DEBUG] Réponses utilisateur: {user_answers_list}")'
        
        # Remplacer le code original par le code avec logging
        modified_content = content.replace(original_code, debug_code)
        
        # Rechercher le code de comparaison des réponses
        comparison_pattern = re.compile(r'(remaining_correct_answers\s*=\s*correct_answers\.copy\(\).*?for\s+user_answer\s+in\s+user_answers_list:.*?if\s+user_answer\.lower\(\)\s*==\s*correct_answer\.lower\(\):.*?correct_blanks\s*\+=\s*1.*?break)', re.DOTALL)
        comparison_match = comparison_pattern.search(fill_in_blanks_code)
        
        if not comparison_match:
            logger.error("Code de comparaison des réponses non trouvé.")
            return False
        
        original_code = comparison_match.group(1)
        
        # Ajouter du logging
        debug_code = '        app.logger.debug(f"[DEBUG] Réponses correctes: {correct_answers}")\n        ' + original_code + '\n        app.logger.debug(f"[DEBUG] Nombre de réponses correctes: {correct_blanks}/{total_blanks}")'
        
        # Remplacer le code original par le code avec logging
        modified_content = modified_content.replace(original_code, debug_code)
        
        # Écrire le contenu modifié dans le fichier
        with open(APP_PY_PATH, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        logger.info("Code de débogage ajouté avec succès.")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du code de débogage: {e}")
        return False

def suggest_fixes():
    """Suggère des corrections pour le problème de comptage des réponses"""
    logger.info("\n=== SUGGESTIONS DE CORRECTIONS ===")
    
    logger.info("1. Vérifier le déploiement:")
    logger.info("   - Assurez-vous que la dernière version du code est déployée")
    logger.info("   - Redémarrez l'application après le déploiement")
    logger.info("   - Utilisez le script deploy_fill_in_blanks_fix_final.py pour déployer les corrections")
    
    logger.info("\n2. Vérifier la structure de l'exercice dans la base de données:")
    logger.info("   - Assurez-vous que le nombre de blancs dans 'sentences' correspond au nombre de mots dans 'words'")
    logger.info("   - Vérifiez que les réponses correctes sont correctement définies")
    
    logger.info("\n3. Ajouter du logging de débogage:")
    logger.info("   - Utilisez ce script pour ajouter du logging détaillé")
    logger.info("   - Analysez les logs pour comprendre pourquoi seule la première réponse est comptée")
    
    logger.info("\n4. Utiliser la route de débogage:")
    logger.info("   - Exécutez le script add_debug_route.py pour ajouter une route de débogage")
    logger.info("   - Utilisez cette route pour analyser les données du formulaire")
    
    logger.info("\n5. Vérifier la soumission du formulaire:")
    logger.info("   - Assurez-vous que tous les champs input ont des noms corrects (answer_0, answer_1, etc.)")
    logger.info("   - Vérifiez qu'il n'y a pas de JavaScript qui interfère avec la soumission")

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== VÉRIFICATION DE LA ROUTE DE SOUMISSION DES EXERCICES ===")
    
    # Vérifier si le fichier app.py existe
    if not os.path.exists(APP_PY_PATH):
        logger.error(f"Le fichier {APP_PY_PATH} n'existe pas.")
        sys.exit(1)
    
    # Créer une sauvegarde du fichier
    if not backup_file(APP_PY_PATH, BACKUP_PATH):
        logger.error("Impossible de créer une sauvegarde. Arrêt du script.")
        sys.exit(1)
    
    # Trouver et analyser la route de soumission des exercices
    logger.info("\n=== ANALYSE DE LA ROUTE DE SOUMISSION DES EXERCICES ===")
    find_submit_exercise_route()
    
    # Analyser la soumission du formulaire dans les templates
    logger.info("\n=== ANALYSE DE LA SOUMISSION DU FORMULAIRE ===")
    analyze_form_submission()
    
    # Demander si l'utilisateur souhaite ajouter du code de débogage
    response = input("Souhaitez-vous ajouter du code de débogage pour la route de soumission des exercices? (o/n): ")
    if response.lower() == 'o':
        if add_debug_code():
            logger.info("Code de débogage ajouté avec succès.")
        else:
            logger.error("Impossible d'ajouter le code de débogage.")
    
    # Suggérer des corrections
    suggest_fixes()
    
    logger.info(f"\nVérification terminée. Résultats enregistrés dans {LOG_FILE}")

if __name__ == "__main__":
    main()
