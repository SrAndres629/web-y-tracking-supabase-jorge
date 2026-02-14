"""
NEXUS-7 Orchestrator
═══════════════════════════════════════════════════════════════════════════════
Orquestador central - Único punto de entrada para ejecución de agentes.

Responsabilidades:
1. Recibir mensajes del MessageBus
2. Validar permisos contra AgentRegistry
3. Ejecutar agentes via AgentRunner
4. Actualizar estado via StateEngine

Diseño:
- Sin conocimiento del filesystem del proyecto (solo .ai/)
- Inyección de dependencias (Registry, StateEngine)
- Extensible via handlers de mensajes
- Thread-safe

Anti-patterns evitados:
- NO hardcodear comandos de agentes
- NO conocer estructura de venv/
- NO mezclar lógica de negocio con orquestación

Usage:
    from .ai.core import Orchestrator, Registry, StateEngine
    
    registry = Registry.load(".ai/core/registry.yaml")
    state = StateEngine()
    orchestrator = Orchestrator(registry, state)
    
    # Iniciar loop principal
    orchestrator.run()
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import json
import yaml
import signal
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread, Event, Lock
import queue

from .state_engine import StateEngine, TaskState, TaskStatus


# Configurar logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("nexus7.orchestrator")


class MessageType(Enum):
    """Tipos de mensajes soportados"""
    TASK = "task"
    SIGNAL = "signal"
    AUDIT = "audit"
    RESPONSE = "response"
    COMMAND = "command"
    EVENT = "event"


class AgentRegistry:
    """
    Registro de agentes basado en registry.yaml.
    Cachea configuración para acceso rápido.
    """
    
    def __init__(self, registry_path: str = ".ai/core/registry.yaml"):
        self.registry_path = Path(registry_path)
        self._config: Optional[dict] = None
        self._load_registry()
    
    def _load_registry(self):
        """Carga y valida el registro"""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {self.registry_path}")
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        
        logger.info(f"Registry loaded: v{self._config['system']['version']}")
    
    def reload(self):
        """Recarga el registro (hot-reload)"""
        self._load_registry()
        logger.info("Registry reloaded")
    
    def get_agent_config(self, agent_id: str) -> Optional[dict]:
        """Obtiene configuración de un agente"""
        return self._config.get("agents", {}).get(agent_id)
    
    def get_all_agents(self) -> Dict[str, dict]:
        """Obtiene todos los agentes"""
        return self._config.get("agents", {})
    
    def get_skill_config(self, skill_id: str) -> Optional[dict]:
        """Obtiene configuración de un skill"""
        return self._config.get("skills", {}).get(skill_id)
    
    def get_system_config(self) -> dict:
        """Obtiene configuración del sistema"""
        return self._config.get("system", {})
    
    def validate_agent_exists(self, agent_id: str) -> bool:
        """Valida que un agente exista en el registro"""
        return agent_id in self._config.get("agents", {})


@dataclass
class ExecutionResult:
    """Resultado de ejecución de un agente"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentRunner:
    """
    Ejecutor de agentes.
    Abstrae la ejecución de comandos específicos.
    """
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self._active_processes: Dict[str, subprocess.Popen] = {}
        self._lock = Lock()
    
    def execute(self, task: TaskState, working_dir: str = ".") -> ExecutionResult:
        """
        Ejecuta una tarea en el agente correspondiente.
        
        Args:
            task: Estado de la tarea a ejecutar
            working_dir: Directorio de trabajo
        
        Returns:
            ExecutionResult con resultado y métricas
        """
        agent_config = self.registry.get_agent_config(task.agent)
        if not agent_config:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Agent {task.agent} not found in registry",
                duration=0.0
            )
        
        # Construir comando
        cmd = [agent_config["execution"]["command"]]
        cmd.extend(agent_config["execution"].get("args", []))
        
        # Injectar protocolo Hive Mind
        protocol = self._build_protocol(task)
        cmd.append(protocol)
        
        # Configurar environment
        env = self._prepare_environment(agent_config)
        
        # Timeout
        timeout = agent_config["execution"].get("timeout", 1800)
        
        logger.info(f"Executing: {task.agent} | Task: {task.id} | Timeout: {timeout}s")
        
        start_time = time.time()
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            with self._lock:
                self._active_processes[task.id] = process
            
            # Esperar con timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                logger.warning(f"Task {task.id} timed out after {timeout}s")
            
            duration = time.time() - start_time
            
            with self._lock:
                self._active_processes.pop(task.id, None)
            
            # Parsear resultado
            success = process.returncode == 0
            
            return ExecutionResult(
                success=success,
                exit_code=process.returncode,
                stdout=stdout,
                stderr=stderr,
                duration=duration,
                metadata={
                    "command": " ".join(cmd[:3]) + "...",
                    "agent_version": agent_config.get("id")
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Execution failed: {e}")
            
            with self._lock:
                self._active_processes.pop(task.id, None)
            
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=duration
            )
    
    def _build_protocol(self, task: TaskState) -> str:
        """Construye el protocolo Hive Mind para el agente"""
        protocol_path = Path(".ai/core/hive_mind_protocol.md")
        
        base_protocol = ""
        if protocol_path.exists():
            base_protocol = protocol_path.read_text(encoding='utf-8')
        
        task_context = f"""

═══════════════════════════════════════════════════════════════════════════════
TASK CONTEXT
═══════════════════════════════════════════════════════════════════════════════
Task ID: {task.id}
Agent: {task.agent}
Created: {task.created_at}
Permissions:
  Read: {task.permissions.read}
  Write: {task.permissions.write}
  Deny: {task.permissions.deny}

CONTENT:
{task.content}

═══════════════════════════════════════════════════════════════════════════════
"""
        return base_protocol + task_context
    
    def _prepare_environment(self, agent_config: dict) -> dict:
        """Prepara variables de entorno para el agente"""
        env = os.environ.copy()
        
        # Encoding
        env["PYTHONIOENCODING"] = "utf-8"
        env["LANG"] = "en_US.UTF-8"
        
        # NEXUS-7 specific
        env["NEXUS7_AGENT"] = agent_config["id"]
        env["NEXUS7_VERSION"] = "1.0.0"
        
        return env
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancela una tarea en ejecución"""
        with self._lock:
            process = self._active_processes.get(task_id)
        
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            logger.info(f"Task {task_id} cancelled")
            return True
        
        return False


class MessageBus:
    """
    Bus de mensajes unificado.
    Reemplaza: archivos en motor/, signals/, sensory/
    """
    
    def __init__(self, inbox_dir: str = ".ai/messages/inbox", 
                 archive_dir: str = ".ai/messages/archive"):
        self.inbox_dir = Path(inbox_dir)
        self.archive_dir = Path(archive_dir)
        
        # Asegurar directorios
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def send(self, message: dict) -> str:
        """
        Envía un mensaje al bus.
        
        Args:
            message: Dict con el mensaje (validado contra schema)
        
        Returns:
            ID del mensaje
        """
        message_id = message.get("id") or self._generate_id()
        message["id"] = message_id
        
        # Validar versión
        if "version" not in message:
            message["version"] = "1.0.0"
        
        # Guardar en inbox
        msg_file = self.inbox_dir / f"{message_id}.json"
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(message, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Message sent: {message_id} | Type: {message.get('type')}")
        return message_id
    
    def receive(self, message_types: Optional[List[str]] = None,
                timeout: Optional[float] = None) -> Optional[dict]:
        """
        Recibe el siguiente mensaje disponible.
        
        Args:
            message_types: Filtrar por tipos específicos
            timeout: Timeout en segundos
        
        Returns:
            Mensaje o None si no hay mensajes
        """
        start = time.time()
        
        while True:
            messages = self._list_messages()
            
            for msg_file in messages:
                try:
                    with open(msg_file, 'r', encoding='utf-8') as f:
                        message = json.load(f)
                    
                    # Filtrar por tipo
                    if message_types and message.get("type") not in message_types:
                        continue
                    
                    # Mover a archive
                    archived = self.archive_dir / msg_file.name
                    msg_file.rename(archived)
                    
                    logger.debug(f"Message received: {message.get('id')}")
                    return message
                    
                except Exception as e:
                    logger.error(f"Error reading message {msg_file}: {e}")
                    continue
            
            # Check timeout
            if timeout and (time.time() - start) > timeout:
                return None
            
            time.sleep(0.1)
    
    def peek(self) -> Optional[dict]:
        """Vea el siguiente mensaje sin removerlo"""
        messages = self._list_messages()
        if messages:
            try:
                with open(messages[0], 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def _list_messages(self) -> List[Path]:
        """Lista mensajes ordenados por timestamp"""
        messages = list(self.inbox_dir.glob("msg_*.json"))
        messages.sort(key=lambda p: p.stat().st_mtime)
        return messages
    
    def _generate_id(self) -> str:
        """Genera ID único para mensaje"""
        import hashlib
        timestamp = int(time.time())
        random = hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]
        return f"msg_{timestamp}_{random}"


class Orchestrator:
    """
    Orquestador central de NEXUS-7.
    
    Coordina:
    - Recepción de mensajes (MessageBus)
    - Gestión de estado (StateEngine)
    - Ejecución de agentes (AgentRunner)
    - Validación de permisos (AgentRegistry)
    """
    
    def __init__(self, 
                 registry: Optional[AgentRegistry] = None,
                 state: Optional[StateEngine] = None,
                 bus: Optional[MessageBus] = None):
        
        self.registry = registry or AgentRegistry()
        self.state = state or StateEngine()
        self.bus = bus or MessageBus()
        self.runner = AgentRunner(self.registry)
        
        # Control
        self._running = Event()
        self._shutdown_requested = False
        
        # Handlers de mensajes
        self._handlers: Dict[str, Callable] = {
            MessageType.TASK.value: self._handle_task,
            MessageType.SIGNAL.value: self._handle_signal,
            MessageType.AUDIT.value: self._handle_audit,
            MessageType.COMMAND.value: self._handle_command,
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de sistema"""
        logger.info(f"Signal {signum} received, shutting down...")
        self._shutdown_requested = True
        self._running.set()
    
    def run(self):
        """Loop principal del orquestador"""
        logger.info("═══════════════════════════════════════════════════════")
        logger.info("  NEXUS-7 Orchestrator v1.0.0")
        logger.info("═══════════════════════════════════════════════════════")
        logger.info("System ready. Waiting for messages...")
        
        self._running.set()
        
        while not self._shutdown_requested:
            try:
                # Intentar recibir mensaje (non-blocking)
                message = self.bus.receive(timeout=1.0)
                
                if message:
                    self._process_message(message)
                else:
                    # No messages - check for pending tasks
                    self._process_pending_tasks()
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(1)
        
        logger.info("Orchestrator shutdown complete")
    
    def _process_message(self, message: dict):
        """Procesa un mensaje según su tipo"""
        msg_type = message.get("type")
        handler = self._handlers.get(msg_type)
        
        if handler:
            logger.info(f"Processing {msg_type} message from {message.get('from')}")
            handler(message)
        else:
            logger.warning(f"No handler for message type: {msg_type}")
    
    def _handle_task(self, message: dict):
        """Crea y ejecuta una tarea"""
        payload = message.get("payload", {})
        
        agent = message.get("to")
        if not self.registry.validate_agent_exists(agent):
            logger.error(f"Invalid agent: {agent}")
            return
        
        # Crear tarea en estado engine
        task = self.state.create_task(
            agent=agent,
            content=payload.get("content", ""),
            permissions=payload.get("permissions", {}),
            max_retries=payload.get("max_retries", 3),
            metadata={
                "triggered_by": message.get("id"),
                "skill_id": payload.get("skill_id")
            }
        )
        
        logger.info(f"Task created: {task.id} for agent {agent}")
        
        # Ejecutar inmediatamente (o encolar para ejecución paralela)
        self._execute_task(task)
    
    def _execute_task(self, task: TaskState):
        """Ejecuta una tarea específica"""
        # Transicionar a running
        self.state.transition_task(task.id, TaskStatus.RUNNING.value)
        
        # Ejecutar
        result = self.runner.execute(task)
        
        # Determinar siguiente estado
        if result.success:
            new_status = TaskStatus.COMPLETED.value
        else:
            new_status = TaskStatus.FAILED.value
        
        # Transicionar
        self.state.transition_task(
            task.id,
            new_status,
            metadata={
                "duration": result.duration,
                "exit_code": result.exit_code,
                "stdout_preview": result.stdout[:500] if result.stdout else ""
            }
        )
        
        logger.info(f"Task {task.id} {new_status} in {result.duration:.2f}s")
        
        # Enviar respuesta si es necesario
        self._send_response(message_id=None, task_id=task.id, result=result)
    
    def _handle_signal(self, message: dict):
        """Procesa señales de control"""
        signal_type = message.get("payload", {}).get("signal_type")
        
        if signal_type == "WAKE_UP":
            logger.info("WAKE_UP signal received - checking pending tasks")
            self._process_pending_tasks()
        
        elif signal_type == "HALT":
            logger.info("HALT signal received - initiating shutdown")
            self._shutdown_requested = True
        
        elif signal_type == "RETRY":
            task_id = message.get("payload", {}).get("data", {}).get("task_id")
            if task_id:
                self._retry_task(task_id)
    
    def _handle_audit(self, message: dict):
        """Inicia una auditoría"""
        logger.info("Audit request received - delegating to auditor skill")
        # TODO: Implementar integración con auditor
        pass
    
    def _handle_command(self, message: dict):
        """Procesa comandos directos"""
        command = message.get("payload", {}).get("command")
        
        if command == "reload_registry":
            self.registry.reload()
        
        elif command == "status":
            metrics = self.state.get_metrics()
            logger.info(f"System status: {metrics.to_dict()}")
    
    def _process_pending_tasks(self):
        """Procesa tareas pendientes"""
        pending = self.state.get_pending_tasks()
        
        for task in pending[:5]:  # Procesar máximo 5 a la vez
            self._execute_task(task)
    
    def _retry_task(self, task_id: str):
        """Reintenta una tarea fallida"""
        task = self.state.get_task(task_id)
        if task and task.can_retry():
            self.state.transition_task(task_id, TaskStatus.PENDING.value)
            logger.info(f"Task {task_id} queued for retry")
    
    def _send_response(self, message_id: Optional[str], task_id: str, 
                       result: ExecutionResult):
        """Envía respuesta de ejecución"""
        response = {
            "type": MessageType.RESPONSE.value,
            "from": "orchestrator",
            "to": "user",  # o el emisor original
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "payload": {
                "request_id": message_id,
                "task_id": task_id,
                "status": "success" if result.success else "error",
                "result": {
                    "exit_code": result.exit_code,
                    "duration": result.duration
                }
            },
            "trace": {
                "correlation_id": task_id
            }
        }
        
        self.bus.send(response)
    
    def create_task(self, agent: str, content: str, 
                    permissions: Optional[dict] = None) -> str:
        """
        API pública para crear tareas programáticamente.
        
        Returns:
            ID de la tarea creada
        """
        message = {
            "type": MessageType.TASK.value,
            "from": "user",
            "to": agent,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "payload": {
                "content": content,
                "permissions": permissions or {"read": ["**/*"], "write": []}
            }
        }
        
        return self.bus.send(message)
    
    def get_status(self) -> dict:
        """Obtiene estado del sistema"""
        metrics = self.state.get_metrics()
        pending = len(self.state.get_pending_tasks())
        
        return {
            "version": "1.0.0",
            "status": "running" if self._running.is_set() else "stopped",
            "metrics": metrics.to_dict(),
            "pending_tasks": pending,
            "agents": list(self.registry.get_all_agents().keys())
        }


def main():
    """Entry point para ejecutar el orchestrator standalone"""
    orchestrator = Orchestrator()
    
    try:
        orchestrator.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")


if __name__ == "__main__":
    main()
