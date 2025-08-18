"""
Script pour ajouter la route logout à app.py
"""
import os

def add_logout_route():
    app_path = os.path.join(os.getcwd(), 'app.py')
    
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Vérifier si la route logout existe déjà
    if '@app.route(\'/logout\')' in content:
        print("La route logout existe déjà.")
        return
    
    # Ajouter la route logout à la fin du fichier
    logout_route = """
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))
"""
    
    with open(app_path, 'a', encoding='utf-8') as file:
        file.write(logout_route)
    
    print("Route logout ajoutée avec succès.")

if __name__ == "__main__":
    add_logout_route()
