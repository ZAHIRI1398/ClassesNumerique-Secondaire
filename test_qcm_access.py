import requests
import json

# Test accessing the QCM exercise directly
base_url = "http://127.0.0.1:5000"

# Test the exercise view endpoint
exercise_id = 4  # The "Test image QCM" exercise
url = f"{base_url}/exercise/{exercise_id}"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("[OK] Exercise page accessible")
        # Check if the image path is in the response
        if "/static/uploads/Capture" in response.text:
            print("[OK] Image path found in HTML response")
        else:
            print("[ERROR] Image path not found in HTML response")
            
        # Check for the image tag
        if '<img src=' in response.text:
            print("[OK] Image tag found in response")
            # Extract the image src for verification
            import re
            img_matches = re.findall(r'<img[^>]+src="([^"]+)"', response.text)
            if img_matches:
                print(f"Image sources found: {img_matches}")
        else:
            print("[ERROR] No image tag found")
            
    else:
        print(f"[ERROR] Error accessing exercise: {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("[ERROR] Cannot connect to Flask app. Make sure it's running on port 5000")
except Exception as e:
    print(f"[ERROR] Error: {e}")

# Also test direct image access
image_path = "/static/uploads/Capture d'écran 2025-08-12 174224_20250823_141027_v17mTz.png"
image_url = f"{base_url}{image_path}"

try:
    img_response = requests.get(image_url)
    print(f"\nImage access status: {img_response.status_code}")
    if img_response.status_code == 200:
        print(f"[OK] Image accessible, size: {len(img_response.content)} bytes")
        if len(img_response.content) == 0:
            print("[WARNING] Image file is empty (0 bytes)")
    else:
        print(f"[ERROR] Image not accessible: {img_response.status_code}")
except Exception as e:
    print(f"[ERROR] Error accessing image: {e}")
