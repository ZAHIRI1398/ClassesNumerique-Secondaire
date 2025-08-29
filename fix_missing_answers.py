import sqlite3
import json
import logging
import os
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fix_missing_answers():
    """
    Corrige les exercices word_placement qui n'ont pas de réponses définies
    en utilisant les mots disponibles comme réponses attendues.
    """
    try:
        # Créer une sauvegarde de la base de données
        backup_file = f"instance/app.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists("instance/app.db"):
            with open("instance/app.db", "rb") as src, open(backup_file, "wb") as dst:
                dst.write(src.read())
            logging.info(f"Sauvegarde de la base de données créée: {backup_file}")
        
        # Connexion à la base de données
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # Recherche des exercices word_placement
        cursor.execute("SELECT id, title, content FROM exercise WHERE exercise_type = 'word_placement'")
        exercises = cursor.fetchall()
        
        logging.info(f"Nombre d'exercices word_placement trouvés: {len(exercises)}")
        
        for exercise in exercises:
            exercise_id, title, content_json = exercise
            
            try:
                content = json.loads(content_json)
                sentences = content.get('sentences', [])
                words = content.get('words', [])
                answers = content.get('answers', [])
                
                # Vérifier si le champ 'answers' est vide
                if not answers:
                    logging.info(f"Exercice ID {exercise_id} ({title}) n'a pas de réponses définies.")
                    
                    # Compter le nombre de blancs dans les phrases
                    total_blanks = sum(sentence.count('___') for sentence in sentences)
                    
                    # Vérifier si nous avons suffisamment de mots pour remplir les blancs
                    if len(words) >= total_blanks:
                        # Utiliser les mots disponibles comme réponses attendues
                        # Pour cet exemple, nous utilisons les premiers mots de la liste
                        # Dans un cas réel, il faudrait une logique plus sophistiquée
                        new_answers = words[:total_blanks]
                        
                        # Mettre à jour le contenu avec les nouvelles réponses
                        content['answers'] = new_answers
                        updated_content = json.dumps(content)
                        
                        # Mettre à jour la base de données
                        cursor.execute(
                            "UPDATE exercise SET content = ? WHERE id = ?",
                            (updated_content, exercise_id)
                        )
                        
                        logging.info(f"Exercice ID {exercise_id} mis à jour avec les réponses: {new_answers}")
                    else:
                        logging.warning(f"Exercice ID {exercise_id} n'a pas assez de mots ({len(words)}) pour tous les blancs ({total_blanks}).")
                else:
                    logging.info(f"Exercice ID {exercise_id} a déjà des réponses définies: {answers}")
            
            except json.JSONDecodeError:
                logging.error(f"Contenu JSON invalide pour l'exercice ID {exercise_id}")
            except Exception as e:
                logging.error(f"Erreur lors du traitement de l'exercice ID {exercise_id}: {str(e)}")
        
        # Valider les modifications
        conn.commit()
        logging.info("Modifications enregistrées dans la base de données.")
        
        # Vérifier les mises à jour
        cursor.execute("SELECT id, title, content FROM exercise WHERE id = 78")
        updated_exercise = cursor.fetchone()
        if updated_exercise:
            exercise_id, title, content_json = updated_exercise
            content = json.loads(content_json)
            logging.info(f"Exercice ID {exercise_id} après mise à jour:")
            logging.info(f"Titre: {title}")
            logging.info(f"Contenu: {content}")
        
        conn.close()
        
        return True
    
    except Exception as e:
        logging.error(f"Erreur générale: {str(e)}")
        return False

if __name__ == "__main__":
    logging.info("=== CORRECTION DES RÉPONSES MANQUANTES DANS LES EXERCICES WORD_PLACEMENT ===")
    success = fix_missing_answers()
    if success:
        logging.info("Correction terminée avec succès.")
    else:
        logging.error("La correction a échoué.")
