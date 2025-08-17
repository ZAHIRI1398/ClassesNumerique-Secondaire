#!/usr/bin/env python3
"""
Script pour corriger le problème de scoring de l'exercice 2 en modifiant le code dans app.py.
Le problème est que le champ 'words' peut contenir des objets/dictionnaires au lieu de simples chaînes.
"""
import os
import re
import shutil
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_app_py():
    """Crée une sauvegarde du fichier app.py."""
    try:
        app_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
        backup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'app.py.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        if not os.path.exists(app_py_path):
            logger.error(f"❌ Fichier app.py non trouvé: {app_py_path}")
            return False
            
        shutil.copy2(app_py_path, backup_path)
        logger.info(f"✅ Sauvegarde créée: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de la sauvegarde: {str(e)}")
        return False

def modify_app_py():
    """Modifie le code de scoring dans app.py pour gérer correctement le format des mots."""
    try:
        app_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
        
        if not os.path.exists(app_py_path):
            logger.error(f"❌ Fichier app.py non trouvé: {app_py_path}")
            return False
            
        # Lire le contenu du fichier
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher le bloc de code qui traite les exercices fill_in_blanks
        fill_in_blanks_pattern = r"(elif exercise\.exercise_type == 'fill_in_blanks'.*?# Récupérer les réponses correctes \(peut être 'words' ou 'available_words'\).*?correct_answers = content\.get\('words', \[\]\).*?if not correct_answers:.*?correct_answers = content\.get\('available_words', \[\]\))"
        fill_in_blanks_match = re.search(fill_in_blanks_pattern, content, re.DOTALL)
        
        if not fill_in_blanks_match:
            logger.error("❌ Bloc de code pour fill_in_blanks non trouvé dans app.py")
            return False
        
        original_code = fill_in_blanks_match.group(1)
        logger.info(f"✅ Bloc de code pour fill_in_blanks trouvé dans app.py")
        
        # Créer le code modifié avec la gestion des mots au format objet/dictionnaire
        modified_code = """elif exercise.exercise_type == 'fill_in_blanks':
            # Gestion des exercices Texte à trous avec la même logique que Mots à placer
            content = json.loads(exercise.content)
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Processing fill_in_blanks exercise {exercise_id}")
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Form data: {dict(request.form)}")
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Exercise content keys: {list(content.keys())}")
            
            # Compter le nombre réel de blancs dans le contenu
            total_blanks_in_content = 0
            
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
                # Log détaillé pour chaque phrase et ses blancs
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'text' détecté: {text_blanks} blancs dans text")
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Total blancs trouvés dans le contenu: {total_blanks_in_content}")
            # Log détaillé pour chaque phrase et ses blancs
            if 'sentences' in content:
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
            
            # Récupérer les réponses correctes (peut être 'words' ou 'available_words')
            raw_answers = content.get('words', [])
            if not raw_answers:
                raw_answers = content.get('available_words', [])
            
            # Traiter les réponses pour gérer à la fois les chaînes simples et les objets/dictionnaires
            correct_answers = []
            for answer in raw_answers:
                if isinstance(answer, dict) and 'word' in answer:
                    # Si c'est un dictionnaire avec une clé 'word', utiliser cette valeur
                    correct_answers.append(answer['word'])
                elif isinstance(answer, str):
                    # Si c'est déjà une chaîne, l'utiliser directement
                    correct_answers.append(answer)
                else:
                    # Sinon, convertir en chaîne (fallback)
                    correct_answers.append(str(answer))
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement des réponses: {raw_answers} -> {correct_answers}")"""
        
        # Remplacer le bloc de code original par le bloc modifié
        updated_content = content.replace(original_code, modified_code)
        
        # Écrire le contenu modifié dans le fichier
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"✅ Code de scoring modifié avec succès dans app.py")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la modification du code: {str(e)}")
        return False

def main():
    """Fonction principale."""
    logger.info("=== CORRECTION DU PROBLÈME DE SCORING DE L'EXERCICE 2 ===")
    
    # Créer une sauvegarde du fichier app.py
    if not backup_app_py():
        logger.error("❌ Impossible de continuer sans sauvegarde")
        return
    
    # Modifier le code de scoring dans app.py
    if modify_app_py():
        logger.info("✅ Modification du code de scoring terminée avec succès")
        logger.info("✅ Le problème de scoring de l'exercice 2 devrait être résolu")
        logger.info("✅ Redémarrez l'application pour appliquer les modifications")
    else:
        logger.error("❌ Échec de la modification du code de scoring")
        logger.error("❌ Veuillez vérifier le fichier app.py manuellement")

if __name__ == "__main__":
    main()
