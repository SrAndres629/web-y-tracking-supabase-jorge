"""
Antigravity API Client
Cliente unificado para la API de Antigravity
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests


@dataclass
class QuotaInfo:
    total: int
    used: int
    remaining: int
    reset_date: str
    percentage_used: float


@dataclass
class Model:
    id: str
    name: str
    description: str
    max_tokens: int
    pricing_input: float
    pricing_output: float
    capabilities: List[str]
    status: str


class AntigravityClient:
    """Cliente para API de Antigravity"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTIGRAVITY_API_KEY")
        self.base_url = base_url or os.getenv(
            "ANTIGRAVITY_BASE_URL", "https://api.antigravity.ai/v1"
        )

        if not self.api_key:
            raise ValueError("ANTIGRAVITY_API_KEY no configurada")

        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        )

    def get_quota(self) -> QuotaInfo:
        """Obtiene información de quota"""
        try:
            response = self.session.get(f"{self.base_url}/quota")
            response.raise_for_status()
            data = response.json()

            total = data.get("total_quota", 0)
            used = data.get("used_quota", 0)
            remaining = total - used

            return QuotaInfo(
                total=total,
                used=used,
                remaining=remaining,
                reset_date=data.get("reset_date", "N/A"),
                percentage_used=(used / total * 100) if total > 0 else 0,
            )
        except Exception as e:
            print(f"❌ Error obteniendo quota: {e}")
            return QuotaInfo(0, 0, 0, "N/A", 0)

    def get_models(self) -> List[Model]:
        """Lista todos los modelos disponibles"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()

            models = []
            for m in data.get("data", []):
                models.append(
                    Model(
                        id=m.get("id", "unknown"),
                        name=m.get("name", "Unknown"),
                        description=m.get("description", ""),
                        max_tokens=m.get("max_tokens", 0),
                        pricing_input=m.get("pricing", {}).get("input", 0),
                        pricing_output=m.get("pricing", {}).get("output", 0),
                        capabilities=m.get("capabilities", []),
                        status=m.get("status", "unknown"),
                    )
                )
            return models
        except Exception as e:
            print(f"❌ Error obteniendo modelos: {e}")
            return []

    def get_mcps(self) -> List[Dict[str, Any]]:
        """Lista MCPs disponibles"""
        try:
            response = self.session.get(f"{self.base_url}/mcps")
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            print(f"❌ Error obteniendo MCPs: {e}")
            return []

    def use_mcp(self, mcp_name: str, input_data: Dict) -> Dict:
        """Usa un MCP específico"""
        try:
            response = self.session.post(f"{self.base_url}/mcps/{mcp_name}/invoke", json=input_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Status completo del sistema"""
        return {
            "quota": self.get_quota(),
            "models": self.get_models(),
            "mcps": self.get_mcps(),
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    client = AntigravityClient()
    print(json.dumps(client.get_status(), indent=2, default=str))
