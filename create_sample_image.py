from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_image(output_path, text="Sample Image", width=600, height=300, bg_color=(255, 255, 200)):
    """
    Create a sample image with text for testing exercises
    """
    # Create a new image with a light yellow background
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Draw a border
    border_width = 5
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=(0, 0, 200),
        width=border_width
    )
    
    # Try to use a standard font that should be available on Windows
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        # Fallback to default font if arial is not available
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_width = draw.textlength(text, font=font)
    text_position = ((width - text_width) / 2, height / 2 - 18)
    
    # Draw the text
    draw.text(text_position, text, fill=(0, 0, 0), font=font)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the image
    image.save(output_path)
    print(f"Image created: {output_path}")

if __name__ == "__main__":
    # Create the sample image in the static/exercise_images directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(base_dir, 'static', 'exercise_images', 'sample.png')
    create_sample_image(sample_path)
    
    # Also create specific images for each exercise type
    create_sample_image(
        os.path.join(base_dir, 'static', 'uploads', 'qcm', 'decimal_numbers_qcm.png'),
        text="QCM Nombres Décimaux"
    )
    
    create_sample_image(
        os.path.join(base_dir, 'static', 'uploads', 'fill_in_blanks', 'decimal_numbers_fill.png'),
        text="Exercice à Trous - Nombres Décimaux"
    )
    
    create_sample_image(
        os.path.join(base_dir, 'static', 'uploads', 'pairs', 'decimal_numbers_pairs.png'),
        text="Exercice d'Appariement - Nombres Décimaux"
    )
    
    create_sample_image(
        os.path.join(base_dir, 'static', 'uploads', 'drag_drop', 'decimal_numbers_order.png'),
        text="Exercice Glisser-Déposer - Nombres Décimaux"
    )
    
    print("All sample images created successfully!")
