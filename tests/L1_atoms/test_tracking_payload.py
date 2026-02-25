from app.tracking import _build_payload, hash_data

def test_tracking_payload_generation():
    # Test case 1: minimal inputs
    payload1 = _build_payload(
        event_name="PageView",
        event_source_url="http://example.com",
        client_ip="127.0.0.1",
        user_agent="Mozilla/5.0",
        event_id="evt_1",
    )
    user_data1 = payload1["data"][0]["user_data"]
    assert user_data1["client_ip_address"] == "127.0.0.1"
    assert user_data1["client_user_agent"] == "Mozilla/5.0"

    # Test case 2: full inputs
    payload2 = _build_payload(
        event_name="Purchase",
        event_source_url="http://example.com/buy",
        client_ip="1.2.3.4",
        user_agent="Chrome",
        event_id="evt_2",
        fbclid="IwAR123",
        fbp="fb.1.123.456",
        external_id="user_123",
        phone="+59160000000",
        email="test@example.com",
        country="BO",
        city="La Paz",
        state="La Paz",
        zip_code="0000",
        first_name="Juan",
        last_name="Perez",
        fb_browser_id="browser_id",
        fbc="fb.1.123.IwAR123"
    )

    # Validate some fields in Payload 2
    user_data = payload2["data"][0]["user_data"]
    assert user_data["client_ip_address"] == "1.2.3.4"
    assert user_data["client_user_agent"] == "Chrome"
    assert user_data["external_id"] == hash_data("user_123")
    assert user_data["fbc"] == "fb.1.123.IwAR123" # fbc overrides fbclid generation
    assert user_data["fbp"] == "fb.1.123.456"
    assert user_data["ph"] == hash_data("59160000000")
    assert user_data["em"] == hash_data("test@example.com")
    assert user_data["country"] == hash_data("bo")
    assert user_data["ct"] == hash_data("lapaz")
    assert user_data["st"] == hash_data("lapaz")
    assert user_data["zp"] == hash_data("0000")
    assert user_data["fn"] == hash_data("juan")
    assert user_data["ln"] == hash_data("perez")
