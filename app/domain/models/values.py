"""
💎 Value Objects - Objetos inmutables sin identidad.

Características:
- Inmutables (frozen dataclasses)
- Validación en constructor
- Igualdad por valor, no por identidad
- Pueden ser compartidos
"""

from __future__ import annotations

import re
import hashlib
import random
import string
import time
from dataclasses import dataclass
from typing import Optional

from app.core.result import Result
from app.core.validators import (
    validate_phone,
    validate_email,
    validate_event_id,
    generate_external_id,
    hash_sha256,
)


@dataclass(frozen=True, slots=True)
class EventId:
    """
    Identificador único de evento.
    
    Formato: evt_<timestamp_ns>_<entropy>
    Ejemplo: evt_1707612345678901234_a3f9b2
    """
    value: str
    
    def __post_init__(self):
        is_valid, error = validate_event_id(self.value)
        if not is_valid:
            raise ValueError(f"Invalid EventId: {error}")
    
    @classmethod
    def generate(cls):
        """Genera nuevo EventId único."""
        timestamp = time.time_ns()
        entropy = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return cls(f"evt_{timestamp}_{entropy}")
    
    @classmethod
    def from_string(cls, value: str):
        """Intenta crear desde string, retorna Result."""
        try:
            return Result.ok(cls(value))
        except ValueError as e:
            return Result.err(str(e))
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"EventId({self.value!r})"


@dataclass(frozen=True, slots=True)
class ExternalId:
    """
    ID externo del visitante (hash de IP + User-Agent).
    
    Formato: 32 caracteres hex (SHA256 truncado)
    """
    value: str
    
    def __post_init__(self):
        if not re.match(r'^[a-f0-9]{32}$', self.value):
            raise ValueError(f"Invalid ExternalId format: {self.value}")
    
    @classmethod
    def from_request(cls, ip: str, user_agent: str):
        """Genera ExternalId desde IP y User-Agent."""
        return cls(generate_external_id(ip, user_agent))
    
    @classmethod
    def from_string(cls, value: str):
        try:
            return Result.ok(cls(value))
        except ValueError as e:
            return Result.err(str(e))
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"ExternalId({self.value[:8]}...)"


@dataclass(frozen=True, slots=True)
class Phone:
    """
    Número de teléfono normalizado.
    
    Siempre almacenado en formato E.164: +591XXXXXXXX
    """
    number: str  # Formato: +59164714751
    country_code: str = "BO"
    
    def __post_init__(self):
        if not self.number.startswith("+"):
            raise ValueError(f"Phone must start with +: {self.number}")
    
    @classmethod
    def parse(cls, raw: Optional[str], country: str = "BO"):
        """
        Parsea teléfono desde string crudo.
        
        Examples:
            >>> Phone.parse("64714751")
            Ok(Phone(+59164714751))
            >>> Phone.parse("+591 647-14751")
            Ok(Phone(+59164714751))
        """
        if raw is None:
            return Result.err("Phone is required (None provided)")
        if not str(raw).strip():
            return Result.err("Phone is required (Empty string provided)")
        
        result = validate_phone(str(raw), country)
        if not result.is_valid:
            return Result.err(result.error or "Invalid phone")
        
        return Result.ok(cls(
            number=result.normalized or "",
            country_code=result.country_code or country
        ))
    
    @property
    def hash(self) -> str:
        """SHA256 hash para Meta CAPI (normalizado lowercase)."""
        return hash_sha256(self.number)
    
    @property
    def local_format(self) -> str:
        """Formato local (sin código de país)."""
        if self.number.startswith("+591"):
            return self.number[4:]
        return self.number
    
    def __str__(self) -> str:
        return self.number
    
    def __repr__(self) -> str:
        return f"Phone({self.number})"


@dataclass(frozen=True, slots=True)
class Email:
    """
    Email validado y normalizado.
    """
    address: str  # lowercase, stripped
    
    def __post_init__(self):
        is_valid, normalized, error = validate_email(self.address)
        if not is_valid:
            raise ValueError(f"Invalid email: {error}")
        # Enforce lowercase in frozen dataclass via object.__setattr__
        object.__setattr__(self, 'address', normalized or self.address.lower().strip())
    
    @classmethod
    def parse(cls, raw: Optional[str]):
        if raw is None:
            return Result.err("Email is required (None provided)")
        if not str(raw).strip():
            return Result.err("Email is required (Empty string provided)")
        
        is_valid, normalized, error = validate_email(str(raw))
        if not is_valid:
            return Result.err(error or "Invalid email")
        
        return Result.ok(cls(address=normalized or ""))
    
    @property
    def hash(self) -> str:
        """SHA256 hash para Meta CAPI."""
        return hash_sha256(self.address)
    
    @property
    def domain(self) -> str:
        """Dominio del email."""
        return self.address.split("@")[1]
    
    def __str__(self) -> str:
        return self.address
    
    def __repr__(self) -> str:
        return f"Email({self.address})"


@dataclass(frozen=True, slots=True)
class GeoLocation:
    """
    Ubicación geográfica (opcional, para matching avanzado).
    """
    country: Optional[str] = None   # ISO 3166-1 alpha-2: "BO"
    city: Optional[str] = None
    region: Optional[str] = None
    zip_code: Optional[str] = None
    
    def to_meta_format(self) -> dict[str, str]:
        """Convierte a formato requerido por Meta CAPI."""
        result: dict[str, str] = {}
        if self.country:
            result["country"] = hash_sha256(self.country.lower())
        if self.city:
            result["city"] = hash_sha256(self.city.lower().replace(" ", ""))
        if self.region:
            result["state"] = hash_sha256(self.region.lower())
        if self.zip_code:
            result["zip"] = hash_sha256(self.zip_code)
        return result


@dataclass(frozen=True, slots=True)
class UTMParams:
    """
    Parámetros UTM de tracking.
    """
    source: Optional[str] = None
    medium: Optional[str] = None
    campaign: Optional[str] = None
    term: Optional[str] = None
    content: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        from app.core.validators import sanitize_utm
        return cls(
            source=sanitize_utm(data.get("utm_source")),
            medium=sanitize_utm(data.get("utm_medium")),
            campaign=sanitize_utm(data.get("utm_campaign")),
            term=sanitize_utm(data.get("utm_term")),
            content=sanitize_utm(data.get("utm_content")),
        )
    
    def to_dict(self) -> dict[str, Optional[str]]:
        return {
            "utm_source": self.source,
            "utm_medium": self.medium,
            "utm_campaign": self.campaign,
            "utm_term": self.term,
            "utm_content": self.content,
        }
    
    @property
    def is_empty(self) -> bool:
        return all(v is None for v in [self.source, self.medium, self.campaign])
