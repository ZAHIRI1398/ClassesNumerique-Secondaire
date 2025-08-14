#!/usr/bin/env python3
"""
Script pour créer des images de placeholder pour les exercices manquants
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_image(filename, exercise_title="Exercice", width=800, height=400):
    """Crée une image de placeholder avec le titre de l'exercice"""
    try:
        # Créer une image avec un fond dégradé
        img = Image.new('RGB', (width, height), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Dessiner un rectangle de bordure
        draw.rectangle([10, 10, width-10, height-10], outline='#cccccc', width=3)
        
        # Ajouter le texte
        try:
            # Essayer d'utiliser une police système
            font_large = ImageFont.truetype("arial.ttf", 36)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            # Utiliser la police par défaut si arial n'est pas disponible
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Texte principal
        text1 = "IMAGE DE L'EXERCICE"
        text2 = exercise_title
        text3 = "Image temporairement indisponible"
        
        # Calculer les positions pour centrer le texte
        bbox1 = draw.textbbox((0, 0), text1, font=font_large)
        bbox2 = draw.textbbox((0, 0), text2, font=font_large)
        bbox3 = draw.textbbox((0, 0), text3, font=font_small)
        
        x1 = (width - (bbox1[2] - bbox1[0])) // 2
        x2 = (width - (bbox2[2] - bbox2[0])) // 2
        x3 = (width - (bbox3[2] - bbox3[0])) // 2
        
        y1 = height // 2 - 60
        y2 = height // 2 - 10
        y3 = height // 2 + 40
        
        # Dessiner les textes
        draw.text((x1, y1), text1, fill='#666666', font=font_large)
        draw.text((x2, y2), text2, fill='#333333', font=font_large)
        draw.text((x3, y3), text3, fill='#999999', font=font_small)
        
        return img
        
    except Exception as e:
        print(f"Erreur lors de la creation de l'image placeholder: {e}")
        # Créer une image très simple en cas d'erreur
        img = Image.new('RGB', (width, height), color='#f0f0f0')
        return img

def main():
    """Crée des images de placeholder pour les exercices manquants"""
    
    # Images connues manquantes (basées sur les exercices vus)
    missing_images = [
        ("Capture d'écran 2025-08-14 145027_20250814_182421_Da3gvm.png", "Les coordonnées"),
        ("triangle.png", "Exercice Triangle"),
        ("clopepe.png", "Droite Graduée"),
        ("corps_humain_exemple.jpg", "Corps Humain")
    ]
    
    # Créer le répertoire static/uploads s'il n'existe pas
    uploads_dir = Path('static/uploads')
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creation d'images de placeholder...")
    print("=" * 50)
    
    for filename, title in missing_images:
        output_path = uploads_dir / filename
        
        if not output_path.exists():
            print(f"Creation: {filename} pour '{title}'")
            
            # Créer l'image de placeholder
            placeholder_img = create_placeholder_image(filename, title)
            
            # Sauvegarder l'image
            try:
                placeholder_img.save(output_path, 'PNG')
                print(f"  -> Sauvegarde reussie: {output_path}")
            except Exception as e:
                print(f"  -> Erreur sauvegarde: {e}")
        else:
            print(f"Existe deja: {filename}")
    
    print("\n" + "=" * 50)
    print("TERMINE: Images de placeholder creees")
    print("Les exercices devraient maintenant afficher des images temporaires")

if __name__ == "__main__":
    main()
