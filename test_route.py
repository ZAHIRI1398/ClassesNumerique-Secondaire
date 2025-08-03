#!/usr/bin/env python3
"""
Test direct de la route handle_exercise_answer
"""

import requests

def test_route():
    """Test direct de la route handle_exercise_answer"""
    url = "http://127.0.0.1:5000/exercise/8/answer"
    
    # Données de test pour drag_and_drop
    data = {
        'csrf_token': 'test',
        'answer_0': '1',  # Banane
        'answer_1': '2',  # Cerise  
        'answer_2': '3',  # Pomme
        'answer_3': '0'   # Ananas
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return response.status_code == 200 or response.status_code == 302
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == '__main__':
    print("=== TEST ROUTE handle_exercise_answer ===")
    success = test_route()
    print(f"Route accessible: {'✅ OUI' if success else '❌ NON'}")
