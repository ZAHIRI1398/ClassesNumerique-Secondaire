import json
from app import app, db, Exercise

def analyze_exercise(exercise_id):
    """Analyser la structure d'un exercice de type texte à trous."""
    with app.app_context():
        exercise = Exercise.query.filter_by(id=exercise_id).first()
        
        if not exercise:
            print(f"Exercice avec ID {exercise_id} non trouvé.")
            return
        
        print(f"Exercice ID: {exercise.id}")
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        
        # Convertir le contenu JSON en dictionnaire Python
        content_str = exercise.content
        print(f"Contenu brut: {content_str}")
        
        try:
            content = json.loads(content_str) if isinstance(content_str, str) else content_str
        except json.JSONDecodeError:
            print("⚠️ ERREUR: Impossible de décoder le contenu JSON")
            return
        
        # Analyse détaillée du contenu
        if exercise.exercise_type == 'fill_in_blanks':
            print("\nAnalyse détaillée du texte à trous:")
            
            # Vérifier les formats possibles
            if 'sentences' in content:
                print(f"Format 'sentences' détecté: {content.get('sentences')}")
                blanks_count = sum(s.count('___') for s in content.get('sentences', []))
                print(f"Nombre de blancs dans 'sentences': {blanks_count}")
            
            if 'text' in content:
                print(f"Format 'text' détecté: {content.get('text')}")
                blanks_count = content.get('text', '').count('___')
                print(f"Nombre de blancs dans 'text': {blanks_count}")
            
            # Analyser les mots disponibles
            if 'words' in content:
                words = content.get('words', [])
                print(f"Mots disponibles: {words}")
                print(f"Nombre de mots: {len(words)}")
                
                # Vérifier le format des mots (string vs dict)
                if words and isinstance(words[0], dict):
                    print("Format des mots: dictionnaire avec clé 'word'")
                    words_list = [w.get('word', '') for w in words]
                    print(f"Mots extraits: {words_list}")
                else:
                    print("Format des mots: chaînes de caractères simples")
            
            if 'available_words' in content:
                available_words = content.get('available_words', [])
                print(f"Mots disponibles (available_words): {available_words}")
                print(f"Nombre de mots (available_words): {len(available_words)}")
            
            # Vérifier la cohérence
            total_blanks = 0
            if 'sentences' in content:
                total_blanks = sum(s.count('___') for s in content.get('sentences', []))
            elif 'text' in content:
                total_blanks = content.get('text', '').count('___')
            
            total_words = len(content.get('words', [])) + len(content.get('available_words', []))
            
            print(f"\nCohérence: {total_blanks} blancs vs {total_words} mots")
            if total_blanks != total_words:
                print("PROBLEME DETECTE: Le nombre de blancs ne correspond pas au nombre de mots!")
            else:
                print("OK: Le nombre de blancs correspond au nombre de mots.")
                
            # Analyser le problème spécifique de l'exercice
            print("\nAnalyse du problème de scoring:")
            if 'sentences' in content:
                sentences = content.get('sentences', [])
                for i, sentence in enumerate(sentences):
                    print(f"Phrase {i+1}: '{sentence}'")
                    blanks = sentence.count('___')
                    print(f"  - Nombre de blancs: {blanks}")
                    
                    # Vérifier si les blancs sont séparés par du texte
                    if '___<___' in sentence:
                        print("  PROBLEME DETECTE: Blancs adjacents separes uniquement par '<'")
                        print("  -> Le systeme pourrait interpreter '<' comme faisant partie du texte a remplir")
                        print("  -> Solution: Ajouter des espaces autour des '<' pour les separer des blancs")

if __name__ == "__main__":
    analyze_exercise(7)  # Analyser l'exercice avec ID 7
