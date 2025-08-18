"""
Script pour créer une sauvegarde de app.py et recréer la route /login correctement
"""
import os
import shutil
import re
from datetime import datetime

def fix_login_route_complete():
    """
    Crée une sauvegarde de app.py et recréer la route /login correctement
    """
    # Chemin vers le fichier app.py
    app_path = 'app.py'
    
    # Vérifier si le fichier existe
    if not os.path.exists(app_path):
        print(f"Le fichier {app_path} n'existe pas.")
        return False
    
    # Créer une sauvegarde du fichier app.py
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'app.py.bak_{timestamp}'
    shutil.copy2(app_path, backup_path)
    print(f"Sauvegarde créée : {backup_path}")
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Supprimer la route login existante qui pourrait être mal placée
    content = re.sub(r'@app\.route\([\'\"]/login[\'\"].*?def login\(\):.*?(?=@app\.route|\n\n\n)', '', content, flags=re.DOTALL)
    
    # Trouver un bon endroit pour ajouter la route login (avant app.run)
    app_run_pattern = r'if __name__ == [\'"]__main__[\'"]:.*?app\.run\(debug=True\)'
    app_run_match = re.search(app_run_pattern, content, re.DOTALL)
    
    if app_run_match:
        position = app_run_match.start()
        
        # Code de la route login à ajouter
        login_route = """
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == '1'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.subscription_status == 'approved' or user.role == 'admin':
                login_user(user, remember=remember_me)
                flash('Connexion réussie!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            elif user.subscription_status == 'rejected':
                flash('Votre demande d\\'abonnement a été rejetée. Contactez l\\'administrateur.', 'error')
                return render_template('login.html')
            elif user.subscription_status == 'pending':
                # Exception spéciale pour mr.zahiri@gmail.com - accès admin direct
                if user.email == 'mr.zahiri@gmail.com':
                    try:
                        user.subscription_status = 'approved'
                        user.role = 'teacher'  # Changé en teacher pour avoir accès à la création d'exercices
                        user.subscription_type = 'admin'
                        user.approved_by = None  # Pas d'ID admin spécifique pour l'auto-approbation
                        db.session.commit()
                        login_user(user, remember=remember_me)
                        flash('Connexion réussie en tant qu\\'administrateur!', 'success')
                        return redirect(url_for('admin.dashboard'))
                    except Exception as e:
                        db.session.rollback()
                        flash(f'Erreur lors de la connexion: {str(e)}', 'error')
                        return render_template('login.html')
                else:
                    flash('Votre demande d\\'abonnement est en attente d\\'approbation.', 'warning')
                    return render_template('login.html')
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('login.html')

"""
        
        # Insérer la route login
        new_content = content[:position] + login_route + content[position:]
        
        # Écrire le contenu modifié dans le fichier
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("La route /login a été recréée avec succès dans app.py.")
        return True
    else:
        print("Impossible de trouver l'instruction app.run() dans app.py.")
        return False

if __name__ == "__main__":
    fix_login_route_complete()
