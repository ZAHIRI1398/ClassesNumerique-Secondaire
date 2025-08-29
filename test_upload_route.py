
@app.route('/test_upload', methods=['GET', 'POST'])
def test_upload():
    """Page de test pour l'upload d'images"""
    if request.method == 'POST':
        if 'test_image' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        file = request.files['test_image']
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = generate_unique_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Utiliser la fonction sécurisée
            if safe_file_save(file, filepath):
                image_path = f'/static/uploads/{filename}'
                flash(f'Image uploadée avec succès: {image_path}', 'success')
                return render_template('test_upload.html', uploaded_image=image_path)
            else:
                flash('Erreur lors de l\'upload de l\'image', 'error')
        else:
            flash('Type de fichier non autorisé', 'error')
    
    return render_template('test_upload.html')
