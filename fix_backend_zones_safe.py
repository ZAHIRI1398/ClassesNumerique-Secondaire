#!/usr/bin/env python3
"""
Script de correction pour la logique backend de parsing des zones.
Version sans emojis Unicode pour compatibilité Windows.

PROBLEME IDENTIFIE :
- La logique backend utilise une boucle while consecutive qui s'arrete au premier "trou"
- Si zone_6_x existe mais pas zone_5_x, la boucle s'arrete avant d'atteindre zone_6
- Resultat : les nouvelles zones ajoutees ne sont pas sauvegardees

SOLUTION :
- Remplacer la boucle while par un scan de TOUS les champs zone_* possibles
- Traiter toutes les zones trouvees, meme si la numerotation n'est pas consecutive
"""

import re

def fix_backend_zone_parsing():
    """Corrige la logique de parsing des zones dans modified_submit.py"""
    
    file_path = "modified_submit.py"
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher la section problematique avec une approche plus simple
    old_section = """zone_index = 1  # Commencer à 1 pour s'aligner avec le frontend
                while f'zone_{zone_index}_x' in request.form:"""
    
    # Nouvelle logique corrigee
    new_section = """# CORRECTION CRITIQUE : Scanner TOUS les champs zone_* possibles
                # au lieu d'utiliser une boucle while consecutive qui s'arrete au premier trou
                zone_fields = [key for key in request.form.keys() if key.startswith('zone_') and key.endswith('_x')]
                zone_indices = [int(key.split('_')[1]) for key in zone_fields]
                
                print(f"[LEGEND_EDIT_DEBUG] Zone fields found: {zone_fields}")
                print(f"[LEGEND_EDIT_DEBUG] Zone indices: {sorted(zone_indices)}")
                
                for zone_index in sorted(zone_indices):"""
    
    # Vérifier si le pattern existe
    if old_section in content:
        print("OK - Pattern de la boucle while problematique trouve !")
        
        # Appliquer la correction
        content = content.replace(old_section, new_section)
        
        # Aussi corriger la ligne d'increment qui n'est plus necessaire
        content = content.replace("zone_index += 1", "pass  # Plus besoin d'increment avec la nouvelle logique")
        
        # Sauvegarder le fichier corrigé
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("CORRECTION APPLIQUEE AVEC SUCCES !")
        print("Changements effectues :")
        print("   - Remplacement de la boucle while consecutive")
        print("   - Ajout du scan de TOUS les champs zone_*")
        print("   - Traitement de toutes les zones trouvees")
        print("   - Ajout de logs de diagnostic detailles")
        print()
        print("REDEMARREZ FLASK pour appliquer les changements")
        print("TESTEZ l'ajout d'une nouvelle zone pour valider la correction")
        
    else:
        print("ERREUR - Pattern de la boucle while non trouve")
        print("Contenu autour de 'zone_index' :")
        
        # Rechercher des patterns similaires
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'zone_index' in line:
                start = max(0, i-2)
                end = min(len(lines), i+3)
                print(f"Lignes {start}-{end}:")
                for j in range(start, end):
                    marker = " >>> " if j == i else "     "
                    print(f"{marker}{j}: {lines[j]}")
                print()

if __name__ == "__main__":
    print("CORRECTION DE LA LOGIQUE BACKEND DE PARSING DES ZONES")
    print("=" * 60)
    fix_backend_zone_parsing()
