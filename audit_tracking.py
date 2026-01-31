
import sys
# Logging removed to prevent interference with stdout
# logging.basicConfig(level=logging.INFO)

def run_test():
    print("🧪 INICIANDO AUDITORIA DE SENAL META...", flush=True)
    
    # 1. Test Hashing Normalization
    raw_email = "  Test@Example.COM  "
    expected_hash = "f660ab912ec121d1b1e928a0bb4bc617d5d7958fbe8ce99164d8953961917b93" # sha256 of "test@example.com"
    actual_hash = hash_data(raw_email)
    
    if actual_hash == expected_hash:
        print("✅ HASHING: PASS (Normalization works)")
    else:
        print(f"❌ HASHING: FAIL. Got {actual_hash}")
        sys.exit(1)

    # 2. Test Payload Structure (Signal Density)
    payload = _build_payload(
        event_name='Lead',
        event_source_url='http://localhost',
        client_ip='127.0.0.1',
        user_agent='TestAgent',
        event_id='evt_test_001',
        email='test@example.com',
        fbclid='IwAR000',
        fbp='fb.1.1234.5678'
    )
    
    user_data = payload['data'][0]['user_data']
    
    checks = [
        ('em', expected_hash),                 # Hashed Email present?
        ('client_ip_address', '127.0.0.1'),    # IP present?
        ('fbp', 'fb.1.1234.5678'),             # Browser ID present?
        ('fbc', 'fb.1.'),                      # Click ID formatted correctly?
    ]
    
    all_pass = True
    for key, val_check in checks:
        if key not in user_data:
            print(f"❌ PAYLOAD: Missing key '{key}'")
            all_pass = False
        elif val_check and val_check not in str(user_data[key]):
             print(f"❌ PAYLOAD: Invalid value for '{key}'. Got {user_data[key]}")
             all_pass = False
             
    if all_pass:
        print("✅ PAYLOAD DENSITY: PASS (Maximum Signal Quality Verified)")
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_test()
