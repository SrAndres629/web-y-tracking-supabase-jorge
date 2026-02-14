"""
⚠️ Domain Exceptions - Errores del dominio.

Estas excepciones representan casos de error del negocio,
no errores técnicos (que van en infrastructure).
"""


class DomainError(Exception):
    """Base para todas las excepciones de dominio."""
    pass


# ===== Visitor Errors =====

class VisitorError(DomainError):
    """Error relacionado con visitantes."""
    pass


class VisitorNotFoundError(VisitorError):
    """Visitante no encontrado."""
    def __init__(self, external_id: str):
        self.external_id = external_id
        super().__init__(f"Visitor not found: {external_id}")


class DuplicateVisitorError(VisitorError):
    """Visitante duplicado."""
    pass


# ===== Lead Errors =====

class LeadError(DomainError):
    """Error relacionado con leads."""
    pass


class LeadNotFoundError(LeadError):
    """Lead no encontrado."""
    def __init__(self, lead_id: str):
        self.lead_id = lead_id
        super().__init__(f"Lead not found: {lead_id}")


class DuplicateLeadError(LeadError):
    """Lead duplicado (teléfono ya existe)."""
    def __init__(self, phone: str):
        self.phone = phone
        super().__init__(f"Lead with phone already exists: {phone}")


class InvalidLeadStatusError(LeadError):
    """Transición de estado inválida."""
    pass


# ===== Event Errors =====

class EventError(DomainError):
    """Error relacionado con eventos."""
    pass


class DuplicateEventError(EventError):
    """Evento duplicado."""
    pass


class InvalidEventError(EventError):
    """Datos de evento inválidos."""
    pass


# ===== Validation Errors =====

class ValidationError(DomainError):
    """Error de validación de datos."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class InvalidPhoneError(ValidationError):
    """Teléfono inválido."""
    def __init__(self, phone: str):
        super().__init__("phone", f"Invalid phone format: {phone}")


class InvalidEmailError(ValidationError):
    """Email inválido."""
    def __init__(self, email: str):
        super().__init__("email", f"Invalid email format: {email}")


# ===== Tracking Errors =====

class TrackingError(DomainError):
    """Error en sistema de tracking."""
    pass


class DeduplicationError(TrackingError):
    """Error en deduplicación."""
    pass


class AttributionError(TrackingError):
    """Error en atribución."""
    pass
