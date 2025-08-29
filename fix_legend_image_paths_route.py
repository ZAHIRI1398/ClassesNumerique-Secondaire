"""
Route Flask pour corriger les chemins d'images dans les exercices de type légende.
À intégrer dans app.py.
"""

@app.route('/fix-legend-image-paths', methods=['GET', 'POST'])
@login_required
def fix_legend_image_paths_route():
    # Vérifier que l'utilisateur est administrateur
    if not current_user.is_admin:
        flash("Accès non autorisé. Seuls les administrateurs peuvent accéder à cette page.", "error")
        return redirect(url_for('index'))
    
    # Initialiser les variables
    fixed_exercises = []
    error_message = None
    
    # Traitement de la requête POST (bouton de correction)
    if request.method == 'POST':
        try:
            # Créer un backup de la base de données
            from datetime import datetime
            import shutil
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f'backup_legend_fix_{timestamp}.db'
            try:
                shutil.copy2('instance/app.db', f'instance/{backup_file}')
                current_app.logger.info(f"Backup de la base de données créé: instance/{backup_file}")
            except Exception as e:
                current_app.logger.error(f"Erreur lors de la création du backup: {str(e)}")
                flash(f"Erreur lors de la création du backup: {str(e)}", "error")
                return redirect(url_for('fix_legend_image_paths_route'))
            
            # Récupérer tous les exercices de type légende
            legend_exercises = Exercise.query.filter_by(exercise_type='legend').all()
            current_app.logger.info(f"Trouvé {len(legend_exercises)} exercices de type légende")
            
            # S'assurer que les répertoires nécessaires existent
            import os
            os.makedirs('static/uploads', exist_ok=True)
            os.makedirs('static/uploads/legend', exist_ok=True)
            
            # Fonction pour normaliser les chemins
            def normalize_path(path):
                if not path:
                    return None
                
                # Nettoyer les chemins
                path = path.replace('\\', '/')
                
                # Extraire le nom du fichier
                filename = os.path.basename(path)
                
                # Construire le chemin normalisé
                if 'legend' in path.lower():
                    normalized_path = f"/static/uploads/legend/{filename}"
                else:
                    normalized_path = f"/static/uploads/{filename}"
                
                return normalized_path
            
            # Fonction pour copier l'image si nécessaire
            def copy_image_if_needed(old_path, new_path):
                # Convertir les chemins web en chemins locaux
                if old_path and old_path.startswith('/static/'):
                    old_local_path = old_path[8:]  # Enlever '/static/'
                else:
                    old_local_path = old_path
                
                if new_path and new_path.startswith('/static/'):
                    new_local_path = new_path[8:]  # Enlever '/static/'
                else:
                    new_local_path = new_path
                
                # Chemins complets
                old_full_path = os.path.join('static', old_local_path)
                new_full_path = os.path.join('static', new_local_path)
                
                # Vérifier si l'ancienne image existe
                if os.path.isfile(old_full_path):
                    # S'assurer que le répertoire de destination existe
                    os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                    
                    # Copier l'image si elle n'existe pas déjà à la destination
                    if not os.path.isfile(new_full_path):
                        shutil.copy2(old_full_path, new_full_path)
                        current_app.logger.info(f"Image copiée de {old_full_path} vers {new_full_path}")
                    return True
                else:
                    current_app.logger.warning(f"Image source non trouvée: {old_full_path}")
                    return False
            
            # Corriger les chemins d'images
            fixed_count = 0
            for exercise in legend_exercises:
                current_app.logger.info(f"Traitement de l'exercice #{exercise.id}: {exercise.title}")
                
                content = exercise.get_content()
                main_image = content.get('main_image')
                image_path = exercise.image_path
                
                # Stocker l'état initial pour le rapport
                initial_state = {
                    'id': exercise.id,
                    'title': exercise.title,
                    'main_image': main_image,
                    'image_path': image_path
                }
                
                # Cas 1: Aucune image définie
                if not main_image and not image_path:
                    initial_state['status'] = 'ignored'
                    initial_state['message'] = 'Aucune image définie'
                    fixed_exercises.append(initial_state)
                    continue
                
                # Cas 2: Seulement main_image est défini
                if main_image and not image_path:
                    normalized_path = normalize_path(main_image)
                    exercise.image_path = normalized_path
                    content['main_image'] = normalized_path
                    exercise.content = json.dumps(content)
                    
                    initial_state['status'] = 'fixed'
                    initial_state['message'] = f"image_path défini à partir de main_image: {normalized_path}"
                    initial_state['new_path'] = normalized_path
                    fixed_exercises.append(initial_state)
                    fixed_count += 1
                
                # Cas 3: Seulement image_path est défini
                elif not main_image and image_path:
                    normalized_path = normalize_path(image_path)
                    exercise.image_path = normalized_path
                    content['main_image'] = normalized_path
                    exercise.content = json.dumps(content)
                    
                    initial_state['status'] = 'fixed'
                    initial_state['message'] = f"main_image défini à partir de image_path: {normalized_path}"
                    initial_state['new_path'] = normalized_path
                    fixed_exercises.append(initial_state)
                    fixed_count += 1
                
                # Cas 4: Les deux sont définis mais différents
                elif main_image != image_path:
                    # Préférer main_image car c'est celui utilisé dans le template
                    normalized_path = normalize_path(main_image)
                    
                    # Copier l'image si nécessaire
                    if image_path and main_image:
                        copy_image_if_needed(image_path, normalized_path)
                    
                    exercise.image_path = normalized_path
                    content['main_image'] = normalized_path
                    exercise.content = json.dumps(content)
                    
                    initial_state['status'] = 'fixed'
                    initial_state['message'] = f"Synchronisation des chemins: {normalized_path}"
                    initial_state['new_path'] = normalized_path
                    fixed_exercises.append(initial_state)
                    fixed_count += 1
                
                # Cas 5: Les deux sont définis et identiques mais pas au format normalisé
                elif main_image == image_path:
                    normalized_path = normalize_path(main_image)
                    if normalized_path != main_image:
                        exercise.image_path = normalized_path
                        content['main_image'] = normalized_path
                        exercise.content = json.dumps(content)
                        
                        initial_state['status'] = 'fixed'
                        initial_state['message'] = f"Normalisation des chemins: {normalized_path}"
                        initial_state['new_path'] = normalized_path
                        fixed_exercises.append(initial_state)
                        fixed_count += 1
                    else:
                        initial_state['status'] = 'ok'
                        initial_state['message'] = "Chemin déjà normalisé"
                        fixed_exercises.append(initial_state)
            
            # Sauvegarder les modifications
            if fixed_count > 0:
                try:
                    db.session.commit()
                    flash(f"Correction terminée: {fixed_count} exercices corrigés", "success")
                    current_app.logger.info(f"Modifications sauvegardées en base de données: {fixed_count} exercices corrigés")
                except Exception as e:
                    db.session.rollback()
                    error_message = f"Erreur lors de la sauvegarde: {str(e)}"
                    flash(error_message, "error")
                    current_app.logger.error(error_message)
            else:
                flash("Aucune correction nécessaire", "info")
                current_app.logger.info("Aucune correction nécessaire")
        
        except Exception as e:
            error_message = f"Erreur lors de la correction: {str(e)}"
            flash(error_message, "error")
            current_app.logger.error(error_message)
    
    # Affichage de la page (GET ou après traitement POST)
    legend_exercises = Exercise.query.filter_by(exercise_type='legend').all()
    
    # Analyser l'état actuel des exercices
    exercises_status = []
    for exercise in legend_exercises:
        content = exercise.get_content()
        main_image = content.get('main_image')
        image_path = exercise.image_path
        
        status = {
            'id': exercise.id,
            'title': exercise.title,
            'main_image': main_image,
            'image_path': image_path
        }
        
        if not main_image and not image_path:
            status['status'] = 'error'
            status['message'] = 'Aucune image définie'
        elif main_image and not image_path:
            status['status'] = 'warning'
            status['message'] = 'image_path manquant'
        elif not main_image and image_path:
            status['status'] = 'warning'
            status['message'] = 'main_image manquant'
        elif main_image != image_path:
            status['status'] = 'warning'
            status['message'] = 'Chemins incohérents'
        else:
            # Vérifier si le chemin est normalisé
            if main_image.startswith('/static/uploads/'):
                status['status'] = 'ok'
                status['message'] = 'Chemin correct'
            else:
                status['status'] = 'warning'
                status['message'] = 'Chemin non normalisé'
        
        exercises_status.append(status)
    
    return render_template(
        'admin/fix_legend_image_paths.html',
        exercises_status=exercises_status,
        fixed_exercises=fixed_exercises,
        error_message=error_message
    )
