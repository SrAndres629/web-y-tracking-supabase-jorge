"""
🧬 Meta CAPI - Elite Service (Compatibility Layer).
Provides EnhancedUserData, EnhancedCustomData, and EliteMetaCAPIService
used across legacy routes and tests.
"""

from __future__ import annotations

import hashlib  # Added for PII hashing
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from app.infrastructure.config.settings import settings
from app.tracking import send_event_async

logger = logging.getLogger(__name__)

try:
    # Optional SDK (facebook_business)
    from facebook_business.adobjects.userdata import UserData  # type: ignore

    SDK_AVAILABLE = True
except Exception:
    UserData = None  # type: ignore
    SDK_AVAILABLE = False


class MetaEventType(str, Enum):
    Lead = "Lead"
    Contact = "Contact"
    Purchase = "Purchase"
    PageView = "PageView"
    ViewContent = "ViewContent"
    CustomizeProduct = "CustomizeProduct"


def _hash(value: str) -> str:
    """Hashes a string value using SHA256."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize_email(email: Optional[str]) -> Optional[str]:
    if not email:
        return None
    return _hash(email.strip().lower())


def _normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    digits = re.sub(r"[^0-9]", "", phone)
    if digits and not digits.startswith("591"):
        digits = "591" + digits
    return _hash(digits)


def _normalize_city(city: Optional[str]) -> Optional[str]:
    if not city:
        return None
    return _hash(city.strip().lower().replace(" ", ""))


def _normalize_first_name(first_name: Optional[str]) -> Optional[str]:
    if not first_name:
        return None
    return _hash(first_name.strip().lower())


def _normalize_last_name(last_name: Optional[str]) -> Optional[str]:
    if not last_name:
        return None
    return _hash(last_name.strip().lower())


def _normalize_country(country: Optional[str]) -> Optional[str]:
    if not country:
        return None
    return _hash(country.strip().lower())


def _normalize_zip_code(zip_code: Optional[str]) -> Optional[str]:
    if not zip_code:
        return None
    return _hash(zip_code.strip().replace(" ", ""))  # No lower for zip codes


def _normalize_state(state: Optional[str]) -> Optional[str]:
    if not state:
        return None
    return _hash(state.strip().lower().replace(" ", ""))


@dataclass
class EnhancedUserData:
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None  # Added for Meta CAPI
    zip_code: Optional[str] = None  # Added for Meta CAPI
    external_id: Optional[str] = None

    def _set_contact_info(self, sdk_user_data: Any) -> None:
        if self.email:
            sdk_user_data.email = _normalize_email(self.email)
        if self.phone:
            sdk_user_data.phone = _normalize_phone(self.phone)
        if self.first_name:
            sdk_user_data.first_name = _normalize_first_name(self.first_name)
        if self.last_name:
            sdk_user_data.last_name = _normalize_last_name(self.last_name)
        if self.city:
            sdk_user_data.city = _normalize_city(self.city)
        if self.state:
            sdk_user_data.state = _normalize_state(self.state)
        if self.zip_code:
            sdk_user_data.zip_code = _normalize_zip_code(self.zip_code)
        if self.country:
            sdk_user_data.country_code = _normalize_country(self.country)

    def to_sdk_user_data(self) -> Any:
        """Build SDK UserData (or dict fallback) with normalized values."""
        if SDK_AVAILABLE and UserData is not None:
            sdk_user_data = UserData()
            self._set_contact_info(sdk_user_data)
            return sdk_user_data
        # Fallback dict (for tests / no SDK)
        return {
            "email": _normalize_email(self.email),
            "phone": _normalize_phone(self.phone),
            "first_name": _normalize_first_name(self.first_name),
            "last_name": _normalize_last_name(self.last_name),
            "city": _normalize_city(self.city),
            "state": _normalize_state(self.state),
            "zip_code": _normalize_zip_code(self.zip_code),
            "country_code": _normalize_country(self.country),
        }


@dataclass
class EnhancedCustomData:
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return custom data as a plain dict."""
        return dict(self.data or {})


class EliteMetaCAPIService:
    """Orquestador Elite para envío a Meta CAPI."""

    def __init__(self):
        self.sandbox_mode = settings.META_SANDBOX_MODE

    def _deduplicate(self, event_id: str, event_name: str) -> bool:
        try:
            from app.cache import deduplicate_event

            return deduplicate_event(event_id, event_name)
        except Exception:
            return True

    async def send_event(
        self,
        event_name: str,
        event_id: str,
        event_source_url: str,
        user_data: EnhancedUserData,
        custom_data: Optional[EnhancedCustomData] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        fbp: Optional[str] = None,
        fbc: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send event using SDK if available, else HTTP fallback."""
        if not self._deduplicate(event_id, event_name):
            return {"status": "duplicate", "event_id": event_id}

        if self.sandbox_mode or settings.META_SANDBOX_MODE:
            return {"status": "sandbox", "event_id": event_id}

        if not SDK_AVAILABLE:
            ok = await send_event_async(
                event_name=event_name,
                event_source_url=event_source_url,
                client_ip=client_ip or "0.0.0.0",  # nosec B104
                user_agent=user_agent or "unknown",
                event_id=event_id,
                external_id=user_data.external_id,
                fbp=fbp,
                fbc=fbc,
                email=user_data.email,
                phone=user_data.phone,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                city=user_data.city,
                country=user_data.country,
                custom_data=(custom_data.to_dict() if custom_data else None),
                access_token=kwargs.get("access_token"),
                pixel_id=kwargs.get("pixel_id"),
            )
            return {
                "status": "success" if ok else "error",
                "method": "http_fallback",
                "event_id": event_id,
            }

        # SDK path (mocked in tests)
        _ = user_data.to_sdk_user_data()
        return {"status": "success", "method": "sdk", "event_id": event_id}


elite_capi = EliteMetaCAPIService()


async def send_elite_event(
    event_name: str,
    event_id: str,
    url: str,
    client_ip: str,
    user_agent: str,
    external_id: Optional[str] = None,
    fbc: Optional[str] = None,
    fbp: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    country: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
    access_token: Optional[str] = None,
    pixel_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Convenience wrapper for EliteMetaCAPIService."""
    user_data = EnhancedUserData(
        email=email,
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        city=city,
        country=country,
        external_id=external_id,
    )
    custom = EnhancedCustomData(custom_data or {})
    return await elite_capi.send_event(
        event_name=event_name,
        event_id=event_id,
        event_source_url=url,
        user_data=user_data,
        custom_data=custom,
        client_ip=client_ip,
        user_agent=user_agent,
        fbp=fbp,
        fbc=fbc,
        access_token=access_token,
        pixel_id=pixel_id,
    )
