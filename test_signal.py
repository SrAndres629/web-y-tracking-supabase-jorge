import hashlib
import time
from app.tracking import _build_payload, hash_data
from app.config import settings

def test_mock_conversion_signal():
    print("\n--- [A-002.1] MOCK CONVERSION TEST ---")
    
    # 1. Inputs
    test_external_id = "user_test_12345"
    test_ip = "1.2.3.4"
    test_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    event_id = f"test_evt_{int(time.time())}"
    
    # 2. Expected Hash (SHA256)
    expected_hash = hashlib.sha256(test_external_id.lower().strip().encode('utf-8')).hexdigest()
    
    # 3. Build Payload
    payload = _build_payload(
        event_name="Contact",
        event_source_url="http://localhost:8000/",
        client_ip=test_ip,
        user_agent=test_ua,
        event_id=event_id,
        external_id=test_external_id
    )
    
    # 4. Extraction & Validation
    generated_hash = payload['data'][0]['user_data']['external_id']
    
    print(f"External ID: {test_external_id}")
    print(f"Expected Hash:  {expected_hash}")
    print(f"Generated Hash: {generated_hash}")
    
    assert generated_hash == expected_hash, "❌ Hash SHA256 mismatch!"
    print("✅ SIGNAL INTEGRITY: SHA256 Hash is correct.")
    
    # 5. Deduplication check
    assert payload['data'][0]['event_id'] == event_id, "❌ Event ID mismatch!"
    print(f"✅ DEDUPLICATION: Event ID {event_id} persistent.")

if __name__ == "__main__":
    try:
        test_mock_conversion_signal()
        print("\n[RESULT] A-002.1: SUCCESS")
    except AssertionError as e:
        print(f"\n[RESULT] A-002.1: FAILED - {e}")
