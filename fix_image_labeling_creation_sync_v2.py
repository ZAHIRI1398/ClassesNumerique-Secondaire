import os
import re
import json
import time
import shutil
from datetime import datetime

def create_backup(file_path):
    """Crée une sauvegarde du fichier avant modification."""
    timestamp = int(time.time())
    backup_path = f"{file_path}.backup_{timestamp}"
    try:
        shutil.copy2(file_path, backup_path)
        print(f"[INFO] Sauvegarde créée: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"[ERREUR] Impossible de créer une sauvegarde: {str(e)}")
        return None

def find_app_py():
    """Recherche le fichier app.py dans différents emplacements possibles."""
    possible_locations = [
        "app.py",
        "production_code/ClassesNumerique-Secondaire-main/app.py",
        "../app.py",
        "../../app.py"
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            print(f"[INFO] Fichier app.py trouvé: {location}")
            return location
    
    print("[ERREUR] Fichier app.py non trouvé.")
    return None

def fix_image_labeling_edit_route(file_path):
    """Modifie le code de la route d'édition des exercices image_labeling pour synchroniser les chemins d'images."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Recherche du bloc de code pour l'édition des exercices image_labeling
        pattern = r'(# Gestion spéciale pour les exercices de type image_labeling.*?if exercise\.exercise_type == \'image_labeling\'.*?main_image_url = f"/static/uploads/.*?".*?)app\.logger\.info\(f"\[EDIT_DEBUG\] Image principale mise à jour pour image_labeling: \{main_image_url\}"\)'
        
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print("[ERREUR] Code d'édition des exercices image_labeling non trouvé.")
            return False
        
        # Bloc de code trouvé
        edit_block = match.group(1)
        print("[INFO] Bloc de code d'édition des exercices image_labeling trouvé.")
        
        # Vérifier si la synchronisation est déjà présente
        if "exercise.image_path = main_image_url" in edit_block:
            print("[INFO] La synchronisation est déjà présente dans le code d'édition.")
            return True
        
        # Ajouter la synchronisation
        modified_block = edit_block + "exercise.image_path = main_image_url  # Synchronisation avec content.main_image\n                                            "
        
        # Remplacer le bloc dans le contenu
        modified_content = content.replace(edit_block, modified_block)
        
        # Sauvegarder les modifications
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print("[INFO] Code d'édition des exercices image_labeling modifié avec succès.")
        return True
    
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la modification du code d'édition: {str(e)}")
        return False

def fix_image_labeling_create_route(file_path):
    """Recherche et modifie toutes les routes qui créent des exercices image_labeling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Recherche des blocs de code qui créent des exercices image_labeling
        # Nous cherchons les endroits où content['main_image'] est défini pour les exercices image_labeling
        patterns = [
            r'(if\s+exercise_type\s*==\s*[\'"]image_labeling[\'"].*?content\s*=\s*\{.*?[\'"]main_image[\'"]\s*:\s*[^\n]+)',
            r'(content\s*=\s*\{.*?[\'"]main_image[\'"]\s*:\s*[^\n]+.*?exercise\.exercise_type\s*=\s*[\'"]image_labeling[\'"])',
            r'(exercise\.exercise_type\s*=\s*[\'"]image_labeling[\'"].*?content\s*=\s*\{.*?[\'"]main_image[\'"]\s*:\s*[^\n]+)'
        ]
        
        found = False
        modified_content = content
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                found = True
                block = match.group(1)
                print(f"[INFO] Bloc de code de création d'exercice image_labeling trouvé: {block[:100]}...")
                
                # Vérifier si le bloc contient déjà une synchronisation
                if "exercise.image_path = " in block and "main_image" in block:
                    print("[INFO] La synchronisation est déjà présente dans ce bloc.")
                    continue
                
                # Trouver l'endroit où main_image est défini
                main_image_match = re.search(r'[\'"]main_image[\'"]\s*:\s*([^\n,}]+)', block)
                if main_image_match:
                    main_image_var = main_image_match.group(1).strip()
                    
                    # Ajouter la synchronisation après ce bloc
                    end_index = match.end()
                    sync_code = f"\n        # Synchroniser exercise.image_path avec content['main_image']\n        exercise.image_path = {main_image_var}"
                    
                    # Insérer le code de synchronisation
                    modified_content = modified_content[:end_index] + sync_code + modified_content[end_index:]
                    print(f"[INFO] Synchronisation ajoutée: exercise.image_path = {main_image_var}")
        
        if not found:
            print("[ERREUR] Aucun bloc de code de création d'exercice image_labeling trouvé.")
            return False
        
        # Sauvegarder les modifications
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print("[INFO] Code de création des exercices image_labeling modifié avec succès.")
        return True
    
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la modification du code de création: {str(e)}")
        return False

def create_route_fix(file_path):
    """Crée une route Flask pour corriger automatiquement tous les exercices image_labeling existants."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si la route existe déjà
        if "@app.route('/fix-image-labeling-paths')" in content:
            print("[INFO] La route de correction existe déjà.")
            return True
        
        # Code de la route à ajouter
        route_code = """
@app.route('/fix-image-labeling-paths')
@login_required
@admin_required
def fix_image_labeling_paths():
    # Route pour corriger les chemins d'images dans les exercices image_labeling
    try:
        from models import Exercise
        import json
        
        # Récupérer tous les exercices de type image_labeling
        exercises = Exercise.query.filter_by(exercise_type='image_labeling').all()
        
        results = []
        fixed_count = 0
        
        for exercise in exercises:
            try:
                # Récupérer le contenu
                content = json.loads(exercise.content) if exercise.content else {}
                
                # Vérifier si main_image existe
                if 'main_image' in content:
                    main_image = content['main_image']
                    
                    # Normaliser le chemin si nécessaire
                    if main_image and not main_image.startswith('/static/'):
                        if main_image.startswith('static/'):
                            main_image = f"/{main_image}"
                        elif main_image.startswith('uploads/'):
                            main_image = f"/static/{main_image}"
                        elif not main_image.startswith('/'):
                            main_image = f"/static/uploads/{main_image}"
                        
                        # Mettre à jour content.main_image
                        content['main_image'] = main_image
                        exercise.content = json.dumps(content)
                    
                    # Synchroniser exercise.image_path avec content.main_image
                    if exercise.image_path != main_image:
                        old_path = exercise.image_path or "None"
                        exercise.image_path = main_image
                        fixed_count += 1
                        results.append(f"Exercice #{exercise.id}: image_path mis à jour de '{old_path}' à '{main_image}'")
                    else:
                        results.append(f"Exercice #{exercise.id}: déjà synchronisé ('{main_image}')")
                else:
                    results.append(f"Exercice #{exercise.id}: Pas de main_image dans le contenu")
            
            except Exception as e:
                results.append(f"Erreur pour l'exercice #{exercise.id}: {str(e)}")
        
        # Sauvegarder les modifications
        db.session.commit()
        
        return render_template('admin/fix_results.html', 
                              title="Correction des chemins d'images",
                              results=results,
                              fixed_count=fixed_count,
                              total_count=len(exercises))
    
    except Exception as e:
        db.session.rollback()
        return f"<h2>ERREUR:</h2><p>{str(e)}</p>"
"""
        
        # Ajouter la route à la fin du fichier
        modified_content = content + route_code
        
        # Sauvegarder les modifications
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print("[INFO] Route de correction ajoutée avec succès.")
        return True
    
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'ajout de la route de correction: {str(e)}")
        return False

def create_template_file():
    """Crée le template pour afficher les résultats de la correction."""
    template_dir = "templates/admin"
    template_path = os.path.join(template_dir, "fix_results.html")
    
    # Vérifier si le répertoire existe
    if not os.path.exists(template_dir):
        try:
            os.makedirs(template_dir)
            print(f"[INFO] Répertoire créé: {template_dir}")
        except Exception as e:
            print(f"[ERREUR] Impossible de créer le répertoire: {str(e)}")
            return False
    
    # Vérifier si le fichier existe déjà
    if os.path.exists(template_path):
        print(f"[INFO] Le template existe déjà: {template_path}")
        return True
    
    # Contenu du template
    template_content = """{% extends "base.html" %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card shadow">
        <div class="card-header bg-primary text-white">
            <h4 class="mb-0">{{ title }}</h4>
        </div>
        <div class="card-body">
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle"></i> Résumé</h5>
                <p>{{ fixed_count }} exercices corrigés sur {{ total_count }} exercices image_labeling.</p>
            </div>
            
            <h5>Détails des corrections:</h5>
            <div class="list-group">
                {% for result in results %}
                <div class="list-group-item {% if 'Erreur' in result %}list-group-item-danger{% elif 'mis à jour' in result %}list-group-item-success{% else %}list-group-item-info{% endif %}">
                    {{ result }}
                </div>
                {% endfor %}
            </div>
            
            <div class="mt-4">
                <a href="{{ url_for('admin_dashboard') }}" class="btn btn-primary">
                    <i class="fas fa-arrow-left"></i> Retour au tableau de bord
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"[INFO] Template créé: {template_path}")
        return True
    
    except Exception as e:
        print(f"[ERREUR] Impossible de créer le template: {str(e)}")
        return False

def main():
    """Fonction principale."""
    print("[INFO] Démarrage du script de correction des exercices image_labeling...")
    
    # Trouver le fichier app.py
    app_py_path = find_app_py()
    if not app_py_path:
        return
    
    # Créer une sauvegarde
    backup_path = create_backup(app_py_path)
    if not backup_path:
        return
    
    # Modifier le code d'édition des exercices image_labeling
    edit_success = fix_image_labeling_edit_route(app_py_path)
    
    # Modifier le code de création des exercices image_labeling
    create_success = fix_image_labeling_create_route(app_py_path)
    
    # Ajouter la route de correction
    route_success = create_route_fix(app_py_path)
    
    # Créer le template
    template_success = create_template_file()
    
    # Résumé
    print("\n[INFO] Résumé des modifications:")
    print(f"- Modification du code d'édition: {'OK' if edit_success else 'ECHEC'}")
    print(f"- Modification du code de création: {'OK' if create_success else 'ECHEC'}")
    print(f"- Ajout de la route de correction: {'OK' if route_success else 'ECHEC'}")
    print(f"- Création du template: {'OK' if template_success else 'ECHEC'}")
    
    if not (edit_success or create_success):
        print("\n[ERREUR] Aucune modification n'a été effectuée.")
        print(f"[INFO] Vous pouvez restaurer la sauvegarde depuis {backup_path}")
    else:
        print("\n[INFO] Modifications effectuées avec succès.")
        print("[INFO] Pour appliquer les corrections aux exercices existants, accédez à la route /fix-image-labeling-paths")

if __name__ == "__main__":
    main()
