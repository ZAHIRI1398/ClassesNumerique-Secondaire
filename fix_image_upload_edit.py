from flask import Flask, request, redirect, url_for, flash
from models import db, Exercise
import json
import os
from werkzeug.utils import secure_filename
import cloud_storage

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev_key'  # Pour les messages flash
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db.init_app(app)

# Fonction pour s'assurer que le dossier d'upload existe
def ensure_upload_folder():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

# Route pour tester l'upload d'image lors de l'édition
@app.route('/test-image-upload/<int:exercise_id>', methods=['GET', 'POST'])
def test_image_upload(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if request.method == 'POST':
        # Vérifier si un fichier a été uploadé
        if 'exercise_image' in request.files:
            file = request.files['exercise_image']
            
            if file and file.filename != '':
                # Sécuriser le nom du fichier
                filename = secure_filename(file.filename)
                
                # S'assurer que le dossier d'upload existe
                ensure_upload_folder()
                
                # Sauvegarder le fichier
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Mettre à jour le chemin de l'image dans l'exercice
                relative_path = f"/{file_path}"  # Chemin relatif pour l'URL
                
                # Mettre à jour image_path
                exercise.image_path = relative_path
                
                # Mettre à jour le contenu JSON
                content = json.loads(exercise.content)
                content['image'] = relative_path
                exercise.content = json.dumps(content)
                
                # Sauvegarder les modifications
                db.session.commit()
                
                flash('Image uploadée avec succès!', 'success')
                return redirect(url_for('test_image_upload', exercise_id=exercise_id))
        
        # Vérifier si l'utilisateur a demandé de supprimer l'image
        if 'delete_image' in request.form:
            # Supprimer l'image de l'exercice
            exercise.image_path = None
            
            # Supprimer l'image du contenu JSON
            content = json.loads(exercise.content)
            if 'image' in content:
                del content['image']
            if 'main_image' in content:
                del content['main_image']
            exercise.content = json.dumps(content)
            
            # Sauvegarder les modifications
            db.session.commit()
            
            flash('Image supprimée avec succès!', 'success')
            return redirect(url_for('test_image_upload', exercise_id=exercise_id))
    
    # Préparer les données pour l'affichage
    content = json.loads(exercise.content)
    image_in_content = content.get('image') or content.get('main_image')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Upload Image - Exercice {exercise_id}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Test Upload Image - Exercice {exercise_id}</h1>
            
            <div class="card mb-4">
                <div class="card-header">
                    Informations de l'exercice
                </div>
                <div class="card-body">
                    <h5 class="card-title">{exercise.title}</h5>
                    <p class="card-text">{exercise.description}</p>
                    <p><strong>Type:</strong> {exercise.exercise_type}</p>
                    <p><strong>Image path:</strong> {exercise.image_path or 'Aucune'}</p>
                    <p><strong>Image dans content:</strong> {image_in_content or 'Aucune'}</p>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    Image actuelle
                </div>
                <div class="card-body">
                    {f'<img src="{exercise.image_path}" class="img-fluid mb-3" style="max-width: 300px;">' if exercise.image_path else '<p>Aucune image</p>'}
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    Upload d'une nouvelle image
                </div>
                <div class="card-body">
                    <form method="POST" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="exercise_image" class="form-label">Sélectionner une image</label>
                            <input type="file" class="form-control" id="exercise_image" name="exercise_image" accept="image/*">
                        </div>
                        <button type="submit" class="btn btn-primary">Upload</button>
                        
                        {f'<button type="submit" name="delete_image" class="btn btn-danger ms-2">Supprimer l\'image</button>' if exercise.image_path else ''}
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
