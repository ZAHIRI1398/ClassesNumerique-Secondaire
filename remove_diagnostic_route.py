#!/usr/bin/env python3
"""
Script pour supprimer complètement la route de diagnostic qui cause des crashs
"""

import os
import re
import sys

def remove_diagnostic_route():
    """Supprime complètement la route de diagnostic problématique"""
    app_path = 'app.py'
    
    # Vérifier que le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: {app_path} n'existe pas!")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la route existe
    if '@app.route(\'/diagnostic-fill-in-blanks\')' not in content:
        print("La route de diagnostic n'existe pas dans le fichier!")
        return True  # Déjà supprimée, c'est bon
    
    # Extraire et supprimer la route
    route_pattern = r'# Route de diagnostic pour fill_in_blanks\s*@app\.route\(\'/diagnostic-fill-in-blanks\'\)(.*?)def diagnostic_fill_in_blanks\(\):(.*?)return .*?results\)'
    
    # Chercher la route avec une expression régulière plus flexible
    route_match = re.search(r'# Route de diagnostic pour fill_in_blanks.*?@app\.route.*?diagnostic-fill-in-blanks.*?return.*?results\)', content, re.DOTALL)
    
    if not route_match:
        print("Impossible de trouver la route de diagnostic avec l'expression régulière!")
        
        # Approche alternative: rechercher et supprimer ligne par ligne
        lines = content.split('\n')
        start_index = -1
        end_index = -1
        
        for i, line in enumerate(lines):
            if '# Route de diagnostic pour fill_in_blanks' in line:
                start_index = i
            elif start_index != -1 and 'return' in line and 'results' in line and ')' in line:
                end_index = i
                break
        
        if start_index != -1 and end_index != -1:
            print(f"Route trouvée entre les lignes {start_index+1} et {end_index+1}")
            new_lines = lines[:start_index] + lines[end_index+1:]
            modified_content = '\n'.join(new_lines)
            
            # Écrire le contenu modifié
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"Route de diagnostic supprimée avec succès de {app_path}!")
            return True
        else:
            print("Impossible de trouver la route de diagnostic même avec l'approche ligne par ligne!")
            return False
    
    # Supprimer la route
    modified_content = re.sub(route_pattern, '', content, flags=re.DOTALL)
    
    # Si la regex n'a pas fonctionné, essayer une approche plus simple
    if '@app.route(\'/diagnostic-fill-in-blanks\')' in modified_content:
        print("La regex n'a pas fonctionné, essai avec une approche plus simple...")
        
        # Supprimer tout le bloc entre les commentaires
        start_marker = '# Route de diagnostic pour fill_in_blanks'
        end_marker = '# Configuration du logging'
        
        start_pos = modified_content.find(start_marker)
        end_pos = modified_content.find(end_marker, start_pos)
        
        if start_pos != -1 and end_pos != -1:
            modified_content = modified_content[:start_pos] + modified_content[end_pos:]
            print("Route supprimée avec l'approche des marqueurs!")
        else:
            print("Impossible de trouver les marqueurs de début et de fin!")
            return False
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"Route de diagnostic supprimée avec succès de {app_path}!")
    return True

if __name__ == '__main__':
    remove_diagnostic_route()
