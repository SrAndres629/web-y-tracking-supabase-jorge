"""
🎨 Core Decorators - Cross-cutting concerns.

Decoradores puros reutilizables en cualquier capa.
Proporcionan: retries, circuit breaker, timing, logging.
"""

from __future__ import annotations

import functools
import time
import logging
from typing import Callable, TypeVar, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum, auto

T = TypeVar("T")
logger = logging.getLogger(__name__)


# ===== Timing Decorator =====

def timed(metric_name: Optional[str] = None) -> Callable:
    """
    Mide y loguea el tiempo de ejecución de una función.
    
    Example:
        >>> @timed("db.query.visitors")
        ... async def find_visitor(id: str) -> Visitor: ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        name = metric_name or func.__qualname__
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                start = time.perf_counter()
                try:
                    return await func(*args, **kwargs)
                finally:
                    elapsed = (time.perf_counter() - start) * 1000
                    logger.debug(f"⏱️ {name}: {elapsed:.2f}ms")
            return async_wrapper  # type: ignore
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> T:
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = (time.perf_counter() - start) * 1000
                    logger.debug(f"⏱️ {name}: {elapsed:.2f}ms")
            return sync_wrapper
    
    return decorator


# ===== Retry Decorator =====

class RetryConfig:
    """Configuración para retry policy."""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        exceptions: tuple[type[Exception], ...] = (Exception,),
        on_retry: Optional[Callable[[Exception, int], None]] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.exceptions = exceptions
        self.on_retry = on_retry


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Retry decorator con exponential backoff.
    
    Example:
        >>> @retry(max_attempts=3, exceptions=(ConnectionError,))
        ... async def call_external_api() -> dict: ...
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exceptions=exceptions
    )
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except config.exceptions as e:
                    last_exception = e
                    if attempt == config.max_attempts:
                        break
                    
                    # Exponential backoff con jitter
                    delay = min(
                        config.base_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay
                    )
                    logger.warning(
                        f"🔄 Retry {attempt}/{config.max_attempts} for {func.__name__}: {e}. "
                        f"Waiting {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
            
            raise last_exception or Exception("Retry failed")
        
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except config.exceptions as e:
                    last_exception = e
                    if attempt == config.max_attempts:
                        break
                    
                    delay = min(
                        config.base_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay
                    )
                    logger.warning(
                        f"🔄 Retry {attempt}/{config.max_attempts} for {func.__name__}: {e}. "
                        f"Waiting {delay:.1f}s..."
                    )
                    time.sleep(delay)
            
            raise last_exception or Exception("Retry failed")
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# ===== Circuit Breaker =====

class CircuitState(Enum):
    CLOSED = auto()      # Normal operation
    OPEN = auto()        # Failing, reject fast
    HALF_OPEN = auto()   # Testing if recovered


@dataclass
class CircuitStats:
    failures: int = 0
    successes: int = 0
    last_failure_time: float = 0.0
    state: CircuitState = CircuitState.CLOSED


class CircuitBreaker:
    """
    Circuit Breaker pattern para prevenir cascada de fallos.
    
    States:
    - CLOSED: Todo funciona, pasan requests
    - OPEN: Umbral de fallos alcanzado, rechaza requests rápido
    - HALF_OPEN: Después de timeout, permite 1 request para testear
    """
    
    _circuits: dict[str, CircuitStats] = {}
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exception: type[Exception] = Exception
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
    
    def _get_stats(self) -> CircuitStats:
        if self.name not in self._circuits:
            self._circuits[self.name] = CircuitStats()
        return self._circuits[self.name]
    
    def _update_state(self, stats: CircuitStats) -> None:
        if stats.state == CircuitState.OPEN:
            # Check if should try half-open
            if time.time() - stats.last_failure_time > self.recovery_timeout:
                stats.state = CircuitState.HALF_OPEN
                stats.failures = 0
                stats.successes = 0
                logger.info(f"🔌 Circuit {self.name}: OPEN -> HALF_OPEN")
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            stats = self._get_stats()
            self._update_state(stats)
            
            if stats.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(
                    f"Circuit {self.name} is OPEN"
                )
            
            try:
                result = await func(*args, **kwargs)
                # Success
                if stats.state == CircuitState.HALF_OPEN:
                    stats.successes += 1
                    if stats.successes >= 2:  # Need 2 consecutive successes
                        stats.state = CircuitState.CLOSED
                        stats.failures = 0
                        logger.info(f"🔌 Circuit {self.name}: HALF_OPEN -> CLOSED")
                return result
                
            except self.expected_exception as e:
                stats.failures += 1
                stats.last_failure_time = time.time()
                
                if stats.failures >= self.failure_threshold:
                    if stats.state != CircuitState.OPEN:
                        stats.state = CircuitState.OPEN
                        logger.error(f"🔌 Circuit {self.name}: CLOSED -> OPEN ({stats.failures} failures)")
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            stats = self._get_stats()
            self._update_state(stats)
            
            if stats.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(
                    f"Circuit {self.name} is OPEN"
                )
            
            try:
                result = func(*args, **kwargs)
                if stats.state == CircuitState.HALF_OPEN:
                    stats.successes += 1
                    if stats.successes >= 2:
                        stats.state = CircuitState.CLOSED
                        stats.failures = 0
                        logger.info(f"🔌 Circuit {self.name}: HALF_OPEN -> CLOSED")
                return result
                
            except self.expected_exception as e:
                stats.failures += 1
                stats.last_failure_time = time.time()
                
                if stats.failures >= self.failure_threshold:
                    if stats.state != CircuitState.OPEN:
                        stats.state = CircuitState.OPEN
                        logger.error(f"🔌 Circuit {self.name}: CLOSED -> OPEN ({stats.failures} failures)")
                
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


class CircuitBreakerOpenError(Exception):
    """Circuit breaker está abierto, rechazando requests."""
    pass


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    expected_exception: type[Exception] = Exception
) -> Callable:
    """
    Decorator factory para circuit breaker.
    
    Example:
        >>> @circuit_breaker("meta_capi", failure_threshold=3)
        ... async def send_to_meta(event: dict) -> None: ...
    """
    breaker = CircuitBreaker(name, failure_threshold, recovery_timeout, expected_exception)
    return breaker


# ===== Cache Decorator (memoization) =====

def memoize(maxsize: int = 128) -> Callable:
    """
    Memoization simple para funciones puras.
    No usar con funciones que tienen side effects o dependen de estado externo.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache: dict = {}
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create key from arguments
            key = str(args) + str(sorted(kwargs.items()))
            
            if key not in cache:
                if len(cache) >= maxsize:
                    # Simple LRU: clear half
                    for k in list(cache.keys())[:maxsize//2]:
                        del cache[k]
                cache[key] = func(*args, **kwargs)
            
            return cache[key]
        
        wrapper.cache = cache  # type: ignore
        wrapper.cache_clear = lambda: cache.clear()  # type: ignore
        return wrapper
    
    return decorator


# ===== Import asyncio aquí para evitar problemas con type hints =====
import asyncio
