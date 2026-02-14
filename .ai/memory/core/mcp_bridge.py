"""
NEXUS-7: MCP Bridge
═══════════════════════════════════════════════════════════════════════════════
Puente de integración con Model Context Protocol (MCP).

Conecta la colmena neural con:
- Vision Neuronal (tu MCP principal)
- MCPs externos (filesystem, web, database, etc.)
- Tools y recursos de MCP

Funciones:
1. Auto-discovery de MCPs disponibles
2. Routing de requests a MCPs apropiados
3. Caching de respuestas MCP
4. Fallback entre MCPs
5. Rate limiting y manejo de errores

Los 4 cerebros acceden a MCPs a través de este puente unificado.
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import subprocess
import threading


class MCPStatus(Enum):
    """Estado de un MCP"""
    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class MCPConnection:
    """Conexión a un MCP"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    status: str = "offline"
    capabilities: List[str] = field(default_factory=list)
    last_used: float = 0
    error_count: int = 0
    process: Optional[subprocess.Popen] = None
    
    def is_available(self) -> bool:
        return self.status == MCPStatus.AVAILABLE.value


@dataclass
class MCPRequest:
    """Request a un MCP"""
    id: str
    tool: str
    params: Dict[str, Any]
    brain_origin: str
    timestamp: float
    timeout: float = 30.0
    priority: int = 5


@dataclass
class MCPResponse:
    """Respuesta de un MCP"""
    request_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    duration: float = 0.0
    mcp_used: Optional[str] = None


class MCPBridge:
    """
    Puente de integración con MCPs.
    
    Analogía: Es como el sistema nervioso periférico que conecta
    el cerebro central (la colmena) con los órganos sensoriales
    y efectores (MCPs externos).
    
    Features:
    - Descubrimiento automático de MCPs
    - Balanceo de carga entre MCPs similares
    - Caching de respuestas
    - Circuit breaker para MCPs fallidos
    """
    
    def __init__(self, config_path: str = ".ai/memory/core/mcp/mcp_config.json"):
        self.config_path = Path(config_path)
        self.mcps: Dict[str, MCPConnection] = {}
        self.request_cache: Dict[str, MCPResponse] = {}
        self.cache_ttl = 300  # 5 minutos
        
        # Circuit breaker
        self.failure_counts: Dict[str, int] = {}
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60
        self.circuit_breaker_timers: Dict[str, float] = {}
        
        # Stats
        self.stats = {
            "requests": 0,
            "cache_hits": 0,
            "errors": 0
        }
        
        self._load_config()
    
    def _load_config(self):
        """Carga configuración de MCPs"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for name, mcp_config in config.get("mcps", {}).items():
                self.mcps[name] = MCPConnection(
                    name=name,
                    command=mcp_config["command"],
                    args=mcp_config.get("args", []),
                    env=mcp_config.get("env", {}),
                    capabilities=mcp_config.get("capabilities", [])
                )
        else:
            # Config por defecto con Vision Neuronal
            self.mcps["vision_neuronal"] = MCPConnection(
                name="vision_neuronal",
                command="python",
                args=["-m", "mcp_vision_neuronal"],
                env={},
                capabilities=["vision", "analysis", "pattern_recognition"]
            )
            self._save_config()
    
    def _save_config(self):
        """Guarda configuración de MCPs"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {
            "mcps": {
                name: {
                    "command": mcp.command,
                    "args": mcp.args,
                    "env": mcp.env,
                    "capabilities": mcp.capabilities
                }
                for name, mcp in self.mcps.items()
            }
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def register_mcp(self, name: str, command: str, args: List[str] = None,
                     capabilities: List[str] = None):
        """Registra un nuevo MCP"""
        self.mcps[name] = MCPConnection(
            name=name,
            command=command,
            args=args or [],
            env={},
            capabilities=capabilities or []
        )
        self._save_config()
    
    async def call_tool(self, tool: str, params: Dict[str, Any],
                        brain_origin: str = "system",
                        timeout: float = 30.0,
                        use_cache: bool = True) -> MCPResponse:
        """
        Llama a una tool de MCP.
        
        Args:
            tool: Nombre de la tool
            params: Parámetros de la tool
            brain_origin: Cerebro que origina la llamada
            timeout: Timeout en segundos
            use_cache: Usar cache si está disponible
        
        Returns:
            MCPResponse con resultado o error
        """
        request_id = f"mcp_{int(time.time())}_{hash(str(params)) % 10000}"
        
        # Verificar cache
        if use_cache:
            cache_key = f"{tool}:{json.dumps(params, sort_keys=True)}"
            cached = self.request_cache.get(cache_key)
            if cached and time.time() - cached.duration < self.cache_ttl:
                self.stats["cache_hits"] += 1
                return MCPResponse(
                    request_id=request_id,
                    success=True,
                    result=cached.result,
                    mcp_used="cache"
                )
        
        # Seleccionar MCP apropiado
        mcp_name = self._select_mcp_for_tool(tool)
        if not mcp_name:
            return MCPResponse(
                request_id=request_id,
                success=False,
                error=f"No MCP available for tool: {tool}",
                mcp_used=None
            )
        
        # Verificar circuit breaker
        if self._is_circuit_open(mcp_name):
            return MCPResponse(
                request_id=request_id,
                success=False,
                error=f"Circuit breaker open for {mcp_name}",
                mcp_used=mcp_name
            )
        
        # Ejecutar llamada
        start = time.time()
        try:
            result = await self._execute_mcp_call(mcp_name, tool, params, timeout)
            duration = time.time() - start
            
            # Guardar en cache
            if use_cache:
                self.request_cache[cache_key] = MCPResponse(
                    request_id=request_id,
                    success=True,
                    result=result,
                    duration=duration,
                    mcp_used=mcp_name
                )
            
            self.stats["requests"] += 1
            
            return MCPResponse(
                request_id=request_id,
                success=True,
                result=result,
                duration=duration,
                mcp_used=mcp_name
            )
            
        except Exception as e:
            self.stats["errors"] += 1
            self._record_failure(mcp_name)
            
            return MCPResponse(
                request_id=request_id,
                success=False,
                error=str(e),
                mcp_used=mcp_name
            )
    
    def _select_mcp_for_tool(self, tool: str) -> Optional[str]:
        """Selecciona el mejor MCP para una tool"""
        available_mcps = []
        
        for name, mcp in self.mcps.items():
            if not self._is_circuit_open(name) and mcp.is_available():
                # Verificar si el MCP soporta esta tool
                if tool in mcp.capabilities or "*" in mcp.capabilities:
                    available_mcps.append((name, mcp.last_used))
        
        if not available_mcps:
            return None
        
        # Seleccionar el menos recientemente usado (balanceo simple)
        available_mcps.sort(key=lambda x: x[1])
        return available_mcps[0][0]
    
    async def _execute_mcp_call(self, mcp_name: str, tool: str, 
                                params: Dict, timeout: float) -> Any:
        """Ejecuta la llamada a MCP"""
        mcp = self.mcps[mcp_name]
        
        # Construir comando
        cmd = [mcp.command] + mcp.args + [tool, json.dumps(params)]
        
        # Ejecutar
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**mcp.env, "PATH": mcp.env.get("PATH", "")}
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
            
            if proc.returncode != 0:
                raise Exception(f"MCP error: {stderr.decode()}")
            
            result = json.loads(stdout.decode())
            mcp.last_used = time.time()
            return result
            
        except asyncio.TimeoutError:
            proc.kill()
            raise Exception(f"MCP timeout after {timeout}s")
    
    def _is_circuit_open(self, mcp_name: str) -> bool:
        """Verifica si el circuit breaker está abierto"""
        if mcp_name not in self.failure_counts:
            return False
        
        if self.failure_counts[mcp_name] >= self.circuit_breaker_threshold:
            # Verificar si ya pasó el timeout
            last_failure = self.circuit_breaker_timers.get(mcp_name, 0)
            if time.time() - last_failure < self.circuit_breaker_timeout:
                return True
            else:
                # Reset circuit breaker
                self.failure_counts[mcp_name] = 0
        
        return False
    
    def _record_failure(self, mcp_name: str):
        """Registra una falla de MCP"""
        self.failure_counts[mcp_name] = self.failure_counts.get(mcp_name, 0) + 1
        self.circuit_breaker_timers[mcp_name] = time.time()
    
    def get_mcp_status(self) -> Dict[str, dict]:
        """Obtiene estado de todos los MCPs"""
        return {
            name: {
                "status": mcp.status,
                "capabilities": mcp.capabilities,
                "last_used": mcp.last_used,
                "failures": self.failure_counts.get(name, 0),
                "circuit_open": self._is_circuit_open(name)
            }
            for name, mcp in self.mcps.items()
        }
    
    def vision_analyze(self, image_path: str, query: str = "") -> MCPResponse:
        """
        Wrapper específico para Vision Neuronal.
        Facilita el uso del MCP de visión.
        """
        return asyncio.run(self.call_tool(
            tool="analyze_image",
            params={
                "image_path": image_path,
                "query": query
            },
            brain_origin="collective"
        ))
    
    def vision_detect_patterns(self, data: Any) -> MCPResponse:
        """
        Detecta patrones usando Vision Neuronal.
        """
        return asyncio.run(self.call_tool(
            tool="detect_patterns",
            params={"data": data},
            brain_origin="collective"
        ))
    
    def clear_cache(self):
        """Limpia el cache de requests"""
        self.request_cache.clear()
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del bridge"""
        return {
            **self.stats,
            "mcps_registered": len(self.mcps),
            "cache_size": len(self.request_cache)
        }


# Instancia global del bridge
_mcp_bridge = None

def get_mcp_bridge() -> MCPBridge:
    """Obtiene instancia singleton del MCP Bridge"""
    global _mcp_bridge
    if _mcp_bridge is None:
        _mcp_bridge = MCPBridge()
    return _mcp_bridge
