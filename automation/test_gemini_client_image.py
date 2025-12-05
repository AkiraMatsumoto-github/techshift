import os
import sys
from dotenv import load_dotenv

# Add current directory to path to import automation modules
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from automation.gemini_client import GeminiClient

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

def test_image_generation():
    print("Initializing GeminiClient...")
    client = GeminiClient()
    
    prompt = "A futuristic logistics warehouse with autonomous robots, photorealistic, 4k"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_client_image.png')
    
    print(f"Testing generate_image with prompt: {prompt}")
    result = client.generate_image(prompt, output_path)
    
    if result and os.path.exists(result):
        print(f"SUCCESS: Image generated at {result}")
        # Verify file size is not zero
        size = os.path.getsize(result)
        print(f"Image size: {size} bytes")
        
        # Verify dimensions
        from PIL import Image
        with Image.open(result) as img:
            width, height = img.size
            ratio = width / height
            print(f"Image dimensions: {width}x{height}")
            print(f"Aspect ratio: {ratio:.2f}")
            
            if 1.7 <= ratio <= 1.85:
                print("Aspect ratio is approximately 16:9 (PASS)")
            else:
                print("Aspect ratio is NOT 16:9 (FAIL)")
    else:
        print("FAILURE: Image generation failed.")

if __name__ == "__main__":
    test_image_generation()
