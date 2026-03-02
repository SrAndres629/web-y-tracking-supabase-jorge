import pytest
import asyncio
import time
from app.core.decorators import retry

class MyError(Exception):
    pass

def test_retry_async_success():
    count = 0
    @retry(max_attempts=3, base_delay=0.01, exceptions=(MyError,))
    async def task():
        nonlocal count
        count += 1
        if count < 2:
            raise MyError("fail")
        return "success"

    result = asyncio.run(task())
    assert result == "success"
    assert count == 2

def test_retry_async_failure():
    count = 0
    @retry(max_attempts=3, base_delay=0.01, exceptions=(MyError,))
    async def task():
        nonlocal count
        count += 1
        raise MyError("fail")

    with pytest.raises(MyError):
        asyncio.run(task())
    assert count == 3

def test_retry_sync_success():
    count = 0
    @retry(max_attempts=3, base_delay=0.01, exceptions=(MyError,))
    def task():
        nonlocal count
        count += 1
        if count < 2:
            raise MyError("fail")
        return "success"

    result = task()
    assert result == "success"
    assert count == 2

def test_retry_sync_failure():
    count = 0
    @retry(max_attempts=3, base_delay=0.01, exceptions=(MyError,))
    def task():
        nonlocal count
        count += 1
        raise MyError("fail")

    with pytest.raises(MyError):
        task()
    assert count == 3
