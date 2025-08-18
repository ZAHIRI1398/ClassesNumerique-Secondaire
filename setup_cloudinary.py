"""
Script pour configurer et tester la connexion à Cloudinary
"""

import os
import sys
import cloudinary
import cloudinary.uploader
import cloudinary.api

def test_cloudinary_connection():
    """
    Teste la connexion à Cloudinary avec les variables d'environnement actuelles
    """
    # Vérifier que les variables d'environnement sont définies
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ Variables d'environnement Cloudinary manquantes:")
        print(f"  - CLOUDINARY_CLOUD_NAME: {'✅ Défini' if cloud_name else '❌ Manquant'}")
        print(f"  - CLOUDINARY_API_KEY: {'✅ Défini' if api_key else '❌ Manquant'}")
        print(f"  - CLOUDINARY_API_SECRET: {'✅ Défini' if api_secret else '❌ Manquant'}")
        return False
    
    # Configurer Cloudinary
    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        print("✅ Configuration Cloudinary réussie")
    except Exception as e:
        print(f"❌ Erreur lors de la configuration de Cloudinary: {str(e)}")
        return False
    
    # Tester la connexion en récupérant les informations du compte
    try:
        account_info = cloudinary.api.account_info()
        print("✅ Connexion à Cloudinary réussie")
        print(f"  - Plan: {account_info.get('plan', 'Inconnu')}")
        print(f"  - Crédits restants: {account_info.get('credits', {}).get('usage', 'Inconnu')}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à Cloudinary: {str(e)}")
        return False

def setup_cloudinary_env():
    """
    Configure les variables d'environnement Cloudinary interactivement
    """
    print("\n=== Configuration des variables d'environnement Cloudinary ===\n")
    print("Vous pouvez trouver ces informations dans votre dashboard Cloudinary:")
    print("https://cloudinary.com/console\n")
    
    cloud_name = input("Cloud Name: ")
    api_key = input("API Key: ")
    api_secret = input("API Secret: ")
    
    # Définir les variables d'environnement pour la session actuelle
    os.environ['CLOUDINARY_CLOUD_NAME'] = cloud_name
    os.environ['CLOUDINARY_API_KEY'] = api_key
    os.environ['CLOUDINARY_API_SECRET'] = api_secret
    
    # Enregistrer dans .env.cloudinary
    with open('.env.cloudinary', 'w') as f:
        f.write(f"CLOUDINARY_CLOUD_NAME={cloud_name}\n")
        f.write(f"CLOUDINARY_API_KEY={api_key}\n")
        f.write(f"CLOUDINARY_API_SECRET={api_secret}\n")
    
    print("\n✅ Variables d'environnement enregistrées dans .env.cloudinary")
    
    # Tester la connexion
    return test_cloudinary_connection()

if __name__ == "__main__":
    # Vérifier si les variables sont déjà définies
    if all([
        os.environ.get('CLOUDINARY_CLOUD_NAME'),
        os.environ.get('CLOUDINARY_API_KEY'),
        os.environ.get('CLOUDINARY_API_SECRET')
    ]):
        print("Variables d'environnement Cloudinary déjà définies")
        if test_cloudinary_connection():
            print("\n✅ Tout est prêt pour la migration des images!")
            print("Vous pouvez maintenant exécuter:")
            print("python migrate_images_to_cloudinary.py")
        else:
            print("\n❌ Problème avec les variables d'environnement actuelles")
            if input("Voulez-vous reconfigurer? (o/N) ").lower() == 'o':
                setup_cloudinary_env()
    else:
        if setup_cloudinary_env():
            print("\n✅ Tout est prêt pour la migration des images!")
            print("Vous pouvez maintenant exécuter:")
            print("python migrate_images_to_cloudinary.py")
        else:
            print("\n❌ Configuration incomplète")
            print("Veuillez vérifier vos informations Cloudinary et réessayer")
