# =================================================================
# RATE LIMITER ANTI-FRAUDE - Event Protection
# =================================================================
"""
Previene spam de eventos que Meta detecta como fraude.

Penalizaciones de Meta por comportamiento sospechoso:
- >1 evento mismo tipo por usuario en < 5 min = bot
- Eventos duplicados sin deduplicación = fraude
- Picos de tráfico sin patrón orgánico = invalid traffic
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuración de rate limits por tipo de evento"""

    max_events: int
    window_seconds: int
    cooldown_seconds: int = 0
    require_unique: bool = False  # Si requiere event_id único


class EventRateLimiter:
    """
    Rate limiter especializado para eventos de tracking.
    Protege contra:
    - Event flooding (spam)
    - Duplicate events (sin dedup)
    - Bot traffic patterns
    - Accidental loops
    """

    # Configuración por tipo de evento (basado en políticas de Meta)
    DEFAULT_LIMITS = {
        "PageView": RateLimitConfig(
            max_events=3,
            window_seconds=60,  # Max 3 pageviews por minuto por usuario
            cooldown_seconds=10,  # Esperar 10s entre pageviews
        ),
        "Lead": RateLimitConfig(
            max_events=2,
            window_seconds=3600,  # Max 2 leads por hora
            cooldown_seconds=300,  # 5 min entre leads
            require_unique=True,
        ),
        "Purchase": RateLimitConfig(
            max_events=5,
            window_seconds=86400,  # Max 5 compras por día
            cooldown_seconds=60,
            require_unique=True,
        ),
        "AddToCart": RateLimitConfig(
            max_events=10,
            window_seconds=300,  # Max 10 addtocart en 5 min
            cooldown_seconds=5,
        ),
        "ViewContent": RateLimitConfig(
            max_events=20,
            window_seconds=60,  # Max 20 views por minuto
            cooldown_seconds=2,
        ),
        "InitiateCheckout": RateLimitConfig(
            max_events=3,
            window_seconds=3600,  # Max 3 checkouts por hora
            cooldown_seconds=300,
        ),
        "default": RateLimitConfig(
            max_events=5, window_seconds=300, cooldown_seconds=10
        ),
    }

    def __init__(self, redis_client=None):
        from app.infrastructure.cache.redis_provider import redis_provider

        self.redis = redis_client or redis_provider.sync_client
        self.memory_cache: Dict[str, Dict[str, Any]] = {}  # Fallback si no hay Redis
        self.blocked_ips: Dict[str, float] = {}  # IPs temporalmente bloqueadas

    def is_allowed(
        self,
        user_id: str,
        event_type: str,
        event_id: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Verifica si se permite enviar un evento.

        Returns:
            (allowed: bool, reason: str)
        """
        # Verificar IP bloqueada
        if client_ip and self._is_ip_blocked(client_ip):
            return False, f"IP {client_ip} temporarily blocked for suspicious activity"

        # Obtener configuración
        config = self.DEFAULT_LIMITS.get(event_type, self.DEFAULT_LIMITS["default"])

        # Key única por usuario y tipo de evento
        rate_key = f"rate_limit:{user_id}:{event_type}"

        # Verificar duplicado si es requerido
        if config.require_unique and event_id:
            if self._is_duplicate(user_id, event_type, event_id):
                return False, f"Duplicate event_id: {event_id}"

        # Verificar rate limit
        current_count = self._get_count(rate_key, config.window_seconds)

        if current_count >= config.max_events:
            # Bloquear IP si excede mucho (posible bot)
            if current_count >= config.max_events * 2 and client_ip:
                self._block_ip(client_ip)
                logger.warning(
                    f"🚫 IP {client_ip} blocked for event flooding ({event_type})"
                )

            return (
                False,
                f"Rate limit exceeded: {config.max_events} {event_type} per {config.window_seconds}s",
            )

        # Verificar cooldown
        last_event_key = f"last_event:{user_id}:{event_type}"
        last_time = self._get_timestamp(last_event_key)

        if last_time and config.cooldown_seconds > 0:
            elapsed = time.time() - last_time
            if elapsed < config.cooldown_seconds:
                remaining = config.cooldown_seconds - elapsed
                return (
                    False,
                    f"Cooldown active: wait {remaining:.0f}s before next {event_type}",
                )

        # Incrementar contador y actualizar timestamp
        self._increment_count(rate_key, config.window_seconds)
        self._set_timestamp(last_event_key)

        # Registrar event ID si es necesario
        if config.require_unique and event_id:
            self._register_event_id(user_id, event_type, event_id)

        return True, "OK"

    def _is_duplicate(self, user_id: str, event_type: str, event_id: str) -> bool:
        """Verifica si un event_id ya fue usado"""
        dedup_key = f"event_dedup:{user_id}:{event_type}:{event_id}"

        if self.redis:
            return self.redis.exists(dedup_key)
        else:
            # Memoria local con expiración
            now = time.time()
            # Limpiar entradas viejas
            expired_keys = [
                key
                for key in self.memory_cache
                if self.memory_cache[key].get("expires", 0) < now
            ]
            for key in expired_keys:
                self.memory_cache.pop(key, None)

            return dedup_key in self.memory_cache

    def _register_event_id(self, user_id: str, event_type: str, event_id: str):
        """Registra un event_id para deduplicación"""
        dedup_key = f"event_dedup:{user_id}:{event_type}:{event_id}"
        ttl = 86400  # 24 horas

        if self.redis:
            self.redis.setex(dedup_key, ttl, "1")
        else:
            self.memory_cache[dedup_key] = {"value": "1", "expires": time.time() + ttl}

    def _get_count(self, key: str, window: int) -> int:
        """Obtiene contador actual"""
        if self.redis:
            count = self.redis.get(key)
            return int(count) if count else 0
        else:
            entry = self.memory_cache.get(key)
            if not entry:
                return 0
            if entry.get("expires", 0) < time.time():
                self.memory_cache.pop(key, None)
                return 0
            return entry.get("count", 0)

    def _increment_count(self, key: str, window: int):
        """Incrementa contador — Upstash REST compatible (no pipeline)."""
        if self.redis:
            # Individual calls instead of pipeline() for Upstash REST compatibility
            self.redis.incr(key)
            self.redis.expire(key, window)
        else:
            entry = self.memory_cache.get(key)
            if not entry or entry.get("expires", 0) < time.time():
                self.memory_cache[key] = {
                    "count": 1,
                    "expires": time.time() + window,
                }
            else:
                if entry is not None:
                    current_count: int = int(entry.get("count", 0))
                    entry["count"] = current_count + 1

    def _get_timestamp(self, key: str) -> Optional[float]:
        """Obtiene timestamp del último evento"""
        if self.redis:
            ts = self.redis.get(key)
            return float(ts) if ts else None
        else:
            entry = self.memory_cache.get(key)
            return entry.get("timestamp") if entry else None

    def _set_timestamp(self, key: str):
        """Actualiza timestamp"""
        if self.redis:
            self.redis.setex(key, 3600, str(time.time()))  # TTL 1 hora
        else:
            self.memory_cache[key] = {
                "timestamp": time.time(),
                "expires": time.time() + 3600,
            }

    def _is_ip_blocked(self, ip: str) -> bool:
        """Verifica si IP está bloqueada"""
        if ip not in self.blocked_ips:
            return False

        # Verificar si el bloqueo expiró (30 min)
        if time.time() - self.blocked_ips[ip] > 1800:
            self.blocked_ips.pop(ip, None)
            return False

        return True

    def _block_ip(self, ip: str, duration: int = 1800):
        """Bloquea una IP temporalmente"""
        self.blocked_ips[ip] = time.time()
        logger.warning(f"🚫 IP {ip} blocked for {duration}s due to suspicious activity")

    def get_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene estadísticas de rate limiting"""
        stats = {
            "blocked_ips": len(self.blocked_ips),
            "memory_entries": len(self.memory_cache),
            "timestamp": datetime.utcnow().isoformat(),
        }

        if user_id:
            user_events = {
                k: v
                for k, v in self.memory_cache.items()
                if k.startswith(f"rate_limit:{user_id}:")
            }
            stats["user_events"] = len(user_events)

        return stats

    def reset_for_user(self, user_id: str):
        """Resetea rate limits para un usuario (útil para testing)"""
        keys_to_remove = [
            k
            for k in self.memory_cache.keys()
            if k.startswith(f"rate_limit:{user_id}:")
            or k.startswith(f"last_event:{user_id}:")
        ]

        for key in keys_to_remove:
            self.memory_cache.pop(key, None)

        logger.info(f"Rate limits reset for user {user_id}")


# Singleton — now auto-injected with redis_provider
rate_limiter = EventRateLimiter()
