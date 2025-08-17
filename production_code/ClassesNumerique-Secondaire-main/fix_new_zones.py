#!/usr/bin/env python3
"""
Script de correction pour ajouter la logique de traitement des nouvelles zones manuelles.

PROBLÈME IDENTIFIÉ :
- Le backend traite les zones existantes (zone_1_x, zone_2_x, etc.)
- Mais il ignore les nouvelles zones ajoutées manuellement (new_zone_x, new_zone_y, new_zone_legend)
- Résultat : les nouvelles zones ne sont pas sauvegardées

SOLUTION :
Ajouter la logique pour traiter les champs new_zone_* après la boucle des zones existantes
"""

import re

def fix_new_zone_handling():
    """Ajoute la logique pour traiter les nouvelles zones manuelles"""
    
    file_path = "modified_submit.py"
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher le point d'insertion (après la boucle des zones)
    insertion_pattern = r'print\(f"\[LEGEND_EDIT_DEBUG\] Total zones found: \{len\(zones\)\}"\)\s*\n\s*if not zones:'
    
    # Code à insérer
    new_code = '''print(f"[LEGEND_EDIT_DEBUG] Total zones found: {len(zones)}")
                
                # Traiter les nouvelles zones ajoutées manuellement
                new_x = request.form.get('new_zone_x', type=int)
                new_y = request.form.get('new_zone_y', type=int)
                new_legend = request.form.get('new_zone_legend', '').strip()
                
                if new_x is not None and new_y is not None and new_legend:
                    print(f"[LEGEND_EDIT_DEBUG] Processing manual new zone: x={new_x}, y={new_y}, legend='{new_legend}'")
                    zones.append({
                        'x': new_x,
                        'y': new_y,
                        'legend': new_legend,
                        'id': len(zones)  # Utiliser l'index suivant
                    })
                    print(f"[LEGEND_EDIT_DEBUG] Manual zone added successfully. Total zones now: {len(zones)}")
                else:
                    print(f"[LEGEND_EDIT_DEBUG] No valid manual zone to add (x={new_x}, y={new_y}, legend='{new_legend}')")
                
                if not zones:'''
    
    # Vérifier si le pattern existe
    if re.search(insertion_pattern, content):
        print("Pattern d'insertion trouvé !")
        
        # Appliquer la correction
        content = re.sub(insertion_pattern, new_code, content)
        
        # Sauvegarder le fichier corrigé
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Correction appliquée avec succès !")
        print("Changements effectués :")
        print("   - Ajout de la logique pour traiter new_zone_x, new_zone_y, new_zone_legend")
        print("   - Ajout de logs de debug pour les nouvelles zones manuelles")
        print("Redémarrez Flask pour appliquer les changements")
        
    else:
        print("Pattern d'insertion non trouvé dans le fichier")
        
        # Rechercher des patterns similaires pour diagnostic
        debug_patterns = re.findall(r'print\(f"\[LEGEND_EDIT_DEBUG\].*?\)', content)
        if debug_patterns:
            print("Patterns de debug trouvés :")
            for i, pattern in enumerate(debug_patterns[:5]):  # Limiter à 5
                print(f"   {i+1}. {pattern}")
        
        # Rechercher la section légende
        legend_section = re.search(r'elif exercise\.exercise_type == \'legend\':', content)
        if legend_section:
            print("Section légende trouvée à la position:", legend_section.start())
        else:
            print("Section légende non trouvée")

if __name__ == "__main__":
    print("CORRECTION DU TRAITEMENT DES NOUVELLES ZONES")
    print("=" * 50)
    fix_new_zone_handling()
