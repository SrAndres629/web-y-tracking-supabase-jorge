import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ExternalIntegrationBase(ABC):
    """
    Abstract Base Class for external platform integrations.

    Provides a consistent interface and basic logging for different
    third-party services like CRM, Email, Analytics, etc.
    """

    platform_name: str

    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        logger.info(f"Initialized {self.platform_name} Integration Base.")

    @abstractmethod
    async def send_event(
        self,
        event_name: str,
        payload: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Abstract method to send a generic event to the external platform.

        Args:
            event_name: The name of the event (e.g., "LeadCaptured", "UserSignedUp").
            payload: A dictionary containing event-specific data.
            user_context: Optional dictionary with user identification and context.

        Returns:
            True if the event was successfully sent, False otherwise.
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Abstract method to get the current status or health of the integration.

        Returns:
            A dictionary containing status information (e.g., {"status": "ok", "last_event_sent": "timestamp"}).
        """
        pass

    async def log_integration_call(self, method: str, success: bool, details: Optional[str] = None):
        """
        Logs an integration call outcome.

        Args:
            method: The method that was called (e.g., "send_event", "authenticate").
            success: Boolean indicating if the call was successful.
            details: Optional additional details about the call or error.
        """
        status = "SUCCESS" if success else "FAILURE"
        log_message = f"[{self.platform_name}] {method} call: {status}"
        if details:
            log_message += f" - Details: {details}"

        if success:
            logger.info(log_message)
        else:
            logger.error(log_message)

    # You can add more common methods here that all integrations might share, e.g.:
    # @abstractmethod
    # async def authenticate(self) -> bool:
    #     """Authenticates with the external platform."""
    #     pass
