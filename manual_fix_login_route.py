"""
Script pour corriger manuellement la route /login dans app.py
"""
import os
import shutil
from datetime import datetime

def manual_fix_login_route():
    """
    Corrige manuellement la route /login dans app.py
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
    
    # Lire le contenu du fichier original
    with open(backup_path, 'r', encoding='utf-8') as file:
        original_content = file.read()
    
    # Chercher la position de la route racine
    root_route_pos = original_content.find("@app.route('/')")
    if root_route_pos == -1:
        print("Route racine (/) non trouvée.")
        return False
    
    # Chercher la position de app.run
    app_run_pos = original_content.find("app.run(debug=True)")
    if app_run_pos == -1:
        print("Instruction app.run() non trouvée.")
        return False
    
    # Créer le nouveau contenu avec la route /login correctement placée
    new_content = original_content[:root_route_pos + 100]  # Inclure la route racine
    
    # Ajouter la route login
    new_content += """
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
    
    # Ajouter le reste du contenu, en excluant l'ancienne route login
    login_route_pos = original_content.find("@app.route('/login'", app_run_pos)
    if login_route_pos != -1:
        # Trouver la fin de la route login
        next_route_pos = original_content.find("@app.route", login_route_pos + 1)
        if next_route_pos != -1:
            # Exclure l'ancienne route login
            new_content += original_content[root_route_pos + 100:login_route_pos]
            new_content += original_content[next_route_pos:]
        else:
            # Si c'est la dernière route, ajouter tout jusqu'à la route login
            new_content += original_content[root_route_pos + 100:login_route_pos]
    else:
        # Si la route login n'est pas trouvée après app.run, ajouter le reste du contenu
        new_content += original_content[root_route_pos + 100:]
    
    # Écrire le nouveau contenu dans le fichier
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("La route /login a été corrigée manuellement avec succès dans app.py.")
    return True

if __name__ == "__main__":
    manual_fix_login_route()
