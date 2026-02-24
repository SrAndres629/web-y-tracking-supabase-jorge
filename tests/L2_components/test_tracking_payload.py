import hashlib
import time
from app.tracking import _build_payload, hash_data

def test_build_payload_user_data_hashing():
    """Test user data hashing logic in _build_payload."""
    email = "test@example.com"
    phone = "59170012345"
    external_id = "user123"
    first_name = "John"
    last_name = "Doe"
    city = "La Paz"
    state = "La Paz"
    country = "BO"
    zip_code = "12345"

    payload = _build_payload(
        event_name="TestEvent",
        event_source_url="http://example.com",
        client_ip="127.0.0.1",
        user_agent="TestAgent",
        event_id="evt_123",
        email=email,
        phone=phone,
        external_id=external_id,
        first_name=first_name,
        last_name=last_name,
        city=city,
        state=state,
        country=country,
        zip_code=zip_code,
    )

    user_data = payload["data"][0]["user_data"]

    assert user_data["em"] == hash_data(email)
    assert user_data["ph"] == hash_data(phone)
    assert user_data["external_id"] == hash_data(external_id)
    assert user_data["fn"] == hash_data(first_name.lower())
    assert user_data["ln"] == hash_data(last_name.lower())
    assert user_data["ct"] == hash_data(city.lower().replace(" ", ""))
    assert user_data["st"] == hash_data(state.lower().replace(" ", ""))
    assert user_data["country"] == hash_data(country.lower())
    assert user_data["zp"] == hash_data(zip_code.replace(" ", ""))

def test_build_payload_phone_normalization():
    """Test phone normalization logic."""
    # Test phone without country code
    phone = "70012345"
    payload = _build_payload(
        event_name="TestEvent",
        event_source_url="http://example.com",
        client_ip="127.0.0.1",
        user_agent="TestAgent",
        event_id="evt_123",
        phone=phone,
    )
    user_data = payload["data"][0]["user_data"]
    expected_phone = "591" + phone
    assert user_data["ph"] == hash_data(expected_phone)

    # Test phone with non-digits
    phone_dirty = "+591-700-12345"
    payload = _build_payload(
        event_name="TestEvent",
        event_source_url="http://example.com",
        client_ip="127.0.0.1",
        user_agent="TestAgent",
        event_id="evt_123",
        phone=phone_dirty,
    )
    user_data = payload["data"][0]["user_data"]
    expected_phone = "59170012345"
    assert user_data["ph"] == hash_data(expected_phone)

def test_build_payload_defaults():
    """Test default values logic."""
    payload = _build_payload(
        event_name="TestEvent",
        event_source_url="http://example.com",
        client_ip="127.0.0.1",
        user_agent="TestAgent",
        event_id="evt_123",
    )
    user_data = payload["data"][0]["user_data"]

    # Default country is BO
    assert user_data["country"] == hash_data("bo")

    # Optional fields should be absent
    assert "em" not in user_data
    assert "ph" not in user_data
    assert "external_id" not in user_data

def test_build_payload_fbc_logic():
    """Test fbc generation logic."""
    # Case 1: fbclid provided
    fbclid = "IwAR123"
    payload = _build_payload(
        event_name="TestEvent",
        event_source_url="http://example.com",
        client_ip="127.0.0.1",
        user_agent="TestAgent",
        event_id="evt_123",
        fbclid=fbclid,
    )
    user_data = payload["data"][0]["user_data"]
    assert "fbc" in user_data
    assert fbclid in user_data["fbc"]
    assert user_data["fbc"].startswith("fb.1.")

    # Case 2: fbc provided
    fbc = "fb.1.1234567890.IwAR123"
    payload = _build_payload(
        event_name="TestEvent",
        event_source_url="http://example.com",
        client_ip="127.0.0.1",
        user_agent="TestAgent",
        event_id="evt_123",
        fbc=fbc,
    )
    user_data = payload["data"][0]["user_data"]
    assert user_data["fbc"] == fbc
