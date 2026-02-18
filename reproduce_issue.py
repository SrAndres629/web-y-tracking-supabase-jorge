import sys
import os

# Add app to path
sys.path.insert(0, os.getcwd())

try:
    print("Attempting to import app.infrastructure.config.settings...")
    from app.infrastructure.config.settings import settings
    print("Success!")
except Exception as e:
    print(f"Failed with error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nAttempting to import main and start TestClient...")
    from main import app
    from fastapi.testclient import TestClient
    
    print("Initializing TestClient...")
    with TestClient(app) as client:
        print("TestClient started successfully!")
        response = client.get("/")
        print(f"Root response: {response.status_code}")
        
    print("Success!")
except Exception as e:
    print(f"Failed with error: {e}")
    import traceback
    traceback.print_exc()

