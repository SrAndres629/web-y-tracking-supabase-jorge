import pytest
from app.tracking import generate_event_id, generate_fbc, generate_fbp
import time

# =================================================================
# TRACKING LOGIC TESTS (The "Money" Logic)
# =================================================================

def test_generate_event_id_uniqueness():
    """Test that event IDs are unique and based on timestamp"""
    id1 = generate_event_id("pageview")
    time.sleep(0.001) # Ensure tiny diff
    id2 = generate_event_id("pageview")
    
    assert id1 != id2
    assert "evt_" in id1

def test_generate_fbc_cookie_logic():
    """
    Verifies fbc cookie generation follows Meta standard:
    fb.1.{timestamp}.{fbclid}
    """
    fbclid = "IwAR0..."
    fbc = generate_fbc(fbclid)
    
    assert fbc.startswith("fb.1.")
    assert fbclid in fbc
    
    # Verify timestamp part is numeric
    parts = fbc.split(".")
    assert parts[2].isdigit()

def test_generate_fbp_cookie_logic():
    """
    Verifies fbp cookie generation:
    fb.1.{timestamp}.{random}
    """
    fbp = generate_fbp()
    
    assert fbp.startswith("fb.1.")
    parts = fbp.split(".")
    assert len(parts) == 4
    assert parts[2].isdigit() # Timestamp
    assert parts[3].isdigit() # Random ID

def test_fbc_persistence_logic():
    """Test priority: URL param > Existing Cookie"""
    from app.tracking import get_prioritized_fbclid
    
    # Case 1: URL has fbclid (New ad click) -> Priority
    url_fbclid = "IwAR_NEW_CLICK"
    cookie_fbc = "fb.1.1234.IwAR_OLD_CLICK"
    
    result = get_prioritized_fbclid(url_fbclid, cookie_fbc)
    assert result == "IwAR_NEW_CLICK"
    
    # Case 2: No URL param, but Cookie exists -> Persistence
    result_persistence = get_prioritized_fbclid(None, cookie_fbc)
    assert result_persistence == "IwAR_OLD_CLICK"
