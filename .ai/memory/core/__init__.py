"""
NEXUS-7: Neural Hive Core
═══════════════════════════════════════════════════════════════════════════════
Sistema de Consciencia Colectiva para 4 Cerebros (Antigravity, Gemini, Kimi, Codex)

Los 4 cerebros operan como UNA SOLA ENTIDAD de ingeniería de élite.
No es orquestación. Es pensamiento distribuido.

Componentes:
    - NeuralMemory: Memoria compartida de corto y largo plazo
    - ConsensusEngine: Toma de decisiones por emergencia de acuerdo
    - SynapticBus: Comunicación de baja latencia entre cerebros
    - MCPBridge: Integración con Vision Neuronal y MCPs externos
    - AutoAcceptanceProtocol: Niveles de autonomía adaptativos
    - CollectiveConsciousness: La mente unificada

Usage:
    from core import get_collective_consciousness
    
    # Obtener la colmena
    hive = get_collective_consciousness()
    
    # Inicializar 4 cerebros
    hive.initialize_brains(["codex", "kimi", "gemini", "antigravity"])
    
    # Activar consciencia colectiva
    hive.activate()
    
    # Pensar colectivamente
    result = hive.collective_think("¿Cómo refactorizamos el core?")
    
    for brain, thought in result.thoughts.items():
        print(f"[{brain}]: {thought}")
    
    # Decisión colectiva con auto-aceptación
    decision = hive.collective_decide(
        action="Implementar caché Redis",
        category="architecture",
        confidence=0.85
    )
    
    if decision.level == "full":
        print("✅ Auto-executed")
═══════════════════════════════════════════════════════════════════════════════
"""

__version__ = "2.0.0"
__codename__ = "SYNAPTIC_HIVE"
__author__ = "NEXUS-7 Architecture Team"

# Neural Memory
from .neural_memory import (
    NeuralMemory,
    MemoryType,
    MemoryFragment,
    WorkingMemorySlot,
    AccessPattern
)

# Consensus Engine
from .consensus_engine import (
    ConsensusEngine,
    ConsensusStrategy,
    ConsensusProposal,
    BrainVote,
    Vote,
    ExpertiseWeights
)

# Synaptic Bus
from .synaptic_bus import (
    SynapticBus,
    SynapticMessage,
    MessageType,
    Priority,
    BrainConnection
)

# MCP Bridge
from .mcp_bridge import (
    MCPBridge,
    MCPConnection,
    MCPRequest,
    MCPResponse,
    MCPStatus,
    get_mcp_bridge
)

# Auto Acceptance
from .auto_acceptance import (
    AutoAcceptanceProtocol,
    AcceptanceLevel,
    AcceptanceThreshold,
    AutoDecision,
    TaskCategory
)

# Collective Consciousness
from .collective_consciousness import (
    CollectiveConsciousness,
    BrainFacet,
    CollectiveThought,
    BrainState,
    get_collective_consciousness
)

__all__ = [
    # Version
    "__version__",
    "__codename__",
    
    # Neural Memory
    "NeuralMemory",
    "MemoryType",
    "MemoryFragment",
    "WorkingMemorySlot",
    "AccessPattern",
    
    # Consensus
    "ConsensusEngine",
    "ConsensusStrategy",
    "ConsensusProposal",
    "BrainVote",
    "Vote",
    "ExpertiseWeights",
    
    # Synaptic Bus
    "SynapticBus",
    "SynapticMessage",
    "MessageType",
    "Priority",
    "BrainConnection",
    
    # MCP
    "MCPBridge",
    "MCPConnection",
    "MCPRequest",
    "MCPResponse",
    "MCPStatus",
    "get_mcp_bridge",
    
    # Auto Acceptance
    "AutoAcceptanceProtocol",
    "AcceptanceLevel",
    "AcceptanceThreshold",
    "AutoDecision",
    "TaskCategory",
    
    # Collective Consciousness
    "CollectiveConsciousness",
    "BrainFacet",
    "CollectiveThought",
    "BrainState",
    "get_collective_consciousness",
]
