"""
NEXUS-7: Auto-Acceptance Protocol
═══════════════════════════════════════════════════════════════════════════════
Protocolo de auto-aceptación de peticiones para la colmena neural.

Permite que los 4 cerebros auto-acepten peticiones basándose en:
- Confianza histórica del cerebro en el dominio
- Impacto potencial de la decisión
- Complejidad de la tarea
- Consenso implícito previo

Niveles de auto-aceptación:
- FULL: El cerebro puede actuar sin consultar (tareas rutinarias)
- CONDITIONAL: Auto-acepta con condiciones/notificaciones
- SUPERVISED: Requiere validación de otro cerebro
- MANUAL: Requiere aprobación humana

Este protocolo permite que la colmena opere autónomamente
imitando equipos de investigación de élite.
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AcceptanceLevel(Enum):
    """Niveles de auto-aceptación"""
    FULL = "full"              # Actuar sin consultar
    CONDITIONAL = "conditional"  # Auto-aceptar con notificación
    SUPERVISED = "supervised"   # Validación de otro cerebro requerida
    MANUAL = "manual"          # Aprobación humana requerida


class TaskCategory(Enum):
    """Categorías de tareas"""
    REFACTOR = "refactor"          # Refactorización de código
    BUGFIX = "bugfix"              # Corrección de bugs
    ARCHITECTURE = "architecture"  # Cambios arquitectónicos
    SECURITY = "security"          # Seguridad
    OPTIMIZATION = "optimization"  # Optimización
    DOCUMENTATION = "documentation" # Documentación
    TEST = "test"                  # Tests
    DEPLOY = "deploy"              # Despliegue


@dataclass
class AcceptanceThreshold:
    """Umbral de auto-aceptación para un cerebro en una categoría"""
    brain: str
    category: str
    level: str  # AcceptanceLevel
    min_confidence: float  # Confianza mínima requerida (0-1)
    max_impact: str  # Impacto máximo permitido (low, medium, high, critical)
    success_rate: float = 0.0  # Tasa de éxito histórica
    total_tasks: int = 0
    successful_tasks: int = 0
    
    def update_success_rate(self, success: bool):
        """Actualiza tasa de éxito con nuevo resultado"""
        self.total_tasks += 1
        if success:
            self.successful_tasks += 1
        self.success_rate = self.successful_tasks / self.total_tasks


@dataclass
class AutoDecision:
    """Decisión auto-aceptada"""
    id: str
    brain: str
    category: str
    action: str
    level: str
    confidence: float
    impact: str
    timestamp: float
    justification: str
    conditions: List[str]
    executed: bool = False
    execution_time: Optional[float] = None
    result: Optional[str] = None


class AutoAcceptanceProtocol:
    """
    Protocolo de auto-aceptación para la colmena neural.
    
    Analogía: Es como la autonomía que tienen los miembros de un
    equipo de investigación de élite. Saben cuándo pueden actuar
    solos y cuándo necesitan consultar al equipo.
    
    Features:
    - Perfiles de auto-aceptación por cerebro y categoría
    - Learning de tasas de éxito
    - Escalación automática si hay dudas
    - Logging completo de decisiones auto-aceptadas
    """
    
    # Impactos permitidos por nivel
    IMPACT_HIERARCHY = {
        "low": 0,
        "medium": 1,
        "high": 2,
        "critical": 3
    }
    
    def __init__(self, config_path: str = ".ai/memory/core/auto_acceptance.json"):
        self.config_path = Path(config_path)
        self.thresholds: Dict[str, AcceptanceThreshold] = {}
        self.decision_history: List[AutoDecision] = []
        self.pending_notifications: List[AutoDecision] = []
        
        # Callbacks
        self.on_full_auto_accept: Optional[Callable] = None
        self.on_conditional_accept: Optional[Callable] = None
        self.on_supervision_required: Optional[Callable] = None
        
        self._load_thresholds()
    
    def _load_thresholds(self):
        """Carga umbrales de auto-aceptación"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for key, threshold_data in data.get("thresholds", {}).items():
                self.thresholds[key] = AcceptanceThreshold(**threshold_data)
        else:
            # Crear thresholds por defecto
            self._initialize_default_thresholds()
    
    def _initialize_default_thresholds(self):
        """Inicializa thresholds por defecto para los 4 cerebros"""
        default_configs = [
            # Codex: Experto en implementación
            ("codex", TaskCategory.REFACTOR.value, AcceptanceLevel.CONDITIONAL, 0.8, "high"),
            ("codex", TaskCategory.BUGFIX.value, AcceptanceLevel.FULL, 0.7, "medium"),
            ("codex", TaskCategory.OPTIMIZATION.value, AcceptanceLevel.CONDITIONAL, 0.8, "high"),
            ("codex", TaskCategory.TEST.value, AcceptanceLevel.FULL, 0.6, "medium"),
            
            # Kimi: Experto en arquitectura
            ("kimi", TaskCategory.ARCHITECTURE.value, AcceptanceLevel.SUPERVISED, 0.9, "critical"),
            ("kimi", TaskCategory.REFACTOR.value, AcceptanceLevel.CONDITIONAL, 0.8, "high"),
            ("kimi", TaskCategory.DOCUMENTATION.value, AcceptanceLevel.FULL, 0.6, "low"),
            
            # Gemini: Experto en seguridad
            ("gemini", TaskCategory.SECURITY.value, AcceptanceLevel.SUPERVISED, 0.95, "critical"),
            ("gemini", TaskCategory.ARCHITECTURE.value, AcceptanceLevel.CONDITIONAL, 0.85, "high"),
            ("gemini", TaskCategory.BUGFIX.value, AcceptanceLevel.CONDITIONAL, 0.75, "high"),
            
            # Antigravity: Orquestador
            ("antigravity", TaskCategory.DEPLOY.value, AcceptanceLevel.SUPERVISED, 0.9, "critical"),
            ("antigravity", TaskCategory.ARCHITECTURE.value, AcceptanceLevel.CONDITIONAL, 0.8, "high"),
        ]
        
        for brain, category, level, confidence, impact in default_configs:
            key = f"{brain}:{category}"
            self.thresholds[key] = AcceptanceThreshold(
                brain=brain,
                category=category,
                level=level.value,
                min_confidence=confidence,
                max_impact=impact
            )
        
        self._save_thresholds()
    
    def _save_thresholds(self):
        """Guarda umbrales a disco"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "thresholds": {
                key: {
                    "brain": t.brain,
                    "category": t.category,
                    "level": t.level,
                    "min_confidence": t.min_confidence,
                    "max_impact": t.max_impact,
                    "success_rate": t.success_rate,
                    "total_tasks": t.total_tasks,
                    "successful_tasks": t.successful_tasks
                }
                for key, t in self.thresholds.items()
            }
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def evaluate(self,
                 brain: str,
                 category: str,
                 action: str,
                 confidence: float,
                 impact: str,
                 justification: str,
                 conditions: Optional[List[str]] = None) -> AutoDecision:
        """
        Evalúa si una acción puede ser auto-aceptada.
        
        Args:
            brain: Cerebro que propone la acción
            category: Categoría de la tarea
            action: Descripción de la acción
            confidence: Confianza del cerebro (0-1)
            impact: Impacto potencial (low, medium, high, critical)
            justification: Justificación de la decisión
            conditions: Condiciones adicionales
        
        Returns:
            AutoDecision con el nivel de aceptación determinado
        """
        key = f"{brain}:{category}"
        threshold = self.thresholds.get(key)
        
        if not threshold:
            # Sin threshold definido = requiere supervisión
            decision = AutoDecision(
                id=f"auto_{int(time.time())}_{brain}",
                brain=brain,
                category=category,
                action=action,
                level=AcceptanceLevel.SUPERVISED.value,
                confidence=confidence,
                impact=impact,
                timestamp=time.time(),
                justification="No threshold defined - requires supervision",
                conditions=conditions or []
            )
        else:
            # Evaluar contra threshold
            level = self._determine_acceptance_level(threshold, confidence, impact)
            
            decision = AutoDecision(
                id=f"auto_{int(time.time())}_{brain}",
                brain=brain,
                category=category,
                action=action,
                level=level.value,
                confidence=confidence,
                impact=impact,
                timestamp=time.time(),
                justification=justification,
                conditions=conditions or []
            )
        
        # Notificar según nivel
        self._handle_decision(decision)
        
        # Guardar en historial
        self.decision_history.append(decision)
        
        return decision
    
    def _determine_acceptance_level(self,
                                    threshold: AcceptanceThreshold,
                                    confidence: float,
                                    impact: str) -> AcceptanceLevel:
        """Determina nivel de aceptación basado en threshold"""
        # Verificar confianza mínima
        if confidence < threshold.min_confidence:
            return AcceptanceLevel.SUPERVISED
        
        # Verificar impacto máximo permitido
        impact_level = self.IMPACT_HIERARCHY.get(impact, 0)
        max_impact_level = self.IMPACT_HIERARCHY.get(threshold.max_impact, 3)
        
        if impact_level > max_impact_level:
            # Impacto mayor al permitido = escalar
            if threshold.level == AcceptanceLevel.FULL.value:
                return AcceptanceLevel.CONDITIONAL
            elif threshold.level == AcceptanceLevel.CONDITIONAL.value:
                return AcceptanceLevel.SUPERVISED
            else:
                return AcceptanceLevel.MANUAL
        
        # Ajustar por tasa de éxito histórica
        if threshold.success_rate > 0.9 and threshold.total_tasks > 10:
            # Cerebro con excelente track record = más autonomía
            if threshold.level == AcceptanceLevel.CONDITIONAL.value:
                return AcceptanceLevel.FULL
        
        return AcceptanceLevel(threshold.level)
    
    def _handle_decision(self, decision: AutoDecision):
        """Maneja la decisión según su nivel"""
        if decision.level == AcceptanceLevel.FULL.value:
            # Ejecutar inmediatamente
            if self.on_full_auto_accept:
                self.on_full_auto_accept(decision)
        
        elif decision.level == AcceptanceLevel.CONDITIONAL.value:
            # Guardar para notificación
            self.pending_notifications.append(decision)
            if self.on_conditional_accept:
                self.on_conditional_accept(decision)
        
        elif decision.level == AcceptanceLevel.SUPERVISED.value:
            # Requiere supervisión
            if self.on_supervision_required:
                self.on_supervision_required(decision)
    
    def record_execution(self, decision_id: str, success: bool, result: str):
        """Registra resultado de ejecución para learning"""
        # Buscar decisión
        decision = None
        for d in self.decision_history:
            if d.id == decision_id:
                decision = d
                break
        
        if not decision:
            return
        
        decision.executed = True
        decision.execution_time = time.time()
        decision.result = result
        
        # Actualizar threshold
        key = f"{decision.brain}:{decision.category}"
        threshold = self.thresholds.get(key)
        if threshold:
            threshold.update_success_rate(success)
            self._save_thresholds()
    
    def get_brain_autonomy_score(self, brain: str) -> float:
        """
        Calcula score de autonomía de un cerebro.
        0 = siempre requiere supervisión
        1 = totalmente autónomo
        """
        brain_thresholds = [
            t for key, t in self.thresholds.items()
            if key.startswith(f"{brain}:")
        ]
        
        if not brain_thresholds:
            return 0.0
        
        # Calcular basado en niveles y tasas de éxito
        scores = []
        for t in brain_thresholds:
            level_score = {
                AcceptanceLevel.FULL.value: 1.0,
                AcceptanceLevel.CONDITIONAL.value: 0.7,
                AcceptanceLevel.SUPERVISED.value: 0.3,
                AcceptanceLevel.MANUAL.value: 0.0
            }.get(t.level, 0.0)
            
            # Ajustar por tasa de éxito
            adjusted_score = level_score * (0.5 + 0.5 * t.success_rate)
            scores.append(adjusted_score)
        
        return sum(scores) / len(scores)
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del protocolo"""
        total_decisions = len(self.decision_history)
        executed = sum(1 for d in self.decision_history if d.executed)
        successful = sum(1 for d in self.decision_history 
                        if d.executed and d.result == "success")
        
        return {
            "total_decisions": total_decisions,
            "executed": executed,
            "successful": successful,
            "pending_notifications": len(self.pending_notifications),
            "brains": list(set(t.brain for t in self.thresholds.values()))
        }
