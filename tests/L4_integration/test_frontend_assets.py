import os


def test_css_bundling_integrity():
    """Verify that crucial CSS classes are present in the final bundle."""
    bundle_path = os.path.join(os.getcwd(), "static/dist/css/app.min.css")
    assert os.path.exists(bundle_path), "CSS bundle app.min.css missing"

    with open(bundle_path, "r") as f:
        content = f.read()

    # Check for modular classes that were previously missing
    assert "skip-link" in content, ".skip-link missing from CSS bundle"
    assert "glass-nav-premium" in content, ".glass-nav-premium missing from CSS bundle"
    assert "hero-image-container" in content, "Hero animation classes missing"


def test_template_selector_sync():
    """Verify that selectors used in JS engines exist in HTML templates."""
    # This is a static analysis test to prevent 'Broken Selector' regressions
    js_selectors = [".hero-portrait", ".slider-container", ".foreground-img", ".glass-nav-premium"]

    templates_dir = os.path.join(os.getcwd(), "api/templates")
    all_template_content = ""
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith(".html"):
                with open(os.path.join(root, file), "r") as f:
                    all_template_content += f.read()

    for selector in js_selectors:
        # Simple check for class existence (removing the dot)
        class_name = selector.replace(".", "")
        assert class_name in all_template_content, (
            f"Selector '{selector}' used in JS but not found in any HTML template"
        )


def test_javascript_bundle_availability():
    """Ensure all engine files are present and accessible."""
    base_js_path = "static/engines"
    engines = ["tracking/index.js", "motion/index.js", "ui/index.js", "legacy-adapter.js"]

    for engine in engines:
        full_path = os.path.join(os.getcwd(), base_js_path, engine)
        assert os.path.exists(full_path), f"JS Engine file {engine} missing"
