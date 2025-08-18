"""
Script pour ajouter les routes / et /login dans app.py
"""
import os
import re
from datetime import datetime

def add_root_and_login_routes():
    """
    Ajoute les routes / et /login dans app.py
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
    with open(app_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    print(f"Sauvegarde créée : {backup_path}")
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Vérifier si les routes existent déjà et les supprimer
    content = re.sub(r'@app\.route\([\'\"]/[\'\"].*?def index\(\):.*?return redirect\(.*?\)\n', '', content, flags=re.DOTALL)
    content = re.sub(r'@app\.route\([\'\"]\/login[\'\"].*?def login\(\):.*?return render_template\(.*?\)\n', '', content, flags=re.DOTALL)
    
    # Trouver un bon endroit pour ajouter les routes
    # Chercher après la définition de l'application Flask
    app_definition = re.search(r'app = Flask\(__name__\).*?\n', content)
    
    if app_definition:
        position = app_definition.end()
        
        # Code des routes à ajouter
        routes_code = """
@app.route('/')
def index():
    # Route racine qui redirige vers la page de connexion
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == '1'
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember_me)
            
            if user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Identifiants invalides. Veuillez réessayer.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('login'))

"""
        
        # Insérer les routes
        new_content = content[:position] + routes_code + content[position:]
        
        # Écrire le contenu modifié dans le fichier
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("Les routes / et /login ont été ajoutées avec succès dans app.py.")
        return True
    else:
        print("Impossible de trouver la définition de l'application Flask.")
        return False

if __name__ == "__main__":
    add_root_and_login_routes()
