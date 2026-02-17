"""
Antigravity Extension para Kimi CLI
Extensión profesional para integración nativa
"""

__version__ = "1.0.0"
__author__ = "NEXUS-7"

from .client import AntigravityClient, Model, QuotaInfo

__all__ = ["AntigravityClient", "QuotaInfo", "Model"]
