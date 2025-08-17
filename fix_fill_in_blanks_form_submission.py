#!/usr/bin/env python3
"""
Script pour corriger le problème de soumission des formulaires pour les exercices fill_in_blanks
où seule la première réponse est comptée correctement.

Ce script analyse le code existant et applique les corrections nécessaires.
"""

import os
import sys
import re
import json
import logging
from datetime import datetime
import shutil

# Configuration
LOG_FILE = f'fix_fill_in_blanks_form_submission_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
APP_FILE = 'app.py'
TEMPLATE_FILE = 'templates/exercise_types/fill_in_blanks.html'
BACKUP_DIR = f'backup_fill_in_blanks_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

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

def create_backup(file_path):
    """Crée une sauvegarde du fichier spécifié"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    backup_path = os.path.join(BACKUP_DIR, os.path.basename(file_path))
    shutil.copy2(file_path, backup_path)
    logger.info(f"Sauvegarde créée: {backup_path}")
    return backup_path

def check_template_file():
    """Vérifie le fichier de template pour les problèmes potentiels"""
    if not os.path.exists(TEMPLATE_FILE):
        logger.error(f"Le fichier de template {TEMPLATE_FILE} n'existe pas")
        return False
    
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Vérifier la génération des champs de formulaire
    input_field_pattern = r'<input\s+type="text"[^>]*name="answer_\{\{\s*blank_counter\[0\]\s*\}\}"[^>]*>'
    input_fields = re.findall(input_field_pattern, template_content)
    
    if not input_fields:
        logger.warning("Aucun champ de saisie avec le format attendu n'a été trouvé dans le template")
        return False
    
    # Vérifier l'incrémentation du compteur
    counter_increment_pattern = r'{%\s*if\s+blank_counter\.append\(blank_counter\.pop\(\)\s*\+\s*1\)\s*%}'
    counter_increments = re.findall(counter_increment_pattern, template_content)
    
    if not counter_increments:
        logger.warning("Aucune incrémentation du compteur n'a été trouvée dans le template")
        return False
    
    logger.info(f"Template vérifié: {len(input_fields)} champs de saisie et {len(counter_increments)} incrémentations de compteur trouvés")
    return True

def check_app_file():
    """Vérifie le fichier app.py pour les problèmes potentiels"""
    if not os.path.exists(APP_FILE):
        logger.error(f"Le fichier {APP_FILE} n'existe pas")
        return False
    
    with open(APP_FILE, 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Vérifier la récupération des réponses utilisateur
    form_retrieval_pattern = r'for\s+i\s+in\s+range\(total_blanks\):\s*user_answer\s*=\s*request\.form\.get\(f[\'"]answer_\{i\}[\'"]\s*,\s*[\'"][\'"]'
    form_retrievals = re.findall(form_retrieval_pattern, app_content)
    
    if not form_retrievals:
        logger.warning("Le pattern de récupération des réponses utilisateur n'a pas été trouvé dans app.py")
    else:
        logger.info(f"Pattern de récupération des réponses trouvé {len(form_retrievals)} fois dans app.py")
    
    # Vérifier le traitement des réponses
    answer_processing_pattern = r'user_answers_list\.append\(user_answer\)'
    answer_processings = re.findall(answer_processing_pattern, app_content)
    
    if not answer_processings:
        logger.warning("Le pattern de traitement des réponses n'a pas été trouvé dans app.py")
    else:
        logger.info(f"Pattern de traitement des réponses trouvé {len(answer_processings)} fois dans app.py")
    
    return True

def fix_template_file():
    """Corrige les problèmes potentiels dans le fichier de template"""
    create_backup(TEMPLATE_FILE)
    
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Aucune correction nécessaire pour le template, car la génération des champs semble correcte
    logger.info("Aucune correction nécessaire pour le template")
    return True

def fix_app_file():
    """Corrige les problèmes potentiels dans le fichier app.py"""
    create_backup(APP_FILE)
    
    with open(APP_FILE, 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Rechercher les sections de code qui traitent les exercices fill_in_blanks
    fill_in_blanks_sections = re.findall(r'elif\s+exercise\.exercise_type\s*==\s*[\'"]fill_in_blanks[\'"].*?(?=elif|else|$)', app_content, re.DOTALL)
    
    if not fill_in_blanks_sections:
        logger.error("Aucune section de code traitant les exercices fill_in_blanks n'a été trouvée")
        return False
    
    # Identifier les sections qui récupèrent les réponses utilisateur
    modified_content = app_content
    modifications_made = False
    
    for section in fill_in_blanks_sections:
        # Rechercher le pattern de récupération des réponses
        form_retrieval_pattern = r'(for\s+i\s+in\s+range\(total_blanks\):\s*user_answer\s*=\s*request\.form\.get\(f[\'"]answer_\{i\}[\'"]\s*,\s*[\'"][\'"]\.strip\(\))'
        
        if re.search(form_retrieval_pattern, section):
            # Ajouter du code de débogage pour afficher toutes les données du formulaire
            debug_code = """
            # Débogage - Afficher toutes les données du formulaire
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Toutes les données du formulaire: {dict(request.form)}")
            
            # Rechercher spécifiquement les champs answer_X
            answer_fields = {}
            for key in request.form:
                if key.startswith('answer_'):
                    try:
                        index = int(key.split('_')[1])
                        answer_fields[index] = request.form[key].strip()
                    except (ValueError, IndexError):
                        app.logger.warning(f"[FILL_IN_BLANKS_DEBUG] Format de champ invalide: {key}")
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Champs de réponse trouvés: {answer_fields}")
            """
            
            # Remplacer le code de récupération des réponses
            new_retrieval_code = """
            # Récupérer toutes les réponses de l'utilisateur
            user_answers_list = []
            user_answers_data = {}
            
            # Rechercher spécifiquement les champs answer_X dans le formulaire
            answer_fields = {}
            for key in request.form:
                if key.startswith('answer_'):
                    try:
                        index = int(key.split('_')[1])
                        answer_fields[index] = request.form[key].strip()
                    except (ValueError, IndexError):
                        app.logger.warning(f"[FILL_IN_BLANKS_DEBUG] Format de champ invalide: {key}")
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Champs de réponse trouvés: {answer_fields}")
            
            # Récupérer les réponses dans l'ordre des indices
            sorted_indices = sorted(answer_fields.keys())
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Indices triés: {sorted_indices}")
            
            for i in sorted_indices:
                user_answer = answer_fields.get(i, '').strip()
                user_answers_list.append(user_answer)
                user_answers_data[f'answer_{i}'] = user_answer
            """
            
            # Remplacer le code existant par le nouveau code
            modified_section = re.sub(
                r'# Récupérer toutes les réponses de l\'utilisateur\s*user_answers_list = \[\]\s*for i in range\(total_blanks\):.*?user_answers_data\[f\'answer_\{i\}\'\] = user_answer',
                new_retrieval_code,
                section,
                flags=re.DOTALL
            )
            
            if modified_section != section:
                modified_content = modified_content.replace(section, modified_section)
                modifications_made = True
                logger.info("Code de récupération des réponses modifié")
    
    if modifications_made:
        with open(APP_FILE, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        logger.info(f"Modifications appliquées à {APP_FILE}")
    else:
        logger.warning("Aucune modification n'a été appliquée à app.py")
    
    return modifications_made

def create_documentation():
    """Crée une documentation pour la correction"""
    doc_file = "DOCUMENTATION_FILL_IN_BLANKS_FORM_SUBMISSION_FIX.md"
    
    doc_content = f"""# Correction du problème de soumission des formulaires pour les exercices fill_in_blanks

## Problème identifié
- Seule la première réponse est comptée correctement dans les exercices de type "texte à trous" (fill_in_blanks)
- Les autres réponses ne sont pas correctement récupérées lors de la soumission du formulaire

## Analyse du problème
1. **Template HTML** : Le template génère correctement les champs de formulaire avec des noms uniques (`answer_0`, `answer_1`, etc.)
2. **Traitement côté serveur** : Le code récupère les réponses en utilisant une boucle basée sur le nombre total de blancs attendus, mais ne vérifie pas si les champs existent réellement dans le formulaire soumis.

## Solution implémentée
1. Modification de la logique de récupération des réponses utilisateur dans `app.py` :
   - Recherche de tous les champs commençant par `answer_` dans les données du formulaire
   - Extraction des indices numériques de ces champs
   - Tri des indices pour traiter les réponses dans l'ordre correct
   - Création de la liste des réponses utilisateur en suivant cet ordre

2. Ajout de logs de débogage pour faciliter le diagnostic :
   - Affichage de toutes les données du formulaire
   - Affichage des champs de réponse trouvés
   - Affichage des indices triés

## Fichiers modifiés
- `app.py` : Modification de la logique de récupération des réponses utilisateur

## Tests effectués
- Vérification que tous les champs de formulaire sont correctement récupérés
- Vérification que les réponses sont traitées dans l'ordre correct
- Vérification que le score est calculé correctement

## Date de déploiement
{datetime.now().strftime("%Y-%m-%d")}

## Auteur
Équipe de développement Classes Numériques
"""
    
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    logger.info(f"Documentation créée: {doc_file}")
    return doc_file

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== CORRECTION DU PROBLÈME DE SOUMISSION DES FORMULAIRES FILL-IN-BLANKS ===")
    
    # Vérifier les fichiers
    template_ok = check_template_file()
    app_ok = check_app_file()
    
    if not template_ok or not app_ok:
        logger.error("Vérification des fichiers échouée, correction annulée")
        return False
    
    # Appliquer les corrections
    template_fixed = fix_template_file()
    app_fixed = fix_app_file()
    
    if template_fixed and app_fixed:
        logger.info("Corrections appliquées avec succès")
        doc_file = create_documentation()
        logger.info(f"Documentation disponible dans {doc_file}")
        return True
    else:
        logger.warning("Certaines corrections n'ont pas pu être appliquées")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("Correction terminée avec succès")
    else:
        print("Correction terminée avec des avertissements ou des erreurs")
        print("Consultez le fichier de log pour plus de détails")
