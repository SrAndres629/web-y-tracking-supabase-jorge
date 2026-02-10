# =================================================================
# RETRY_QUEUE.PY - Meta CAPI Resilience Logic (DLQ)
# Jorge Aguirre Flores Web
# =================================================================
import json
import os
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

QUEUE_FILE = "capi_retry_queue.json"

def add_to_retry_queue(event_name: str, payload: Dict[str, Any]):
    """Adds a failed event to the local retry queue"""
    try:
        queue = []
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "r") as f:
                queue = json.load(f)
        
        # Add event with retry metadata
        queue.append({
            "event_name": event_name,
            "payload": payload,
            "failed_at": int(time.time()),
            "retries": 0
        })
        
        # Keep queue manageable (max 1000 items)
        if len(queue) > 1000:
            queue = queue[-1000:]
            
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f)
            
        logger.info(f"📥 [DLQ] Event '{event_name}' added to local queue.")
    except Exception as e:
        logger.error(f"❌ [DLQ] Failed to write to retry queue: {e}")

def _process_single_item(item: Dict[str, Any]) -> bool:
    """Helper to process a single event retry"""
    try:
        # Basic exponential backoff check
        wait_time = (2 ** item["retries"]) * 300 # 5 min start
        if int(time.time()) - item["failed_at"] < wait_time:
            return False # Not time yet
        
        logger.info(f"✨ [DLQ] Resending {item['event_name']}...")
        
        # ⚡ CODEX FIX: Actually resend the event using Elite CAPI
        # We need to bridge Sync -> Async here because this runs in a thread
        from app.meta_capi import elite_capi, EnhancedUserData, EnhancedCustomData
        import asyncio
        
        payload = item["payload"]
        user_data_dict = payload.get("user_data", {})
        custom_data_dict = payload.get("custom_data", {})
        
        # Reconstruct objects
        user_data = EnhancedUserData(**user_data_dict)
        custom_data = EnhancedCustomData(**custom_data_dict) if custom_data_dict else None
        
        # Run async function in new loop (safe for thread)
        result = asyncio.run(elite_capi.send_event(
            event_name=item["event_name"],
            event_id=payload.get("event_id"),
            event_source_url=payload.get("url"),
            user_data=user_data,
            custom_data=custom_data
        ))
        
        if result.get("status") in ["success", "duplicate", "sandbox"]:
            logger.info(f"✅ [DLQ] Retry SUCCESS: {item['event_name']}")
            return True # Remove from queue
        else:
            logger.warning(f"⚠️ [DLQ] Retry FAILED: {result}")
            item["retries"] += 1
            return False # Keep in queue
            
    except Exception as e:
        logger.error(f"❌ [DLQ] Retry exception for {item['event_name']}: {e}")
        item["retries"] += 1
        return False

def process_retry_queue():
    """Attempts to resend events in the queue (Run in Background)"""
    if not os.path.exists(QUEUE_FILE):
        return
    
    try:
        with open(QUEUE_FILE, "r") as f:
            queue = json.load(f)
            
        if not queue:
            return
            
        logger.info(f"🔄 [DLQ] Processing {len(queue)} pending events...")
        remaining_queue = []
        
        for item in queue:
            processed = _process_single_item(item)
            
            # If too many retries (max 5), drop it
            if item["retries"] > 5:
                logger.warning(f"🗑️ [DLQ] Dropping event {item['event_name']} after 5 failures.")
                continue
                
            remaining_queue.append(item)
        
        with open(QUEUE_FILE, "w") as f:
            json.dump(remaining_queue, f)
            
    except Exception as e:
        logger.error(f"❌ [DLQ] Failed to process queue: {e}")
