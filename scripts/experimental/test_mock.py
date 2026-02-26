import asyncio
from unittest.mock import patch, AsyncMock
from contextlib import asynccontextmanager

class CircuitBreakerOpenException(Exception): pass

class DistributedCircuitBreaker:
    @asynccontextmanager
    async def execute(self):
        print("Real execute called!")
        yield

class MetaTracker:
    async def track(self):
        breaker = DistributedCircuitBreaker()
        try:
            async with breaker.execute():
                print("Inside context")
                return True
        except CircuitBreakerOpenException:
            return False

async def main():
    @asynccontextmanager
    async def fake_execute(*args, **kwargs):
        raise CircuitBreakerOpenException("Circuit is OPEN")
        yield

    with patch("__main__.DistributedCircuitBreaker.execute", fake_execute):
        tracker = MetaTracker()
        result = await tracker.track()
        print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
