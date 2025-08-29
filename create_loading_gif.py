from PIL import Image, ImageDraw
import os

def create_loading_gif():
    """
    Crée une simple image GIF de chargement et la sauvegarde dans static/img/loading.gif
    """
    # Dimensions de l'image
    width, height = 200, 200
    
    # Créer une image blanche
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Dessiner un cercle bleu au centre
    circle_radius = 50
    circle_center = (width // 2, height // 2)
    circle_bbox = (
        circle_center[0] - circle_radius,
        circle_center[1] - circle_radius,
        circle_center[0] + circle_radius,
        circle_center[1] + circle_radius
    )
    draw.ellipse(circle_bbox, fill='lightblue', outline='blue')
    
    # Ajouter du texte
    draw.text((width // 2 - 30, height // 2 - 10), "Chargement...", fill='black')
    
    # Sauvegarder l'image
    output_path = os.path.join('static', 'img', 'loading.gif')
    img.save(output_path)
    
    print(f"Image de chargement créée: {output_path}")

if __name__ == "__main__":
    create_loading_gif()
