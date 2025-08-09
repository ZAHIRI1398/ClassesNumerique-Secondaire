import sqlite3
import json

def fix_exercise_18():
    conn = sqlite3.connect('instance/app.db')
    cursor = conn.cursor()
    
    try:
        # Récupérer l'exercice 18
        cursor.execute('SELECT id, title, content FROM exercise WHERE id = 18')
        result = cursor.fetchone()
        
        if result:
            print('=== EXERCICE 18 ACTUEL ===')
            content = json.loads(result[2])
            print('Zones:', len(content.get('zones', [])))
            print('Elements:', len(content.get('elements', [])))
            print()
            
            # Créer les éléments manquants à partir des zones
            if 'zones' in content and len(content['zones']) > 0:
                elements = []
                for i, zone in enumerate(content['zones']):
                    elements.append({
                        'id': i + 1,
                        'text': zone['legend'],
                        'type': 'text'
                    })
                
                content['elements'] = elements
                
                # Sauvegarder la correction
                cursor.execute('UPDATE exercise SET content = ? WHERE id = 18', (json.dumps(content, ensure_ascii=False),))
                conn.commit()
                
                print('=== EXERCICE 18 CORRIGÉ ===')
                print('Zones:', len(content.get('zones', [])))
                print('Elements:', len(content.get('elements', [])))
                print('Elements créés:')
                for elem in elements:
                    print(f'  - ID {elem["id"]}: "{elem["text"]}"')
                    
                print('\n✅ Correction appliquée avec succès!')
            else:
                print('❌ Aucune zone trouvée pour créer les éléments')
        else:
            print('❌ Exercice 18 non trouvé')
            
    except Exception as e:
        print(f'❌ Erreur: {e}')
    finally:
        conn.close()

if __name__ == '__main__':
    fix_exercise_18()
