"""
✅ Core Validators - Validación de Value Objects.

Funciones puras para validar datos de entrada.
No dependen de infraestructura externa.
"""

from __future__ import annotations

import re
import hashlib
from typing import Optional, Tuple
from dataclasses import dataclass


# ===== Phone Validation =====

@dataclass(frozen=True)
class PhoneValidationResult:
    """Resultado de validación de teléfono."""
    is_valid: bool
    normalized: Optional[str] = None
    country_code: Optional[str] = None
    error: Optional[str] = None


def validate_phone(phone: Optional[str], default_country: str = "BO") -> PhoneValidationResult:
    """
    Valida y normaliza número de teléfono.
    
    Bolivia (BO):
    - Móviles: 7 dígitos, prefijo opcional +591 o 591
    - Fijos: 7 dígitos con código de área
    
    Returns:
        PhoneValidationResult con número normalizado (+591XXXXXXXX)
    """
    if not phone:
        return PhoneValidationResult(is_valid=False, error="Phone is required")
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) < 7:
        return PhoneValidationResult(is_valid=False, error="Phone too short")
    
    if len(digits) > 15:
        return PhoneValidationResult(is_valid=False, error="Phone too long")
    
    # Bolivia specific logic
    if default_country == "BO":
        # If starts with 591, keep it
        if digits.startswith("591"):
            if len(digits) == 10:  # 591 + 7 digits
                return PhoneValidationResult(
                    is_valid=True,
                    normalized=f"+{digits}",
                    country_code="BO"
                )
        # If 7 digits, add 591
        elif len(digits) == 7:
            return PhoneValidationResult(
                is_valid=True,
                normalized=f"+591{digits}",
                country_code="BO"
            )
        # If 8 digits starting with 7, 6, etc (mobile), add 591
        elif len(digits) == 8 and digits[0] in "765":
            return PhoneValidationResult(
                is_valid=True,
                normalized=f"+591{digits}",
                country_code="BO"
            )
    
    # Generic international format
    if digits.startswith("1") and len(digits) == 11:  # US
        return PhoneValidationResult(
            is_valid=True,
            normalized=f"+{digits}",
            country_code="US"
        )
    
    # Fallback: assume it needs +
    return PhoneValidationResult(
        is_valid=True,
        normalized=f"+{digits}" if not digits.startswith("+") else digits,
        country_code=default_country
    )


# ===== Email Validation =====

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


def validate_email(email: Optional[str]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Valida email y retorna (is_valid, normalized, error).
    """
    if not email:
        return False, None, "Email is required"
    
    normalized = email.lower().strip()
    
    if len(normalized) > 254:
        return False, None, "Email too long"
    
    if not EMAIL_REGEX.match(normalized):
        return False, None, "Invalid email format"
    
    return True, normalized, None


def normalize_email(email: str) -> str:
    """Normaliza email (lowercase, strip)."""
    return email.lower().strip()


# ===== Hashing Utilities =====

def hash_sha256(value: str) -> str:
    """Hash SHA256 para PII (Meta CAPI requirement)."""
    return hashlib.sha256(value.lower().strip().encode('utf-8')).hexdigest()


def hash_email(email: str) -> str:
    """Hash email normalizado."""
    return hash_sha256(normalize_email(email))


def hash_phone(phone: str) -> str:
    """Hash teléfono normalizado."""
    result = validate_phone(phone)
    if result.is_valid and result.normalized:
        return hash_sha256(result.normalized)
    return hash_sha256(phone)  # Fallback


# ===== ID Validation =====

EXTERNAL_ID_REGEX = re.compile(r'^[a-f0-9]{32}$')


def validate_external_id(external_id: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Valida external_id (formato SHA256 truncado a 32 chars hex).
    """
    if not external_id:
        return False, "External ID is required"
    
    if not EXTERNAL_ID_REGEX.match(external_id):
        return False, "Invalid external_id format"
    
    return True, None


def generate_external_id(ip: str, user_agent: str) -> str:
    """
    Genera external_id determinístico desde IP + User-Agent.
    """
    combined = f"{ip}_{user_agent}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:32]


# ===== URL Validation =====

def validate_url(url: Optional[str], allowed_schemes: Optional[list[str]] = None) -> Tuple[bool, Optional[str]]:
    """
    Valida URL básica.
    """
    if not url:
        return False, "URL is required"
    
    schemes = allowed_schemes or ["https", "http"]
    
    if "://" not in url:
        return False, "Invalid URL format"
    
    scheme = url.split("://")[0].lower()
    if scheme not in schemes:
        return False, f"Scheme must be one of: {schemes}"
    
    return True, None


# ===== Event ID Validation =====

EVENT_ID_REGEX = re.compile(r'^evt_\d+_[a-z0-9]{6,}$')


def validate_event_id(event_id: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Valida formato de event_id.
    Formato esperado: evt_<timestamp>_<entropy>
    """
    if not event_id:
        return False, "Event ID is required"
    
    if not EVENT_ID_REGEX.match(event_id):
        return False, "Invalid event_id format (expected: evt_<timestamp>_<entropy>)"
    
    return True, None


# ===== String Sanitization =====

def sanitize_string(value: Optional[str], max_length: int = 500) -> Optional[str]:
    """
    Sanitiza string para almacenamiento seguro.
    - Strip whitespace
    - Truncate
    - Remove null bytes
    """
    if not value:
        return None
    
    # Remove null bytes and control chars except newlines
    cleaned = value.replace('\x00', '').replace('\r', '')
    cleaned = ''.join(c for c in cleaned if ord(c) >= 32 or c == '\n')
    
    # Strip and truncate
    cleaned = cleaned.strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned if cleaned else None


def sanitize_utm(value: Optional[str]) -> Optional[str]:
    """Sanitiza parámetros UTM (alphanumeric + some chars)."""
    if not value:
        return None
    
    # Allow alphanumeric, hyphen, underscore
    cleaned = re.sub(r'[^a-zA-Z0-9\-_\.]', '', value)
    return cleaned[:100] if cleaned else None
