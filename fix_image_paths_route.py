from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from models import db, Exercise
from utils.image_path_synchronizer import synchronize_all_exercises
from functools import wraps
from flask_login import current_user

# Créer un blueprint pour la route de correction des chemins d'images
fix_image_paths_bp = Blueprint('fix_image_paths', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès réservé aux administrateurs.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@fix_image_paths_bp.route('/fix-image-paths')
@admin_required
def fix_image_paths():
    """
    Route pour corriger et synchroniser tous les chemins d'images des exercices.
    Accessible uniquement aux administrateurs.
    """
    try:
        # Synchroniser tous les chemins d'images
        stats = synchronize_all_exercises(db, Exercise)
        
        # Préparer le message de résultat
        if stats['modified'] > 0:
            flash(f"{stats['modified']} exercices ont été corrigés avec succès.", 'success')
        else:
            flash("Aucune correction nécessaire. Tous les chemins d'images sont déjà synchronisés.", 'info')
        
        # Journaliser les résultats
        current_app.logger.info(f"[FIX_IMAGE_PATHS] {stats['total']} exercices analysés, {stats['modified']} corrigés, {stats['errors']} erreurs")
        
        # Préparer les données pour le template
        return render_template(
            'admin/fix_image_paths_result.html',
            stats=stats,
            title="Correction des chemins d'images"
        )
    except Exception as e:
        current_app.logger.error(f"[FIX_IMAGE_PATHS] Erreur lors de la correction des chemins d'images: {str(e)}")
        flash(f"Une erreur est survenue lors de la correction des chemins d'images: {str(e)}", 'danger')
        return redirect(url_for('admin.dashboard'))
