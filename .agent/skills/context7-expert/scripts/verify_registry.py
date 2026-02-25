import json
import os

def verify():
    registry_path = os.path.join(os.path.dirname(__file__), "..", "resources", "PROJECT_LIB_IDS.json")
    print(f"Verifying registry at {registry_path}...")
    
    try:
        with open(registry_path, 'r') as f:
            data = json.load(f)
            libs = data.get('project_libraries', [])
            print(f"Found {len(libs)} registered libraries.")
            for lib in libs:
                print(f" - {lib['name']}: {lib['id']}")
        print("Success: Registry is valid JSON and contains library definitions.")
    except Exception as e:
        print(f"Error: Registry verification failed: {e}")

if __name__ == "__main__":
    verify()
