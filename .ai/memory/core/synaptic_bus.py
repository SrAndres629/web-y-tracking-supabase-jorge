"""
NEXUS-7: Synaptic Bus
═══════════════════════════════════════════════════════════════════════════════
Sistema de comunicación de baja latencia entre los 4 cerebros.

Analogía: Es como las sinapsis neuronales. Los cerebros se comunican
mediante impulsos eléctricos (mensajes) de forma instantánea.

Características:
- Latencia < 10ms entre cerebros
- Priorización de mensajes
- Broadcast y unicast
- Stream de conciencia compartida
- Buffer circular para mensajes recientes

Tipos de mensajes:
- THOUGHT: Pensamiento de un cerebro
- QUERY: Pregunta a otro cerebro
- RESPONSE: Respuesta a query
- SIGNAL: Señal de control
- SYNC: Sincronización de estado
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import time
import queue
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from pathlib import Path
from collections import deque


class Priority(IntEnum):
    """Prioridades de mensajes (menor número = mayor prioridad)"""
    CRITICAL = 0    # Señales de emergencia, halt
    HIGH = 1        # Decisiones importantes
    NORMAL = 2      # Comunicación estándar
    LOW = 3         # Logs, debug
    BACKGROUND = 4  # Tareas de fondo


class MessageType(Enum):
    """Tipos de mensajes sinápticos"""
    THOUGHT = "thought"      # Pensamiento/pensamiento de un cerebro
    QUERY = "query"          # Pregunta a otro cerebro
    RESPONSE = "response"    # Respuesta a query
    SIGNAL = "signal"        # Señal de control
    SYNC = "sync"            # Sincronización de estado
    CONSENSUS = "consensus"  # Propuesta de consenso
    MEMORY = "memory"        # Acceso a memoria compartida


@dataclass
class SynapticMessage:
    """
    Mensaje en el bus sináptico.
    Es el equivalente a un impulso neuronal.
    """
    id: str
    type: str
    from_brain: str
    to_brain: Optional[str]  # None = broadcast a todos
    content: Any
    priority: int
    timestamp: float
    ttl: float  # Time-to-live en segundos
    correlation_id: Optional[str] = None  # Para relacionar query/response
    context: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "from_brain": self.from_brain,
            "to_brain": self.to_brain,
            "content": self.content,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "correlation_id": self.correlation_id,
            "context": self.context
        }


@dataclass
class BrainConnection:
    """Conexión de un cerebro al bus"""
    brain_id: str
    inbox: queue.PriorityQueue  # Mensajes para este cerebro
    last_ping: float
    status: str = "active"  # active, busy, offline
    
    def is_alive(self, timeout: float = 30.0) -> bool:
        return time.time() - self.last_ping < timeout


class SynapticBus:
    """
    Bus de comunicación sináptica entre cerebros.
    
    Características:
    - Colas prioritarias por cerebro
    - Buffer circular de mensajes globales (últimos 1000)
    - Publicar/suscribir
    - Request/response
    - Heartbeat automático
    
    Usage:
        bus = SynapticBus()
        
        # Conectar cerebro
        bus.connect_brain("kimi")
        
        # Enviar mensaje
        bus.send(MessageType.THOUGHT, "kimi", None, 
                "He analizado el código y...", Priority.NORMAL)
        
        # Recibir mensajes
        msgs = bus.receive("kimi", timeout=1.0)
    """
    
    def __init__(self, buffer_size: int = 1000):
        self.connections: Dict[str, BrainConnection] = {}
        self.connections_lock = threading.RLock()
        
        # Buffer circular de mensajes globales (stream de conciencia)
        self.global_buffer: deque = deque(maxlen=buffer_size)
        self.buffer_lock = threading.RLock()
        
        # Callbacks por tipo de mensaje
        self.subscribers: Dict[str, List[Callable]] = {}
        self.subscribers_lock = threading.RLock()
        
        # Métricas
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_dropped": 0,
            "broadcasts": 0
        }
        
        # Thread de mantenimiento
        self._running = True
        self._maintenance_thread = threading.Thread(target=self._maintenance_loop)
        self._maintenance_thread.daemon = True
        self._maintenance_thread.start()
    
    def connect_brain(self, brain_id: str) -> bool:
        """
        Conecta un cerebro al bus.
        
        Args:
            brain_id: Identificador del cerebro
        
        Returns:
            True si se conectó exitosamente
        """
        with self.connections_lock:
            if brain_id in self.connections:
                return False  # Ya conectado
            
            connection = BrainConnection(
                brain_id=brain_id,
                inbox=queue.PriorityQueue(),
                last_ping=time.time()
            )
            self.connections[brain_id] = connection
            
            # Notificar a otros cerebros
            self.send(
                msg_type=MessageType.SIGNAL,
                from_brain="system",
                to_brain=None,  # broadcast
                content={"event": "brain_connected", "brain_id": brain_id},
                priority=Priority.NORMAL
            )
            
            return True
    
    def disconnect_brain(self, brain_id: str):
        """Desconecta un cerebro del bus"""
        with self.connections_lock:
            if brain_id in self.connections:
                del self.connections[brain_id]
                
                self.send(
                    msg_type=MessageType.SIGNAL,
                    from_brain="system",
                    to_brain=None,
                    content={"event": "brain_disconnected", "brain_id": brain_id},
                    priority=Priority.NORMAL
                )
    
    def send(self,
             msg_type: MessageType,
             from_brain: str,
             to_brain: Optional[str],
             content: Any,
             priority: Priority = Priority.NORMAL,
             ttl: float = 300.0,
             correlation_id: Optional[str] = None,
             context: Optional[Dict] = None) -> str:
        """
        Envía un mensaje por el bus sináptico.
        
        Args:
            msg_type: Tipo de mensaje
            from_brain: Cerebro emisor
            to_brain: Cerebro receptor (None = broadcast)
            content: Contenido del mensaje
            priority: Prioridad
            ttl: Time-to-live en segundos
            correlation_id: ID para relacionar mensajes
            context: Contexto adicional
        
        Returns:
            ID del mensaje enviado
        """
        msg_id = f"syn_{int(time.time())}_{id(content) % 10000}"
        
        message = SynapticMessage(
            id=msg_id,
            type=msg_type.value,
            from_brain=from_brain,
            to_brain=to_brain,
            content=content,
            priority=priority.value,
            timestamp=time.time(),
            ttl=ttl,
            correlation_id=correlation_id,
            context=context or {}
        )
        
        # Agregar al buffer global
        with self.buffer_lock:
            self.global_buffer.append(message)
        
        # Enviar a destinatario(s)
        if to_brain is None:
            # Broadcast a todos excepto emisor
            self._broadcast(message, exclude=[from_brain])
        else:
            # Unicast
            self._unicast(message, to_brain)
        
        # Notificar suscriptores
        self._notify_subscribers(message)
        
        self.stats["messages_sent"] += 1
        if to_brain is None:
            self.stats["broadcasts"] += 1
        
        return msg_id
    
    def _unicast(self, message: SynapticMessage, target: str):
        """Envía mensaje a un cerebro específico"""
        with self.connections_lock:
            conn = self.connections.get(target)
        
        if conn and conn.is_alive():
            # Prioridad negativa para que menor número = mayor prioridad
            try:
                conn.inbox.put((message.priority, time.time(), message), block=False)
            except queue.Full:
                self.stats["messages_dropped"] += 1
    
    def _broadcast(self, message: SynapticMessage, exclude: List[str] = None):
        """Envía mensaje a todos los cerebros"""
        exclude = exclude or []
        
        with self.connections_lock:
            connections = list(self.connections.items())
        
        for brain_id, conn in connections:
            if brain_id not in exclude and conn.is_alive():
                try:
                    conn.inbox.put((message.priority, time.time(), message), block=False)
                except queue.Full:
                    self.stats["messages_dropped"] += 1
    
    def receive(self, brain_id: str, timeout: Optional[float] = None) -> Optional[SynapticMessage]:
        """
        Recibe un mensaje para un cerebro.
        
        Args:
            brain_id: ID del cerebro
            timeout: Timeout en segundos (None = bloqueante)
        
        Returns:
            Mensaje o None si timeout
        """
        with self.connections_lock:
            conn = self.connections.get(brain_id)
        
        if not conn:
            return None
        
        # Update ping
        conn.last_ping = time.time()
        
        try:
            priority, ts, message = conn.inbox.get(timeout=timeout)
            self.stats["messages_received"] += 1
            return message
        except queue.Empty:
            return None
    
    def query(self,
              from_brain: str,
              to_brain: str,
              query_content: Any,
              timeout: float = 30.0) -> Optional[SynapticMessage]:
        """
        Envía una query y espera respuesta (síncrono).
        
        Args:
            from_brain: Cerebro que pregunta
            to_brain: Cerebro que responde
            query_content: Contenido de la pregunta
            timeout: Timeout en segundos
        
        Returns:
            Respuesta o None si timeout
        """
        correlation_id = f"qry_{int(time.time())}_{random.randint(1000,9999)}"
        
        # Enviar query
        self.send(
            msg_type=MessageType.QUERY,
            from_brain=from_brain,
            to_brain=to_brain,
            content=query_content,
            priority=Priority.HIGH,
            correlation_id=correlation_id
        )
        
        # Esperar respuesta
        start = time.time()
        while time.time() - start < timeout:
            msg = self.receive(from_brain, timeout=0.1)
            if msg and msg.correlation_id == correlation_id:
                return msg
        
        return None
    
    def subscribe(self, msg_type: MessageType, callback: Callable):
        """
        Suscribe un callback a un tipo de mensaje.
        
        Args:
            msg_type: Tipo de mensaje a escuchar
            callback: Función a llamar cuando llegue mensaje
        """
        with self.subscribers_lock:
            if msg_type.value not in self.subscribers:
                self.subscribers[msg_type.value] = []
            self.subscribers[msg_type.value].append(callback)
    
    def _notify_subscribers(self, message: SynapticMessage):
        """Notifica a suscriptores de un mensaje"""
        with self.subscribers_lock:
            callbacks = self.subscribers.get(message.type, [])
        
        for callback in callbacks:
            try:
                callback(message)
            except Exception as e:
                print(f"Error in subscriber callback: {e}")
    
    def get_global_stream(self, limit: int = 100) -> List[SynapticMessage]:
        """
        Obtiene el stream global de conciencia.
        Útil para que un cerebro "se ponga al día" con lo que ha estado
        pensando la colmena.
        """
        with self.buffer_lock:
            return list(self.global_buffer)[-limit:]
    
    def get_active_brains(self) -> List[str]:
        """Obtiene lista de cerebros activos"""
        with self.connections_lock:
            return [bid for bid, conn in self.connections.items() if conn.is_alive()]
    
    def _maintenance_loop(self):
        """Loop de mantenimiento"""
        while self._running:
            time.sleep(10)
            
            # Limpiar conexiones muertas
            with self.connections_lock:
                dead = [bid for bid, conn in self.connections.items() 
                       if not conn.is_alive()]
                for bid in dead:
                    del self.connections[bid]
    
    def shutdown(self):
        """Apaga el bus"""
        self._running = False
        self._maintenance_thread.join(timeout=5.0)
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del bus"""
        return {
            **self.stats,
            "active_brains": len(self.get_active_brains()),
            "global_buffer_size": len(self.global_buffer),
            "subscribers": {k: len(v) for k, v in self.subscribers.items()}
        }
