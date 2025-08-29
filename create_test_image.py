import os

# Créer le répertoire s'il n'existe pas
os.makedirs('static/uploads', exist_ok=True)

# Créer une image SVG simple
svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#e3f2fd"/>
  <text x="50" y="100" font-family="Arial" font-size="24" fill="#1976d2">Image de test QCM</text>
  <text x="50" y="150" font-family="Arial" font-size="20" fill="#0d47a1">Appareil digestif</text>
  <circle cx="320" cy="80" r="30" fill="#4caf50"/>
  <rect x="280" y="180" width="80" height="60" fill="#ff9800" rx="10"/>
</svg>'''

# Sauvegarder l'image SVG
with open('static/uploads/qcm_test_image.png', 'w', encoding='utf-8') as f:
    f.write(svg_content)

print("Image de test créée: static/uploads/qcm_test_image.png")
