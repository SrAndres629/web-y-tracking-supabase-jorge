# =================================================================
# TEST_ZARAZ_TEMPLATES.PY - Template × Zaraz Compatibility Audit
# Validates that HTML templates are correctly configured for
# Cloudflare Zaraz (no duplicate tracking, proper noscript, etc.)
# =================================================================
import os
import re
from pathlib import Path

import pytest

# ─── Constants ───────────────────────────────────────────────────
PROJECT_ROOT = Path(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
TEMPLATES_DIR = PROJECT_ROOT / "api" / "templates"
TRACKING_DIR = PROJECT_ROOT / "static" / "engines" / "tracking"

# Patterns that indicate tracking conflicts
BANNED_PATTERNS = {
    # Direct fbq() init — Zaraz handles pixel initialization
    r'fbq\s*\(\s*["\']init["\']': "Direct fbq('init') call — Zaraz handles pixel initialization",
    # GTM container script — should not coexist with Zaraz
    r"googletagmanager\.com/gtm\.js": "Google Tag Manager script — conflicts with Zaraz",
    # Direct GA script — should be a Zaraz tool
    r"google-analytics\.com/analytics\.js": "Direct Google Analytics script — use Zaraz tool",
    r"gtag/js\?id=": "Direct gtag.js script — use Zaraz tool",
}

# Patterns that SHOULD be present
REQUIRED_PATTERNS = {
    "base.html": {
        r"Cloudflare Zaraz": "Zaraz reference comment",
        r"<noscript>": "Noscript fallback for non-JS browsers",
    }
}


def _read_file(filepath: Path) -> str:
    """Read file contents."""
    return filepath.read_text(encoding="utf-8", errors="ignore")


def _find_all_templates():
    """Find all HTML template files."""
    return list(TEMPLATES_DIR.rglob("*.html"))


# =================================================================
# SECTION 1: No Conflicting Tracking Scripts
# =================================================================


class TestNoTrackingConflicts:
    """Ensure templates don't contain scripts that conflict with Zaraz."""

    @pytest.mark.parametrize(
        "template", _find_all_templates(), ids=lambda p: str(p.relative_to(TEMPLATES_DIR))
    )
    def test_no_banned_patterns(self, template):
        """Templates must not contain direct tracking scripts that conflict with Zaraz."""
        content = _read_file(template)
        for pattern, description in BANNED_PATTERNS.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert len(matches) == 0, (
                f"{template.name}: Found banned pattern: {description}\n  Matches: {matches}"
            )

    @pytest.mark.parametrize(
        "template", _find_all_templates(), ids=lambda p: str(p.relative_to(TEMPLATES_DIR))
    )
    def test_no_inline_clarity(self, template):
        """Microsoft Clarity must NOT be loaded via inline script (use Zaraz tool)."""
        content = _read_file(template)
        assert "clarity.ms/tag/" not in content, (
            f"{template.name}: Inline Clarity script found — should be a Zaraz tool"
        )

    @pytest.mark.parametrize(
        "template", _find_all_templates(), ids=lambda p: str(p.relative_to(TEMPLATES_DIR))
    )
    def test_no_duplicate_pixel_init(self, template):
        """Templates must not initialize the Meta Pixel directly (Zaraz does this)."""
        content = _read_file(template)
        # Check for direct fbq('init', ...) calls
        has_init = re.search(r'fbq\s*\(\s*["\']init["\']', content)
        assert not has_init, (
            f"{template.name}: Direct fbq('init') found — Zaraz handles pixel initialization"
        )


# =================================================================
# SECTION 2: Base Template Zaraz Integration
# =================================================================


class TestBaseTemplateZaraz:
    """Verify the base template has proper Zaraz integration."""

    def _get_base_html(self):
        base = TEMPLATES_DIR / "layouts" / "base.html"
        assert base.exists(), "base.html not found"
        return _read_file(base)

    def test_zaraz_comment_exists(self):
        """Base template must reference Cloudflare Zaraz."""
        content = self._get_base_html()
        assert "Cloudflare Zaraz" in content, "No Zaraz reference found in base.html"

    def test_noscript_fallback_exists(self):
        """Base template must have a <noscript> fallback for pixel tracking."""
        content = self._get_base_html()
        assert "<noscript>" in content, "Missing <noscript> fallback in base.html"

    def test_noscript_has_pixel(self):
        """The noscript tag must contain a Meta Pixel tracking pixel."""
        content = self._get_base_html()
        assert "facebook.com/tr" in content, "Noscript fallback missing Facebook tracking pixel"

    def test_no_duplicate_zaraz_script(self):
        """Base template must NOT manually load Zaraz script (autoInject handles it)."""
        content = self._get_base_html()
        assert "zaraz.js" not in content, (
            "Manual Zaraz script inclusion found — autoInjectScript handles this"
        )

    def test_clarity_not_inline(self):
        """Microsoft Clarity must not be loaded as inline script."""
        content = self._get_base_html()
        assert "clarity.ms/tag/" not in content, (
            "Inline Clarity script found in base.html — use Zaraz tool"
        )

    def test_clarity_has_zaraz_comment(self):
        """There should be a comment indicating Clarity is managed via Zaraz."""
        content = self._get_base_html()
        assert "Zaraz Dashboard" in content or "Zaraz" in content, (
            "Missing comment about Clarity being managed via Zaraz"
        )


# =================================================================
# SECTION 3: tracking.js Zaraz Integration
# =================================================================


class TestTrackingJsZaraz:
    """Verify tracking.js uses zaraz.track() properly."""

    def _get_pixel_bridge(self):
        path = TRACKING_DIR / "pixel-bridge.js"
        assert path.exists(), "pixel-bridge.js not found"
        return _read_file(path)

    def _get_tracking_engine(self):
        path = TRACKING_DIR / "index.js"
        assert path.exists(), "tracking engine not found"
        return _read_file(path)

    def test_zaraz_track_bridge_exists(self):
        """tracking.js must check for zaraz.track before falling back to fbq."""
        content = self._get_pixel_bridge()
        assert "zaraz" in content and "window.zaraz.track" in content, (
            "tracking.js does not reference zaraz.track() — missing Zaraz bridge"
        )

    def test_no_duplicate_pageview_pixel(self):
        """tracking.js must NOT fire PageView via safeFbq/fbq (Zaraz handles this)."""
        content = self._get_tracking_engine()
        # Pixel-side PageView should not be sent explicitly
        has_duplicate = re.search(r"PixelBridge\.track\s*\(\s*['\"]PageView['\"]", content)
        assert not has_duplicate, (
            "tracking.js fires PageView via safeFbq — this duplicates Zaraz's AllPageviews action"
        )

    def test_capi_pageview_exists(self):
        """tracking.js should still send PageView to CAPI for server-side dedup."""
        content = self._get_tracking_engine()
        assert "CAPI.track('PageView'" in content or 'CAPI.track("PageView"' in content, (
            "tracking.js missing CAPI PageView event — needed for server-side deduplication"
        )

    def test_zaraz_first_priority(self):
        """Zaraz should be checked BEFORE fbq in the safeFbq function."""
        content = self._get_pixel_bridge()
        zaraz_pos = content.find("window.zaraz")
        fbq_pos = content.find("window.fbq")
        # Allow for both existing, but zaraz should come first in safeFbq
        if zaraz_pos >= 0 and fbq_pos >= 0:
            assert zaraz_pos < fbq_pos, "zaraz.track() must be checked before fbq() in safeFbq()"

    def test_retry_queue_supports_zaraz(self):
        """The retry queue should attempt zaraz.track before fbq."""
        content = self._get_pixel_bridge()
        # In the retry interval, zaraz should be checked
        retry_section = content[content.find("_startRetryLoop") :]
        assert "window.zaraz.track" in retry_section, (
            "Retry queue does not check for zaraz — events may be lost"
        )


# =================================================================
# SECTION 4: CTA Templates Have Tracking Hooks
# =================================================================


class TestCTATrackingHooks:
    """Verify section templates have proper tracking integration."""

    def test_hero_has_conversion_handler(self):
        """Hero section must have a handleConversion call."""
        content = _read_file(TEMPLATES_DIR / "sections" / "hero.html")
        assert "handleConversion" in content, (
            "hero.html missing handleConversion — CTA clicks won't be tracked"
        )

    def test_cta_final_has_conversion_handler(self):
        """CTA Final section must have a handleConversion call."""
        content = _read_file(TEMPLATES_DIR / "sections" / "cta_final.html")
        assert "handleConversion" in content, (
            "cta_final.html missing handleConversion — CTA clicks won't be tracked"
        )

    def test_services_has_data_attributes(self):
        """Services section must have data-service-category for ViewContent tracking."""
        content = _read_file(TEMPLATES_DIR / "sections" / "services.html")
        assert "data-service-category" in content, (
            "services.html missing data-service-category — ViewContent won't fire"
        )

    def test_gallery_has_conversion_handler(self):
        """Gallery section must have a handleConversion call."""
        content = _read_file(TEMPLATES_DIR / "sections" / "gallery.html")
        assert "handleConversion" in content, (
            "gallery.html missing handleConversion — CTA clicks won't be tracked"
        )
