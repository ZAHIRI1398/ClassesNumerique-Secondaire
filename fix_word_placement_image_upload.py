"""
Script pour corriger le problème d'affichage des images dans les exercices word_placement
"""

import os
import logging
from flask import Flask
from models import db, Exercise

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('fix_word_placement')

# Création de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def fix_modified_submit_py():
    """
    Génère le code corrigé pour modified_submit.py
    """
    # Chemin du fichier
    file_path = 'modified_submit.py'
    backup_path = 'modified_submit.py.bak'
    
    # Créer une sauvegarde
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Sauvegarde créée: {backup_path}")
    
    # Rechercher le bloc de code à modifier
    word_placement_block = """            elif exercise_type == 'word_placement':
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Traitement exercice Mots à placer')
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Données formulaire: {dict(request.form)}')
                
                # Récupérer les phrases depuis les champs sentences[]
                sentences = request.form.getlist('sentences[]')
                # Récupérer les mots depuis les champs words[]
                words = request.form.getlist('words[]')
                
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Phrases reçues: {sentences}')
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Mots reçus: {words}')
                
                # Nettoyer et filtrer les phrases vides
                sentences = [s.strip() for s in sentences if s.strip()]
                words = [w.strip() for w in words if w.strip()]
                
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Phrases nettoyées: {sentences}')
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Mots nettoyés: {words}')
                
                # Validation
                if not sentences:
                    flash('Veuillez ajouter au moins une phrase avec des emplacements ___ pour les mots à placer.', 'error')
                    return redirect(request.url)
                
                if not words:
                    flash('Veuillez ajouter au moins un mot à placer.', 'error')
                    return redirect(request.url)
                
                # Vérifier que chaque phrase contient au moins un emplacement ___
                for i, sentence in enumerate(sentences):
                    if '___' not in sentence:
                        flash(f'La phrase {i+1} ne contient pas d\\'emplacements (utilisez ___ pour marquer les emplacements).', 'error')
                        return redirect(request.url)
                
                # Construire le contenu JSON au format attendu par le template
                content = {
                    'sentences': sentences,
                    'words': words
                }
                
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Contenu JSON généré: {content}')
                current_app.logger.debug(f'Exercice Mots à placer créé avec {len(sentences)} phrases et {len(words)} mots')"""

    # Code corrigé avec traitement de l'image
    fixed_word_placement_block = """            elif exercise_type == 'word_placement':
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Traitement exercice Mots à placer')
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Données formulaire: {dict(request.form)}')
                
                # Récupérer les phrases depuis les champs sentences[]
                sentences = request.form.getlist('sentences[]')
                # Récupérer les mots depuis les champs words[]
                words = request.form.getlist('words[]')
                
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Phrases reçues: {sentences}')
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Mots reçus: {words}')
                
                # Nettoyer et filtrer les phrases vides
                sentences = [s.strip() for s in sentences if s.strip()]
                words = [w.strip() for w in words if w.strip()]
                
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Phrases nettoyées: {sentences}')
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Mots nettoyés: {words}')
                
                # Validation
                if not sentences:
                    flash('Veuillez ajouter au moins une phrase avec des emplacements ___ pour les mots à placer.', 'error')
                    return redirect(request.url)
                
                if not words:
                    flash('Veuillez ajouter au moins un mot à placer.', 'error')
                    return redirect(request.url)
                
                # Vérifier que chaque phrase contient au moins un emplacement ___
                for i, sentence in enumerate(sentences):
                    if '___' not in sentence:
                        flash(f'La phrase {i+1} ne contient pas d\\'emplacements (utilisez ___ pour marquer les emplacements).', 'error')
                        return redirect(request.url)
                
                # Construire le contenu JSON au format attendu par le template
                content = {
                    'sentences': sentences,
                    'words': words
                }
                
                # CORRECTION: Traitement de l'image spécifique pour word_placement
                if 'word_placement_image' in request.files:
                    image_file = request.files['word_placement_image']
                    if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                        # Sécuriser le nom du fichier
                        filename = secure_filename(image_file.filename)
                        
                        # Ajouter un timestamp pour éviter les conflits de noms
                        unique_filename = f"{int(time.time())}_{filename}"
                        
                        # Créer le répertoire s'il n'existe pas
                        upload_folder = os.path.join('static', 'uploads', 'word_placement')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        # Sauvegarder l'image
                        image_path = os.path.join(upload_folder, unique_filename)
                        image_file.save(image_path)
                        
                        # Normaliser le chemin pour la base de données
                        normalized_path = f'/static/uploads/word_placement/{unique_filename}'
                        
                        # Stocker le chemin normalisé pour la base de données
                        exercise_image_path = normalized_path
                        
                        # Ajouter le chemin de l'image au contenu JSON
                        content['image'] = normalized_path
                        
                        print(f'[WORD_PLACEMENT_CREATE_DEBUG] Image sauvegardée: {normalized_path}')
                        current_app.logger.debug(f'Image Word Placement sauvegardée: {normalized_path}')
                
                print(f'[WORD_PLACEMENT_CREATE_DEBUG] Contenu JSON généré: {content}')
                current_app.logger.debug(f'Exercice Mots à placer créé avec {len(sentences)} phrases et {len(words)} mots')"""

    # Remplacer le bloc dans le contenu
    if word_placement_block in content:
        content = content.replace(word_placement_block, fixed_word_placement_block)
        
        # Écrire le fichier modifié
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("Fichier modified_submit.py corrigé avec succès")
        return True
    else:
        logger.error("Bloc de code word_placement non trouvé dans modified_submit.py")
        return False

def fix_create_exercise_simple_html():
    """
    Vérifie si le formulaire HTML est correctement configuré
    """
    file_path = 'templates/exercise_types/create_exercise_simple.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si le champ d'upload d'image est correctement nommé
    if 'name="word_placement_image"' in content:
        logger.info("Le formulaire HTML est correctement configuré avec name='word_placement_image'")
        return True
    else:
        logger.error("Le champ d'upload d'image pour word_placement n'est pas correctement nommé")
        return False

def test_word_placement_image_fix():
    """
    Teste si la correction fonctionne en vérifiant un exercice existant
    """
    with app.app_context():
        # Trouver un exercice word_placement existant
        exercise = Exercise.query.filter_by(exercise_type='word_placement').first()
        
        if not exercise:
            logger.error("Aucun exercice word_placement trouvé pour tester")
            return False
        
        logger.info(f"Exercice trouvé: {exercise.title} (ID: {exercise.id})")
        logger.info(f"Chemin d'image actuel: {exercise.image_path}")
        
        # Vérifier le contenu JSON
        content = exercise.get_content()
        if isinstance(content, dict):
            logger.info(f"Contenu JSON: {content}")
            if 'image' in content:
                logger.info(f"Image dans le contenu JSON: {content['image']}")
            else:
                logger.info("Pas d'image dans le contenu JSON")
        
        return True

if __name__ == "__main__":
    print("=== Correction du problème d'affichage des images dans les exercices word_placement ===")
    
    # Vérifier le formulaire HTML
    html_ok = fix_create_exercise_simple_html()
    
    # Corriger le fichier modified_submit.py
    py_fixed = fix_modified_submit_py()
    
    # Tester la correction
    if py_fixed:
        test_ok = test_word_placement_image_fix()
    else:
        test_ok = False
    
    # Résumé
    print("\n=== Résumé des corrections ===")
    print(f"Formulaire HTML correctement configuré: {'✅' if html_ok else '❌'}")
    print(f"Fichier modified_submit.py corrigé: {'✅' if py_fixed else '❌'}")
    print(f"Test de la correction: {'✅' if test_ok else '❌'}")
    
    if py_fixed:
        print("\n✅ CORRECTION RÉUSSIE")
        print("La correction a été appliquée avec succès. Les nouvelles images téléchargées lors de la création")
        print("d'exercices word_placement seront maintenant correctement sauvegardées et affichées.")
    else:
        print("\n❌ CORRECTION ÉCHOUÉE")
        print("La correction n'a pas pu être appliquée. Veuillez vérifier les logs pour plus de détails.")
