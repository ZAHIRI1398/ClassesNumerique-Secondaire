#!/usr/bin/env python3
"""
Script pour corriger spécifiquement l'exercice "Les coordonnées"
Ce script vérifie et corrige le problème de scoring pour cet exercice particulier
"""
import os
import sys
import json
import argparse
import subprocess
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def run_command(command):
    """Exécute une commande et affiche le résultat"""
    print(f"\n>>> Exécution: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               capture_output=True, text=True)
        print(f"[OK] Succès: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Échec: {e}")
        print(f"Sortie d'erreur: {e.stderr}")
        return False

def connect_to_db():
    """Établit une connexion à la base de données"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("[ERREUR] Variable d'environnement DATABASE_URL non définie!")
        return None
    
    try:
        engine = create_engine(database_url)
        connection = engine.connect()
        print("[INFO] Connexion à la base de données établie avec succès!")
        return connection
    except Exception as e:
        print(f"[ERREUR] Impossible de se connecter à la base de données: {e}")
        return None

def find_coordonnees_exercise(connection):
    """Recherche l'exercice 'Les coordonnées' dans la base de données"""
    try:
        # Rechercher par titre exact
        result = connection.execute(text("SELECT id, title, exercise_type, content FROM exercise WHERE title LIKE '%coordonnées%'"))
        exercises = result.fetchall()
        
        if not exercises:
            print("[INFO] Aucun exercice avec 'coordonnées' dans le titre trouvé.")
            # Rechercher par contenu
            result = connection.execute(text("SELECT id, title, exercise_type, content FROM exercise WHERE content LIKE '%coordonnées%'"))
            exercises = result.fetchall()
        
        if not exercises:
            print("[ERREUR] Exercice 'Les coordonnées' non trouvé!")
            return None
        
        print(f"[INFO] {len(exercises)} exercice(s) trouvé(s) avec 'coordonnées':")
        for ex in exercises:
            print(f"  - ID: {ex.id}, Titre: {ex.title}, Type: {ex.exercise_type}")
        
        # Si plusieurs exercices trouvés, demander à l'utilisateur de choisir
        if len(exercises) > 1:
            exercise_id = input("Entrez l'ID de l'exercice à corriger: ")
            try:
                exercise_id = int(exercise_id)
                for ex in exercises:
                    if ex.id == exercise_id:
                        return ex
                print(f"[ERREUR] Exercice avec ID {exercise_id} non trouvé dans les résultats!")
                return None
            except ValueError:
                print("[ERREUR] ID invalide!")
                return None
        
        return exercises[0]
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la recherche de l'exercice: {e}")
        return None

def analyze_exercise_content(exercise):
    """Analyse le contenu de l'exercice pour identifier les problèmes"""
    try:
        print(f"\n[INFO] Analyse de l'exercice '{exercise.title}' (ID: {exercise.id})...")
        content = json.loads(exercise.content)
        
        # Afficher les clés du contenu
        print(f"[INFO] Clés du contenu: {list(content.keys())}")
        
        # Compter les blancs dans le contenu
        total_blanks_in_content = 0
        
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            print(f"[INFO] Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
            # Log détaillé pour chaque phrase et ses blancs
            for i, sentence in enumerate(content['sentences']):
                blanks_in_sentence = sentence.count('___')
                print(f"[INFO] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            print(f"[INFO] Format 'text' détecté: {text_blanks} blancs dans text")
        
        print(f"[INFO] Total blancs trouvés dans le contenu: {total_blanks_in_content}")
        
        # Récupérer les réponses correctes (peut être 'words' ou 'available_words')
        correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        if not correct_answers:
            print(f"[ERREUR] Aucune réponse correcte trouvée dans le contenu de l'exercice!")
            return False
        
        print(f"[INFO] {len(correct_answers)} réponses correctes trouvées: {correct_answers}")
        
        # Vérifier la cohérence
        if total_blanks_in_content != len(correct_answers):
            print(f"[ALERTE] Incohérence détectée: {total_blanks_in_content} blancs mais {len(correct_answers)} réponses!")
            return False
        
        print(f"[INFO] L'exercice semble cohérent: {total_blanks_in_content} blancs et {len(correct_answers)} réponses.")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'analyse du contenu: {e}")
        return False

def fix_exercise(connection, exercise):
    """Corrige l'exercice si nécessaire"""
    try:
        print(f"\n[INFO] Tentative de correction de l'exercice '{exercise.title}' (ID: {exercise.id})...")
        content = json.loads(exercise.content)
        
        # Vérifier si l'exercice a besoin d'être corrigé
        needs_fixing = False
        
        # Compter les blancs dans le contenu
        total_blanks_in_content = 0
        
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
        
        # Récupérer les réponses correctes (peut être 'words' ou 'available_words')
        correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
            if correct_answers:
                # Si les réponses sont dans available_words mais pas dans words, c'est un problème
                content['words'] = correct_answers
                needs_fixing = True
                print("[INFO] Correction: Copie des réponses de 'available_words' vers 'words'")
        
        # Vérifier la cohérence
        if total_blanks_in_content != len(correct_answers):
            print(f"[ALERTE] Incohérence détectée: {total_blanks_in_content} blancs mais {len(correct_answers)} réponses!")
            
            # Si le nombre de blancs est supérieur au nombre de réponses, ajouter des réponses vides
            if total_blanks_in_content > len(correct_answers):
                for i in range(len(correct_answers), total_blanks_in_content):
                    correct_answers.append("")
                content['words'] = correct_answers
                needs_fixing = True
                print(f"[INFO] Correction: Ajout de {total_blanks_in_content - len(correct_answers)} réponses vides")
            
            # Si le nombre de réponses est supérieur au nombre de blancs, supprimer les réponses en trop
            elif len(correct_answers) > total_blanks_in_content:
                content['words'] = correct_answers[:total_blanks_in_content]
                needs_fixing = True
                print(f"[INFO] Correction: Suppression de {len(correct_answers) - total_blanks_in_content} réponses en trop")
        
        if needs_fixing:
            # Mettre à jour l'exercice dans la base de données
            new_content = json.dumps(content, ensure_ascii=False)
            connection.execute(
                text("UPDATE exercise SET content = :content WHERE id = :id"),
                {"content": new_content, "id": exercise.id}
            )
            connection.commit()
            print(f"[SUCCÈS] Exercice '{exercise.title}' (ID: {exercise.id}) corrigé avec succès!")
            return True
        else:
            print(f"[INFO] Aucune correction nécessaire pour l'exercice '{exercise.title}' (ID: {exercise.id}).")
            return False
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la correction de l'exercice: {e}")
        return False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Corriger l'exercice 'Les coordonnées'")
    parser.add_argument("--check-only", action="store_true", help="Vérifier seulement, sans appliquer les corrections")
    args = parser.parse_args()
    
    print("[INFO] Connexion à la base de données...")
    connection = connect_to_db()
    if not connection:
        sys.exit(1)
    
    try:
        print("[INFO] Recherche de l'exercice 'Les coordonnées'...")
        exercise = find_coordonnees_exercise(connection)
        if not exercise:
            sys.exit(1)
        
        print("[INFO] Analyse du contenu de l'exercice...")
        is_consistent = analyze_exercise_content(exercise)
        
        if args.check_only:
            print("[INFO] Mode vérification uniquement. Aucune modification effectuée.")
            sys.exit(0 if is_consistent else 1)
        
        if not is_consistent:
            print("[INFO] Tentative de correction de l'exercice...")
            fixed = fix_exercise(connection, exercise)
            if fixed:
                print("[SUCCÈS] Exercice corrigé avec succès!")
            else:
                print("[INFO] Aucune correction appliquée.")
        else:
            print("[INFO] L'exercice semble déjà correct, aucune correction nécessaire.")
        
    finally:
        if connection:
            connection.close()
            print("[INFO] Connexion à la base de données fermée.")
    
    print("\n[SUCCÈS] Opération terminée!")

if __name__ == "__main__":
    main()
