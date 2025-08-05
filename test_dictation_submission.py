#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
import requests
import json
import re

def test_dictation_submission():
    """Test la soumission d'un exercice de dictée"""
    
    # URL de l'exercice de dictée
    exercise_url = 'http://127.0.0.1:5000/exercise/12/answer'
    
    # Obtenir d'abord le token CSRF
    session = requests.Session()
    response = session.get('http://127.0.0.1:5000/exercise/12')
    print('Page chargée, status:', response.status_code)
    
    # Extraire le token CSRF de la réponse
    csrf_token = None
    if 'csrf_token' in response.text:
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
            print('Token CSRF trouvé:', csrf_token[:20] + '...')
    
    if not csrf_token:
        print('❌ Token CSRF non trouvé!')
        return
    
    # Données de test pour la soumission
    test_data = {
        'csrf_token': csrf_token,
        'dictation_answer_0': 'Le chat noir dort paisiblement sur le canape.',  # Phrase correcte
        'dictation_answer_1': 'Les enfants jouent dans le jardin fleuri.',      # Phrase correcte
        'dictation_answer_2': 'Ma grand-mere prepare un gateau au chocolat.'    # Phrase avec petites erreurs
    }
    
    print('\n📝 Données de test préparées:')
    for key, value in test_data.items():
        if key != 'csrf_token':
            print(f'  {key}: {value}')
    
    # Soumettre la réponse
    try:
        print('\n🚀 Soumission en cours...')
        response = session.post(exercise_url, data=test_data)
        print(f'Soumission effectuée, status: {response.status_code}')
        print(f'URL finale: {response.url}')
        
        if response.status_code == 200:
            print('✅ Soumission réussie!')
            
            # Vérifier si on a été redirigé vers la page d'exercice
            if '/exercise/12' in response.url:
                print('✅ Redirection vers la page d\'exercice confirmée')
                
                # Chercher des messages de feedback dans la réponse
                if 'Score' in response.text:
                    print('✅ Score détecté dans la réponse!')
                    
                    # Extraire le score si possible
                    score_match = re.search(r'Score\s*:\s*(\d+)', response.text)
                    if score_match:
                        score = score_match.group(1)
                        print(f'🎯 Score obtenu: {score}')
                
        else:
            print('❌ Erreur lors de la soumission')
            print('Contenu de la réponse:', response.text[:500])
            
    except Exception as e:
        print(f'❌ Erreur lors de la soumission: {str(e)}')

if __name__ == '__main__':
    test_dictation_submission()
