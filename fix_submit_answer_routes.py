#!/usr/bin/env python3
"""
Script de correction automatique des erreurs submit_answer
Remplace tous les url_for('submit_answer', exercise_id=exercise.id) 
par url_for('submit_answer', exercise_id=exercise.id, course_id=course.id if course else 0)
"""

import os
import re
import glob

def fix_submit_answer_routes():
    """Corrige toutes les erreurs submit_answer dans les templates"""
    
    # Répertoire des templates
    templates_dir = "templates"
    
    # Pattern de remplacement pour submit_answer
    old_pattern = r"url_for\('submit_answer',\s*exercise_id=exercise\.id\)"
    new_replacement = "url_for('submit_answer', exercise_id=exercise.id, course_id=course.id if course else 0)"
    
    # Compteurs
    files_processed = 0
    total_replacements = 0
    
    # Parcourir tous les fichiers HTML
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                
                try:
                    # Lire le fichier
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Appliquer le remplacement
                    matches = re.findall(old_pattern, content)
                    if matches:
                        content = re.sub(old_pattern, new_replacement, content)
                        file_replacements = len(matches)
                        
                        # Sauvegarder si des changements ont été faits
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"[OK] {file_path}: {file_replacements} corrections appliquees")
                        files_processed += 1
                        total_replacements += file_replacements
                    
                except Exception as e:
                    print(f"[ERROR] Erreur avec {file_path}: {e}")
    
    print(f"\n[DONE] CORRECTION TERMINEE !")
    print(f"[FILES] Fichiers traites: {files_processed}")
    print(f"[FIXES] Total corrections: {total_replacements}")
    
    return files_processed, total_replacements

if __name__ == "__main__":
    print("[START] DEMARRAGE DE LA CORRECTION AUTOMATIQUE DES ERREURS submit_answer...")
    print("=" * 70)
    
    files_processed, total_replacements = fix_submit_answer_routes()
    
    if total_replacements > 0:
        print(f"\n[SUCCESS] {total_replacements} erreurs submit_answer corrigees dans {files_processed} fichiers.")
        print("[INFO] Les exercices 'texte a trous' et autres devraient maintenant fonctionner.")
    else:
        print("\n[OK] Aucune erreur submit_answer trouvee. Les templates sont deja corrects.")
