#!/usr/bin/env python3
import sys
import os
import json
import re

def validate_report(filepath):
    print(f"📊 [Session Reporter] Validando formato del reporte: {filepath}")
    
    if not os.path.exists(filepath):
        print("❌ Error: Report file does not exist.")
        sys.exit(1)

    with open(filepath, 'r') as f:
        content = f.read()

    # Validar Frontmatter (YAML)
    if not content.startswith("---"):
        print("❌ Error: Missing YAML frontmatter block.")
        sys.exit(1)

    # Validar JSON Block al final
    json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
    if not json_match:
        print("❌ Error: Missing or invalid JSON block at the end.")
        sys.exit(1)
        
    try:
        json_str = json_match.group(1)
        json_data = json.loads(json_str)
        if "session" not in json_data:
            print("❌ Error: JSON structure missing root 'session' key.")
            sys.exit(1)
            
        print("✅ Frontmatter (YAML) validado conceptualmente.")
        print("✅ Componente JSON validado estructuralmente.")
        print("🎉 ¡Reporte listo para almacenar en los registros de Élite!")

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON block parsing. {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_report.py <path_to_report.md>")
        sys.exit(1)
    
    validate_report(sys.argv[1])
