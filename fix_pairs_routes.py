"""
Routes à ajouter à app.py pour corriger les problèmes d'images dans les exercices de type 'pairs'
"""

# Routes à ajouter à app.py
@app.route('/admin/fix-pairs-images', methods=['GET'])
@login_required
@admin_required
def fix_pairs_images():
    """Route pour corriger automatiquement tous les chemins d'images dans les exercices de type 'pairs'"""
    from fix_pairs_exercise_images import fix_all_pairs_exercises
    
    try:
        successful_fixes, failed_fixes = fix_all_pairs_exercises()
        app.logger.info(f"Correction des images terminée. Réussites: {successful_fixes}, Échecs: {failed_fixes}")
        flash(f'Correction des images terminée. Réussites: {successful_fixes}, Échecs: {failed_fixes}', 'success')
    except Exception as e:
        app.logger.error(f"Erreur lors de la correction des images: {str(e)}")
        flash(f'Erreur lors de la correction des images: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/fix-pairs-image/<int:exercise_id>', methods=['GET'])
@login_required
@admin_required
def fix_specific_pairs_image(exercise_id):
    """Route pour corriger les chemins d'images d'un exercice spécifique de type 'pairs'"""
    from fix_pairs_exercise_images import fix_specific_exercise
    
    try:
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            flash(f'Exercice {exercise_id} non trouvé', 'warning')
            return redirect(url_for('admin_dashboard'))
            
        if exercise.type != 'pairs':
            flash(f'L\'exercice {exercise_id} n\'est pas de type "pairs" (type: {exercise.type})', 'warning')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
        success = fix_specific_exercise(exercise_id)
        if success:
            app.logger.info(f"Correction des images de l'exercice {exercise_id} réussie")
            flash(f'Correction des images de l\'exercice {exercise_id} réussie', 'success')
        else:
            app.logger.warning(f"Échec de la correction des images de l'exercice {exercise_id}")
            flash(f'Échec de la correction des images de l\'exercice {exercise_id}', 'warning')
    except Exception as e:
        app.logger.error(f"Erreur lors de la correction des images de l'exercice {exercise_id}: {str(e)}")
        flash(f'Erreur lors de la correction des images: {str(e)}', 'danger')
    
    return redirect(url_for('view_exercise', exercise_id=exercise_id))
