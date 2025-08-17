#!/usr/bin/env python3
"""
Script de correction pour la logique backend de parsing des zones.

PROBLÈME IDENTIFIÉ :
- La logique backend utilise une boucle while consécutive qui s'arrête au premier "trou"
- Si zone_6_x existe mais pas zone_5_x, la boucle s'arrête avant d'atteindre zone_6
- Résultat : les nouvelles zones ajoutées ne sont pas sauvegardées

SOLUTION :
- Remplacer la boucle while par un scan de TOUS les champs zone_* possibles
- Traiter toutes les zones trouvées, même si la numérotation n'est pas consécutive
"""

import re

def fix_backend_zone_parsing():
    """Corrige la logique de parsing des zones dans modified_submit.py"""
    
    file_path = "modified_submit.py"
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher la logique de parsing des zones (boucle while problématique)
    old_pattern = r"""                # Récupérer les zones et légendes
                zones = \[\]
                zone_index = 1  # Commencer à 1 pour s'aligner avec le frontend
                while f'zone_\{zone_index\}_x' in request\.form:
                    x = request\.form\.get\(f'zone_\{zone_index\}_x', type=int\)
                    y = request\.form\.get\(f'zone_\{zone_index\}_y', type=int\)
                    legend_text = request\.form\.get\(f'zone_\{zone_index\}_legend', ''\)\.strip\(\)
                    
                    if x is not None and y is not None and legend_text:
                        zones\.append\(\{
                            'x': x,
                            'y': y,
                            'legend': legend_text,
                            'id': zone_index
                        \}\)
                    
                    zone_index \+= 1"""
    
    # Nouvelle logique corrigée
    new_logic = """                # Récupérer les zones et légendes
                zones = []
                
                # CORRECTION CRITIQUE : Scanner TOUS les champs zone_* possibles
                # au lieu d'utiliser une boucle while consécutive qui s'arrête au premier trou
                zone_fields = [key for key in request.form.keys() if key.startswith('zone_') and key.endswith('_x')]
                zone_indices = [int(key.split('_')[1]) for key in zone_fields]
                
                print(f"[LEGEND_EDIT_DEBUG] Zone fields found: {zone_fields}")
                print(f"[LEGEND_EDIT_DEBUG] Zone indices: {sorted(zone_indices)}")
                
                for zone_index in sorted(zone_indices):
                    x = request.form.get(f'zone_{zone_index}_x', type=int)
                    y = request.form.get(f'zone_{zone_index}_y', type=int)
                    legend_text = request.form.get(f'zone_{zone_index}_legend', '').strip()
                    
                    print(f"[LEGEND_EDIT_DEBUG] Processing zone {zone_index}: x={x}, y={y}, legend='{legend_text}'")
                    
                    if x is not None and y is not None and legend_text:
                        zones.append({
                            'x': x,
                            'y': y,
                            'legend': legend_text,
                            'id': zone_index
                        })
                        print(f"[LEGEND_EDIT_DEBUG] Zone {zone_index} added successfully")
                    else:
                        print(f"[LEGEND_EDIT_DEBUG] Zone {zone_index} skipped (incomplete data)")"""
    
    # Vérifier si le pattern existe
    if re.search(old_pattern, content, re.MULTILINE):
        print("✅ Pattern de la boucle while problématique trouvé !")
        
        # Appliquer la correction
        content = re.sub(old_pattern, new_logic, content, flags=re.MULTILINE)
        
        # Sauvegarder le fichier corrigé
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("🚀 CORRECTION APPLIQUÉE AVEC SUCCÈS !")
        print("Changements effectués :")
        print("   ✅ Remplacement de la boucle while consécutive")
        print("   ✅ Ajout du scan de TOUS les champs zone_*")
        print("   ✅ Traitement de toutes les zones trouvées")
        print("   ✅ Ajout de logs de diagnostic détaillés")
        print()
        print("🔧 REDÉMARREZ FLASK pour appliquer les changements")
        print("🎯 TESTEZ l'ajout d'une nouvelle zone pour valider la correction")
        
    else:
        print("❌ Pattern de la boucle while non trouvé")
        print("Recherche de patterns alternatifs...")
        
        # Rechercher des patterns similaires
        zone_patterns = re.findall(r'zone_index.*?while.*?zone_.*?request\.form', content, re.DOTALL)
        if zone_patterns:
            print("Patterns de zones trouvés :")
            for i, pattern in enumerate(zone_patterns[:3]):  # Limiter à 3
                print(f"   {i+1}. {pattern[:100]}...")
        else:
            print("Aucun pattern de zone trouvé dans le fichier")

if __name__ == "__main__":
    print("CORRECTION DE LA LOGIQUE BACKEND DE PARSING DES ZONES")
    print("=" * 60)
    fix_backend_zone_parsing()
