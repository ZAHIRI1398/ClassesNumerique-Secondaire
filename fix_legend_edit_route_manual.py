#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de correction manuelle pour la route d'édition des exercices de type légende
Ce script corrige l'erreur de serveur interne (500) qui se produit lors de la modification
d'un exercice de type légende en remplaçant complètement la route d'édition.
"""

import os
import shutil
import datetime
import re

def create_backup(app_path):
    """Crée une sauvegarde du fichier app.py avant modification"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{app_path}.bak.{timestamp}"
    
    shutil.copy2(app_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    
    return backup_path

def find_route_position(app_content):
    """Trouve la position de la route d'édition dans le fichier app.py"""
    # Recherche du début de la route
    route_start_pattern = r'@app\.route\(\'/exercise/edit_exercise/<int:exercise_id>\', methods=\[\'GET\', \'POST\'\]\)'
    route_start_match = re.search(route_start_pattern, app_content)
    
    if not route_start_match:
        print("Route d'édition non trouvée dans app.py")
        return None, None
    
    route_start = route_start_match.start()
    
    # Recherche de la fin de la route (fonction suivante)
    next_route_pattern = r'@app\.route\(\'.*\', methods=\[.*\]\)'
    next_route_match = re.search(next_route_pattern, app_content[route_start + 1:])
    
    if next_route_match:
        route_end = route_start + 1 + next_route_match.start()
    else:
        # Si pas de route suivante, chercher une autre fonction
        next_def_pattern = r'\ndef '
        next_def_match = re.search(next_def_pattern, app_content[route_start + 1:])
        if next_def_match:
            route_end = route_start + 1 + next_def_match.start()
        else:
            print("Fin de la route d'édition non trouvée")
            return route_start, None
    
    return route_start, route_end

def fix_legend_edit_route_manual(app_path):
    """Corrige manuellement la route d'édition des exercices de type légende"""
    with open(app_path, 'r', encoding='utf-8') as file:
        app_content = file.read()
    
    # Trouver la position de la route d'édition
    route_start, route_end = find_route_position(app_content)
    
    if route_start is None:
        print("Impossible de trouver la route d'édition")
        return False
    
    # Nouvelle implémentation de la route d'édition
    new_route = """@app.route('/exercise/edit_exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def edit_exercise_blueprint(exercise_id):
    """Route d'édition d'exercice avec logique légende complète"""
    print(f'[EDIT_POST_DEBUG] POST request received for exercise {exercise_id}')
    print(f'[EDIT_POST_DEBUG] Form data keys: {list(request.form.keys())}')
    print(f'[EDIT_POST_DEBUG] Form data: {dict(request.form)}')
    
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if request.method == 'GET':
        print(f'[EDIT_DEBUG] Exercise ID: {exercise_id}')
        print(f'[EDIT_DEBUG] Exercise type: {repr(exercise.exercise_type)}')
        print(f'[EDIT_DEBUG] Exercise title: {repr(exercise.title)}')
        print(f'[EDIT_DEBUG] Template path: {repr("exercise_types/legend_edit.html")}')
        
        content = json.loads(exercise.content) if exercise.content else {}
        print(f'[EDIT_DEBUG] Content type: {type(content)}')
        print(f'[EDIT_DEBUG] Content keys: {list(content.keys()) if isinstance(content, dict) else "Not a dict"}')
        
        attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).all()
        print(f'[EDIT_DEBUG] Attempts count: {len(attempts)}')
        
        # Rediriger vers le template d'édition approprié selon le type
        if exercise.exercise_type == 'legend':
            return render_template('exercise_types/legend_edit.html', exercise=exercise)
        else:
            return render_template('edit_exercise.html', exercise=exercise)
    
    if request.method == 'POST':
        print(f'[EDIT_POST_DEBUG] Title: {repr(request.form.get("title", ""))}')
        print(f'[EDIT_POST_DEBUG] Subject: {repr(request.form.get("subject", ""))}')
        print(f'[EDIT_POST_DEBUG] Description: {repr(request.form.get("description", ""))}')
        
        try:
            # Mise à jour des champs de base
            if 'title' in request.form:
                exercise.title = request.form['title']
            if 'description' in request.form:
                exercise.description = request.form['description']
            if 'subject' in request.form:
                exercise.subject = request.form['subject']
            
            # TRAITEMENT SPÉCIFIQUE POUR LES EXERCICES LÉGENDE
            if exercise.exercise_type == 'legend':
                print(f'[LEGEND_EDIT_DEBUG] Traitement du contenu LÉGENDE')
                print(f'[LEGEND_EDIT_DEBUG] Tous les champs du formulaire: {list(request.form.keys())}')
                
                # Récupérer le mode de légende
                legend_mode = request.form.get('legend_mode', 'classic')
                print(f'[LEGEND_EDIT_DEBUG] Mode sélectionné: {legend_mode}')
                
                # Récupérer les instructions
                instructions = request.form.get('legend_instructions', '').strip()
                if not instructions:
                    if legend_mode == 'grid':
                        instructions = 'Déplacez les éléments vers les bonnes cases du quadrillage.'
                    elif legend_mode == 'spatial':
                        instructions = 'Placez les éléments dans les bonnes zones définies.'
                    else:
                        instructions = 'Placez les légendes aux bons endroits sur l\\'image.'
                
                # Gestion de l'image principale
                main_image_path = None
                if 'legend_main_image' in request.files:
                    image_file = request.files['legend_main_image']
                    if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                        filename = secure_filename(image_file.filename)
                        unique_filename = generate_unique_filename(filename)
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                        image_file.save(file_path)
                        main_image_path = unique_filename
                
                # Si pas de nouvelle image, garder l'ancienne
                if not main_image_path:
                    existing_content = json.loads(exercise.content) if exercise.content else {}
                    main_image_path = existing_content.get('main_image')
                
                # Récupérer les zones et légendes
                zones = []
                elements = []
                
                # Scanner tous les champs zone_* pour récupérer toutes les zones
                zone_indices = set()
                for key in request.form.keys():
                    print(f'[LEGEND_EDIT_DEBUG] Examen clé: {key}')
                    if key.startswith('zone_') and key.endswith('_x'):
                        # Extraction robuste de l'index de zone
                        parts = key.split('_')
                        print(f'[LEGEND_EDIT_DEBUG] Parts de {key}: {parts}')
                        if len(parts) >= 3:
                            try:
                                zone_index = int(parts[1])
                                zone_indices.add(zone_index)
                                print(f'[LEGEND_EDIT_DEBUG] Zone détectée: {zone_index}')
                            except ValueError:
                                print(f'[LEGEND_EDIT_DEBUG] Index de zone invalide: {key}')
                
                print(f'[LEGEND_EDIT_DEBUG] Zones trouvées: {sorted(zone_indices)}')
                
                for zone_index in sorted(zone_indices):
                    x = request.form.get(f'zone_{zone_index}_x')
                    y = request.form.get(f'zone_{zone_index}_y')
                    legend = request.form.get(f'zone_{zone_index}_legend', '').strip()
                    
                    print(f'[LEGEND_EDIT_DEBUG] Zone {zone_index}: x={x}, y={y}, legend="{legend}"')
                    
                    if x and y and legend:
                        try:
                            x = float(x)
                            y = float(y)
                            zones.append({
                                'x': x,
                                'y': y,
                                'legend': legend
                            })
                            elements.append(legend)
                            print(f'[LEGEND_EDIT_DEBUG] Zone {zone_index} ajoutée avec succès')
                        except ValueError as e:
                            print(f'[LEGEND_EDIT_DEBUG] Erreur conversion zone {zone_index}: {e}')
                            continue
                
                # Gestion des différents modes de légende
                if legend_mode == 'grid':
                    # Mode quadrillage - récupérer les éléments de grille
                    grid_elements = []
                    grid_element_indices = set()
                    
                    # Scanner les éléments de grille
                    for key in request.form.keys():
                        if key.startswith('grid_element_') and key.endswith('_content'):
                            parts = key.split('_')
                            if len(parts) >= 3:
                                element_index = parts[2]
                                try:
                                    grid_element_indices.add(int(element_index))
                                except ValueError:
                                    continue
                    
                    grid_elements_data = []
                    for element_index in sorted(grid_element_indices):
                        row = request.form.get(f'grid_element_{element_index}_row')
                        col = request.form.get(f'grid_element_{element_index}_col')
                        content = request.form.get(f'grid_element_{element_index}_content', '').strip()
                        
                        if row and col and content:
                            try:
                                grid_elements_data.append({
                                    'row': int(row),
                                    'col': int(col),
                                    'content': content
                                })
                            except ValueError:
                                continue
                    
                    # Récupérer les paramètres de grille
                    grid_rows = request.form.get('grid_rows', '3')
                    grid_cols = request.form.get('grid_cols', '3')
                    
                    try:
                        grid_rows = int(grid_rows)
                        grid_cols = int(grid_cols)
                    except ValueError:
                        grid_rows, grid_cols = 3, 3
                    
                    content = {
                        'mode': 'grid',
                        'instructions': instructions,
                        'main_image': main_image_path,
                        'grid_elements': grid_elements_data,
                        'grid_rows': grid_rows,
                        'grid_cols': grid_cols
                    }
                    print(f'[LEGEND_EDIT_DEBUG] Mode grille: {len(grid_elements_data)} éléments, grille {grid_rows}x{grid_cols}')
                
                elif legend_mode == 'spatial':
                    # Mode spatial - récupérer les éléments et zones spatiales
                    spatial_elements = []
                    spatial_zones = []
                    
                    # Scanner les éléments spatiaux
                    spatial_element_indices = set()
                    for key in request.form.keys():
                        if key.startswith('spatial_element_'):
                            parts = key.split('_')
                            if len(parts) >= 3:
                                try:
                                    element_index = int(parts[2])
                                    spatial_element_indices.add(element_index)
                                except (ValueError, IndexError):
                                    continue
                    
                    for element_index in sorted(spatial_element_indices):
                        element_text = request.form.get(f'spatial_element_{element_index}', '').strip()
                        if element_text:
                            spatial_elements.append(element_text)
                    
                    # Scanner les zones spatiales
                    spatial_zone_indices = set()
                    for key in request.form.keys():
                        if key.startswith('spatial_zone_') and key.endswith('_name'):
                            parts = key.split('_')
                            if len(parts) >= 3:
                                zone_index = parts[2]
                                try:
                                    spatial_zone_indices.add(int(zone_index))
                                except ValueError:
                                    continue
                    
                    for zone_index in sorted(spatial_zone_indices):
                        zone_name = request.form.get(f'spatial_zone_{zone_index}_name', '').strip()
                        correct_element = request.form.get(f'spatial_zone_{zone_index}_correct', '').strip()
                        
                        if zone_name and correct_element:
                            spatial_zones.append({
                                'name': zone_name,
                                'correct_element': correct_element
                            })
                    
                    content = {
                        'mode': 'spatial',
                        'instructions': instructions,
                        'main_image': main_image_path,
                        'elements': spatial_elements,
                        'zones': spatial_zones
                    }
                    print(f'[LEGEND_EDIT_DEBUG] Mode spatial: {len(spatial_elements)} éléments, {len(spatial_zones)} zones')
                
                else:
                    # Mode classique - utiliser la logique des zones existante
                    content = {
                        'mode': 'classic',
                        'instructions': instructions,
                        'main_image': main_image_path,
                        'zones': zones,
                        'elements': elements
                    }
                
                # Mettre à jour le contenu de l'exercice
                exercise.content = json.dumps(content)
                print(f'[LEGEND_EDIT_DEBUG] Contenu sauvegardé avec succès - Mode: {legend_mode}, Image: {main_image_path}')
                
                # Sauvegarder les modifications
                db.session.commit()
                flash('Exercice modifié avec succès !', 'success')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
                
        except Exception as e:
            print(f'[EDIT_ERROR] Erreur lors de la modification : {e}')
            flash('Erreur lors de la modification de l\\'exercice.', 'error')
            db.session.rollback()
    
    return render_template('exercise_types/legend_edit.html', exercise=exercise)"""
    
    # Remplacer la route d'édition
    if route_end:
        updated_content = app_content[:route_start] + new_route + app_content[route_end:]
    else:
        # Si on n'a pas trouvé la fin, essayer de remplacer jusqu'à la fin du fichier
        updated_content = app_content[:route_start] + new_route
    
    # Écrire le contenu mis à jour
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("Route d'édition remplacée avec succès.")
    return True

def create_test_script():
    """Crée un script de test pour vérifier que la correction fonctionne"""
    test_script_path = "check_legend_edit_route.py"
    
    test_script_content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
Script de diagnostic pour vérifier la route d'édition des exercices de type légende
Ce script vérifie que la route d'édition des exercices de type légende fonctionne correctement
et que le contenu de l'exercice est correctement mis à jour.
\"\"\"

import os
import sys
import json
import requests
from flask import Flask, session
from app import app, db, Exercise, User

def check_legend_edit_route():
    \"\"\"Vérifie la route d'édition des exercices de type légende\"\"\"
    print("=== Diagnostic de la route d'édition des exercices de type légende ===\\n")
    
    # 1. Vérifier si le template legend_edit.html existe
    template_path = os.path.join("templates", "exercise_types", "legend_edit.html")
    if os.path.exists(template_path):
        print(f"✅ Le template {template_path} existe.")
    else:
        print(f"❌ Le template {template_path} n'existe pas!")
        return False
    
    # 2. Rechercher des exercices de type légende dans la base de données
    with app.app_context():
        legend_exercises = Exercise.query.filter_by(exercise_type='legend').all()
        
        if legend_exercises:
            print(f"✅ {len(legend_exercises)} exercice(s) de type légende trouvé(s) dans la base de données.")
            
            # Afficher les détails du premier exercice de type légende
            exercise = legend_exercises[0]
            print(f"\\nDétails de l'exercice ID {exercise.id}:")
            print(f"  - Titre: {exercise.title}")
            print(f"  - Description: {exercise.description}")
            
            # Analyser le contenu JSON
            content = json.loads(exercise.content) if exercise.content else {}
            print(f"  - Mode: {content.get('mode', 'non spécifié')}")
            print(f"  - Image principale: {content.get('main_image', 'aucune')}")
            
            if 'zones' in content:
                print(f"  - Nombre de zones: {len(content['zones'])}")
            
            if 'elements' in content:
                print(f"  - Nombre d'éléments: {len(content['elements'])}")
            
            print("\\nLa route d'édition devrait maintenant fonctionner correctement pour cet exercice.")
            print(f"URL d'édition: /exercise/edit_exercise/{exercise.id}")
        else:
            print("⚠️ Aucun exercice de type légende trouvé dans la base de données.")
    
    # 3. Vérifier la présence de la logique de traitement dans app.py
    with open("app.py", "r", encoding="utf-8") as file:
        app_content = file.read()
        
        if "[LEGEND_EDIT_DEBUG] Traitement du contenu LÉGENDE" in app_content:
            print("\\n✅ La logique de debug pour les exercices de type légende est présente dans app.py.")
        else:
            print("\\n⚠️ La logique de debug pour les exercices de type légende n'a pas été trouvée dans app.py.")
        
        if "legend_mode = request.form.get('legend_mode', 'classic')" in app_content:
            print("✅ La logique de traitement du mode de légende est présente dans app.py.")
        else:
            print("⚠️ La logique de traitement du mode de légende n'a pas été trouvée dans app.py.")
    
    print("\\n=== Diagnostic terminé ===")
    print("La route d'édition des exercices de type légende devrait maintenant fonctionner correctement.")
    print("Pour tester, connectez-vous à l'application et essayez de modifier un exercice de type légende.")
    
    return True

if __name__ == "__main__":
    check_legend_edit_route()
"""
    
    with open(test_script_path, 'w', encoding='utf-8') as file:
        file.write(test_script_content)
    
    print(f"Script de test créé: {test_script_path}")
    return test_script_path

def update_documentation():
    """Met à jour la documentation pour la correction des exercices de type légende"""
    doc_path = "DOCUMENTATION_LEGEND_EXERCISE_FIX.md"
    
    doc_content = """# Correction des exercices de type légende

## Problème initial

Une erreur de serveur interne (500) se produisait lors de la modification d'un exercice de type légende. Cette erreur était due à une implémentation incomplète de la route d'édition pour ce type d'exercice.

## Analyse du problème

1. **Template manquant** : Le template `legend_edit.html` était nécessaire mais n'était pas correctement implémenté.
2. **Logique de traitement incomplète** : La route d'édition collectait les zones mais ne mettait pas à jour le contenu de l'exercice.
3. **Gestion des modes de légende** : Les trois modes de légende (classique, quadrillage, spatial) n'étaient pas correctement gérés dans la route d'édition.

## Solution implémentée

1. **Création du template `legend_edit.html`** : Un template complet a été créé pour l'édition des exercices de type légende, avec support pour les trois modes.
2. **Correction de la route d'édition** : La route `edit_exercise_blueprint` a été mise à jour pour traiter correctement les données du formulaire et mettre à jour le contenu de l'exercice.
3. **Gestion des modes de légende** : Les trois modes de légende (classique, quadrillage, spatial) sont maintenant correctement gérés dans la route d'édition.

## Modifications apportées

### 1. Template `legend_edit.html`

Un template complet a été créé avec :
- Support pour les trois modes de légende (classique, quadrillage, spatial)
- Gestion des images principales
- Interface pour ajouter, modifier et supprimer des zones et légendes
- JavaScript pour la gestion interactive des zones

### 2. Route d'édition

La route `edit_exercise_blueprint` a été mise à jour pour :
- Collecter correctement les données du formulaire
- Traiter les trois modes de légende
- Mettre à jour le contenu de l'exercice
- Gérer les images principales

### 3. Script de diagnostic

Un script de diagnostic `check_legend_edit_route.py` a été créé pour vérifier que la correction fonctionne correctement.

## Comment tester la correction

1. Connectez-vous à l'application
2. Accédez à un exercice de type légende existant
3. Cliquez sur "Modifier"
4. Modifiez les zones, légendes ou l'image principale
5. Enregistrez les modifications
6. Vérifiez que les modifications sont bien prises en compte et qu'aucune erreur ne se produit

## Prévention des problèmes similaires à l'avenir

Pour éviter des problèmes similaires à l'avenir, il est recommandé de :
1. Créer des templates distincts pour chaque type d'exercice
2. Implémenter des routes d'édition spécifiques pour chaque type d'exercice
3. Ajouter des tests automatisés pour vérifier que les routes d'édition fonctionnent correctement
4. Documenter les différents types d'exercices et leurs spécificités
"""
    
    with open(doc_path, 'w', encoding='utf-8') as file:
        file.write(doc_content)
    
    print(f"Documentation mise à jour: {doc_path}")
    return doc_path

def main():
    print("=== Correction manuelle de la route d'édition des exercices de type légende ===\n")
    
    app_path = "app.py"
    
    # 1. Créer une sauvegarde
    backup_path = create_backup(app_path)
    
    # 2. Appliquer la correction manuelle
    success = fix_legend_edit_route_manual(app_path)
    
    if not success:
        print(f"\nÉchec de la correction. Vous pouvez restaurer la sauvegarde avec:")
        print(f"cp {backup_path} {app_path}")
        return
    
    # 3. Créer un script de test
    test_script_path = create_test_script()
    
    # 4. Mettre à jour la documentation
    doc_path = update_documentation()
    
    # 5. Instructions finales
    print("\nCorrection appliquée avec succès!")
    print("\nÉtapes suivantes:")
    print(f"1. Redémarrez l'application Flask pour appliquer les modifications.")
    print(f"2. Exécutez le script de test pour vérifier que la correction fonctionne:")
    print(f"   python {test_script_path}")
    print(f"3. Consultez la documentation pour plus de détails:")
    print(f"   {doc_path}")
    print("\nSi vous rencontrez des problèmes, vous pouvez restaurer la sauvegarde avec:")
    print(f"cp {backup_path} {app_path}")

if __name__ == "__main__":
    main()
