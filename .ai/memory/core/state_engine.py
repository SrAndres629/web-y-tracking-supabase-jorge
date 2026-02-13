"""
NEXUS-7 State Engine
═══════════════════════════════════════════════════════════════════════════════
Motor de estado centralizado - Única fuente de verdad para el estado del sistema.

Responsabilidades:
1. Persistencia atómica del estado
2. Transiciones de estado validadas
3. Historial completo de ejecución
4. Recuperación ante fallos

Principios:
- Atomicidad: Todas las operaciones son transacciones
- Inmutabilidad: El estado anterior se preserva
- Trazabilidad: Cada cambio tiene audit trail

Usage:
    state = StateEngine(".ai/core/state.json")
    
    # Crear tarea
    task = state.create_task(
        agent="codex",
        content="Fix bug in tracking.py",
        permissions={"read": ["app/"], "write": ["app/tracking.py"]}
    )
    
    # Transicionar
    state.transition_task(task.id, "running")
    # ... ejecución ...
    state.transition_task(task.id, "completed", metadata={"duration": 120})
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import hashlib
import time
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Literal
from pathlib import Path
from enum import Enum
import threading
import shutil


class TaskStatus(Enum):
    """Estados válidos de una tarea"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskPermissions:
    """Permisos específicos de una tarea"""
    read: List[str] = field(default_factory=list)
    write: List[str] = field(default_factory=list)
    deny: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "read": self.read,
            "write": self.write,
            "deny": self.deny
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TaskPermissions":
        return cls(
            read=data.get("read", []),
            write=data.get("write", []),
            deny=data.get("deny", [])
        )


@dataclass
class TaskState:
    """
    Representación completa del estado de una tarea.
    Inmutable después de la creación (excepto transiciones de estado).
    """
    id: str
    agent: str
    status: str
    content: str
    permissions: TaskPermissions
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    content_hash: str = ""
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Computa hash del contenido para verificar integridad"""
        content = f"{self.agent}:{self.content}:{self.created_at}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent": self.agent,
            "status": self.status,
            "content": self.content,
            "permissions": self.permissions.to_dict(),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "content_hash": self.content_hash,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TaskState":
        return cls(
            id=data["id"],
            agent=data["agent"],
            status=data["status"],
            content=data["content"],
            permissions=TaskPermissions.from_dict(data["permissions"]),
            created_at=data["created_at"],
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            content_hash=data.get("content_hash", ""),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            metadata=data.get("metadata", {}),
            history=data.get("history", [])
        )
    
    def can_retry(self) -> bool:
        """Determina si la tarea puede reintentarse"""
        return self.retry_count < self.max_retries and self.status == TaskStatus.FAILED.value


@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    average_task_duration: float = 0.0
    last_audit: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "SystemMetrics":
        return cls(**data)


@dataclass
class SystemState:
    """
    Estado completo del sistema NEXUS-7.
    """
    version: str = "1.0.0"
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    active_tasks: List[TaskState] = field(default_factory=list)
    task_history: List[TaskState] = field(default_factory=list)
    metrics: SystemMetrics = field(default_factory=SystemMetrics)
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "last_updated": self.last_updated,
            "active_tasks": [t.to_dict() for t in self.active_tasks],
            "task_history": [t.to_dict() for t in self.task_history[-100:]],  # Solo últimos 100
            "metrics": self.metrics.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SystemState":
        return cls(
            version=data.get("version", "1.0.0"),
            last_updated=data.get("last_updated", datetime.utcnow().isoformat()),
            active_tasks=[TaskState.from_dict(t) for t in data.get("active_tasks", [])],
            task_history=[TaskState.from_dict(t) for t in data.get("task_history", [])],
            metrics=SystemMetrics.from_dict(data.get("metrics", {}))
        )


class StateEngine:
    """
    Motor de estado centralizado para NEXUS-7.
    
    Garantiza:
    - Atomicidad: Todas las operaciones son transacciones
    - Durabilidad: Persistencia inmediata a disco
    - Consistencia: Validación de transiciones de estado
    - Aislamiento: Thread-safe con locks
    """
    
    def __init__(self, state_file: str = ".ai/core/state.json"):
        self.state_file = Path(state_file)
        self.backup_dir = self.state_file.parent / "backups"
        self._lock = threading.RLock()
        self._state: Optional[SystemState] = None
        
        # Asegurar directorios existen
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Cargar estado inicial
        self._load_state()
    
    def _load_state(self) -> SystemState:
        """Carga el estado desde disco o crea uno nuevo"""
        if self._state is not None:
            return self._state
        
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._state = SystemState.from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                # Corrupted state - try backup
                self._state = self._restore_from_backup() or SystemState()
        else:
            self._state = SystemState()
        
        return self._state
    
    def _save_state(self) -> None:
        """Persiste el estado actual a disco (atómico)"""
        # Create backup first
        if self.state_file.exists():
            backup_file = self.backup_dir / f"state_{int(time.time())}.json"
            shutil.copy2(self.state_file, backup_file)
            
            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob("state_*.json"))
            for old_backup in backups[:-10]:
                old_backup.unlink()
        
        # Atomic write
        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self._state.to_dict(), f, indent=2, ensure_ascii=False)
        
        temp_file.replace(self.state_file)
    
    def _restore_from_backup(self) -> Optional[SystemState]:
        """Intenta restaurar desde el backup más reciente"""
        backups = sorted(self.backup_dir.glob("state_*.json"), reverse=True)
        for backup in backups[:3]:  # Try last 3 backups
            try:
                with open(backup, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return SystemState.from_dict(data)
            except:
                continue
        return None
    
    def _generate_task_id(self) -> str:
        """Genera ID único para tarea"""
        timestamp = int(time.time())
        random_part = hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]
        return f"task_{timestamp}_{random_part}"
    
    def get_state(self) -> SystemState:
        """Obtiene el estado actual del sistema"""
        with self._lock:
            return self._load_state()
    
    def create_task(
        self,
        agent: str,
        content: str,
        permissions: Dict[str, List[str]],
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskState:
        """
        Crea una nueva tarea con validación de esquema.
        
        Args:
            agent: ID del agente asignado
            content: Contenido/descripción de la tarea
            permissions: Dict con 'read', 'write', 'deny'
            max_retries: Máximo de reintentos permitidos
            metadata: Metadatos adicionales
        
        Returns:
            TaskState: Estado inicial de la tarea
        """
        with self._lock:
            state = self._load_state()
            
            task = TaskState(
                id=self._generate_task_id(),
                agent=agent,
                status=TaskStatus.PENDING.value,
                content=content,
                permissions=TaskPermissions(
                    read=permissions.get("read", []),
                    write=permissions.get("write", []),
                    deny=permissions.get("deny", [])
                ),
                created_at=datetime.utcnow().isoformat(),
                max_retries=max_retries,
                metadata=metadata or {}
            )
            
            state.active_tasks.append(task)
            state.metrics.total_tasks += 1
            state.last_updated = datetime.utcnow().isoformat()
            
            self._save_state()
            return task
    
    def transition_task(
        self,
        task_id: str,
        new_status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskState:
        """
        Transiciona una tarea a un nuevo estado.
        
        Validaciones:
        - pending → running | cancelled
        - running → completed | failed | cancelled
        - failed → pending (retry) | cancelled
        
        Args:
            task_id: ID de la tarea
            new_status: Nuevo estado
            metadata: Metadatos adicionales para la transición
        
        Returns:
            TaskState: Estado actualizado
        
        Raises:
            ValueError: Si la transición no es válida
        """
        with self._lock:
            state = self._load_state()
            
            # Find task
            task = None
            for t in state.active_tasks:
                if t.id == task_id:
                    task = t
                    break
            
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            # Validate transition
            valid_transitions = {
                TaskStatus.PENDING.value: [TaskStatus.RUNNING.value, TaskStatus.CANCELLED.value],
                TaskStatus.RUNNING.value: [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value],
                TaskStatus.FAILED.value: [TaskStatus.PENDING.value, TaskStatus.CANCELLED.value],  # retry
                TaskStatus.COMPLETED.value: [],
                TaskStatus.CANCELLED.value: []
            }
            
            if new_status not in valid_transitions.get(task.status, []):
                raise ValueError(
                    f"Invalid transition: {task.status} → {new_status}"
                )
            
            # Record history
            transition_record = {
                "from": task.status,
                "to": new_status,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            task.history.append(transition_record)
            
            # Update state
            old_status = task.status
            task.status = new_status
            
            if new_status == TaskStatus.RUNNING.value and not task.started_at:
                task.started_at = datetime.utcnow().isoformat()
            
            if new_status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                task.completed_at = datetime.utcnow().isoformat()
                
                # Move to history
                state.active_tasks = [t for t in state.active_tasks if t.id != task_id]
                state.task_history.append(task)
                
                # Update metrics
                if new_status == TaskStatus.COMPLETED.value:
                    state.metrics.completed_tasks += 1
                    
                    # Calculate duration
                    if task.started_at:
                        start = datetime.fromisoformat(task.started_at)
                        end = datetime.fromisoformat(task.completed_at)
                        duration = (end - start).total_seconds()
                        
                        # Running average
                    total = state.metrics.completed_tasks
                    old_avg = state.metrics.average_task_duration
                    state.metrics.average_task_duration = (
                        (old_avg * (total - 1) + duration) / total
                    )
                    
                elif new_status == TaskStatus.FAILED.value:
                    state.metrics.failed_tasks += 1
                    task.retry_count += 1
                    
                    # Auto-retry logic
                    if task.can_retry():
                        # Create new pending task with retry
                        task.status = TaskStatus.PENDING.value
                        task.started_at = None
                        task.completed_at = None
                        state.active_tasks.append(task)
                
                elif new_status == TaskStatus.CANCELLED.value:
                    state.metrics.cancelled_tasks += 1
            
            if metadata:
                task.metadata.update(metadata)
            
            state.last_updated = datetime.utcnow().isoformat()
            self._save_state()
            
            return task
    
    def get_task(self, task_id: str) -> Optional[TaskState]:
        """Obtiene una tarea por ID (busca en activas e históricas)"""
        with self._lock:
            state = self._load_state()
            
            for task in state.active_tasks:
                if task.id == task_id:
                    return task
            
            for task in state.task_history:
                if task.id == task_id:
                    return task
            
            return None
    
    def get_tasks_by_agent(self, agent: str, active_only: bool = False) -> List[TaskState]:
        """Obtiene todas las tareas de un agente"""
        with self._lock:
            state = self._load_state()
            tasks = []
            
            for task in state.active_tasks:
                if task.agent == agent:
                    tasks.append(task)
            
            if not active_only:
                for task in state.task_history:
                    if task.agent == agent:
                        tasks.append(task)
            
            return tasks
    
    def get_pending_tasks(self) -> List[TaskState]:
        """Obtiene todas las tareas pendientes"""
        with self._lock:
            state = self._load_state()
            return [t for t in state.active_tasks if t.status == TaskStatus.PENDING.value]
    
    def cancel_task(self, task_id: str, reason: str = "") -> TaskState:
        """Cancela una tarea activa"""
        return self.transition_task(
            task_id,
            TaskStatus.CANCELLED.value,
            metadata={"cancellation_reason": reason}
        )
    
    def get_metrics(self) -> SystemMetrics:
        """Obtiene métricas del sistema"""
        with self._lock:
            state = self._load_state()
            return state.metrics
    
    def update_audit_timestamp(self):
        """Actualiza el timestamp de última auditoría"""
        with self._lock:
            state = self._load_state()
            state.metrics.last_audit = datetime.utcnow().isoformat()
            state.last_updated = datetime.utcnow().isoformat()
            self._save_state()
