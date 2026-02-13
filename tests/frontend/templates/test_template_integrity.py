import os
import pytest
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = BASE_DIR / "api" / "templates"

def test_jinja2_template_syntax():
    """
    Scans all .html files in the templates directory and attempts to 
    compile them with Jinja2. This catches missing endblocks, 
    incorrect tags, and structural errors.
    """
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    
    html_files = []
    for root, _, files in os.walk(str(TEMPLATES_DIR)):
        for file in files:
            if file.endswith(".html"):
                relative_path = Path(root).relative_to(TEMPLATES_DIR) / file
                html_files.append(str(relative_path).replace("\\", "/"))
    assert html_files, f"No templates found under {TEMPLATES_DIR}"

    errors = []
    for template_path in html_files:
        try:
            # Attempt to compile the template source
            env.get_template(template_path)
        except TemplateSyntaxError as e:
            errors.append(f"❌ {template_path}:{e.lineno} - {e.message}")
        except Exception as e:
            errors.append(f"⚠️ {template_path}: Unexpected error - {str(e)}")

    if errors:
        pytest.fail("\n".join(["🔥 JINJA2 SYNTAX ERRORS DETECTED:"] + errors))
    else:
        # print(f"\n✅ Template Integrity: {len(html_files)} files verified.")
        pass
