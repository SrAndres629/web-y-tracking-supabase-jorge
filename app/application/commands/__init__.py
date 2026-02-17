"""
📝 Command Handlers - Casos de uso de escritura (CQRS).

Cada handler es responsable de una operación de escritura.
Orquestan: validación, dominio, persistencia, side effects.
"""

from app.application.commands.create_lead import CreateLeadCommand, CreateLeadHandler
from app.application.commands.create_visitor import CreateVisitorCommand, CreateVisitorHandler
from app.application.commands.track_event import TrackEventCommand, TrackEventHandler

__all__ = [
    "TrackEventCommand",
    "TrackEventHandler",
    "CreateVisitorCommand",
    "CreateVisitorHandler",
    "CreateLeadCommand",
    "CreateLeadHandler",
]
