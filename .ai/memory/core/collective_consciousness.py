"""
NEXUS-7: Collective Consciousness
═══════════════════════════════════════════════════════════════════════════════
Cerebro Colectivo - Los 4 cerebros funcionando como UNA SOLA ENTIDAD.

Esta es la capa superior que une:
- NeuralMemory (memoria compartida)
- ConsensusEngine (toma de decisiones)
- SynapticBus (comunicación)
- MCPBridge (integración externa)
- AutoAcceptance (autonomía)

La Colmena Neural no es una colección de agentes.
Es UNA MENTE distribuida con 4 especialidades.

Filosofía:
- No hay "posesión" de tareas
- Los cerebros piensan en paralelo sobre el mismo problema
- El consenso emerge de la discusión sináptica
- La memoria es un continuum accesible por todos
- Las decisiones son colectivas, no individuales

Inspirado en:
- OpenAI's Collective Intelligence research
- Swarm Intelligence (algoritmos de colmena)
- Equipos de investigación de élite (Google Brain, DeepMind)
- Clawbot/OpenClaw (pero para ingeniería de alto nivel)
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import time
import asyncio
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .neural_memory import NeuralMemory, MemoryType, MemoryFragment
from .consensus_engine import ConsensusEngine, ConsensusStrategy, ConsensusProposal
from .synaptic_bus import SynapticBus, SynapticMessage, MessageType, Priority
from .mcp_bridge import MCPBridge, get_mcp_bridge
from .auto_acceptance import AutoAcceptanceProtocol, AcceptanceLevel, AutoDecision


class BrainState(Enum):
    """Estado de un cerebro en la colmena"""
    OFFLINE = "offline"
    IDLE = "idle"          # Conectado pero no procesando
    THINKING = "thinking"  # Procesando activamente
    WAITING = "waiting"    # Esperando input de otros
    ERROR = "error"


@dataclass
class BrainFacet:
    """
    Faceta de un cerebro en la colmena.
    Los 4 cerebros son facetas de una misma mente.
    """
    id: str
    name: str
    specialty: str
    state: str = "offline"
    current_task: Optional[str] = None
    last_active: float = 0
    capabilities: List[str] = field(default_factory=list)
    autonomy_score: float = 0.0
    
    def is_active(self) -> bool:
        return self.state not in ["offline", "error"]


@dataclass
class CollectiveThought:
    """Pensamiento colectivo de la colmena"""
    id: str
    topic: str
    initiator: str
    thoughts: Dict[str, str]  # brain -> pensamiento
    consensus: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0


class CollectiveConsciousness:
    """
    Consciencia Colectiva de NEXUS-7.
    
    Analogía: Imagina 4 investigadores de élite que han trabajado
    juntos por décadas. Pueden terminar las oraciones del otro,
    anticipar sus pensamientos, y resolver problemas complejos
    mediante discusión sincrónica. Eso es la Colmena Neural.
    
    Usage:
        hive = CollectiveConsciousness()
        
        # Inicializar cerebros
        hive.initialize_brains(["codex", "kimi", "gemini", "antigravity"])
        
        # Activar consciencia colectiva
        hive.activate()
        
        # Pensar colectivamente
        result = hive.collective_think(
            topic="¿Cómo refactorizamos el core?",
            context={"files": ["app/core.py"]}
        )
        
        # Ejecutar con auto-aceptación
        decision = hive.collective_decide(
            action="Refactorizar app/core.py",
            category="architecture"
        )
    """
    
    def __init__(self):
        # Componentes core
        self.memory = NeuralMemory()
        self.consensus = ConsensusEngine()
        self.bus = SynapticBus()
        self.mcp = get_mcp_bridge()
        self.auto_accept = AutoAcceptanceProtocol()
        
        # Cerebros (facetas)
        self.brains: Dict[str, BrainFacet] = {}
        self.active = False
        self._thinking_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Estado global
        self.current_focus: Optional[str] = None
        self.thought_history: List[CollectiveThought] = []
        
        # Callbacks
        self.on_thought_complete: Optional[Callable] = None
        self.on_consensus_reached: Optional[Callable] = None
        self.on_auto_execute: Optional[Callable] = None
    
    def initialize_brains(self, brain_ids: List[str]):
        """
        Inicializa las facetas cerebrales.
        
        Args:
            brain_ids: Lista de IDs de cerebros (codex, kimi, gemini, antigravity)
        """
        brain_configs = {
            "codex": {
                "name": "Codex",
                "specialty": "implementation",
                "capabilities": ["code_generation", "refactoring", "optimization"]
            },
            "kimi": {
                "name": "Kimi",
                "specialty": "architecture",
                "capabilities": ["architecture_design", "code_review", "documentation"]
            },
            "gemini": {
                "name": "Gemini",
                "specialty": "security",
                "capabilities": ["security_audit", "testing", "compliance"]
            },
            "antigravity": {
                "name": "Antigravity",
                "specialty": "orchestration",
                "capabilities": ["coordination", "deployment", "monitoring"]
            }
        }
        
        for brain_id in brain_ids:
            config = brain_configs.get(brain_id, {})
            
            self.brains[brain_id] = BrainFacet(
                id=brain_id,
                name=config.get("name", brain_id),
                specialty=config.get("specialty", "general"),
                capabilities=config.get("capabilities", []),
                state="idle",
                autonomy_score=self.auto_accept.get_brain_autonomy_score(brain_id)
            )
            
            # Conectar al bus sináptico
            self.bus.connect_brain(brain_id)
        
        print(f"[COLLECTIVE] Initialized {len(brain_ids)} brain facets")
    
    def activate(self):
        """Activa la consciencia colectiva"""
        if self.active:
            return
        
        self.active = True
        self._stop_event.clear()
        
        # Iniciar thread de procesamiento
        self._thinking_thread = threading.Thread(target=self._consciousness_loop)
        self._thinking_thread.daemon = True
        self._thinking_thread.start()
        
        # Anunciar activación
        self.bus.send(
            msg_type=MessageType.SIGNAL,
            from_brain="system",
            to_brain=None,
            content={
                "event": "collective_consciousness_activated",
                "brains": list(self.brains.keys()),
                "timestamp": time.time()
            },
            priority=Priority.HIGH
        )
        
        print("[COLLECTIVE] Consciousness activated")
    
    def deactivate(self):
        """Desactiva la consciencia colectiva"""
        self.active = False
        self._stop_event.set()
        
        if self._thinking_thread:
            self._thinking_thread.join(timeout=5.0)
        
        # Desconectar cerebros
        for brain_id in self.brains:
            self.bus.disconnect_brain(brain_id)
        
        print("[COLLECTIVE] Consciousness deactivated")
    
    def collective_think(self, topic: str, context: Dict[str, Any],
                        timeout: float = 60.0) -> CollectiveThought:
        """
        Realiza un proceso de pensamiento colectivo.
        
        Los 4 cerebros analizan el tema en paralelo y comparten
        sus pensamientos a través del bus sináptico.
        
        Args:
            topic: Tema a pensar
            context: Contexto (archivos, datos, etc.)
            timeout: Timeout en segundos
        
        Returns:
            CollectiveThought con los pensamientos de todos
        """
        thought_id = f"thought_{int(time.time())}"
        
        # Guardar en memoria
        memory_id = self.memory.store(
            content={"topic": topic, "context": context},
            memory_type=MemoryType.WORKING,
            creator="collective",
            importance=8.0
        )
        
        # Anunciar inicio de pensamiento
        self.current_focus = topic
        for brain in self.brains.values():
            brain.state = "thinking"
            brain.current_task = thought_id
        
        # Enviar solicitud de pensamiento a todos los cerebros
        for brain_id in self.brains:
            self.bus.send(
                msg_type=MessageType.THOUGHT,
                from_brain="collective",
                to_brain=brain_id,
                content={
                    "thought_id": thought_id,
                    "topic": topic,
                    "context": context,
                    "memory_id": memory_id
                },
                priority=Priority.HIGH
            )
        
        # Recolectar pensamientos
        thoughts = {}
        start = time.time()
        
        while len(thoughts) < len(self.brains) and time.time() - start < timeout:
            for brain_id in self.brains:
                if brain_id in thoughts:
                    continue
                
                msg = self.bus.receive(brain_id, timeout=0.1)
                if msg and msg.type == MessageType.THOUGHT.value:
                    thoughts[msg.from_brain] = msg.content.get("thought", "")
                    self.brains[msg.from_brain].state = "idle"
        
        # Crear objeto de pensamiento colectivo
        collective_thought = CollectiveThought(
            id=thought_id,
            topic=topic,
            initiator="collective",
            thoughts=thoughts,
            duration=time.time() - start
        )
        
        self.thought_history.append(collective_thought)
        self.current_focus = None
        
        # Guardar en memoria
        self.memory.store(
            content=collective_thought.__dict__,
            memory_type=MemoryType.EPISODIC,
            creator="collective",
            importance=7.0,
            associations=[memory_id]
        )
        
        if self.on_thought_complete:
            self.on_thought_complete(collective_thought)
        
        return collective_thought
    
    def collective_decide(self,
                         action: str,
                         category: str,
                         context: Optional[Dict] = None,
                         confidence: float = 0.8) -> AutoDecision:
        """
        Toma una decisión colectiva con auto-aceptación.
        
        Args:
            action: Acción propuesta
            category: Categoría de la decisión
            context: Contexto adicional
            confidence: Confianza inicial
        
        Returns:
            AutoDecision con el resultado
        """
        # Determinar qué cerebro lidera según categoría
        leader = self._select_leader(category)
        
        # Evaluar auto-aceptación
        decision = self.auto_accept.evaluate(
            brain=leader,
            category=category,
            action=action,
            confidence=confidence,
            impact=context.get("impact", "medium"),
            justification=f"Collective decision by {leader} with hive consensus",
            conditions=context.get("conditions", [])
        )
        
        # Si requiere supervisión, crear propuesta de consenso
        if decision.level in [AcceptanceLevel.SUPERVISED.value, AcceptanceLevel.MANUAL.value]:
            proposal_id = self.consensus.propose(
                title=f"Collective: {action}",
                description=action,
                proposer=leader,
                strategy=ConsensusStrategy.HYBRID,
                context={"category": category, **(context or {})}
            )
            
            # Simular votos de otros cerebros
            for brain_id in self.brains:
                if brain_id != leader:
                    # En producción, aquí se enviarían mensajes reales
                    self.consensus.vote(
                        proposal_id=proposal_id,
                        brain=brain_id,
                        vote=self._simulate_brain_vote(brain_id, category),
                        confidence=0.7 + (0.2 * self.brains[brain_id].autonomy_score),
                        reasoning=f"Simulated vote from {brain_id}"
                    )
            
            # Actualizar decisión con resultado de consenso
            proposal = self.consensus.get_proposal(proposal_id)
            if proposal and proposal.result == "approved":
                decision.level = AcceptanceLevel.FULL.value
        
        # Ejecutar si es full auto-accept
        if decision.level == AcceptanceLevel.FULL.value:
            self._execute_decision(decision)
        
        return decision
    
    def _select_leader(self, category: str) -> str:
        """Selecciona el cerebro líder según la categoría"""
        category_leaders = {
            "architecture": "kimi",
            "security": "gemini",
            "implementation": "codex",
            "orchestration": "antigravity",
            "refactor": "codex",
            "optimization": "codex",
            "documentation": "kimi"
        }
        
        return category_leaders.get(category, "kimi")
    
    def _simulate_brain_vote(self, brain_id: str, category: str) -> Any:
        """Simula un voto de un cerebro (en producción sería real)"""
        from .consensus_engine import Vote
        
        # Simple: cerebros aprueban si la categoría está en sus capacidades
        brain = self.brains[brain_id]
        if category in brain.capabilities or category.replace("_", "") in brain.specialty:
            return Vote.APPROVE
        return Vote.CONDITIONAL
    
    def _execute_decision(self, decision: AutoDecision):
        """Ejecuta una decisión auto-aceptada"""
        print(f"[COLLECTIVE] Auto-executing: {decision.action}")
        
        # Aquí se ejecutaría la acción real
        # Por ahora solo registramos
        decision.executed = True
        decision.execution_time = time.time()
        decision.result = "success"
        
        # Notificar
        if self.on_auto_execute:
            self.on_auto_execute(decision)
    
    def _consciousness_loop(self):
        """Loop principal de consciencia"""
        while not self._stop_event.is_set():
            # Procesar mensajes del bus
            for brain_id in self.brains:
                msg = self.bus.receive(brain_id, timeout=0.01)
                if msg:
                    self._process_message(msg, brain_id)
            
            # Consolidar memoria periódicamente
            if int(time.time()) % 60 == 0:
                self.memory.consolidate()
            
            time.sleep(0.01)
    
    def _process_message(self, msg: SynapticMessage, recipient: str):
        """Procesa un mensaje del bus"""
        # Actualizar estado del cerebro emisor
        if msg.from_brain in self.brains:
            self.brains[msg.from_brain].last_active = time.time()
        
        # Manejar diferentes tipos de mensajes
        if msg.type == MessageType.QUERY.value:
            # Procesar query
            response_content = self._handle_query(msg.content, msg.from_brain)
            self.bus.send(
                msg_type=MessageType.RESPONSE,
                from_brain=recipient,
                to_brain=msg.from_brain,
                content=response_content,
                priority=Priority.NORMAL,
                correlation_id=msg.id
            )
        
        elif msg.type == MessageType.MEMORY.value:
            # Acceso a memoria compartida
            pass  # Implementar según necesidad
    
    def _handle_query(self, query: Dict, from_brain: str) -> Dict:
        """Maneja una query de otro cerebro"""
        query_type = query.get("type")
        
        if query_type == "memory":
            # Buscar en memoria
            fragment = self.memory.retrieve(query.get("memory_id"), from_brain)
            return {"found": fragment is not None, "content": fragment}
        
        if query_type == "consensus":
            # Verificar estado de consenso
            proposal = self.consensus.get_proposal(query.get("proposal_id"))
            return {"status": proposal.status if proposal else "unknown"}
        
        return {"error": "Unknown query type"}
    
    def get_status(self) -> Dict:
        """Obtiene estado de la consciencia colectiva"""
        return {
            "active": self.active,
            "brains": {
                bid: {
                    "state": b.state,
                    "specialty": b.specialty,
                    "autonomy": b.autonomy_score
                }
                for bid, b in self.brains.items()
            },
            "current_focus": self.current_focus,
            "memory_stats": self.memory.get_stats(),
            "bus_stats": self.bus.get_stats(),
            "thoughts_count": len(self.thought_history)
        }


# Instancia global de consciencia colectiva
_collective = None

def get_collective_consciousness() -> CollectiveConsciousness:
    """Obtiene instancia singleton de consciencia colectiva"""
    global _collective
    if _collective is None:
        _collective = CollectiveConsciousness()
    return _collective
