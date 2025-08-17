#!/usr/bin/env python3
"""
Script pour corriger l'affichage du feedback pour les exercices fill_in_blanks 
avec plusieurs mots par ligne
"""

import os
import re
import sys
import json
import shutil
from datetime import datetime

# Fonction pour créer une sauvegarde du fichier app.py
def backup_app_py():
    """Crée une sauvegarde du fichier app.py"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"app.py.bak.{timestamp}"
    
    try:
        shutil.copy2("app.py", backup_filename)
        print(f"✅ Sauvegarde créée: {backup_filename}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

# Fonction pour modifier le template feedback.html
def fix_feedback_template():
    """Modifie le template feedback.html pour améliorer l'affichage des exercices fill_in_blanks"""
    template_path = "templates/feedback.html"
    
    if not os.path.exists(template_path):
        print(f"❌ Le fichier {template_path} n'existe pas")
        return False
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Rechercher le bloc fill_in_blanks existant
        fill_in_blanks_pattern = r'{% elif exercise\.exercise_type == \'fill_in_blanks\' %}(.*?){% elif'
        fill_in_blanks_block = re.search(fill_in_blanks_pattern, content, re.DOTALL)
        
        if not fill_in_blanks_block:
            print("❌ Bloc fill_in_blanks non trouvé dans le template")
            return False
        
        # Nouveau bloc avec support amélioré pour plusieurs mots par ligne
        new_fill_in_blanks_block = """{% elif exercise.exercise_type == 'fill_in_blanks' %}
                    {% if feedback.details is defined %}
                        {# Nouveau format de feedback avec détails #}
                        {% set sentences = {} %}
                        {% for item in feedback.details %}
                            {% if item.sentence_index is defined %}
                                {% if sentences[item.sentence_index] is not defined %}
                                    {% set _ = sentences.__setitem__(item.sentence_index, {
                                        'sentence': item.sentence if item.sentence is defined else '',
                                        'blanks': []
                                    }) %}
                                {% endif %}
                                {% set _ = sentences[item.sentence_index].blanks.append({
                                    'blank_index': item.blank_index,
                                    'user_answer': item.user_answer,
                                    'correct_answer': item.correct_answer,
                                    'is_correct': item.is_correct
                                }) %}
                            {% else %}
                                {# Format de détails simple #}
                                <div class="card mb-3">
                                    <div class="card-body">
                                        <h5 class="card-title">Réponse {{ loop.index }}</h5>
                                        <p class="mb-2"><strong>Votre réponse:</strong> {{ item.user_answer }}</p>
                                        <p class="mb-2"><strong>Réponse correcte:</strong> {{ item.correct_answer }}</p>
                                        <div class="alert {{ 'alert-success' if item.is_correct else 'alert-danger' }}">
                                            <strong>{{ 'Correct' if item.is_correct else 'Incorrect' }}</strong>
                                        </div>
                                    </div>
                                </div>
                            {% endif %}
                        {% endfor %}
                        
                        {# Afficher les phrases regroupées #}
                        {% for sentence_index, sentence_data in sentences.items() %}
                            <div class="card mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">Phrase {{ sentence_index + 1 }}</h5>
                                    <p class="mb-2"><strong>Phrase avec trous:</strong> {{ sentence_data.sentence }}</p>
                                    
                                    {% for blank in sentence_data.blanks %}
                                        <div class="mb-3">
                                            <p class="mb-1"><strong>Blanc {{ blank.blank_index + 1 }}:</strong></p>
                                            <p class="mb-1"><strong>Votre réponse:</strong> {{ blank.user_answer }}</p>
                                            <p class="mb-1"><strong>Réponse correcte:</strong> {{ blank.correct_answer }}</p>
                                            <div class="alert {{ 'alert-success' if blank.is_correct else 'alert-danger' }} mt-2 mb-2">
                                                <strong>{{ 'Correct' if blank.is_correct else 'Incorrect' }}</strong>
                                            </div>
                                        </div>
                                    {% endfor %}
                                </div>
                            </div>
                        {% endfor %}
                    {% else %}
                        {# Ancien format de feedback #}
                        {% for item in feedback %}
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title">Phrase {{ loop.index }}</h5>
                                <p class="mb-2"><strong>Phrase avec trous:</strong> {{ item.sentence }}</p>
                                <p class="mb-2"><strong>Votre réponse:</strong> {{ item.student_answer }}</p>
                                <div class="alert {{ 'alert-success' if item.is_correct else 'alert-danger' }}">
                                    <strong>{{ 'Correct' if item.is_correct else 'Incorrect' }}</strong>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    {% endif %}
                {% elif"""
        
        # Remplacer le bloc existant
        new_content = re.sub(fill_in_blanks_pattern, new_fill_in_blanks_block, content, flags=re.DOTALL)
        
        # Sauvegarder le template modifié
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"✅ Template {template_path} modifié avec succès")
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors de la modification du template: {e}")
        return False

# Fonction pour modifier le code de préparation du feedback dans app.py
def fix_feedback_preparation():
    """Modifie la préparation du feedback dans app.py pour les exercices fill_in_blanks"""
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Rechercher le bloc de création du feedback pour fill_in_blanks
        feedback_pattern = r'# Créer le feedback pour ce blanc\s+feedback_details\.append\(\{\s+\'blank_index\': i,\s+\'user_answer\': user_answer or \'\',\s+\'correct_answer\': correct_answer,\s+\'is_correct\': is_correct,\s+\'status\': \'Correct\' if is_correct else f\'Attendu: \{correct_answer\}, Réponse: \{user_answer or "Vide"\}\'\s+\}\)'
        
        # Nouveau bloc avec support pour l'index de phrase
        new_feedback_block = """# Créer le feedback pour ce blanc
                # Déterminer l'index de la phrase à laquelle appartient ce blanc
                sentence_index = -1
                if 'sentences' in content:
                    blank_count = 0
                    for idx, sentence in enumerate(content['sentences']):
                        blanks_in_sentence = sentence.count('___')
                        if blank_count <= i < blank_count + blanks_in_sentence:
                            sentence_index = idx
                            break
                        blank_count += blanks_in_sentence
                
                feedback_details.append({
                    'blank_index': i,
                    'user_answer': user_answer or '',
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}',
                    'sentence_index': sentence_index,
                    'sentence': content['sentences'][sentence_index] if sentence_index >= 0 and 'sentences' in content else ''
                })"""
        
        # Remplacer tous les blocs correspondants
        new_content = re.sub(feedback_pattern, new_feedback_block, content)
        
        # Sauvegarder le fichier modifié
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"✅ Préparation du feedback modifiée dans app.py")
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors de la modification de app.py: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔍 Correction du problème d'affichage du feedback pour les exercices fill_in_blanks avec plusieurs mots par ligne")
    
    # Créer une sauvegarde
    if not backup_app_py():
        print("❌ Impossible de continuer sans sauvegarde")
        return
    
    # Modifier le template feedback.html
    if not fix_feedback_template():
        print("❌ Échec de la modification du template")
        return
    
    # Modifier la préparation du feedback dans app.py
    if not fix_feedback_preparation():
        print("❌ Échec de la modification de app.py")
        return
    
    print("✅ Modifications terminées avec succès")
    print("ℹ️ Veuillez redémarrer l'application Flask pour appliquer les modifications")

if __name__ == "__main__":
    main()
