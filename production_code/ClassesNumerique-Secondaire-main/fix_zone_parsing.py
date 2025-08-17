#!/usr/bin/env python3
"""
Script de correction pour le problème de parsing des zones dans les exercices légende.

PROBLÈME IDENTIFIÉ :
- Frontend envoie : zone_1_x, zone_2_x, zone_3_x...
- Backend cherche : zone_0_x, zone_1_x, zone_2_x...
- RÉSULTAT : Aucune correspondance → Erreur "Veuillez ajouter au moins une zone"

SOLUTION :
Modifier la logique backend pour commencer à zone_1_x au lieu de zone_0_x
"""

import re

def fix_zone_parsing():
    """Corrige la logique de parsing des zones dans modified_submit.py"""
    
    file_path = "modified_submit.py"
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher et remplacer la ligne problématique
    old_pattern = r'zone_index = 0'
    new_replacement = 'zone_index = 1  # Commencer à 1 pour s\'aligner avec le frontend'
    
    # Vérifier si le pattern existe
    if old_pattern in content:
        print(f"Pattern trouvé : {old_pattern}")
        
        # Appliquer la correction
        content = content.replace(old_pattern, new_replacement)
        
        # Ajouter des logs de debug
        debug_pattern = r'while f\'zone_{zone_index}_x\' in request\.form:'
        debug_replacement = '''print(f"[LEGEND_EDIT_DEBUG] Starting zone parsing from zone_{zone_index}_x...")
                while f'zone_{zone_index}_x' in request.form:'''
        
        content = content.replace(debug_pattern, debug_replacement)
        
        # Sauvegarder le fichier corrigé
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Correction appliquée avec succès !")
        print("Changements effectués :")
        print(f"   - zone_index = 0 -> zone_index = 1")
        print(f"   - Ajout de logs de debug")
        print("Redémarrez Flask pour appliquer les changements")
        
    else:
        print("Pattern non trouvé dans le fichier")
        
        # Rechercher des patterns similaires
        similar_patterns = re.findall(r'zone_index\s*=\s*\d+', content)
        if similar_patterns:
            print("Patterns similaires trouvés :")
            for pattern in similar_patterns:
                print(f"   - {pattern}")
        else:
            print("Aucun pattern zone_index trouvé")

if __name__ == "__main__":
    print("CORRECTION DU PARSING DES ZONES LEGENDE")
    print("=" * 50)
    fix_zone_parsing()
