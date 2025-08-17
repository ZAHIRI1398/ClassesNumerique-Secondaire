#!/usr/bin/env python3
"""
Script simplifié pour vérifier la route de soumission des exercices fill_in_blanks
"""

import os
import sys
import re
import logging
from datetime import datetime

# Configuration
APP_PY_PATH = 'app.py'
LOG_FILE = f'check_submit_route_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

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

def find_submit_routes():
    """Trouve toutes les routes de soumission possibles"""
    try:
        with open(APP_PY_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        logger.info("Recherche de toutes les routes de soumission possibles...")
        
        # Rechercher toutes les routes qui contiennent "submit" ou "answer"
        all_routes_pattern = re.compile(r'@app\.route\([\'"]\/.*?(submit|answer).*?[\'"].*?\n.*?def (\w+)\(.*?\):', re.DOTALL)
        all_routes_matches = all_routes_pattern.findall(content)
        
        if all_routes_matches:
            logger.info(f"Routes potentielles trouvées: {len(all_routes_matches)}")
            
            for i, (route_text, func_name) in enumerate(all_routes_matches):
                # Extraire l'URL de la route
                route_url_pattern = re.compile(r'@app\.route\([\'"]([^\'"]+)[\'"]')
                route_url_match = route_url_pattern.search(route_text)
                route_url = route_url_match.group(1) if route_url_match else "URL inconnue"
                
                logger.info(f"Route {i+1}: URL={route_url}, Fonction={func_name}")
                
                # Vérifier si cette route traite les exercices fill_in_blanks
                if "fill_in_blanks" in route_text:
                    logger.info(f"  Cette route semble traiter les exercices fill_in_blanks")
                    
                    # Extraire le code de la fonction
                    func_pattern = re.compile(f'def {func_name}\\(.*?\\):.*?(?=@app\\.route|\\n\\n\\n|if __name__)', re.DOTALL)
                    func_match = func_pattern.search(content)
                    
                    if func_match:
                        func_code = func_match.group(0)
                        
                        # Rechercher le code de récupération des réponses utilisateur
                        if "request.form.get" in func_code:
                            logger.info(f"  Cette route récupère des données de formulaire")
                            
                            # Rechercher les patterns spécifiques
                            if "answer_" in func_code:
                                logger.info(f"  Cette route récupère des réponses avec le préfixe 'answer_'")
                                
                                # Extraire les lignes pertinentes
                                answer_lines = [line.strip() for line in func_code.split('\n') if "answer_" in line]
                                for line in answer_lines[:5]:  # Limiter à 5 pour éviter un log trop verbeux
                                    logger.info(f"    {line}")
                            
                            # Rechercher le code de traitement des réponses
                            if "user_answers_list" in func_code:
                                logger.info(f"  Cette route utilise une liste de réponses utilisateur")
                                
                                # Extraire les lignes pertinentes
                                answer_list_lines = [line.strip() for line in func_code.split('\n') if "user_answers_list" in line]
                                for line in answer_list_lines[:5]:
                                    logger.info(f"    {line}")
                            
                            # Rechercher le code de calcul du score
                            if "score" in func_code and "correct_blanks" in func_code:
                                logger.info(f"  Cette route calcule un score basé sur le nombre de réponses correctes")
                                
                                # Extraire les lignes pertinentes
                                score_lines = [line.strip() for line in func_code.split('\n') if "score" in line and "=" in line]
                                for line in score_lines[:3]:
                                    logger.info(f"    {line}")
        else:
            logger.error("Aucune route de soumission trouvée.")
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche des routes: {e}")

def check_form_templates():
    """Vérifie les templates qui contiennent des formulaires pour les exercices fill_in_blanks"""
    try:
        template_dir = os.path.join('templates')
        fill_in_blanks_templates = []
        
        logger.info("Recherche des templates avec des formulaires pour les exercices fill_in_blanks...")
        
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if '<form' in content and ('fill_in_blanks' in content or 'texte à trous' in content.lower()):
                                fill_in_blanks_templates.append(file_path)
                    except Exception as e:
                        logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        
        if not fill_in_blanks_templates:
            logger.info("Aucun template avec formulaire pour les exercices fill_in_blanks trouvé.")
            return
        
        logger.info(f"Templates avec formulaires pour les exercices fill_in_blanks trouvés: {len(fill_in_blanks_templates)}")
        
        for template_path in fill_in_blanks_templates:
            logger.info(f"Analyse du template: {template_path}")
            
            try:
                with open(template_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                
                # Rechercher les formulaires
                form_pattern = re.compile(r'<form[^>]*>.*?</form>', re.DOTALL)
                form_matches = form_pattern.findall(content)
                
                if not form_matches:
                    logger.info(f"  Aucun formulaire trouvé dans {template_path}")
                    continue
                
                logger.info(f"  Formulaires trouvés dans {template_path}: {len(form_matches)}")
                
                for i, form_match in enumerate(form_matches):
                    logger.info(f"  Formulaire {i+1}:")
                    
                    # Extraire l'action du formulaire
                    action_pattern = re.compile(r'action=[\'"]([^\'"]*)[\'"]')
                    action_match = action_pattern.search(form_match)
                    action = action_match.group(1) if action_match else "Action non spécifiée"
                    logger.info(f"    Action: {action}")
                    
                    # Extraire la méthode du formulaire
                    method_pattern = re.compile(r'method=[\'"]([^\'"]*)[\'"]')
                    method_match = method_pattern.search(form_match)
                    method = method_match.group(1) if method_match else "GET (par défaut)"
                    logger.info(f"    Méthode: {method}")
                    
                    # Rechercher les champs input pour les réponses
                    input_pattern = re.compile(r'<input[^>]*name=[\'"]answer_\d+[\'"][^>]*>')
                    input_matches = input_pattern.findall(form_match)
                    
                    if not input_matches:
                        logger.info(f"    Aucun champ input pour les réponses trouvé dans ce formulaire")
                        
                        # Rechercher tous les champs input
                        all_input_pattern = re.compile(r'<input[^>]*name=[\'"]([^\'"]*)[\'"][^>]*>')
                        all_input_matches = all_input_pattern.findall(form_match)
                        
                        if all_input_matches:
                            logger.info(f"    Champs input trouvés: {len(all_input_matches)}")
                            logger.info(f"    Noms des champs: {', '.join(all_input_matches[:10])}")
                    else:
                        logger.info(f"    Champs input pour les réponses trouvés: {len(input_matches)}")
                        
                        # Extraire les noms des champs
                        input_names = []
                        for input_match in input_matches:
                            name_pattern = re.compile(r'name=[\'"]([^\'"]*)[\'"]')
                            name_match = name_pattern.search(input_match)
                            if name_match:
                                input_names.append(name_match.group(1))
                        
                        logger.info(f"    Noms des champs: {', '.join(input_names[:10])}")
            
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse du template {template_path}: {e}")
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des templates: {e}")

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== VÉRIFICATION DE LA ROUTE DE SOUMISSION DES EXERCICES ===")
    
    # Vérifier si le fichier app.py existe
    if not os.path.exists(APP_PY_PATH):
        logger.error(f"Le fichier {APP_PY_PATH} n'existe pas.")
        sys.exit(1)
    
    # Trouver toutes les routes de soumission possibles
    logger.info("\n=== ANALYSE DES ROUTES DE SOUMISSION ===")
    find_submit_routes()
    
    # Vérifier les templates qui contiennent des formulaires
    logger.info("\n=== ANALYSE DES TEMPLATES AVEC FORMULAIRES ===")
    check_form_templates()
    
    logger.info(f"\nVérification terminée. Résultats enregistrés dans {LOG_FILE}")

if __name__ == "__main__":
    main()
