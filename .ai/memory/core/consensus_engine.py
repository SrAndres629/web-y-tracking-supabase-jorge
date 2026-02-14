"""
NEXUS-7: Consensus Engine
═══════════════════════════════════════════════════════════════════════════════
Sistema de toma de decisiones por consenso de los 4 cerebros.

No es una votación simple. Es un proceso de:
1. Propuesta: Un cerebro sugiere una acción
2. Evaluación: Los otros 3 analizan la propuesta
3. Refinamiento: Se discuten mejoras
4. Consenso: Se llega a decisión unánime o mayoritaria
5. Ejecución: Se ejecuta la decisión colectiva

Estrategias:
- UNANIMOUS: Todos deben estar de acuerdo (para cambios críticos)
- MAJORITY: 3 de 4 (para la mayoría de decisiones)
- WEIGHTED: Pesos diferentes según expertise
- AUTO: Consenso automático sin intervención humana
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading


class ConsensusStrategy(Enum):
    """Estrategias de consenso"""
    UNANIMOUS = "unanimous"    # 4/4 - Cambios críticos (arquitectura, seguridad)
    MAJORITY = "majority"      # 3/4 - Decisiones estándar
    WEIGHTED = "weighted"      # Pesos por expertise
    AUTO = "auto"              # Sin votación, consenso implícito
    HYBRID = "hybrid"          # Combinación según tipo de decisión


class Vote(Enum):
    """Tipos de voto"""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    CONDITIONAL = "conditional"  # Aprobar con modificaciones


@dataclass
class BrainVote:
    """Voto de un cerebro"""
    brain: str
    vote: str  # Vote
    confidence: float  # 0.0 - 1.0
    reasoning: str
    timestamp: float
    conditions: Optional[List[str]] = None  # Condiciones para voto condicional
    
    def to_dict(self) -> dict:
        return {
            "brain": self.brain,
            "vote": self.vote,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
            "conditions": self.conditions
        }


@dataclass
class ConsensusProposal:
    """Propuesta para decisión colectiva"""
    id: str
    title: str
    description: str
    proposer: str  # Cerebro que propone
    strategy: str  # ConsensusStrategy
    context: Dict[str, Any]  # Contexto completo
    votes: Dict[str, BrainVote] = field(default_factory=dict)
    status: str = "pending"  # pending, voting, decided, executed
    result: Optional[str] = None  # approved, rejected
    final_decision: Optional[Dict] = None
    created_at: float = field(default_factory=time.time)
    decided_at: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "proposer": self.proposer,
            "strategy": self.strategy,
            "context": self.context,
            "votes": {k: v.to_dict() for k, v in self.votes.items()},
            "status": self.status,
            "result": self.result,
            "final_decision": self.final_decision,
            "created_at": self.created_at,
            "decided_at": self.decided_at
        }


@dataclass
class ExpertiseWeights:
    """Pesos de expertise por tipo de decisión"""
    architecture: Dict[str, float] = field(default_factory=lambda: {
        "kimi": 0.4,
        "gemini": 0.3,
        "codex": 0.2,
        "antigravity": 0.1
    })
    security: Dict[str, float] = field(default_factory=lambda: {
        "gemini": 0.5,
        "kimi": 0.25,
        "codex": 0.15,
        "antigravity": 0.1
    })
    implementation: Dict[str, float] = field(default_factory=lambda: {
        "codex": 0.5,
        "kimi": 0.25,
        "gemini": 0.15,
        "antigravity": 0.1
    })
    optimization: Dict[str, float] = field(default_factory=lambda: {
        "codex": 0.35,
        "kimi": 0.35,
        "gemini": 0.2,
        "antigravity": 0.1
    })


class ConsensusEngine:
    """
    Motor de consenso para toma de decisiones colectiva.
    
    Analogía: Es como si los 4 cerebros tuvieran una reunión
    donde discuten y llegan a acuerdos. No es una votación
    mecánica - es un proceso dialéctico.
    
    Features:
    - Propuestas con contexto completo
    - Votación con confianza y razonamiento
    - Pesos de expertise por dominio
    - Refinamiento iterativo de propuestas
    - Fallback a intervención humana si no hay consenso
    """
    
    # Thresholds de decisión automática
    AUTO_ACCEPT_THRESHOLD = 0.85  # Confianza promedio para auto-aceptar
    AUTO_REJECT_THRESHOLD = 0.15  # Confianza promedio para auto-rechazar
    
    def __init__(self, consensus_dir: str = ".ai/memory/core/consensus"):
        self.consensus_dir = Path(consensus_dir)
        self.consensus_dir.mkdir(parents=True, exist_ok=True)
        
        self.expertise = ExpertiseWeights()
        self.active_proposals: Dict[str, ConsensusProposal] = {}
        self.proposal_history: List[str] = []
        self._lock = threading.RLock()
        
        # Callbacks para eventos
        self.on_consensus_reached: Optional[Callable] = None
        self.on_consensus_failed: Optional[Callable] = None
        
        # Cargar propuestas históricas
        self._load_history()
    
    def propose(self,
                title: str,
                description: str,
                proposer: str,
                strategy: ConsensusStrategy = ConsensusStrategy.MAJORITY,
                context: Optional[Dict] = None,
                auto_execute: bool = False) -> str:
        """
        Crea una nueva propuesta para decisión colectiva.
        
        Args:
            title: Título de la propuesta
            description: Descripción detallada
            proposer: Cerebro que propone
            strategy: Estrategia de consenso
            context: Contexto adicional (archivos, datos, etc.)
            auto_execute: Ejecutar automáticamente si hay consenso
        
        Returns:
            ID de la propuesta
        """
        proposal_id = f"cons_{int(time.time())}_{random.randint(1000, 9999)}"
        
        proposal = ConsensusProposal(
            id=proposal_id,
            title=title,
            description=description,
            proposer=proposer,
            strategy=strategy.value,
            context=context or {},
            status="voting"
        )
        
        with self._lock:
            self.active_proposals[proposal_id] = proposal
        
        # El proponente vota automáticamente a favor
        self.vote(
            proposal_id=proposal_id,
            brain=proposer,
            vote=Vote.APPROVE,
            confidence=0.9,
            reasoning="Propuesta propia"
        )
        
        self._persist_proposal(proposal)
        
        return proposal_id
    
    def vote(self,
             proposal_id: str,
             brain: str,
             vote: Vote,
             confidence: float,
             reasoning: str,
             conditions: Optional[List[str]] = None) -> bool:
        """
        Registra un voto para una propuesta.
        
        Args:
            proposal_id: ID de la propuesta
            brain: Cerebro que vota
            vote: Tipo de voto
            confidence: Confianza (0.0 - 1.0)
            reasoning: Razonamiento del voto
            conditions: Condiciones para voto condicional
        
        Returns:
            True si se alcanzó consenso
        """
        with self._lock:
            proposal = self.active_proposals.get(proposal_id)
            if not proposal:
                return False
            
            brain_vote = BrainVote(
                brain=brain,
                vote=vote.value,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=time.time(),
                conditions=conditions
            )
            
            proposal.votes[brain] = brain_vote
            
            # Verificar si hay consenso
            consensus_reached = self._check_consensus(proposal)
            
            if consensus_reached:
                self._finalize_consensus(proposal_id)
            
            self._persist_proposal(proposal)
            return consensus_reached
    
    def _check_consensus(self, proposal: ConsensusProposal) -> bool:
        """Verifica si se alcanzó consenso según la estrategia"""
        votes = list(proposal.votes.values())
        
        if len(votes) < 2:  # Necesitamos al menos 2 votos
            return False
        
        strategy = ConsensusStrategy(proposal.strategy)
        
        if strategy == ConsensusStrategy.AUTO:
            return True  # Siempre consenso inmediato
        
        if strategy == ConsensusStrategy.UNANIMOUS:
            return self._check_unanimous(votes)
        
        if strategy == ConsensusStrategy.MAJORITY:
            return self._check_majority(votes)
        
        if strategy == ConsensusStrategy.WEIGHTED:
            decision_type = proposal.context.get("type", "architecture")
            return self._check_weighted(votes, decision_type)
        
        if strategy == ConsensusStrategy.HYBRID:
            return self._check_hybrid(votes, proposal)
        
        return False
    
    def _check_unanimous(self, votes: List[BrainVote]) -> bool:
        """Verifica unanimidad (4/4)"""
        if len(votes) < 4:
            return False
        
        approve_count = sum(1 for v in votes if v.vote == Vote.APPROVE.value)
        return approve_count == 4
    
    def _check_majority(self, votes: List[BrainVote]) -> bool:
        """Verifica mayoría (3/4)"""
        if len(votes) < 3:
            return False
        
        approve_count = sum(1 for v in votes if v.vote == Vote.APPROVE.value)
        reject_count = sum(1 for v in votes if v.vote == Vote.REJECT.value)
        
        if approve_count >= 3:
            return True
        if reject_count >= 2:  # Mayoría en contra
            return True  # Consenso para rechazar
        
        return False
    
    def _check_weighted(self, votes: List[BrainVote], decision_type: str) -> bool:
        """Verifica consenso ponderado por expertise"""
        weights = getattr(self.expertise, decision_type, self.expertise.architecture)
        
        total_weight = 0
        approve_weight = 0
        
        for vote in votes:
            weight = weights.get(vote.brain, 0.25)
            total_weight += weight
            if vote.vote == Vote.APPROVE.value:
                approve_weight += weight
        
        # Necesitamos 70% del peso total aprobando
        return total_weight > 0 and (approve_weight / total_weight) >= 0.7
    
    def _check_hybrid(self, votes: List[BrainVote], proposal: ConsensusProposal) -> bool:
        """
        Estrategia híbrida:
        - Decisiones críticas: Unanimidad
        - Decisiones estándar: Mayoría
        - Auto-aceptación si confianza promedio > 0.85
        """
        # Calcular confianza promedio
        avg_confidence = sum(v.confidence for v in votes) / len(votes)
        
        # Auto-aceptación por alta confianza
        if avg_confidence >= self.AUTO_ACCEPT_THRESHOLD:
            return True
        
        # Auto-rechazo por baja confianza
        if avg_confidence <= self.AUTO_REJECT_THRESHOLD:
            return True
        
        # Determinar tipo de decisión
        is_critical = proposal.context.get("critical", False)
        
        if is_critical:
            return self._check_unanimous(votes)
        else:
            return self._check_majority(votes)
    
    def _finalize_consensus(self, proposal_id: str):
        """Finaliza el proceso de consenso"""
        with self._lock:
            proposal = self.active_proposals[proposal_id]
            proposal.status = "decided"
            proposal.decided_at = time.time()
            
            # Determinar resultado
            approve_count = sum(1 for v in proposal.votes.values() 
                              if v.vote == Vote.APPROVE.value)
            reject_count = sum(1 for v in proposal.votes.values() 
                             if v.vote == Vote.REJECT.value)
            
            if approve_count > reject_count:
                proposal.result = "approved"
            else:
                proposal.result = "rejected"
            
            # Construir decisión final
            proposal.final_decision = {
                "action": proposal.context.get("action"),
                "approved_by": [v.brain for v in proposal.votes.values() 
                               if v.vote == Vote.APPROVE.value],
                "confidence": sum(v.confidence for v in proposal.votes.values()) / len(proposal.votes),
                "reasoning_summary": self._summarize_reasoning(proposal)
            }
            
            # Mover a historial
            self.proposal_history.append(proposal_id)
            del self.active_proposals[proposal_id]
        
        # Notificar
        if self.on_consensus_reached:
            self.on_consensus_reached(proposal)
        
        self._persist_proposal(proposal)
    
    def _summarize_reasoning(self, proposal: ConsensusProposal) -> str:
        """Resume el razonamiento de los votos"""
        reasonings = [v.reasoning for v in proposal.votes.values()]
        return " | ".join(reasonings[:3])  # Top 3 razonamientos
    
    def simulate_consensus(self, 
                          title: str,
                          description: str,
                          brain_opinions: Dict[str, Dict]) -> ConsensusProposal:
        """
        Simula un proceso de consenso completo.
        Útil para testing o para procesos automáticos.
        
        Args:
            title: Título de la propuesta
            description: Descripción
            brain_opinions: Dict {brain: {"vote": "approve", "confidence": 0.9, "reasoning": "..."}}
        
        Returns:
            Propuesta finalizada
        """
        proposal_id = self.propose(
            title=title,
            description=description,
            proposer=list(brain_opinions.keys())[0],
            strategy=ConsensusStrategy.HYBRID
        )
        
        for brain, opinion in brain_opinions.items():
            self.vote(
                proposal_id=proposal_id,
                brain=brain,
                vote=Vote(opinion["vote"]),
                confidence=opinion["confidence"],
                reasoning=opinion["reasoning"]
            )
        
        # Recargar propuesta (debería estar finalizada)
        return self.get_proposal(proposal_id) or self._load_from_disk(proposal_id)
    
    def get_proposal(self, proposal_id: str) -> Optional[ConsensusProposal]:
        """Obtiene una propuesta activa"""
        with self._lock:
            return self.active_proposals.get(proposal_id)
    
    def get_history(self, limit: int = 10) -> List[ConsensusProposal]:
        """Obtiene historial de propuestas decididas"""
        proposals = []
        for pid in self.proposal_history[-limit:]:
            p = self._load_from_disk(pid)
            if p:
                proposals.append(p)
        return proposals
    
    def _persist_proposal(self, proposal: ConsensusProposal):
        """Persiste propuesta a disco"""
        proposal_file = self.consensus_dir / f"{proposal.id}.json"
        with open(proposal_file, 'w', encoding='utf-8') as f:
            json.dump(proposal.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _load_from_disk(self, proposal_id: str) -> Optional[ConsensusProposal]:
        """Carga propuesta desde disco"""
        proposal_file = self.consensus_dir / f"{proposal_id}.json"
        if proposal_file.exists():
            try:
                with open(proposal_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return ConsensusProposal(**data)
            except:
                return None
        return None
    
    def _load_history(self):
        """Carga historial de propuestas"""
        for proposal_file in self.consensus_dir.glob("cons_*.json"):
            try:
                with open(proposal_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get("status") == "decided":
                    self.proposal_history.append(data["id"])
            except:
                pass
