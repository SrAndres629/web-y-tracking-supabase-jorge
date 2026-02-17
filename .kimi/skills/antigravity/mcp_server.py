#!/usr/bin/env python3
"""
Antigravity MCP Server
Servidor MCP para integración nativa con Kimi CLI
"""

import json
from typing import Dict

from client import AntigravityClient


class AntigravityMCPServer:
    """Servidor MCP para Antigravity"""

    def __init__(self):
        self.client = AntigravityClient()

    def handle_initialize(self, params: Dict) -> Dict:
        """Inicialización del servidor MCP"""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "antigravity-mcp", "version": "1.0.0"},
            "capabilities": {"tools": {}},
        }

    def handle_tools_list(self) -> Dict:
        """Lista herramientas MCP disponibles"""
        mcps = self.client.get_mcps()

        tools = []
        for mcp in mcps:
            tools.append(
                {
                    "name": mcp.get("name"),
                    "description": mcp.get("description", "MCP de Antigravity"),
                    "inputSchema": mcp.get("input_schema", {"type": "object", "properties": {}}),
                }
            )

        # Añadir herramientas built-in
        tools.extend(
            [
                {
                    "name": "get_quota",
                    "description": "Obtiene quota disponible de Antigravity",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": "list_models",
                    "description": "Lista modelos disponibles en Antigravity",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "string",
                                "description": "Filtro opcional por capacidad",
                            }
                        },
                    },
                },
                {
                    "name": "use_model",
                    "description": "Usa un modelo específico de Antigravity",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "ID del modelo"},
                            "prompt": {"type": "string", "description": "Prompt a enviar"},
                            "temperature": {"type": "number", "default": 0.7},
                        },
                        "required": ["model", "prompt"],
                    },
                },
            ]
        )

        return {"tools": tools}

    def handle_tool_call(self, params: Dict) -> Dict:
        """Ejecuta una herramienta"""
        name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if name == "get_quota":
                quota = self.client.get_quota()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Quota: {quota.remaining:,} tokens disponibles ({quota.percentage_used:.1f}% usado)",
                        }
                    ]
                }

            elif name == "list_models":
                models = self.client.get_models()
                filter_cap = arguments.get("filter", "")

                if filter_cap:
                    models = [m for m in models if filter_cap in m.capabilities]

                text = "Modelos disponibles:\n"
                for m in models:
                    text += f"- {m.name} ({m.id}): {m.max_tokens} tokens max\n"

                return {"content": [{"type": "text", "text": text}]}

            elif name == "use_model":
                model_id = arguments.get("model")
                prompt = arguments.get("prompt")
                temperature = arguments.get("temperature", 0.7)

                # Aquí iría la llamada real al modelo
                result = f"[Usando {model_id} con temperatura {temperature}]\n\nPrompt: {prompt[:100]}..."

                return {"content": [{"type": "text", "text": result}]}

            else:
                # MCP custom de Antigravity
                result = self.client.use_mcp(name, arguments)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}

    def run(self):
        """Loop principal del servidor MCP"""
        while True:
            try:
                line = input()
                message = json.loads(line)

                method = message.get("method")
                params = message.get("params", {})
                request_id = message.get("id")

                if method == "initialize":
                    result = self.handle_initialize(params)
                elif method == "tools/list":
                    result = self.handle_tools_list()
                elif method == "tools/call":
                    result = self.handle_tool_call(params)
                else:
                    result = {"error": f"Método desconocido: {method}"}

                response = {"jsonrpc": "2.0", "id": request_id, "result": result}

                print(json.dumps(response), flush=True)

            except EOFError:
                break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id") if "message" in locals() else None,
                    "error": {"code": -32603, "message": str(e)},
                }
                print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    server = AntigravityMCPServer()
    server.run()
