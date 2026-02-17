#!/usr/bin/env python3
"""
Antigravity Toolkit Server
Servidor local para el dashboard visual de administración de Antigravity
"""

import json
import socketserver
import sys
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from client import AntigravityClient, QuotaInfo

    ANTIGRAVITY_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_AVAILABLE = False
    print("⚠️  Cliente Antigravity no disponible, usando modo demo")


class AntigravityToolkitAPI:
    """API para integración nativa con Antigravity"""

    def __init__(self):
        self.client = None
        self.memory_store = {}
        self.contexts = []
        self.usage_history = []
        self.autocap_enabled = True
        self.autocap_config = {
            "mode": "balanced",
            "quota_limit": 80,
            "memory_limit": 90,
            "auto_clear_memory": True,
            "auto_switch_model": True,
            "auto_notify": True,
        }

        if ANTIGRAVITY_AVAILABLE:
            try:
                self.client = AntigravityClient()
                print("✅ Cliente Antigravity inicializado")
            except Exception as e:
                print(f"⚠️  Error inicializando cliente: {e}")

    def get_quota(self) -> dict:
        """Obtiene información de quota desde Antigravity"""
        if self.client:
            try:
                quota = self.client.get_quota()
                reset_time = self._parse_reset_date(quota.reset_date)

                data = {
                    "total": quota.total,
                    "used": quota.used,
                    "remaining": quota.remaining,
                    "percentage": quota.percentage_used,
                    "reset_date": quota.reset_date,
                    "reset_time": reset_time,
                    "source": "antigravity_api",
                }

                # Guardar en historial
                self._add_to_history(quota.percentage_used)

                return data
            except Exception as e:
                print(f"Error obteniendo quota: {e}")

        # Datos de demo
        return self._get_demo_quota()

    def get_memory(self) -> dict:
        """Obtiene información de memoria"""
        total_size = sum(ctx.get("size", 0) for ctx in self.contexts)
        total_tokens = sum(ctx.get("tokens", 0) for ctx in self.contexts)

        # Simular límite de 100MB
        max_memory = 100
        percentage = (total_size / max_memory) * 100 if max_memory > 0 else 0

        return {
            "used": round(total_size, 2),
            "total": max_memory,
            "percentage": round(percentage, 2),
            "contexts": len(self.contexts),
            "tokens": total_tokens,
        }

    def get_contexts(self) -> list:
        """Lista todos los contextos de memoria"""
        if not self.contexts:
            # Contextos de demo
            self.contexts = [
                {
                    "id": "ctx_001",
                    "name": "Proyecto Alpha",
                    "size": 12.5,
                    "tokens": 15000,
                    "status": "active",
                    "updated": "2 min ago",
                    "created": datetime.now().isoformat(),
                },
                {
                    "id": "ctx_002",
                    "name": "Análisis de Código",
                    "size": 8.3,
                    "tokens": 9800,
                    "status": "active",
                    "updated": "15 min ago",
                    "created": datetime.now().isoformat(),
                },
                {
                    "id": "ctx_003",
                    "name": "Conversación General",
                    "size": 15.2,
                    "tokens": 18200,
                    "status": "active",
                    "updated": "1 hour ago",
                    "created": datetime.now().isoformat(),
                },
            ]

        return self.contexts

    def clear_memory(self) -> dict:
        """Limpia toda la memoria/contextos"""
        cleared_count = len(self.contexts)
        self.contexts = []
        self.memory_store = {}

        return {
            "success": True,
            "cleared_contexts": cleared_count,
            "message": f"{cleared_count} contextos eliminados",
        }

    def archive_context(self, context_id: str) -> dict:
        """Archiva un contexto específico"""
        for ctx in self.contexts:
            if ctx["id"] == context_id:
                ctx["status"] = "archived"
                ctx["updated"] = "just now"
                return {"success": True, "message": "Contexto archivado"}

        return {"success": False, "error": "Contexto no encontrado"}

    def delete_context(self, context_id: str) -> dict:
        """Elimina un contexto específico"""
        self.contexts = [ctx for ctx in self.contexts if ctx["id"] != context_id]
        return {"success": True, "message": "Contexto eliminado"}

    def check_autocap(self, quota_data: dict, memory_data: dict) -> dict:
        """Verifica si se deben activar límites de autocapeo"""
        if not self.autocap_enabled:
            return {"active": False}

        quota_exceeded = quota_data.get("percentage", 0) >= self.autocap_config["quota_limit"]
        memory_exceeded = memory_data.get("percentage", 0) >= self.autocap_config["memory_limit"]

        triggered = quota_exceeded or memory_exceeded
        actions = []

        if triggered:
            if memory_exceeded and self.autocap_config["auto_clear_memory"]:
                self.clear_memory()
                actions.append("memory_cleared")

            if quota_exceeded and self.autocap_config["auto_switch_model"]:
                actions.append("model_switched")

            if self.autocap_config["auto_notify"]:
                actions.append("notification_sent")

        return {
            "active": triggered,
            "quota_exceeded": quota_exceeded,
            "memory_exceeded": memory_exceeded,
            "actions": actions,
            "config": self.autocap_config,
        }

    def update_autocap_config(self, config: dict) -> dict:
        """Actualiza configuración de autocapeo"""
        self.autocap_config.update(config)
        self.autocap_enabled = config.get("enabled", True)

        return {"success": True, "config": self.autocap_config}

    def _parse_reset_date(self, date_str: str) -> int:
        """Parsea fecha de reset a timestamp"""
        try:
            # Intentar parsear fecha
            if date_str != "N/A":
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return int(dt.timestamp() * 1000)
        except:
            pass

        # Default: +3 días
        return int((datetime.now() + timedelta(days=3)).timestamp() * 1000)

    def _get_demo_quota(self) -> dict:
        """Genera datos de quota de demo"""
        total = 1000000
        used = 650000

        return {
            "total": total,
            "used": used,
            "remaining": total - used,
            "percentage": (used / total) * 100,
            "reset_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "reset_time": int((datetime.now() + timedelta(days=3)).timestamp() * 1000),
            "source": "demo",
        }

    def _add_to_history(self, percentage: float):
        """Añade punto al historial de uso"""
        self.usage_history.append(
            {"timestamp": datetime.now().isoformat(), "percentage": percentage}
        )

        # Mantener solo últimos 30 días
        if len(self.usage_history) > 30:
            self.usage_history = self.usage_history[-30:]


class ToolkitHandler(BaseHTTPRequestHandler):
    """HTTP Handler para el Toolkit"""

    api = AntigravityToolkitAPI()
    static_dir = Path(__file__).parent / "static"
    templates_dir = Path(__file__).parent / "templates"

    def log_message(self, format, *args):
        """Override para logging silencioso"""
        pass

    def do_GET(self):
        """Maneja peticiones GET"""
        parsed = urlparse(self.path)
        path = parsed.path

        # API routes
        if path.startswith("/api/"):
            self.handle_api_get(path)
            return

        # Static files
        if path.startswith("/static/"):
            self.serve_static(path[8:])  # Remove /static/
            return

        # Default: serve index
        self.serve_template("index.html")

    def do_POST(self):
        """Maneja peticiones POST"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            self.handle_api_post(path)
            return

        self.send_error(404)

    def do_DELETE(self):
        """Maneja peticiones DELETE"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            self.handle_api_delete(path)
            return

        self.send_error(404)

    def handle_api_get(self, path: str):
        """Maneja endpoints GET de la API"""
        endpoint = path.replace("/api/", "")

        if endpoint == "quota":
            data = self.api.get_quota()
            # Verificar autocapeo
            memory = self.api.get_memory()
            autocap = self.api.check_autocap(data, memory)
            data["autocap"] = autocap
            self.send_json(data)

        elif endpoint == "memory":
            data = self.api.get_memory()
            self.send_json(data)

        elif endpoint == "contexts":
            data = self.api.get_contexts()
            self.send_json(data)

        elif endpoint == "status":
            quota = self.api.get_quota()
            memory = self.api.get_memory()
            autocap = self.api.check_autocap(quota, memory)

            self.send_json(
                {
                    "quota": quota,
                    "memory": memory,
                    "autocap": autocap,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        else:
            self.send_error(404)

    def handle_api_post(self, path: str):
        """Maneja endpoints POST de la API"""
        endpoint = path.replace("/api/", "")

        if endpoint == "memory/clear":
            data = self.api.clear_memory()
            self.send_json(data)

        elif endpoint.startswith("contexts/"):
            parts = endpoint.split("/")
            if len(parts) >= 3 and parts[2] == "archive":
                context_id = parts[1]
                data = self.api.archive_context(context_id)
                self.send_json(data)

        elif endpoint == "autocap/config":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            config = json.loads(body) if body else {}
            data = self.api.update_autocap_config(config)
            self.send_json(data)

        else:
            self.send_error(404)

    def handle_api_delete(self, path: str):
        """Maneja endpoints DELETE de la API"""
        endpoint = path.replace("/api/", "")

        if endpoint.startswith("contexts/"):
            parts = endpoint.split("/")
            context_id = parts[1]
            data = self.api.delete_context(context_id)
            self.send_json(data)

        else:
            self.send_error(404)

    def serve_static(self, filepath: str):
        """Sirve archivos estáticos"""
        file_path = self.static_dir / filepath

        if not file_path.exists():
            self.send_error(404)
            return

        content_types = {
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".svg": "image/svg+xml",
        }

        ext = file_path.suffix
        content_type = content_types.get(ext, "application/octet-stream")

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "max-age=3600")
        self.end_headers()

        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def serve_template(self, filename: str):
        """Sirve templates HTML"""
        file_path = self.templates_dir / filename

        if not file_path.exists():
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        with open(file_path, "r", encoding="utf-8") as f:
            self.wfile.write(f.read().encode("utf-8"))

    def send_json(self, data: dict):
        """Envía respuesta JSON"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(json.dumps(data).encode("utf-8"))


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Servidor HTTP con threading"""

    allow_reuse_address = True
    daemon_threads = True


def run_server(port: int = 8765):
    """Inicia el servidor del Toolkit"""
    server = ThreadedHTTPServer(("localhost", port), ToolkitHandler)

    print(f"""
🛡️  Antigravity Toolkit Server
═══════════════════════════════════════
📊 Dashboard: http://localhost:{port}
🔌 API: http://localhost:{port}/api/
⚡ Endpoints:
   • GET  /api/quota     - Quota info
   • GET  /api/memory    - Memory info
   • GET  /api/contexts  - List contexts
   • POST /api/memory/clear - Clear memory
""")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
        server.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Antigravity Toolkit Server")
    parser.add_argument("-p", "--port", type=int, default=8765, help="Puerto (default: 8765)")
    parser.add_argument("--no-browser", action="store_true", help="No abrir navegador")

    args = parser.parse_args()

    if not args.no_browser:
        import webbrowser

        threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{args.port}")).start()

    run_server(args.port)
