"""
Script d'intégration pour appliquer les modifications de détection et d'évaluation
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

def add_import(content):
    """Ajoute l'import pour les fonctions de détection et d'évaluation."""
    # Vérifier si l'import existe déjà
    if "from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise" in content:
        print("Import déjà présent.")
        return content
    
    # Chercher la section des imports
    import_section = re.search(r"import\s+.*?\n\n", content, re.DOTALL)
    if import_section:
        # Ajouter notre import à la fin de la section des imports
        import_end = import_section.end()
        new_content = (content[:import_end] + 
                      "from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise\n" +
                      content[import_end:])
        print("Import ajouté avec succès.")
        return new_content
    else:
        print("Section d'imports non trouvée. Ajout au début du fichier.")
        return "from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise\n\n" + content

def modify_fill_in_blanks_section(content):
    """Modifie la section de traitement des exercices fill_in_blanks."""
    # Chercher le début de la section fill_in_blanks
    fill_in_blanks_start = content.find("        elif exercise.exercise_type == 'fill_in_blanks':")
    if fill_in_blanks_start == -1:
        print("Section fill_in_blanks non trouvée.")
        return content
    
    # Chercher la fin de la section fill_in_blanks (début de la section suivante)
    next_section_start = content.find("        elif", fill_in_blanks_start + 1)
    if next_section_start == -1:
        print("Fin de la section fill_in_blanks non trouvée.")
        return content
    
    # Extraire la section fill_in_blanks
    fill_in_blanks_section = content[fill_in_blanks_start:next_section_start]
    
    # Chercher la section où nous devons ajouter la vérification d'exercice de rangement
    detection_insertion_point = fill_in_blanks_section.find("            correct_blanks = 0\n            feedback_details = []\n            user_answers_data = {}")
    if detection_insertion_point == -1:
        print("Point d'insertion pour la détection non trouvé.")
        return content
    
    # Calculer la position absolue dans le contenu complet
    detection_insertion_point_abs = fill_in_blanks_start + detection_insertion_point + len("            correct_blanks = 0\n            feedback_details = []\n            user_answers_data = {}")
    
    # Ajouter la vérification d'exercice de rangement
    detection_code = """
            
            # Vérifier si c'est un exercice de rangement par ordre
            is_ordering, ordering_type = is_ordering_exercise(exercise.description)
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Détection exercice de rangement: {is_ordering}, type: {ordering_type}")
"""
    
    # Chercher le début de la boucle de traitement des blanks
    loop_start = fill_in_blanks_section.find("            # Vérifier chaque blanc individuellement")
    if loop_start == -1:
        print("Début de la boucle de traitement des blanks non trouvé.")
        return content
    
    # Calculer la position absolue dans le contenu complet
    loop_start_abs = fill_in_blanks_start + loop_start
    
    # Remplacer la boucle de traitement des blanks par notre code conditionnel
    loop_code = """            # Si c'est un exercice de rangement, utiliser la logique spécifique
            if is_ordering:
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement d'un exercice de rangement {ordering_type}")
                
                # Récupérer toutes les réponses de l'utilisateur
                user_answers_list = []
                for i in range(total_blanks):
                    user_answer = request.form.get(f'answer_{i}', '').strip()
                    user_answers_list.append(user_answer)
                    user_answers_data[f'answer_{i}'] = user_answer
                
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Réponses utilisateur: {user_answers_list}")
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Réponses correctes: {correct_answers}")
                
                # Évaluer les réponses avec la logique de rangement
                correct_count, feedback_list = evaluate_ordering_exercise(user_answers_list, correct_answers, ordering_type)
                correct_blanks = correct_count
                
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Résultat évaluation: {correct_count}/{total_blanks} corrects")
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Feedback détaillé: {feedback_list}")
                
                # Créer le feedback détaillé
                for i in range(len(user_answers_list)):
                    user_answer = user_answers_list[i] if i < len(user_answers_list) else ''
                    correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                    is_correct = feedback_list[i] if i < len(feedback_list) else False
                    
                    # Déterminer l'index de la phrase à laquelle appartient ce blanc
                    sentence_index = -1
                    local_blank_index = -1
                    if 'sentences' in content:
                        sentence_index, local_blank_index = get_blank_location(i, content['sentences'])
                    
                    feedback_details.append({
                        'blank_index': i,
                        'user_answer': user_answer or '',
                        'correct_answer': correct_answer,
                        'is_correct': is_correct,
                        'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}',
                        'sentence_index': sentence_index,
                        'sentence': content['sentences'][sentence_index] if sentence_index >= 0 and 'sentences' in content else ''
                    })
            else:
                # Vérifier chaque blanc individuellement - Même logique que word_placement
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total (exercice standard)")
"""
    
    # Chercher la fin de la boucle de traitement des blanks
    loop_end = fill_in_blanks_section.find("            # Calculer le score final")
    if loop_end == -1:
        print("Fin de la boucle de traitement des blanks non trouvée.")
        return content
    
    # Calculer la position absolue dans le contenu complet
    loop_end_abs = fill_in_blanks_start + loop_end
    
    # Construire le nouveau contenu
    new_content = (content[:detection_insertion_point_abs] + 
                  detection_code + 
                  content[detection_insertion_point_abs:loop_start_abs] + 
                  loop_code + 
                  content[loop_start_abs:])
    
    print("Section fill_in_blanks modifiée avec succès.")
    return new_content

def main():
    """Fonction principale."""
    app_py_path = "app.py"
    
    # Vérifier si le fichier existe
    if not os.path.exists(app_py_path):
        print(f"Erreur: {app_py_path} non trouvé.")
        sys.exit(1)
    
    # Créer une sauvegarde
    backup_path = backup_file(app_py_path)
    
    # Lire le contenu du fichier
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter l'import
    content = add_import(content)
    
    # Modifier la section fill_in_blanks
    content = modify_fill_in_blanks_section(content)
    
    # Écrire le nouveau contenu dans le fichier
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Modifications appliquées avec succès à {app_py_path}.")
    print(f"En cas de problème, vous pouvez restaurer la sauvegarde: {backup_path}")

if __name__ == "__main__":
    main()
