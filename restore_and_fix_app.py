import os
import shutil
import datetime
import re

def backup_file(file_path):
    """Crée une sauvegarde du fichier avec un timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    return backup_path

def restore_from_backup(backup_path, target_path):
    """Restaure un fichier à partir d'une sauvegarde."""
    shutil.copy2(backup_path, target_path)
    print(f"Fichier restauré depuis: {backup_path}")
    return True

def apply_word_format_fix(file_path):
    """Applique la correction du format des mots dans le code de scoring."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Rechercher le bloc de code pour fill_in_blanks
    fill_in_blanks_pattern = r'(elif exercise\.exercise_type == \'fill_in_blanks\':[^\n]*\n)(\s+)# Gestion des exercices Texte à trous'
    fill_in_blanks_match = re.search(fill_in_blanks_pattern, content)
    
    if not fill_in_blanks_match:
        print("Bloc de code fill_in_blanks non trouvé.")
        return False
    
    # Trouver l'indentation correcte
    indentation = fill_in_blanks_match.group(2)
    
    # Rechercher l'endroit où insérer le code de traitement des mots
    words_pattern = r'(# Récupérer les réponses correctes \(peut être \'words\' ou \'available_words\'\)\n\s+raw_answers = content\.get\(\'words\', \[\]\)\n\s+if not raw_answers:\n\s+raw_answers = content\.get\(\'available_words\', \[\]\)\n)'
    
    # Remplacer par le code qui gère les deux formats de mots
    replacement = r'\1\n{}# Traiter les réponses pour gérer à la fois les chaînes simples et les objets/dictionnaires\n{}correct_answers = []\n{}for answer in raw_answers:\n{}    if isinstance(answer, dict) and \'word\' in answer:\n{}        # Si c\'est un dictionnaire avec une clé \'word\', utiliser cette valeur\n{}        correct_answers.append(answer[\'word\'])\n{}    elif isinstance(answer, str):\n{}        # Si c\'est déjà une chaîne, l\'utiliser directement\n{}        correct_answers.append(answer)\n{}    else:\n{}        # Sinon, convertir en chaîne (fallback)\n{}        correct_answers.append(str(answer))\n\n{}app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement des réponses: {{raw_answers}} -> {{correct_answers}}")'.format(
        indentation, indentation, indentation, indentation, indentation, 
        indentation, indentation, indentation, indentation, indentation, 
        indentation, indentation, indentation, indentation
    )
    
    modified_content = re.sub(words_pattern, replacement, content)
    
    # Remplacer les références à raw_answers par correct_answers dans le reste du code
    modified_content = re.sub(
        r'(app\.logger\.info\(f"\[FILL_IN_BLANKS_DEBUG\] Found \{len\()raw_answers(\)\} correct answers: \{)raw_answers(\}"\))',
        r'\1correct_answers\2correct_answers\3',
        modified_content
    )
    
    modified_content = re.sub(
        r'(total_blanks = max\(total_blanks_in_content, len\()raw_answers(\)\))',
        r'\1correct_answers\2',
        modified_content
    )
    
    modified_content = re.sub(
        r'(correct_answer = )raw_answers(\[i\] if i < len\()raw_answers(\) else \'\')',
        r'\1correct_answers\2correct_answers\3',
        modified_content
    )
    
    # Écrire le contenu modifié dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print(f"Correction du format des mots appliquée à {file_path}")
    return True

if __name__ == "__main__":
    app_path = "app.py"
    backup_path = "app.py.bak"  # Utiliser la sauvegarde originale
    
    # Faire une sauvegarde de l'état actuel
    backup_file(app_path)
    
    # Restaurer depuis la sauvegarde
    restore_from_backup(backup_path, app_path)
    
    # Appliquer la correction du format des mots
    if apply_word_format_fix(app_path):
        print("Correction appliquée avec succès. Veuillez redémarrer l'application.")
    else:
        print("Erreur lors de l'application de la correction.")
