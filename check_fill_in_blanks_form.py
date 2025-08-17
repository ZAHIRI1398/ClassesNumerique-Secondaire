#!/usr/bin/env python3
"""
Script pour vérifier la soumission des formulaires fill_in_blanks
et corriger le problème de comptage des réponses
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
LOG_FILE = f'check_fill_in_blanks_form_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

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

def check_form_submission_code():
    """Vérifie le code de soumission des formulaires fill_in_blanks"""
    try:
        with open(APP_PY_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        logger.info("Recherche du code de soumission des formulaires fill_in_blanks...")
        
        # Rechercher le pattern de la route de soumission des exercices
        submit_route_pattern = re.compile(r'@app\.route\([\'"]\/submit_exercise[\'"].*?\n.*?def submit_exercise\(\):.*?if exercise\.exercise_type == [\'"]fill_in_blanks[\'"].*?', re.DOTALL)
        submit_route_match = submit_route_pattern.search(content)
        
        if not submit_route_match:
            logger.error("Route de soumission des exercices non trouvée.")
            return False
        
        submit_route = submit_route_match.group(0)
        logger.info("Route de soumission des exercices trouvée.")
        
        # Rechercher le code de récupération des réponses utilisateur
        user_answers_pattern = re.compile(r'user_answers_list\s*=\s*\[\].*?for i in range\(total_blanks\):.*?user_answer\s*=\s*request\.form\.get\([\'"]answer_\{i\}[\'"]', re.DOTALL)
        user_answers_match = user_answers_pattern.search(submit_route)
        
        if not user_answers_match:
            logger.error("Code de récupération des réponses utilisateur non trouvé.")
            return False
        
        user_answers_code = user_answers_match.group(0)
        logger.info("Code de récupération des réponses utilisateur trouvé:")
        logger.info(user_answers_code)
        
        # Vérifier si le code utilise correctement request.form.get
        if "request.form.get(f'answer_{i}', '').strip()" in user_answers_code:
            logger.info("Le code utilise correctement request.form.get avec une valeur par défaut et strip().")
        else:
            logger.warning("Le code pourrait ne pas gérer correctement les valeurs manquantes ou les espaces.")
        
        # Rechercher le code de comparaison des réponses
        comparison_pattern = re.compile(r'remaining_correct_answers\s*=\s*correct_answers\.copy\(\).*?for user_answer in user_answers_list:.*?if user_answer\.lower\(\) == correct_answer\.lower\(\):', re.DOTALL)
        comparison_match = comparison_pattern.search(submit_route)
        
        if not comparison_match:
            logger.error("Code de comparaison des réponses non trouvé.")
            return False
        
        comparison_code = comparison_match.group(0)
        logger.info("Code de comparaison des réponses trouvé:")
        logger.info(comparison_code)
        
        # Vérifier si le code gère correctement les réponses vides
        if "if not user_answer.strip():" in comparison_code or "if user_answer.strip() == '':" in comparison_code:
            logger.info("Le code gère correctement les réponses vides.")
        else:
            logger.warning("Le code pourrait ne pas gérer correctement les réponses vides.")
        
        # Rechercher le code de calcul du score
        score_pattern = re.compile(r'score\s*=\s*\(correct_blanks\s*\/\s*total_blanks\)\s*\*\s*100')
        score_match = score_pattern.search(submit_route)
        
        if not score_match:
            logger.error("Code de calcul du score non trouvé.")
            return False
        
        score_code = score_match.group(0)
        logger.info("Code de calcul du score trouvé:")
        logger.info(score_code)
        
        # Vérifier si le code utilise le bon nombre de blancs
        if "total_blanks = max(total_blanks_in_content, len(correct_answers))" in submit_route:
            logger.info("Le code utilise correctement max(total_blanks_in_content, len(correct_answers)) pour calculer total_blanks.")
        else:
            logger.warning("Le code pourrait ne pas calculer correctement le nombre total de blancs.")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du code: {e}")
        return False

def check_template_code():
    """Vérifie le code des templates pour les exercices fill_in_blanks"""
    try:
        # Rechercher les templates fill_in_blanks
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
            
            # Rechercher les champs input pour les réponses
            input_pattern = re.compile(r'<input[^>]*name=[\'"]answer_\d+[\'"][^>]*>')
            input_matches = input_pattern.findall(content)
            
            if not input_matches:
                logger.warning(f"Aucun champ input pour les réponses trouvé dans {template_path}.")
                continue
            
            logger.info(f"Champs input pour les réponses trouvés dans {template_path}: {len(input_matches)}")
            
            # Vérifier si les champs input ont des attributs name corrects
            for i, input_match in enumerate(input_matches[:5]):  # Limiter à 5 pour éviter un log trop verbeux
                logger.info(f"Champ input {i+1}: {input_match}")
            
            # Rechercher le formulaire
            form_pattern = re.compile(r'<form[^>]*action=[\'"][^\'"]*/submit_exercise[\'"][^>]*>.*?</form>', re.DOTALL)
            form_match = form_pattern.search(content)
            
            if not form_match:
                logger.warning(f"Formulaire de soumission non trouvé dans {template_path}.")
                continue
            
            form_code = form_match.group(0)
            logger.info(f"Formulaire de soumission trouvé dans {template_path}.")
            
            # Vérifier si le formulaire a une méthode POST
            if 'method="post"' in form_code.lower() or "method='post'" in form_code.lower():
                logger.info("Le formulaire utilise correctement la méthode POST.")
            else:
                logger.warning("Le formulaire pourrait ne pas utiliser la méthode POST.")
            
            # Vérifier si le formulaire a un champ CSRF
            if 'csrf_token' in form_code:
                logger.info("Le formulaire inclut un champ CSRF.")
            else:
                logger.warning("Le formulaire pourrait ne pas inclure de champ CSRF.")
            
            # Vérifier s'il y a du JavaScript qui pourrait interférer
            if '<script' in content:
                logger.info("Le template contient du JavaScript qui pourrait affecter la soumission du formulaire.")
                
                # Rechercher du JavaScript qui manipule les champs du formulaire
                js_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL)
                js_matches = js_pattern.findall(content)
                
                for js_match in js_matches:
                    if 'answer_' in js_match:
                        logger.warning("Le JavaScript manipule les champs de réponse, ce qui pourrait causer des problèmes.")
                        logger.info(f"JavaScript suspect: {js_match[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des templates: {e}")
        return False

def add_debug_logging():
    """Ajoute du logging de débogage pour la soumission des formulaires fill_in_blanks"""
    try:
        with open(APP_PY_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        logger.info("Ajout de logging de débogage pour la soumission des formulaires fill_in_blanks...")
        
        # Rechercher le pattern de la récupération des réponses utilisateur
        pattern = re.compile(r'(user_answers_list\s*=\s*\[\].*?for i in range\(total_blanks\):.*?user_answer\s*=\s*request\.form\.get\([\'"]answer_\{i\}[\'"].*?user_answers_list\.append\(user_answer\))', re.DOTALL)
        match = pattern.search(content)
        
        if not match:
            logger.error("Code de récupération des réponses utilisateur non trouvé.")
            return False
        
        original_code = match.group(1)
        
        # Ajouter du logging
        debug_code = original_code + '\n    app.logger.debug(f"[FILL_IN_BLANKS] Réponses utilisateur: {user_answers_list}")'
        
        # Remplacer le code original par le code avec logging
        modified_content = content.replace(original_code, debug_code)
        
        # Rechercher le pattern de la comparaison des réponses
        pattern = re.compile(r'(remaining_correct_answers\s*=\s*correct_answers\.copy\(\).*?for user_answer in user_answers_list:.*?if user_answer\.lower\(\) == correct_answer\.lower\(\):.*?correct_blanks\s*\+=\s*1.*?break)', re.DOTALL)
        match = pattern.search(content)
        
        if not match:
            logger.error("Code de comparaison des réponses non trouvé.")
            return False
        
        original_code = match.group(1)
        
        # Ajouter du logging
        debug_code = 'app.logger.debug(f"[FILL_IN_BLANKS] Réponses correctes: {correct_answers}")\n    ' + original_code + '\n    app.logger.debug(f"[FILL_IN_BLANKS] Nombre de réponses correctes: {correct_blanks}/{total_blanks}")'
        
        # Remplacer le code original par le code avec logging
        modified_content = modified_content.replace(original_code, debug_code)
        
        # Écrire le contenu modifié dans le fichier
        with open(APP_PY_PATH, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        logger.info("Logging de débogage ajouté avec succès.")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du logging de débogage: {e}")
        return False

def suggest_fixes():
    """Suggère des corrections pour le problème de comptage des réponses"""
    logger.info("\n=== SUGGESTIONS DE CORRECTIONS ===")
    
    logger.info("1. Vérifier la structure de l'exercice dans la base de données:")
    logger.info("   - Assurez-vous que le nombre de blancs dans 'sentences' ou 'text' correspond au nombre de mots dans 'words'")
    logger.info("   - Vérifiez que les réponses correctes sont correctement définies")
    
    logger.info("\n2. Vérifier la soumission du formulaire:")
    logger.info("   - Assurez-vous que tous les champs input ont des noms corrects (answer_0, answer_1, etc.)")
    logger.info("   - Vérifiez qu'il n'y a pas de JavaScript qui interfère avec la soumission")
    
    logger.info("\n3. Ajouter du logging de débogage:")
    logger.info("   - Utilisez le script pour ajouter du logging détaillé")
    logger.info("   - Analysez les logs pour comprendre pourquoi seule la première réponse est comptée")
    
    logger.info("\n4. Vérifier le déploiement:")
    logger.info("   - Assurez-vous que la dernière version du code est déployée")
    logger.info("   - Redémarrez l'application après le déploiement")
    
    logger.info("\n5. Utiliser la route de débogage:")
    logger.info("   - Exécutez le script add_debug_route.py pour ajouter une route de débogage")
    logger.info("   - Utilisez cette route pour analyser les données du formulaire")

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== VÉRIFICATION DES FORMULAIRES FILL_IN_BLANKS ===")
    
    # Vérifier si le fichier app.py existe
    if not os.path.exists(APP_PY_PATH):
        logger.error(f"Le fichier {APP_PY_PATH} n'existe pas.")
        sys.exit(1)
    
    # Créer une sauvegarde du fichier
    if not backup_file(APP_PY_PATH, BACKUP_PATH):
        logger.error("Impossible de créer une sauvegarde. Arrêt du script.")
        sys.exit(1)
    
    # Vérifier le code de soumission des formulaires
    logger.info("\n=== VÉRIFICATION DU CODE DE SOUMISSION DES FORMULAIRES ===")
    check_form_submission_code()
    
    # Vérifier le code des templates
    logger.info("\n=== VÉRIFICATION DES TEMPLATES ===")
    check_template_code()
    
    # Demander si l'utilisateur souhaite ajouter du logging de débogage
    response = input("Souhaitez-vous ajouter du logging de débogage pour la soumission des formulaires? (o/n): ")
    if response.lower() == 'o':
        if add_debug_logging():
            logger.info("Logging de débogage ajouté avec succès.")
        else:
            logger.error("Impossible d'ajouter le logging de débogage.")
    
    # Suggérer des corrections
    suggest_fixes()
    
    logger.info(f"\nVérification terminée. Résultats enregistrés dans {LOG_FILE}")

if __name__ == "__main__":
    main()
