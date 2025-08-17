#!/usr/bin/env python3
"""
Script pour localiser précisément les problèmes de qualité dans les templates
"""

import os
import re

def find_issues_in_file(file_path, patterns):
    """Trouve les problèmes dans un fichier spécifique"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                if pattern.lower() in line.lower():
                    issues.append({
                        'line': line_num,
                        'content': line.strip(),
                        'pattern': pattern
                    })
    
    except Exception as e:
        print(f"Erreur lors de la lecture de {file_path}: {e}")
    
    return issues

def main():
    print("=== LOCALISATION PRECISE DES PROBLEMES DE QUALITE ===")
    print()
    
    templates_dir = "templates/exercise_types"
    
    # Templates à vérifier selon l'audit
    problematic_templates = [
        'fill_in_blanks.html',
        'word_search.html', 
        'pairs.html',
        'drag_and_drop.html'
    ]
    
    # Patterns à rechercher
    patterns = [
        'console.log',
        'BUG',
        'TODO',
        'FIXME'
    ]
    
    total_issues = 0
    
    for template in problematic_templates:
        template_path = os.path.join(templates_dir, template)
        
        if not os.path.exists(template_path):
            print(f"[MANQUANT] {template}")
            continue
        
        print(f"=== ANALYSE DE {template} ===")
        issues = find_issues_in_file(template_path, patterns)
        
        if issues:
            for issue in issues:
                print(f"  Ligne {issue['line']}: {issue['pattern']} -> {issue['content'][:100]}...")
                total_issues += 1
        else:
            print(f"  [PROPRE] Aucun problème détecté")
        
        print()
    
    print(f"=== RESUME ===")
    print(f"Total des problèmes trouvés: {total_issues}")
    
    if total_issues == 0:
        print("Tous les templates semblent propres!")
        print("L'audit peut avoir des faux positifs ou chercher dans d'autres fichiers.")

if __name__ == '__main__':
    main()
