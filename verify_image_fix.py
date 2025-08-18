"""
Script de vérification de la correction d'affichage d'images en production
"""

import os
import sys
import json
import requests
import argparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tabulate import tabulate

def verify_image_fix(base_url, verbose=False):
    """
    Vérifie que la solution de correction d'affichage d'images fonctionne correctement
    
    Args:
        base_url: URL de base de l'application (ex: https://votre-app.railway.app)
        verbose: Afficher les détails complets
    """
    results = {
        "fix_uploads_directory": {"status": "Non testé", "details": None},
        "check_image_paths": {"status": "Non testé", "details": None},
        "create_placeholder_images": {"status": "Non testé", "details": None},
        "sample_exercises": {"status": "Non testé", "details": None}
    }
    
    print(f"Vérification de la correction d'affichage d'images sur {base_url}")
    
    # 1. Vérifier la route fix-uploads-directory
    try:
        print("\n1. Vérification de la création du répertoire uploads...")
        response = requests.get(urljoin(base_url, "/fix-uploads-directory"), timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                results["fix_uploads_directory"]["status"] = "✅ Succès"
                results["fix_uploads_directory"]["details"] = data
                print(f"✅ Répertoire créé avec succès: {data.get('path')}")
            else:
                results["fix_uploads_directory"]["status"] = "❌ Échec"
                results["fix_uploads_directory"]["details"] = data
                print(f"❌ Échec de création du répertoire: {data.get('error', 'Erreur inconnue')}")
        else:
            results["fix_uploads_directory"]["status"] = f"❌ Erreur HTTP {response.status_code}"
            print(f"❌ Erreur HTTP {response.status_code}")
    except Exception as e:
        results["fix_uploads_directory"]["status"] = f"❌ Exception: {str(e)}"
        print(f"❌ Exception: {str(e)}")
    
    # 2. Vérifier la route check-image-paths
    try:
        print("\n2. Analyse des chemins d'images...")
        response = requests.get(urljoin(base_url, "/check-image-paths"), timeout=10)
        
        if response.status_code == 200:
            # Analyser le HTML pour extraire les informations
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire le résumé
            summary = {}
            summary_section = soup.find('div', class_='mb-4')
            if summary_section:
                for li in summary_section.find_all('li'):
                    key, value = li.text.split(':', 1)
                    summary[key.strip()] = value.strip()
            
            # Extraire les détails des images
            images = []
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        image = {
                            "id": cols[0].text.strip(),
                            "title": cols[1].text.strip(),
                            "path": cols[2].text.strip(),
                            "type": cols[3].text.strip(),
                            "status": cols[4].text.strip(),
                            "normalized": cols[5].text.strip()
                        }
                        images.append(image)
            
            results["check_image_paths"]["status"] = "✅ Succès"
            results["check_image_paths"]["details"] = {
                "summary": summary,
                "images": images[:10] if not verbose else images  # Limiter le nombre d'images dans le résultat
            }
            
            # Afficher un résumé
            print(f"✅ Analyse terminée:")
            for key, value in summary.items():
                print(f"   - {key}: {value}")
        else:
            results["check_image_paths"]["status"] = f"❌ Erreur HTTP {response.status_code}"
            print(f"❌ Erreur HTTP {response.status_code}")
    except Exception as e:
        results["check_image_paths"]["status"] = f"❌ Exception: {str(e)}"
        print(f"❌ Exception: {str(e)}")
    
    # 3. Vérifier la route create-placeholder-images
    try:
        print("\n3. Création d'images placeholder...")
        response = requests.get(urljoin(base_url, "/create-placeholder-images"), timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                results["create_placeholder_images"]["status"] = "✅ Succès"
                results["create_placeholder_images"]["details"] = {
                    "created_count": data.get("created_count", 0),
                    "created_images": data.get("created_images", [])[:5] if not verbose else data.get("created_images", [])
                }
                print(f"✅ {data.get('created_count', 0)} images placeholder créées")
            else:
                results["create_placeholder_images"]["status"] = "❌ Échec"
                results["create_placeholder_images"]["details"] = data
                print(f"❌ Échec de création des images: {data.get('error', 'Erreur inconnue')}")
        else:
            results["create_placeholder_images"]["status"] = f"❌ Erreur HTTP {response.status_code}"
            print(f"❌ Erreur HTTP {response.status_code}")
    except Exception as e:
        results["create_placeholder_images"]["status"] = f"❌ Exception: {str(e)}"
        print(f"❌ Exception: {str(e)}")
    
    # 4. Vérifier quelques exercices avec images
    if results["check_image_paths"]["details"] and results["check_image_paths"]["details"]["images"]:
        print("\n4. Vérification d'exercices avec images...")
        
        # Prendre jusqu'à 3 exercices pour vérification
        exercises_to_check = results["check_image_paths"]["details"]["images"][:3]
        exercise_results = []
        
        for ex in exercises_to_check:
            ex_id = ex["id"]
            try:
                # Vérifier la page de l'exercice
                response = requests.get(urljoin(base_url, f"/exercise/{ex_id}"), timeout=10)
                
                if response.status_code == 200:
                    # Vérifier si l'image est présente dans la page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    images = soup.find_all('img')
                    
                    # Chercher une image qui correspond au chemin normalisé
                    image_found = False
                    normalized_path = ex["normalized"].strip('<code>').strip('</code>')
                    
                    for img in images:
                        src = img.get('src', '')
                        if normalized_path in src or ex["path"].strip('<code>').strip('</code>') in src:
                            image_found = True
                            break
                    
                    status = "✅ Image trouvée" if image_found else "❌ Image manquante"
                    exercise_results.append({
                        "id": ex_id,
                        "title": ex["title"],
                        "status": status,
                        "http_status": response.status_code
                    })
                    print(f"   - Exercice #{ex_id} ({ex['title']}): {status}")
                else:
                    exercise_results.append({
                        "id": ex_id,
                        "title": ex["title"],
                        "status": f"❌ Erreur HTTP {response.status_code}",
                        "http_status": response.status_code
                    })
                    print(f"   - Exercice #{ex_id} ({ex['title']}): ❌ Erreur HTTP {response.status_code}")
            except Exception as e:
                exercise_results.append({
                    "id": ex_id,
                    "title": ex["title"],
                    "status": f"❌ Exception: {str(e)}",
                    "http_status": None
                })
                print(f"   - Exercice #{ex_id} ({ex['title']}): ❌ Exception: {str(e)}")
        
        results["sample_exercises"]["status"] = "✅ Vérifié"
        results["sample_exercises"]["details"] = exercise_results
    
    # Afficher un résumé final
    print("\n=== Résumé de la vérification ===")
    table_data = []
    for key, value in results.items():
        table_data.append([key.replace("_", " ").title(), value["status"]])
    
    print(tabulate(table_data, headers=["Test", "Statut"], tablefmt="grid"))
    
    # Sauvegarder les résultats dans un fichier JSON
    with open('verification_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\nRésultats détaillés sauvegardés dans verification_results.json")
    
    # Retourner True si tous les tests ont réussi
    return all(result["status"].startswith("✅") for result in results.values())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vérifier la correction d'affichage d'images")
    parser.add_argument("url", help="URL de base de l'application (ex: https://votre-app.railway.app)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Afficher les détails complets")
    args = parser.parse_args()
    
    try:
        success = verify_image_fix(args.url, args.verbose)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Erreur lors de la vérification: {str(e)}")
        sys.exit(1)
