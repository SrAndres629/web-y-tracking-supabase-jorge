"""
🛡️ Distributed Circuit Breaker Pattern (Serverless/Edge Optimized)

Standard in-memory circuit breakers fail in Serverless environments because
the memory state is wiped between executions or isolated across microVMs.
This implementation uses Upstash Redis to maintain global state:
- CLOSED: Everything is fine.
- OPEN: Fast failure, don't execute the external call.
- HALF-OPEN: One test request is allowed to see if the service recovered.
"""

import logging
from contextlib import asynccontextmanager
from typing import Type

from app.infrastructure.cache.redis_provider import redis_provider

logger = logging.getLogger(__name__)


class CircuitBreakerOpenException(Exception):
    """Raised when the circuit breaker is OPEN and preventing requests."""

    pass


class DistributedCircuitBreaker:
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 3,
        recovery_timeout_sec: int = 30,
        expected_exceptions: tuple[Type[Exception], ...] = (Exception,),
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_sec
        self.expected_exceptions = expected_exceptions

        # Redis Keys
        self.state_key = f"cb:{service_name}:state"  # 'OPEN' or not exists (CLOSED)
        self.fails_key = f"cb:{service_name}:failures"  # Integer count
        self.half_open_key = f"cb:{service_name}:halfopen"  # Lock for half-open test

    async def _get_redis(self):
        """Helper to safely fetch async redis client"""
        if not redis_provider.is_available:
            return None
        return redis_provider.async_client

    async def is_open(self) -> bool:
        """Check if the circuit is currently OPEN."""
        redis = await self._get_redis()
        if not redis:
            return False  # Bypass circuit breaker if Redis is down

        state = await redis.get(self.state_key)
        if state == "OPEN":
            # Are we ready for Half-Open? The TTL of the state_key determines this.
            # If state_key exists, it means we are still deep in the recovery timeout.
            return True
        return False

    async def record_failure(self):
        """Record a failure and optionally open the circuit."""
        redis = await self._get_redis()
        if not redis:
            return

        fails = await redis.incr(self.fails_key)
        # Set expiration so sporadic errors don't accumulate forever
        if fails == 1:
            await redis.expire(self.fails_key, self.recovery_timeout * 2)

        if fails >= self.failure_threshold:
            logger.error(
                f"🛑 [Circuit Breaker] {self.service_name} failure threshold reached! Opening circuit for {self.recovery_timeout}s."
            )
            await redis.set(self.state_key, "OPEN", ex=self.recovery_timeout)
            # Reset the half-open lock and failures
            await redis.delete(self.fails_key)
            await redis.delete(self.half_open_key)

    async def record_success(self):
        """Reset failures on success."""
        redis = await self._get_redis()
        if not redis:
            return

        await redis.delete(self.fails_key)
        await redis.delete(self.state_key)
        await redis.delete(self.half_open_key)

    @asynccontextmanager
    async def execute(self):
        """
        Async context manager protecting a block of code.
        Raises CircuitBreakerOpenException if service is down.
        """
        redis = await self._get_redis()

        if not redis:
            # Degraded mode: If Redis is completely out, just run the code
            yield
            return

        # Check state
        state = await redis.get(self.state_key)

        if state == "OPEN":
            logger.warning(
                f"⚡ [Circuit Breaker] {self.service_name} is OPEN. Rejecting request."
            )
            raise CircuitBreakerOpenException(
                f"Circuit Breaker is OPEN for {self.service_name}"
            )

        # At this point, it's either CLOSED or the OPEN TTL expired (moving to HALF-OPEN)
        # If failures key is 0 or non-existent, we are CLOSED.
        # But if the state_key expired, we might be the lucky request that probes the service.
        yield_test_probe = False

        # If it was recently open but the key expired, we use a simple SETNX to lock the probe
        probe_locked = await redis.set(self.half_open_key, "1", nx=True, ex=10)
        if probe_locked:
            # We are the probe!
            yield_test_probe = True

        try:
            yield
            # If we get here without exception, success!
            await self.record_success()
            if yield_test_probe:
                logger.info(
                    f"🟢 [Circuit Breaker] {self.service_name} Probe successful! Circuit CLOSED."
                )
        except self.expected_exceptions as e:
            # Specific exceptions happen -> track failure
            logger.warning(f"⚠️ [Circuit Breaker] {self.service_name} call failed: {e}")
            await self.record_failure()
            if yield_test_probe:
                # Probe failed, reopen immediately
                await redis.set(self.state_key, "OPEN", ex=self.recovery_timeout)
            raise
        except Exception:
            # Unrelated exceptions pass through without tripping circuit
            raise
