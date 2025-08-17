#!/usr/bin/env python3
"""
Script de correction automatique des erreurs de routage
Remplace tous les url_for('exercise.XXX') par url_for('XXX') dans les templates
"""

import os
import re
import glob

def fix_routing_errors():
    """Corrige toutes les erreurs de routage dans les templates"""
    
    # Répertoire des templates
    templates_dir = "templates"
    
    # Patterns de remplacement
    replacements = {
        # Erreurs de routage les plus communes
        r"url_for\('exercise\.exercise_library'\)": "url_for('exercise_library')",
        r"url_for\('exercise\.edit_exercise'": "url_for('edit_exercise'",
        r"url_for\('exercise\.create_exercise'": "url_for('create_exercise'",
        r"url_for\('exercise\.delete_exercise'": "url_for('delete_exercise'",
        r"url_for\('exercise\.submit_answer'": "url_for('submit_answer'",
        r"url_for\('exercise\.exercise_stats'": "url_for('exercise_stats'",
        r"url_for\('exercise\.preview_exercise'": "url_for('preview_exercise'",
    }
    
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
                    file_replacements = 0
                    
                    # Appliquer tous les remplacements
                    for pattern, replacement in replacements.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            content = re.sub(pattern, replacement, content)
                            file_replacements += len(matches)
                    
                    # Sauvegarder si des changements ont été faits
                    if content != original_content:
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
    print("[START] DEMARRAGE DE LA CORRECTION AUTOMATIQUE DES ERREURS DE ROUTAGE...")
    print("=" * 60)
    
    files_processed, total_replacements = fix_routing_errors()
    
    if total_replacements > 0:
        print(f"\n[SUCCESS] {total_replacements} erreurs de routage corrigees dans {files_processed} fichiers.")
        print("[INFO] L'application Flask devrait maintenant fonctionner sans erreurs de routage.")
    else:
        print("\n[OK] Aucune erreur de routage trouvee. Les templates sont deja corrects.")
