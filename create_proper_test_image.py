from PIL import Image, ImageDraw, ImageFont
import os

# Create a proper test image for the QCM exercise
def create_test_image():
    # Create a new image with white background
    width, height = 400, 300
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simple diagram representing a digestive system
    # Draw stomach (oval)
    draw.ellipse([150, 80, 250, 140], fill='lightblue', outline='blue', width=2)
    
    # Draw intestines (rectangles)
    draw.rectangle([120, 140, 180, 200], fill='lightgreen', outline='green', width=2)
    draw.rectangle([180, 140, 240, 200], fill='lightgreen', outline='green', width=2)
    draw.rectangle([240, 140, 280, 200], fill='lightgreen', outline='green', width=2)
    
    # Add numbers for the QCM question
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    # Add labels with numbers
    draw.text((170, 50), "1", fill='red', font=font)
    draw.text((200, 110), "2", fill='red', font=font)
    draw.text((140, 170), "3", fill='red', font=font)
    draw.text((200, 170), "4", fill='red', font=font)
    
    # Add title
    draw.text((120, 20), "Appareil Digestif", fill='black', font=font)
    
    return image

# Create the image
test_image = create_test_image()

# Save it to replace the empty file
image_path = "static/uploads/Capture d'écran 2025-08-12 174224_20250823_141027_v17mTz.png"
test_image.save(image_path, 'PNG')

print(f"Created test image: {image_path}")
print(f"Image size: {os.path.getsize(image_path)} bytes")

# Also create a backup with a simpler name
backup_path = "static/uploads/qcm_digestive_system_test.png"
test_image.save(backup_path, 'PNG')
print(f"Backup created: {backup_path}")
