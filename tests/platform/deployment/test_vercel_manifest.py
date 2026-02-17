import glob
import json
import os
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_vercel_include_files_physical_contract():
    """
    CONTRACT: Any glob pattern in vercel.json 'includeFiles' MUST resolve to at least one file.
    """
    vercel_json_path = PROJECT_ROOT / "vercel.json"
    assert vercel_json_path.exists(), "🔥 vercel.json missing from project root!"

    with open(vercel_json_path, "r") as f:
        config = json.load(f)

    # Check both ways it might be defined (old vs new schema we fixed)
    include_files = config.get("functions", {}).get("api/index.py", {}).get("includeFiles")
    if not include_files:
        # Fallback check for alternate structures
        include_files = config.get("includeFiles")

    assert include_files, "🔥 No includeFiles defined in vercel.json!"

    if isinstance(include_files, list):
        raw_patterns = include_files
    elif isinstance(include_files, str):
        raw_patterns = [include_files]
    else:
        raise AssertionError(
            f"🔥 includeFiles has unsupported type: {type(include_files).__name__}"
        )

    patterns = []
    for item in raw_patterns:
        match = re.match(r"^\{(.*)\}$", item)
        if match:
            patterns.extend([p.strip() for p in match.group(1).split(",") if p.strip()])
        else:
            patterns.append(item)

    for pattern in patterns:
        search_pattern = str(PROJECT_ROOT / pattern)
        matches = glob.glob(search_pattern, recursive=True)
        assert len(matches) > 0, (
            f"🔥 Glob '{pattern}' (expanded as '{search_pattern}') matched ZERO files. Vercel deployment will miss these!"
        )


def test_critical_templates_not_ignored_by_git():
    """
    CONTRACT: 'api/templates/pages/site/home.html' MUST be tracked by Git.
    This would have caught the '.gitignore: site/' trap.
    """
    critical_file = "api/templates/pages/site/home.html"
    abs_path = PROJECT_ROOT / critical_file

    assert abs_path.exists(), f"🔥 Critical file physically missing: {critical_file}"

    # Check if git ignores it
    result = subprocess.run(
        ["git", "check-ignore", critical_file],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    # If exit code is 0, it means the file IS ignored.
    # If exit code is 1, it means it's NOT ignored.
    assert result.returncode != 0, (
        f"🔥 CRITICAL FAILURE: {critical_file} is IGNORED by git. "
        "Vercel will NOT see this file. Check .gitignore!"
    )


def test_public_folder_name_taboo():
    """
    CONTRACT: No folder named 'public' should exist in templates (Vercel Python Runtime Filter).
    """
    templates_dir = PROJECT_ROOT / "api" / "templates"
    for root, dirs, _ in os.walk(templates_dir):
        assert "public" not in dirs, (
            f"🔥 FORBIDDEN FOLDER NAME: Found 'public' in {root}. "
            "Vercel implicitly ignores folders named 'public' in Python builds."
        )
