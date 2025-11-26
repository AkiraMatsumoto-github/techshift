import os
from dotenv import load_dotenv
import vertexai
from vertexai.preview.generative_models import GenerativeModel

load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")

print(f"Project: {project_id}, Location: {location}")

try:
    vertexai.init(project=project_id, location=location)
    # There isn't a direct list_models method in GenerativeModel class in all versions, 
    # but we can try to instantiate a model and see if it works, or use the Model Garden API if available.
    # A better way to list models is via the model garden service or just trying known models.
    # However, let's try to use the underlying API to list models if possible.
    
    # Using google-cloud-aiplatform directly to list models
    from google.cloud import aiplatform
    aiplatform.init(project=project_id, location=location)
    
    # This lists custom models, not necessarily foundation models.
    # Foundation models are usually queried differently.
    # Let's try to list publisher models.
    
    # This might be complex to implement quickly without the right library version docs.
    # Instead, let's try a simple test with a very basic model name like 'gemini-pro' again but print more debug info.
    
    print("Attempting to use gemini-2.5-flash-preview-09-2025...")
    model = GenerativeModel("gemini-2.5-flash-preview-09-2025")
    response = model.generate_content("Hello")
    print("Success with gemini-2.5-flash-preview-09-2025")
    print(response.text)

except Exception as e:
    print(f"Error: {e}")
