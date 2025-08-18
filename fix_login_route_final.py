"""
Script pour créer une sauvegarde de app.py et recréer la route /login correctement
"""
import os
import shutil
from datetime import datetime

def fix_login_route_final():
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
        lines = file.readlines()
    
    # Trouver l'emplacement de la route racine et de app.run
    root_route_index = -1
    app_run_index = -1
    
    for i, line in enumerate(lines):
        if "@app.route('/')" in line:
            root_route_index = i
        if "app.run(debug=True)" in line:
            app_run_index = i
    
    if root_route_index == -1:
        print("Route racine (/) non trouvée.")
        return False
    
    if app_run_index == -1:
        print("Instruction app.run() non trouvée.")
        return False
    
    # Ajouter la route login juste après la route racine
    login_route = [
        "\n",
        "@app.route('/login', methods=['GET', 'POST'])\n",
        "def login():\n",
        "    if current_user.is_authenticated:\n",
        "        return redirect(url_for('index'))\n",
        "    \n",
        "    if request.method == 'POST':\n",
        "        email = request.form.get('email')\n",
        "        password = request.form.get('password')\n",
        "        remember_me = request.form.get('remember_me') == '1'\n",
        "        \n",
        "        user = User.query.filter_by(email=email).first()\n",
        "        \n",
        "        if user and user.check_password(password):\n",
        "            if user.subscription_status == 'approved' or user.role == 'admin':\n",
        "                login_user(user, remember=remember_me)\n",
        "                flash('Connexion réussie!', 'success')\n",
        "                next_page = request.args.get('next')\n",
        "                return redirect(next_page or url_for('index'))\n",
        "            elif user.subscription_status == 'rejected':\n",
        "                flash('Votre demande d\\'abonnement a été rejetée. Contactez l\\'administrateur.', 'error')\n",
        "                return render_template('login.html')\n",
        "            elif user.subscription_status == 'pending':\n",
        "                # Exception spéciale pour mr.zahiri@gmail.com - accès admin direct\n",
        "                if user.email == 'mr.zahiri@gmail.com':\n",
        "                    try:\n",
        "                        user.subscription_status = 'approved'\n",
        "                        user.role = 'teacher'  # Changé en teacher pour avoir accès à la création d'exercices\n",
        "                        user.subscription_type = 'admin'\n",
        "                        user.approved_by = None  # Pas d'ID admin spécifique pour l'auto-approbation\n",
        "                        db.session.commit()\n",
        "                        login_user(user, remember=remember_me)\n",
        "                        flash('Connexion réussie en tant qu\\'administrateur!', 'success')\n",
        "                        return redirect(url_for('admin.dashboard'))\n",
        "                    except Exception as e:\n",
        "                        db.session.rollback()\n",
        "                        flash(f'Erreur lors de la connexion: {str(e)}', 'error')\n",
        "                        return render_template('login.html')\n",
        "                else:\n",
        "                    flash('Votre demande d\\'abonnement est en attente d\\'approbation.', 'warning')\n",
        "                    return render_template('login.html')\n",
        "        else:\n",
        "            flash('Email ou mot de passe incorrect.', 'error')\n",
        "    \n",
        "    return render_template('login.html')\n",
        "\n"
    ]
    
    # Supprimer l'ancienne route login si elle existe après app.run
    new_lines = []
    skip_mode = False
    
    for i, line in enumerate(lines):
        if i > app_run_index and "@app.route('/login'" in line:
            skip_mode = True
            continue
        
        if skip_mode and line.strip() == "":
            skip_mode = False
            continue
        
        if not skip_mode:
            new_lines.append(line)
    
    # Insérer la nouvelle route login après la route racine
    final_lines = new_lines[:root_route_index + 5] + login_route + new_lines[root_route_index + 5:]
    
    # Écrire le contenu modifié dans le fichier
    with open(app_path, 'w', encoding='utf-8') as file:
        file.writelines(final_lines)
    
    print("La route /login a été recréée avec succès dans app.py.")
    return True

if __name__ == "__main__":
    fix_login_route_final()
