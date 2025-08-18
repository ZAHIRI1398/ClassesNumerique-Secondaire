"""
Script pour nettoyer les fichiers temporaires après restauration GitHub
"""
import os
import shutil
import time

def cleanup_temp_files():
    """
    Nettoie les fichiers temporaires après restauration GitHub
    """
    temp_dir = "temp_github"
    
    # Attendre un peu pour s'assurer que les fichiers ne sont plus utilisés
    print("Attente pour s'assurer que les fichiers ne sont plus utilisés...")
    time.sleep(2)
    
    # Essayer de supprimer le répertoire temporaire
    if os.path.exists(temp_dir):
        try:
            print(f"Suppression du répertoire temporaire {temp_dir}...")
            shutil.rmtree(temp_dir)
            print(f"Répertoire {temp_dir} supprimé avec succès!")
        except Exception as e:
            print(f"Erreur lors de la suppression du répertoire {temp_dir}: {str(e)}")
            print("Vous pourrez supprimer ce répertoire manuellement plus tard.")
    else:
        print(f"Le répertoire {temp_dir} n'existe pas, rien à nettoyer.")
    
    print("\nNettoyage terminé!")

if __name__ == "__main__":
    cleanup_temp_files()
