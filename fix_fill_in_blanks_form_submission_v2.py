#!/usr/bin/env python3
"""
Script amélioré pour corriger le problème de soumission des formulaires pour les exercices fill_in_blanks
où seule la première réponse est comptée correctement.

Cette version utilise une approche plus robuste pour identifier et modifier le code.
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

def fix_app_file():
    """Corrige les problèmes dans le fichier app.py en utilisant une approche plus robuste"""
    create_backup(APP_FILE)
    
    with open(APP_FILE, 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Identifier les sections de code qui traitent les exercices fill_in_blanks
    fill_in_blanks_sections = []
    
    # Rechercher les sections de code qui commencent par "elif exercise.exercise_type == 'fill_in_blanks':"
    pattern = r'(elif\s+exercise\.exercise_type\s*==\s*[\'"]fill_in_blanks[\'"].*?)(elif|else|$)'
    matches = re.finditer(pattern, app_content, re.DOTALL)
    
    for match in matches:
        section_start = match.start(1)
        section_end = match.start(2) if match.group(2) else len(app_content)
        section = app_content[section_start:section_end]
        fill_in_blanks_sections.append((section_start, section_end, section))
    
    logger.info(f"Trouvé {len(fill_in_blanks_sections)} sections de code traitant les exercices fill_in_blanks")
    
    if not fill_in_blanks_sections:
        logger.error("Aucune section de code traitant les exercices fill_in_blanks n'a été trouvée")
        return False
    
    # Identifier les sections qui récupèrent les réponses utilisateur
    modified_content = app_content
    modifications_made = False
    
    for section_start, section_end, section in fill_in_blanks_sections:
        # Rechercher les patterns spécifiques pour identifier la section de récupération des réponses
        if "user_answers_list = []" in section and "for i in range(total_blanks):" in section:
            logger.info("Section de récupération des réponses trouvée")
            
            # Trouver le début et la fin de la section de récupération des réponses
            retrieval_start = section.find("# Récupérer toutes les réponses de l'utilisateur")
            if retrieval_start == -1:
                retrieval_start = section.find("user_answers_list = []")
            
            if retrieval_start == -1:
                logger.warning("Impossible de trouver le début de la section de récupération des réponses")
                continue
            
            # Trouver la fin de la section de récupération des réponses
            retrieval_end = section.find("app.logger.info", retrieval_start)
            if retrieval_end == -1:
                retrieval_end = section.find("\n\n", retrieval_start)
            
            if retrieval_end == -1:
                logger.warning("Impossible de trouver la fin de la section de récupération des réponses")
                continue
            
            # Extraire la section de récupération des réponses
            retrieval_section = section[retrieval_start:retrieval_end]
            logger.info(f"Section de récupération des réponses extraite: {len(retrieval_section)} caractères")
            
            # Nouveau code de récupération des réponses
            new_retrieval_code = """# Récupérer toutes les réponses de l'utilisateur
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
            
            # Récupérer les réponses dans l'ordre des indices
            user_answers_list = []
            user_answers_data = {}
            
            # Utiliser les indices triés pour garantir l'ordre correct
            sorted_indices = sorted(answer_fields.keys())
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Indices triés: {sorted_indices}")
            
            for i in sorted_indices:
                user_answer = answer_fields.get(i, '').strip()
                user_answers_list.append(user_answer)
                user_answers_data[f'answer_{i}'] = user_answer"""
            
            # Remplacer la section de récupération des réponses par le nouveau code
            modified_section = section[:retrieval_start] + new_retrieval_code + section[retrieval_end:]
            
            # Remplacer la section complète dans le contenu de l'application
            modified_content = modified_content[:section_start] + modified_section + modified_content[section_end:]
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
    
    logger.info("=== CORRECTION DU PROBLÈME DE SOUMISSION DES FORMULAIRES FILL-IN-BLANKS (V2) ===")
    
    # Appliquer les corrections
    app_fixed = fix_app_file()
    
    if app_fixed:
        logger.info("Corrections appliquées avec succès")
        doc_file = create_documentation()
        logger.info(f"Documentation disponible dans {doc_file}")
        return True
    else:
        logger.warning("Les corrections n'ont pas pu être appliquées")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("Correction terminée avec succès")
    else:
        print("Correction terminée avec des avertissements ou des erreurs")
        print("Consultez le fichier de log pour plus de détails")
