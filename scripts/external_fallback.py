#!/usr/bin/env python3
"""
🛡️ Antigravity External Fallback
Sistema de redundancia para usar modelos externos (Groq, OpenAI, Anthropic)
cuando la quota natural de Antigravity se agota.
"""

import argparse
import http.client
import json
import os
import sys
from typing import Any, Dict, Optional


class FallbackManager:
    """Manages external model requests as fallbacks."""

    PROVIDERS = {
        "groq": {
            "url": "api.groq.com",
            "path": "/lite/v1/chat/completions",
            "header_key": "Authorization",
            "header_val": "Bearer {key}",
        },
        "openai": {
            "url": "api.openai.com",
            "path": "/v1/chat/completions",
            "header_key": "Authorization",
            "header_val": "Bearer {key}",
        },
    }

    def __init__(self):
        self.api_key = os.getenv("EXTERNAL_FALLBACK_KEY")
        self.provider = os.getenv("EXTERNAL_FALLBACK_PROVIDER", "groq").lower()
        self.default_model = os.getenv("EXTERNAL_FALLBACK_MODEL", "llama-3.3-70b-versatile")

    def _make_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            print("❌ Error: EXTERNAL_FALLBACK_KEY no encontrada.")
            return None

        config = self.PROVIDERS.get(self.provider)
        if not config:
            print(f"❌ Error: Proveedor '{self.provider}' no soportado.")
            return None

        headers = {
            "Content-Type": "application/json",
            config["header_key"]: config["header_val"].format(key=self.api_key),
        }

        try:
            conn = http.client.HTTPSConnection(config["url"])
            conn.request("POST", config["path"], json.dumps(payload), headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()

            if response.status != 200:
                print(f"❌ Error API ({response.status}): {data.decode()}")
                return None

            return json.loads(data)
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return None

    def chat(self, prompt: str, model: Optional[str] = None) -> Optional[str]:
        """Sends a simple chat request."""
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }

        result = self._make_request(payload)
        if result and "choices" in result:
            return result["choices"][0]["message"]["content"]
        return None


def main():
    parser = argparse.ArgumentParser(description="Antigravity Fallback CLI")
    parser.add_argument("prompt", nargs="?", help="El prompt para el modelo")
    parser.add_argument("--model", help="Modelo específico a usar")
    parser.add_argument("--test", action="store_true", help="Probar conexión")

    args = parser.parse_args()

    manager = FallbackManager()

    if args.test:
        print(f"🔍 Probando conexión con {manager.provider}...")
        res = manager.chat("Responde solo con la palabra 'OK' si recibes esto.")
        if res and "OK" in res.upper():
            print("✅ Conexión exitosa.")
        else:
            print("❌ Fallo en la prueba.")
        return

    if not args.prompt:
        parser.print_help()
        return

    content = manager.chat(args.prompt, args.model)
    if content:
        print(content)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
