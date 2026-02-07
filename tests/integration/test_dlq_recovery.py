import pytest
import os
import json
import time
from app.retry_queue import add_to_retry_queue, process_retry_queue, QUEUE_FILE

def _simulate_failure_and_check_persistence():
    # 2. Simulate Catastrophic Failure: Event fails
    dummy_payload = {"id": "123", "data": "very important"}
    add_to_retry_queue("TestEventCritical", dummy_payload)
    
    # Check Persistence
    assert os.path.exists(QUEUE_FILE), "❌ DLQ file not created after failure"
    
    with open(QUEUE_FILE, "r") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["event_name"] == "TestEventCritical"

def test_dlq_recovery_resurrection():
    """🛡️ ARCHITECTURAL AUDIT: Resilience "Resurrection" Test"""
    
    # 1. Clean Slate
    if os.path.exists(QUEUE_FILE):
        os.remove(QUEUE_FILE)
        
    _simulate_failure_and_check_persistence()
    
    # 3. Simulate Recovery Attempt (Too Early)
    process_retry_queue()
    
    with open(QUEUE_FILE, "r") as f:
        data_after = json.load(f)
        assert len(data_after) == 1
        assert data_after[0]["retries"] == 0
        
    # 4. Simulate Time Travel
    with open(QUEUE_FILE, "r") as f:
        hacked_queue = json.load(f)
    hacked_queue[0]["failed_at"] = int(time.time()) - 3600
    with open(QUEUE_FILE, "w") as f:
        json.dump(hacked_queue, f)
        
    # 5. Recover again (Should process now)
    process_retry_queue()
    
    with open(QUEUE_FILE, "r") as f:
        final_queue = json.load(f)
        assert final_queue[0]["retries"] > 0, "❌ System failed to resurrect and retry"

    if os.path.exists(QUEUE_FILE):
        os.remove(QUEUE_FILE)
