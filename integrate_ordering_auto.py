"""
Script d'intégration automatique pour ajouter la détection et l'évaluation
des exercices de rangement dans app.py.
"""
import os
import re
import sys
import shutil
from datetime import datetime

def backup_file(file_path):
    """Crée une sauvegarde du fichier."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    return backup_path

def read_file(file_path):
    """Lit le contenu d'un fichier."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path, content):
    """Écrit le contenu dans un fichier."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fichier modifié: {file_path}")

def main():
    """Fonction principale."""
    app_py_path = "app.py"
    ordering_code_path = "fill_in_blanks_ordering_code.py"
    
    # Vérifier si les fichiers existent
    if not os.path.exists(app_py_path):
        print(f"Erreur: {app_py_path} non trouvé.")
        sys.exit(1)
    if not os.path.exists(ordering_code_path):
        print(f"Erreur: {ordering_code_path} non trouvé.")
        sys.exit(1)
    
    # Créer une sauvegarde
    backup_path = backup_file(app_py_path)
    
    # Lire le contenu des fichiers
    app_content = read_file(app_py_path)
    ordering_code = read_file(ordering_code_path)
    
    # Vérifier si l'import est présent
    if "from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise" not in app_content:
        # Trouver un bon endroit pour ajouter l'import
        import_pattern = r"(from\s+\w+\s+import\s+.*?\n\n)"
        match = re.search(import_pattern, app_content, re.DOTALL)
        if match:
            import_end = match.end()
            app_content = (app_content[:import_end] + 
                          "from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise\n\n" +
                          app_content[import_end:])
            print("Import ajouté.")
        else:
            print("Section d'imports non trouvée. L'import sera ajouté manuellement.")
    else:
        print("Import déjà présent.")
    
    # Remplacer la section de traitement des blanks
    pattern = r"(\s+user_answers_data = \{\}\s+\n\s+# Vérifier chaque blanc individuellement - Même logique que word_placement.*?)(\s+# Calculer le score final)"
    replacement = r"\1\n" + ordering_code + r"\2"
    
    # Utiliser une approche différente pour le remplacement
    sections = app_content.split("            # Vérifier chaque blanc individuellement - Même logique que word_placement")
    if len(sections) >= 2:
        # Trouver la fin de la section à remplacer
        end_pattern = "            # Calculer le score final"
        end_parts = sections[1].split(end_pattern)
        if len(end_parts) >= 2:
            # Construire le nouveau contenu
            new_content = sections[0]
            new_content += "            # Vérifier si c'est un exercice de rangement par ordre\n"
            new_content += "            is_ordering, ordering_type = is_ordering_exercise(exercise.description)\n"
            new_content += "            app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Détection exercice de rangement: {is_ordering}, type: {ordering_type}\")\n\n"
            new_content += "            # Si c'est un exercice de rangement, utiliser la logique spécifique\n"
            new_content += "            if is_ordering:\n"
            new_content += "                app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Traitement d'un exercice de rangement {ordering_type}\")\n"
            new_content += "                \n"
            new_content += "                # Récupérer toutes les réponses de l'utilisateur\n"
            new_content += "                user_answers_list = []\n"
            new_content += "                for i in range(total_blanks):\n"
            new_content += "                    user_answer = request.form.get(f'answer_{i}', '').strip()\n"
            new_content += "                    user_answers_list.append(user_answer)\n"
            new_content += "                    user_answers_data[f'answer_{i}'] = user_answer\n"
            new_content += "                \n"
            new_content += "                app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Réponses utilisateur: {user_answers_list}\")\n"
            new_content += "                app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Réponses correctes: {correct_answers}\")\n"
            new_content += "                \n"
            new_content += "                # Évaluer les réponses avec la logique de rangement\n"
            new_content += "                correct_count, feedback_list = evaluate_ordering_exercise(user_answers_list, correct_answers, ordering_type)\n"
            new_content += "                correct_blanks = correct_count\n"
            new_content += "                \n"
            new_content += "                app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Résultat évaluation: {correct_count}/{total_blanks} corrects\")\n"
            new_content += "                app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Feedback détaillé: {feedback_list}\")\n"
            new_content += "                \n"
            new_content += "                # Créer le feedback détaillé\n"
            new_content += "                for i in range(len(user_answers_list)):\n"
            new_content += "                    user_answer = user_answers_list[i] if i < len(user_answers_list) else ''\n"
            new_content += "                    correct_answer = correct_answers[i] if i < len(correct_answers) else ''\n"
            new_content += "                    is_correct = feedback_list[i] if i < len(feedback_list) else False\n"
            new_content += "                    \n"
            new_content += "                    # Déterminer l'index de la phrase à laquelle appartient ce blanc\n"
            new_content += "                    sentence_index = -1\n"
            new_content += "                    local_blank_index = -1\n"
            new_content += "                    if 'sentences' in content:\n"
            new_content += "                        sentence_index, local_blank_index = get_blank_location(i, content['sentences'])\n"
            new_content += "                    \n"
            new_content += "                    feedback_details.append({\n"
            new_content += "                        'blank_index': i,\n"
            new_content += "                        'user_answer': user_answer or '',\n"
            new_content += "                        'correct_answer': correct_answer,\n"
            new_content += "                        'is_correct': is_correct,\n"
            new_content += "                        'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or \"Vide\"}',\n"
            new_content += "                        'sentence_index': sentence_index,\n"
            new_content += "                        'sentence': content['sentences'][sentence_index] if sentence_index >= 0 and 'sentences' in content else ''\n"
            new_content += "                    })\n"
            new_content += "            else:\n"
            new_content += "                # Vérifier chaque blanc individuellement - Même logique que word_placement\n"
            new_content += "                app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total (exercice standard)\")\n"
            new_content += "                for i in range(total_blanks):\n"
            new_content += "                    # Récupérer la réponse de l'utilisateur pour ce blanc\n"
            new_content += "                    user_answer = request.form.get(f'answer_{i}', '').strip()\n"
            new_content += "                    \n"
            new_content += "                    # Récupérer la réponse correcte correspondante\n"
            new_content += "                    correct_answer = correct_answers[i] if i < len(correct_answers) else ''\n"
            new_content += "                    \n"
            new_content += "                    app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Blank {i}:\")\n"
            new_content += "                    app.logger.info(f\"  - Réponse étudiant (answer_{i}): {user_answer}\")\n"
            new_content += "                    app.logger.info(f\"  - Réponse attendue: {correct_answer}\")\n"
            new_content += "                    \n"
            new_content += "                    # Vérifier si la réponse est correcte (insensible à la casse)\n"
            new_content += "                    is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()\n"
            new_content += "                    if is_correct:\n"
            new_content += "                        correct_blanks += 1\n"
            new_content += "                    \n"
            new_content += "                    # Créer le feedback pour ce blanc\n"
            new_content += "                    # Déterminer l'index de la phrase à laquelle appartient ce blanc\n"
            new_content += "                    sentence_index = -1\n"
            new_content += "                    local_blank_index = -1\n"
            new_content += "                    if 'sentences' in content:\n"
            new_content += "                        sentence_index, local_blank_index = get_blank_location(i, content['sentences'])\n"
            new_content += "                        app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Blank {i} est dans la phrase {sentence_index}, position locale {local_blank_index}\")\n"
            new_content += "                    \n"
            new_content += "                    feedback_details.append({\n"
            new_content += "                        'blank_index': i,\n"
            new_content += "                        'user_answer': user_answer or '',\n"
            new_content += "                        'correct_answer': correct_answer,\n"
            new_content += "                        'is_correct': is_correct,\n"
            new_content += "                        'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or \"Vide\"}',\n"
            new_content += "                        'sentence_index': sentence_index,\n"
            new_content += "                        'sentence': content['sentences'][sentence_index] if sentence_index >= 0 and 'sentences' in content else ''\n"
            new_content += "                    })\n"
            new_content += "                    \n"
            new_content += "                    # Sauvegarder les réponses utilisateur\n"
            new_content += "                    user_answers_data[f'answer_{i}'] = user_answer\n"
            new_content += end_pattern + end_parts[1]
            
            # Écrire le nouveau contenu dans le fichier
            write_file("app.py.modified", new_content)
            print("Modifications appliquées avec succès à app.py.modified.")
            print("Veuillez vérifier le fichier app.py.modified et le renommer en app.py si les modifications sont correctes.")
            print(f"En cas de problème, vous pouvez restaurer la sauvegarde: {backup_path}")
        else:
            print("Fin de la section à remplacer non trouvée.")
    else:
        print("Section à remplacer non trouvée.")

if __name__ == "__main__":
    main()
