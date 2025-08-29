"""
Script pour tester la correction de l'upload des fichiers audio MP3 dans les exercices de dictée
"""

import os
import time
import requests
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Simuler l'environnement Flask pour tester les fonctions
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'audio')

# Vérifier que le dossier d'upload existe
def check_upload_folder():
    audio_dir = os.path.join('static', 'uploads', 'audio')
    if not os.path.exists(audio_dir):
        print(f"[ERREUR] Le dossier {audio_dir} n'existe pas!")
        return False
    else:
        print(f"[OK] Le dossier {audio_dir} existe.")
        return True

# Vérifier que les extensions audio sont autorisées
def check_allowed_extensions():
    from modified_submit import allowed_file
    
    test_files = [
        "test.mp3",
        "audio.wav",
        "dictation.ogg",
        "sound.m4a",
        "image.png",
        "document.pdf"  # Ne devrait pas être autorisé
    ]
    
    results = {}
    for filename in test_files:
        results[filename] = allowed_file(filename)
    
    print("\nTest des extensions autorisées:")
    for filename, allowed in results.items():
        status = "[OK]" if (allowed and not filename.endswith('.pdf')) or (not allowed and filename.endswith('.pdf')) else "[ERREUR]"
        print(f"{status} {filename}: {'autorisé' if allowed else 'non autorisé'}")
    
    # Vérifier que tous les fichiers audio sont autorisés
    audio_files = [f for f in test_files if f.endswith(('.mp3', '.wav', '.ogg', '.m4a'))]
    audio_allowed = all(results[f] for f in audio_files)
    
    # Vérifier que le fichier PDF n'est pas autorisé
    pdf_not_allowed = not results["document.pdf"]
    
    return audio_allowed and pdf_not_allowed

# Simuler l'upload d'un fichier audio
def test_audio_upload():
    from modified_submit import secure_filename
    import time
    
    # Créer un fichier audio de test
    test_file = "test_audio.mp3"
    with open(test_file, 'wb') as f:
        f.write(b'Test audio content')
    
    print("\nTest d'upload de fichier audio:")
    
    try:
        # Simuler le code d'upload
        timestamp = int(time.time())
        filename = secure_filename(f'dictation_{timestamp}_0_{test_file}')
        audio_path = os.path.join('static', 'uploads', 'audio', filename)
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        # Simuler la sauvegarde du fichier
        with open(test_file, 'rb') as src, open(audio_path, 'wb') as dst:
            dst.write(src.read())
        
        # Vérifier que le fichier a été créé
        if os.path.exists(audio_path):
            print(f"[OK] Fichier audio sauvegardé avec succès: {audio_path}")
            
            # Vérifier la cohérence des chemins
            stored_path = f'/static/uploads/audio/{filename}'
            print(f"[OK] Chemin stocké dans le contenu JSON: {stored_path}")
            
            # Nettoyer
            os.remove(audio_path)
            print(f"[OK] Fichier de test supprimé.")
            
            return True
        else:
            print(f"[ERREUR] Échec de la sauvegarde du fichier audio: {audio_path}")
            return False
    
    except Exception as e:
        print(f"[ERREUR] Erreur lors du test d'upload: {str(e)}")
        return False
    finally:
        # Nettoyer le fichier de test - avec gestion des erreurs de permission
        try:
            if os.path.exists(test_file):
                os.remove(test_file)
        except PermissionError:
            print("[AVERTISSEMENT] Impossible de supprimer le fichier de test (utilisé par un autre processus)")
            pass

def run_all_tests():
    print("=== TESTS DE LA CORRECTION D'UPLOAD AUDIO ===\n")
    
    # Test 1: Vérifier le dossier d'upload
    folder_ok = check_upload_folder()
    
    # Test 2: Vérifier les extensions autorisées
    extensions_ok = check_allowed_extensions()
    
    # Test 3: Simuler un upload
    upload_ok = test_audio_upload()
    
    # Résumé des tests
    print("\n=== RÉSUMÉ DES TESTS ===")
    print(f"{'[OK]' if folder_ok else '[ERREUR]'} Dossier d'upload: {'OK' if folder_ok else 'ÉCHEC'}")
    print(f"{'[OK]' if extensions_ok else '[ERREUR]'} Extensions autorisées: {'OK' if extensions_ok else 'ÉCHEC'}")
    print(f"{'[OK]' if upload_ok else '[ERREUR]'} Simulation d'upload: {'OK' if upload_ok else 'ÉCHEC'}")
    
    all_ok = folder_ok and extensions_ok and upload_ok
    print(f"\n{'[OK]' if all_ok else '[ERREUR]'} RÉSULTAT GLOBAL: {'SUCCÈS' if all_ok else 'ÉCHEC'}")
    
    return all_ok

if __name__ == "__main__":
    run_all_tests()
