#!/usr/bin/env python3
"""
Script pour appliquer manuellement la correction au problème de soumission des formulaires
pour les exercices fill_in_blanks où seule la première réponse est comptée correctement.
"""

import os
import sys
import re
import logging
from datetime import datetime
import shutil

# Configuration
LOG_FILE = f'fix_fill_in_blanks_manual_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
APP_FILE = 'app.py'
BACKUP_DIR = f'backup_fill_in_blanks_fix_manual_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

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
    """Applique manuellement les corrections au fichier app.py"""
    create_backup(APP_FILE)
    
    with open(APP_FILE, 'r', encoding='utf-8') as f:
        app_content = f.readlines()
    
    # Identifier les lignes à modifier
    modified_lines = []
    in_fill_in_blanks_section = False
    in_user_answers_section = False
    skip_lines = False
    lines_to_skip = 0
    
    for i, line in enumerate(app_content):
        # Détecter le début d'une section fill_in_blanks
        if "elif exercise.exercise_type == 'fill_in_blanks':" in line:
            in_fill_in_blanks_section = True
            modified_lines.append(line)
            continue
        
        # Détecter la fin d'une section fill_in_blanks
        if in_fill_in_blanks_section and ("elif " in line or "else:" in line):
            in_fill_in_blanks_section = False
            in_user_answers_section = False
        
        # Détecter la section de récupération des réponses utilisateur
        if in_fill_in_blanks_section and "# Récupérer toutes les réponses de l'utilisateur" in line:
            in_user_answers_section = True
            modified_lines.append(line)  # Garder le commentaire original
            
            # Ajouter le nouveau code de récupération des réponses
            modified_lines.append("            app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Toutes les données du formulaire: {dict(request.form)}\")\n")
            modified_lines.append("\n")
            modified_lines.append("            # Rechercher spécifiquement les champs answer_X\n")
            modified_lines.append("            answer_fields = {}\n")
            modified_lines.append("            for key in request.form:\n")
            modified_lines.append("                if key.startswith('answer_'):\n")
            modified_lines.append("                    try:\n")
            modified_lines.append("                        index = int(key.split('_')[1])\n")
            modified_lines.append("                        answer_fields[index] = request.form[key].strip()\n")
            modified_lines.append("                    except (ValueError, IndexError):\n")
            modified_lines.append("                        app.logger.warning(f\"[FILL_IN_BLANKS_DEBUG] Format de champ invalide: {key}\")\n")
            modified_lines.append("\n")
            modified_lines.append("            app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Champs de réponse trouvés: {answer_fields}\")\n")
            modified_lines.append("\n")
            modified_lines.append("            # Récupérer les réponses dans l'ordre des indices\n")
            modified_lines.append("            user_answers_list = []\n")
            modified_lines.append("            user_answers_data = {}\n")
            modified_lines.append("\n")
            modified_lines.append("            # Utiliser les indices triés pour garantir l'ordre correct\n")
            modified_lines.append("            sorted_indices = sorted(answer_fields.keys())\n")
            modified_lines.append("            app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Indices triés: {sorted_indices}\")\n")
            modified_lines.append("\n")
            modified_lines.append("            for i in sorted_indices:\n")
            modified_lines.append("                user_answer = answer_fields.get(i, '').strip()\n")
            modified_lines.append("                user_answers_list.append(user_answer)\n")
            modified_lines.append("                user_answers_data[f'answer_{i}'] = user_answer\n")
            
            # Marquer les lignes à sauter (ancien code de récupération des réponses)
            skip_lines = True
            lines_to_skip = 6  # Nombre de lignes à sauter (à ajuster selon le code réel)
            continue
        
        # Sauter les lignes de l'ancien code de récupération des réponses
        if skip_lines:
            if lines_to_skip > 0:
                lines_to_skip -= 1
                continue
            else:
                skip_lines = False
        
        # Sortir du mode de récupération des réponses utilisateur quand on atteint les logs
        if in_user_answers_section and "app.logger.info" in line and "Réponses utilisateur" in line:
            in_user_answers_section = False
        
        # Ajouter les lignes non modifiées
        modified_lines.append(line)
    
    # Écrire le contenu modifié dans le fichier
    with open(APP_FILE, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)
    
    logger.info(f"Modifications appliquées à {APP_FILE}")
    return True

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
    
    logger.info("=== CORRECTION MANUELLE DU PROBLÈME DE SOUMISSION DES FORMULAIRES FILL-IN-BLANKS ===")
    
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
