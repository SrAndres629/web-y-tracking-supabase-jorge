"""
👤 Visitor Entity - Visitante del sitio web.

Un visitante es una Entidad porque:
- Tiene identidad única (external_id)
- Tiene ciclo de vida (creado, actualizado)
- Puede cambiar de estado (atributos mutables)
- Se identifica por external_id, no por atributos
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Self
from enum import Enum, auto

from app.domain.models.values import ExternalId, UTMParams, GeoLocation


class VisitorSource(Enum):
    """Fuente de tráfico del visitante."""
    PAGEVIEW = "pageview"
    FACEBOOK_AD = "facebook_ad"
    ORGANIC_SEARCH = "organic_search"
    DIRECT = "direct"
    REFERRAL = "referral"
    WHATSAPP = "whatsapp"


@dataclass
class Visitor:
    """
    Entidad: Visitante del sitio web.
    
    Identity: external_id (hash de IP + User-Agent)
    
    Attributes:
        external_id: ID único determinístico
        fbclid: Facebook Click ID (para atribución)
        fbp: Facebook Browser ID (cookie)
        ip_address: IP del visitante (hasheada para privacidad)
        user_agent: User-Agent string
        source: Fuente de tráfico
        utm: Parámetros UTM
        geo: Ubicación geográfica
        created_at: Timestamp de creación
        last_seen: Última actividad
    """
    # Identity
    external_id: ExternalId
    
    # Facebook identifiers (para CAPI)
    fbclid: Optional[str] = None
    fbp: Optional[str] = None
    
    # Personal data (for higher EMQ)
    email: Optional[Email] = None
    phone: Optional[Phone] = None
    
    # Technical data
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Attribution
    source: VisitorSource = field(default_factory=lambda: VisitorSource.PAGEVIEW)
    utm: UTMParams = field(default_factory=UTMParams)
    geo: GeoLocation = field(default_factory=GeoLocation)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    visit_count: int = 1
    
    @classmethod
    def create(
        cls,
        ip: str,
        user_agent: str,
        fbclid: Optional[str] = None,
        fbp: Optional[str] = None,
        source: VisitorSource = VisitorSource.PAGEVIEW,
        utm: Optional[UTMParams] = None,
        geo: Optional[GeoLocation] = None,
        email: Optional[Email] = None,
        phone: Optional[Phone] = None,
    ) -> Self:
        """
        Factory method para crear nuevo visitante.
        
        El external_id es determinístico (mismo IP+UA = mismo ID),
        permitiendo reconocer visitantes recurrentes sin cookies.
        """
        return cls(
            external_id=ExternalId.from_request(ip, user_agent),
            fbclid=fbclid,
            fbp=fbp,
            ip_address=ip,  # Considerar hashear para GDPR
            user_agent=user_agent[:500] if user_agent else None,  # Limitar tamaño
            source=source,
            utm=utm or UTMParams(),
            geo=geo or GeoLocation(),
            email=email,
            phone=phone,
        )
    
    @classmethod
    def reconstruct(
        cls,
        external_id: ExternalId,
        fbclid: Optional[str] = None,
        fbp: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        source: VisitorSource = VisitorSource.PAGEVIEW,
        utm: Optional[UTMParams] = None,
        geo: Optional[GeoLocation] = None,
        created_at: Optional[datetime] = None,
        last_seen: Optional[datetime] = None,
        visit_count: int = 1,
        email: Optional[Email] = None,
        phone: Optional[Phone] = None,
    ) -> Self:
        """
        Reconstruye visitante desde datos persistidos.
        
        Usar solo en repositorios, no para crear nuevos.
        """
        return cls(
            external_id=external_id,
            fbclid=fbclid,
            fbp=fbp,
            ip_address=ip_address,
            user_agent=user_agent,
            source=source,
            utm=utm or UTMParams(),
            geo=geo or GeoLocation(),
            created_at=created_at or datetime.utcnow(),
            last_seen=last_seen or datetime.utcnow(),
            visit_count=visit_count,
            email=email,
            phone=phone,
        )
    
    def record_visit(self) -> None:
        """Actualiza last_seen e incrementa contador."""
        self.last_seen = datetime.utcnow()
        self.visit_count += 1
    
    def update_fbclid(self, fbclid: Optional[str]) -> None:
        """
        Actualiza FBCLID si es nuevo.
        
        No sobreescribe FBCLID existente (primera atribución gana),
        a menos que sea un click nuevo confirmado.
        """
        if fbclid and not self.fbclid:
            self.fbclid = fbclid
    
    def update_fbp(self, fbp: Optional[str]) -> None:
        """Actualiza FBP (Facebook Browser ID)."""
        if fbp:
            self.fbp = fbp
    
    def to_meta_user_data(self) -> dict[str, str]:
        """
        Convierte a formato UserData para Meta CAPI.
        
        Todos los PII deben estar hasheado (SHA256).
        """
        from app.core.validators import hash_sha256
        
        data: dict[str, str] = {
            "external_id": hash_sha256(self.external_id.value),
        }
        
        if self.fbclid:
            # fbc format: fb.1.<timestamp>.<fbclid>
            import time
            data["fbc"] = f"fb.1.{int(time.time())}.{self.fbclid}"
        
        if self.fbp:
            data["fbp"] = self.fbp
        
        if self.email:
            data["em"] = self.email.hash
            
        if self.phone:
            data["ph"] = self.phone.hash

        if self.ip_address:
            data["client_ip_address"] = self.ip_address

        if self.user_agent:
            data["client_user_agent"] = self.user_agent
        
        # Geo data (hashed)
        geo_data = self.geo.to_meta_format()
        data.update(geo_data)
        
        return data
    
    @property
    def is_tracked(self) -> bool:
        """True si tiene algún identificador de tracking."""
        return bool(self.fbclid or self.fbp)
    
    @property
    def days_since_last_visit(self) -> int:
        """Días desde última visita."""
        return (datetime.utcnow() - self.last_seen).days
    
    def __repr__(self) -> str:
        return f"Visitor({self.external_id}, visits={self.visit_count})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Visitor):
            return NotImplemented
        return self.external_id == other.external_id
    
    def __hash__(self) -> int:
        return hash(self.external_id)
