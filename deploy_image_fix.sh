#!/bin/bash
# Script de déploiement de la correction d'affichage d'images pour Linux/macOS
# Auteur: Cascade
# Date: 2025-08-18

echo "===== DEPLOIEMENT DE LA CORRECTION D'AFFICHAGE D'IMAGES ====="
echo

# Vérifier si Git est installé
if ! command -v git &> /dev/null; then
    echo "[ERREUR] Git n'est pas installé"
    echo "Veuillez installer Git avec votre gestionnaire de paquets"
    exit 1
fi

# Vérifier si les fichiers nécessaires existent
if [ ! -f fix_image_display.py ]; then
    echo "[ERREUR] Le fichier fix_image_display.py est manquant"
    exit 1
fi

if [ ! -f app.py ]; then
    echo "[ERREUR] Le fichier app.py est manquant"
    exit 1
fi

echo "[1/5] Vérification des modifications..."
git status

echo
echo "[2/5] Ajout des fichiers au commit..."
git add fix_image_display.py app.py DOCUMENTATION_CORRECTION_AFFICHAGE_IMAGES_PRODUCTION.md GUIDE_DEPLOIEMENT_CORRECTION_IMAGES.md verify_image_fix.py migrate_images_to_cloudinary.py

echo
echo "[3/5] Création du commit..."
git commit -m "Fix: Correction des problèmes d'affichage d'images en production"

echo
echo "[4/5] Push des modifications vers GitHub..."
git push

echo
echo "[5/5] Déploiement terminé avec succès!"
echo
echo "===== PROCHAINES ETAPES ====="
echo
echo "1. Accédez à votre application Railway et vérifiez le déploiement"
echo "2. Une fois déployé, exécutez les routes de diagnostic dans cet ordre:"
echo "   - https://votre-app.railway.app/fix-uploads-directory"
echo "   - https://votre-app.railway.app/check-image-paths"
echo "   - https://votre-app.railway.app/create-placeholder-images"
echo
echo "3. Pour une solution permanente, exécutez le script de migration:"
echo "   python migrate_images_to_cloudinary.py --no-dry-run"
echo
echo "Pour plus d'informations, consultez GUIDE_DEPLOIEMENT_CORRECTION_IMAGES.md"
echo

read -p "Appuyez sur Entrée pour continuer..."
