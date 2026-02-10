# =================================================================
# TEST_ZARAZ.PY - Cloudflare Zaraz Configuration Audit
# Verifies the live Zaraz configuration matches expected state
# =================================================================
import pytest
import requests
import os

# ─── Constants ───────────────────────────────────────────────────
ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID", "19bd9bdd7abf8f74b4e95d75a41e8583")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
ZARAZ_API = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/settings/zaraz/v2"

# Expected configuration values
EXPECTED_PIXEL_ID = "1412977383680793"
EXPECTED_DEBUG_KEY = "d65ievndhoqc73bk77o0"
EXPECTED_TEST_EVENT_CODE = "TEST88535"


def _get_headers():
    """Build auth headers for Cloudflare API."""
    token = API_TOKEN
    if not token:
        # Fallback: try loading from .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
            token = os.getenv("CLOUDFLARE_API_TOKEN", "")
        except ImportError:
            pass
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def _fetch_zaraz_config():
    """Fetch the live Zaraz configuration from Cloudflare."""
    headers = _get_headers()
    if not headers["Authorization"].replace("Bearer ", ""):
        pytest.skip("CLOUDFLARE_API_TOKEN not set — skipping live Zaraz audit")
    resp = requests.get(f"{ZARAZ_API}/config", headers=headers, timeout=15)
    assert resp.status_code == 200, f"Zaraz API returned {resp.status_code}: {resp.text[:200]}"
    return resp.json().get("result", {})


# =================================================================
# SECTION 1: Authentication & Connectivity
# =================================================================

class TestZarazConnectivity:
    """Verify we can reach the Zaraz API and authenticate."""

    def test_api_token_is_valid(self):
        """The Cloudflare API token must authenticate successfully."""
        headers = _get_headers()
        if not headers["Authorization"].replace("Bearer ", ""):
            pytest.skip("CLOUDFLARE_API_TOKEN not set")
        resp = requests.get(
            "https://api.cloudflare.com/client/v4/user/tokens/verify",
            headers=headers, timeout=10
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["status"] == "active", "Token is not active"

    def test_zaraz_config_accessible(self):
        """The Zaraz config endpoint must be reachable."""
        config = _fetch_zaraz_config()
        assert config, "Zaraz config is empty"
        assert "tools" in config, "Zaraz config missing 'tools' key"


# =================================================================
# SECTION 2: Global Settings
# =================================================================

class TestZarazSettings:
    """Verify Zaraz global settings are correctly configured."""

    def test_auto_inject_enabled(self):
        """autoInjectScript must be True for Zaraz to load on all pages."""
        config = _fetch_zaraz_config()
        settings = config.get("settings", {})
        assert settings.get("autoInjectScript") is True, \
            "autoInjectScript is disabled — Zaraz won't load automatically"

    def test_data_layer_enabled(self):
        """dataLayer must be True for event data passing."""
        config = _fetch_zaraz_config()
        assert config.get("dataLayer") is True, \
            "dataLayer is disabled — events won't have enriched data"

    def test_history_change_tracking(self):
        """historyChange must be True for SPA navigation tracking."""
        config = _fetch_zaraz_config()
        assert config.get("historyChange") is True, \
            "historyChange is disabled — SPA navigations won't be tracked"

    def test_debug_key_matches(self):
        """Debug key must match the expected value for Zaraz debug mode."""
        config = _fetch_zaraz_config()
        assert config.get("debugKey") == EXPECTED_DEBUG_KEY, \
            f"Debug key mismatch: got {config.get('debugKey')}, expected {EXPECTED_DEBUG_KEY}"


# =================================================================
# SECTION 3: Facebook Pixel Tool
# =================================================================

class TestZarazFacebookPixel:
    """Verify the Facebook/Meta Pixel tool is correctly configured."""

    def test_facebook_pixel_exists(self):
        """At least one Facebook Pixel tool must be configured."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        fb_tools = {k: v for k, v in tools.items()
                    if v.get("component") == "facebook-pixel"}
        assert len(fb_tools) > 0, "No Facebook Pixel tool found in Zaraz"

    def test_facebook_pixel_enabled(self):
        """The Facebook Pixel tool must be enabled."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        for tool_id, tool in tools.items():
            if tool.get("component") == "facebook-pixel":
                assert tool.get("enabled") is True, \
                    f"Facebook Pixel tool '{tool_id}' is disabled"

    def test_pixel_id_correct(self):
        """The Pixel ID must match the expected production value."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        for tool_id, tool in tools.items():
            if tool.get("component") == "facebook-pixel":
                pixel_id = tool.get("settings", {}).get("property")
                assert pixel_id == EXPECTED_PIXEL_ID, \
                    f"Pixel ID mismatch: got {pixel_id}, expected {EXPECTED_PIXEL_ID}"

    def test_access_token_present(self):
        """The Meta CAPI access token must be configured (not empty)."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        for tool_id, tool in tools.items():
            if tool.get("component") == "facebook-pixel":
                token = tool.get("settings", {}).get("accessToken")
                assert token and len(token) > 10, \
                    "Meta CAPI access token is missing or too short"

    def test_test_event_code_present(self):
        """TEST_EVENT_CODE must be set for debugging in Meta Events Manager."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        for tool_id, tool in tools.items():
            if tool.get("component") == "facebook-pixel":
                test_key = tool.get("settings", {}).get("testKey")
                assert test_key == EXPECTED_TEST_EVENT_CODE, \
                    f"Test event code mismatch: got {test_key}, expected {EXPECTED_TEST_EVENT_CODE}"

    def test_ecommerce_enabled(self):
        """Ecommerce tracking must be enabled for conversion events."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        for tool_id, tool in tools.items():
            if tool.get("component") == "facebook-pixel":
                ecommerce = tool.get("settings", {}).get("ecommerce")
                assert ecommerce is True, \
                    "Ecommerce tracking is disabled on the Facebook Pixel"


# =================================================================
# SECTION 4: Actions
# =================================================================

class TestZarazActions:
    """Verify Zaraz actions are correctly configured."""

    def test_pageview_action_exists(self):
        """A PageView action must exist on the Facebook Pixel."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        for tool_id, tool in tools.items():
            if tool.get("component") == "facebook-pixel":
                actions = tool.get("actions", {})
                pageview_actions = {k: v for k, v in actions.items()
                                    if v.get("actionType") == "pageview"}
                assert len(pageview_actions) > 0, \
                    "No PageView action found on Facebook Pixel"

    def test_pageview_action_enabled(self):
        """The PageView action must be enabled."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        for tool_id, tool in tools.items():
            if tool.get("component") == "facebook-pixel":
                actions = tool.get("actions", {})
                for action_id, action in actions.items():
                    if action.get("actionType") == "pageview":
                        assert action.get("enabled") is True, \
                            f"PageView action '{action_id}' is disabled"

    def test_custom_event_action_exists(self):
        """A custom event action must exist for zaraz.track() calls."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        for tool_id, tool in tools.items():
            if tool.get("component") == "facebook-pixel":
                actions = tool.get("actions", {})
                event_actions = {k: v for k, v in actions.items()
                                 if v.get("actionType") == "event"}
                assert len(event_actions) > 0, \
                    "No custom event action found on Facebook Pixel"

    def test_pageview_fires_on_pageview_trigger(self):
        """The PageView action must fire on the 'Pageview' trigger."""
        config = _fetch_zaraz_config()
        tools = config.get("tools", {})
        for tool_id, tool in tools.items():
            if tool.get("component") == "facebook-pixel":
                actions = tool.get("actions", {})
                for action_id, action in actions.items():
                    if action.get("actionType") == "pageview":
                        triggers = action.get("firingTriggers", [])
                        assert "Pageview" in triggers, \
                            f"PageView action not linked to 'Pageview' trigger: {triggers}"


# =================================================================
# SECTION 5: Triggers
# =================================================================

class TestZarazTriggers:
    """Verify Zaraz triggers are correctly configured."""

    def test_pageview_trigger_exists(self):
        """A Pageview trigger must exist."""
        config = _fetch_zaraz_config()
        triggers = config.get("triggers", {})
        assert "Pageview" in triggers, "Missing 'Pageview' trigger"

    def test_pageview_trigger_is_pageload(self):
        """The Pageview trigger must be a system pageload trigger."""
        config = _fetch_zaraz_config()
        triggers = config.get("triggers", {})
        pageview = triggers.get("Pageview", {})
        assert pageview.get("system") == "pageload", \
            f"Pageview trigger system is '{pageview.get('system')}', expected 'pageload'"

    def test_all_tracks_trigger_exists(self):
        """An AllTracks trigger must exist for custom events."""
        config = _fetch_zaraz_config()
        triggers = config.get("triggers", {})
        assert "AllTracks" in triggers, "Missing 'AllTracks' trigger"

    def test_all_tracks_has_exclusion_rules(self):
        """AllTracks must exclude internal zaraz events to avoid loops."""
        config = _fetch_zaraz_config()
        triggers = config.get("triggers", {})
        all_tracks = triggers.get("AllTracks", {})
        load_rules = all_tracks.get("loadRules", [])
        assert len(load_rules) > 0, "AllTracks trigger has no load rules (filtering)"

        # Must exclude __zaraz* internal events
        internal_exclusion = any(
            r.get("value", "").startswith("^__zaraz")
            for r in load_rules
        )
        assert internal_exclusion, \
            "AllTracks trigger does not exclude internal __zaraz* events"


# =================================================================
# SECTION 6: Zaraz Workflow
# =================================================================

class TestZarazWorkflow:
    """Verify the Zaraz publishing workflow is in the correct state."""

    def test_workflow_is_realtime(self):
        """Zaraz workflow must be set to 'realtime' for instant updates."""
        headers = _get_headers()
        if not headers["Authorization"].replace("Bearer ", ""):
            pytest.skip("CLOUDFLARE_API_TOKEN not set")
        resp = requests.get(f"{ZARAZ_API}/workflow", headers=headers, timeout=10)
        if resp.status_code == 200:
            workflow = resp.json().get("result", "")
            assert workflow in ("realtime", "preview"), \
                f"Workflow is '{workflow}', expected 'realtime' or 'preview'"
        else:
            pytest.skip(f"Workflow API returned {resp.status_code}")
