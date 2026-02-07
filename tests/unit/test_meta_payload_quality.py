import pytest
import hashlib
from app.meta_capi import EliteMetaCAPIService, EnhancedUserData, EnhancedCustomData

def _get_test_user_data():
    return EnhancedUserData(
        email="  Test.User@internal.test  ",
        phone="+591 71234567",
        city="La Paz ",
        client_user_agent="Mozilla/5.0",
        client_ip_address="192.168.1.1"
    )

def test_meta_emq_payload_quality():
    """🛡️ ARCHITECTURAL AUDIT: EMQ (Event Match Quality) Assurance"""
    user_data = _get_test_user_data()
    
    import app.meta_capi
    app.meta_capi.SDK_AVAILABLE = True
    
    try:
        sdk_object = user_data.to_sdk_user_data()
        
        # Email: trimming + lowercase
        expected_email_clean = "test.user@internal.test"
        assert sdk_object.email == expected_email_clean
        
        # Phone: digits only + 591
        expected_phone_clean = "59171234567"
        assert sdk_object.phone == expected_phone_clean
        
        # City: lowercase + remove spaces
        assert sdk_object.city == "lapaz"
        assert sdk_object.client_ip_address == "192.168.1.1"
        assert sdk_object.client_user_agent == "Mozilla/5.0"
        
    except (RuntimeError, ImportError):
        pytest.skip("Meta SDK not installed")
