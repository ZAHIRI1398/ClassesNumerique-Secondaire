#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier que la prévention des fichiers de 0 octets fonctionne correctement.
Ce script crée un fichier de test de 0 octets et vérifie que la fonction allowed_file le rejette.
"""

import os
import sys
import io
import logging
from flask import Flask
from werkzeug.datastructures import FileStorage

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_zero_byte_prevention')

# Créer une application Flask minimale pour le test
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Importer la fonction allowed_file depuis app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from app import allowed_file
    logger.info("Fonction allowed_file importée avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation de allowed_file: {str(e)}")
    sys.exit(1)

def test_zero_byte_file():
    """Teste la détection des fichiers de 0 octets"""
    logger.info("=== Test de détection des fichiers de 0 octets ===")
    
    # Créer un fichier de test de 0 octets
    zero_byte_file = FileStorage(
        stream=io.BytesIO(b''),
        filename='test_zero_byte.png',
        content_type='image/png',
    )
    
    # Vérifier que la fonction allowed_file rejette le fichier de 0 octets
    result = allowed_file(zero_byte_file.filename, zero_byte_file)
    
    if result:
        logger.error("❌ ÉCHEC: La fonction allowed_file a accepté un fichier de 0 octets")
        return False
    else:
        logger.info("✅ SUCCÈS: La fonction allowed_file a correctement rejeté le fichier de 0 octets")
        return True

def test_valid_file():
    """Teste l'acceptation des fichiers valides"""
    logger.info("=== Test d'acceptation des fichiers valides ===")
    
    # Créer un fichier de test avec du contenu
    valid_file = FileStorage(
        stream=io.BytesIO(b'contenu du fichier'),
        filename='test_valid.png',
        content_type='image/png',
    )
    
    # Vérifier que la fonction allowed_file accepte le fichier valide
    result = allowed_file(valid_file.filename, valid_file)
    
    if result:
        logger.info("✅ SUCCÈS: La fonction allowed_file a correctement accepté un fichier valide")
        return True
    else:
        logger.error("❌ ÉCHEC: La fonction allowed_file a rejeté un fichier valide")
        return False

def test_invalid_extension():
    """Teste le rejet des fichiers avec extension non autorisée"""
    logger.info("=== Test de rejet des fichiers avec extension non autorisée ===")
    
    # Créer un fichier de test avec une extension non autorisée
    invalid_file = FileStorage(
        stream=io.BytesIO(b'contenu du fichier'),
        filename='test_invalid.exe',
        content_type='application/octet-stream',
    )
    
    # Vérifier que la fonction allowed_file rejette le fichier avec extension non autorisée
    result = allowed_file(invalid_file.filename, invalid_file)
    
    if result:
        logger.error("❌ ÉCHEC: La fonction allowed_file a accepté un fichier avec extension non autorisée")
        return False
    else:
        logger.info("✅ SUCCÈS: La fonction allowed_file a correctement rejeté un fichier avec extension non autorisée")
        return True

if __name__ == "__main__":
    logger.info("Démarrage des tests de prévention des fichiers de 0 octets")
    
    # Exécuter les tests
    zero_byte_test = test_zero_byte_file()
    valid_file_test = test_valid_file()
    invalid_extension_test = test_invalid_extension()
    
    # Afficher le résumé des tests
    logger.info("\n=== Résumé des tests ===")
    logger.info(f"Test fichier 0 octets: {'✅ SUCCÈS' if zero_byte_test else '❌ ÉCHEC'}")
    logger.info(f"Test fichier valide: {'✅ SUCCÈS' if valid_file_test else '❌ ÉCHEC'}")
    logger.info(f"Test extension invalide: {'✅ SUCCÈS' if invalid_extension_test else '❌ ÉCHEC'}")
    
    # Déterminer le résultat global
    if zero_byte_test and valid_file_test and invalid_extension_test:
        logger.info("✅ TOUS LES TESTS ONT RÉUSSI: La prévention des fichiers de 0 octets fonctionne correctement")
        sys.exit(0)
    else:
        logger.error("❌ CERTAINS TESTS ONT ÉCHOUÉ: La prévention des fichiers de 0 octets ne fonctionne pas correctement")
        sys.exit(1)
