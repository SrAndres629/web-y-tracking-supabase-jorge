import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_vercel_includes_required_paths():
    vercel_path = PROJECT_ROOT / "vercel.json"
    config = json.loads(vercel_path.read_text(encoding="utf-8"))

    include_paths = []

    # Collect from builds array
    for build in config.get("builds", []):
        build_config = build.get("config", {})
        include_files = build_config.get("includeFiles", [])
        if isinstance(include_files, list):
            include_paths.extend(include_files)

    # Collect from functions object
    for fn_config in config.get("functions", {}).values():
        include_files = fn_config.get("includeFiles", [])
        if isinstance(include_files, list):
            include_paths.extend(include_files)
        elif isinstance(include_files, str):
            # Handle string glob (e.g. "path/a/**,path/b/**")
            # Strip braces if present
            clean_str = include_files.strip("{}")
            include_paths.extend([p.strip() for p in clean_str.split(",")])

    assert "api/templates/**" in include_paths, f"api/templates/** not found in {include_paths}"
    assert "static/**" in include_paths, f"static/** not found in {include_paths}"
    assert "app/templates/**" not in include_paths, (
        f"app/templates/** (legacy) should not be in {include_paths}"
    )


def test_required_directories_exist_for_serverless_packaging():
    assert (PROJECT_ROOT / "api" / "templates").exists()
    assert (PROJECT_ROOT / "static").exists()
