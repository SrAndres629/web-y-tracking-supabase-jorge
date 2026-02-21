
import os
import re

def find_and_patch_file():
    # Path to the gemini-cli installation
    gemini_cli_path = "/home/jorand/.nvm/versions/node/v24.13.1/lib/node_modules/@google/gemini-cli"
    
    # The string to search for
    search_string = "Gemini 3.1 Pro"
    
    found = False
    # Walk through the directory to find the file containing the string
    for root, _, files in os.walk(gemini_cli_path):
        for file in files:
            if file.endswith(('.js', '.json')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if search_string in content:
                        print(f"Found string in: {file_path}")
                        
                        # Comment out the line containing the string
                        new_content = []
                        for line in content.splitlines():
                            if search_string in line:
                                new_content.append(f"// {line}")
                            else:
                                new_content.append(line)
                        
                        # Write the new content back to the file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(new_content))
                        
                        print(f"Successfully patched: {file_path}")
                        found = True
                        return

                except Exception as e:
                    print(f"Could not read or write to {file_path}: {e}")
    if not found:
        print("Could not find the target string in any file.")

if __name__ == "__main__":
    find_and_patch_file()
