
import pytest
import asyncio
import time
from unittest.mock import MagicMock, AsyncMock, patch
from app.tracking import send_event_async
from app.config import settings

@pytest.mark.asyncio
async def test_send_event_async_non_blocking():
    """
    Verify that send_event_async is non-blocking.
    This simulates slow Redis and DB, and checks if the event loop remains responsive.
    """

    # Manually modify settings
    original_pixel = settings.meta.pixel_id
    original_token = settings.meta.access_token
    original_sandbox = settings.meta.sandbox_mode

    settings.meta.pixel_id = "mock-pixel"
    settings.meta.access_token = "mock-token"
    settings.meta.sandbox_mode = False

    try:
        # Mock Redis
        mock_async_redis = AsyncMock()
        async def blocking_set_async(*args, **kwargs):
            await asyncio.sleep(0.1)
            return True
        mock_async_redis.set.side_effect = blocking_set_async

        # Mock DB save (via save_emq_score)
        def blocking_save(*args, **kwargs):
            time.sleep(0.1)

        # Mock Async Client
        mock_client = MagicMock()
        mock_client.post = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Patch dependencies
        with patch("app.infrastructure.persistence.deduplication_service.dedup_service._async_redis", mock_async_redis), \
             patch("app.tracking.save_emq_score", side_effect=blocking_save), \
             patch("app.tracking.async_client", mock_client):

            # Measure execution time of the loop while send_event_async runs

            async def monitor_loop():
                max_delay = 0
                while True:
                    start = time.time()
                    await asyncio.sleep(0.01)
                    elapsed = time.time() - start
                    # Ideally elapsed is close to 0.01
                    delay = elapsed - 0.01
                    if delay > max_delay:
                        max_delay = delay
                    if delay > 0.05: # Threshold for "blocking"
                        return delay

            monitor_task = asyncio.create_task(monitor_loop())

            # Run send_event_async
            # Total blocking time if sync: 0.1 (redis) + 0.1 (db) = 0.2s
            # Since async/threaded, main loop should not block.

            await send_event_async(
                event_name="PageView",
                event_source_url="http://example.com",
                client_ip="127.0.0.1",
                user_agent="test-agent",
                event_id="test-async-event",
            )

            monitor_task.cancel()
            try:
                result = await monitor_task
            except asyncio.CancelledError:
                result = None

            # If monitor_loop returned a value, it means it detected blocking
            if result:
                pytest.fail(f"Event loop blocked for {result:.4f}s")

    finally:
        # Restore settings
        settings.meta.pixel_id = original_pixel
        settings.meta.access_token = original_token
        settings.meta.sandbox_mode = original_sandbox
