"""
NEXUS-7: Neural Memory System
═══════════════════════════════════════════════════════════════════════════════
Sistema de memoria compartida para los 4 cerebros de la colmena.

Características:
- Memoria de corto plazo (working memory): Lo que está procesando ahora
- Memoria de largo plazo (episodic): Historial de decisiones
- Memoria semántica: Conocimiento estructurado del proyecto
- Memoria procedimental: Patrones de resolución aprendidos

Los 4 cerebros leen y escriben en la misma memoria. No hay "posesión" de datos.
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading
from collections import deque


class MemoryType(Enum):
    """Tipos de memoria neural"""
    WORKING = "working"      # Corto plazo - activa ahora
    EPISODIC = "episodic"    # Historial de eventos/decisiones
    SEMANTIC = "semantic"    # Conocimiento estructurado
    PROCEDURAL = "procedural" # Patrones aprendidos
    CONSENSUS = "consensus"  # Decisiones colectivas


class AccessPattern(Enum):
    """Patrones de acceso a memoria"""
    READ = "read"
    WRITE = "write"
    MODIFY = "modify"
    DELETE = "delete"


@dataclass
class MemoryFragment:
    """
    Fragmento de memoria neural.
    Cada pensamiento, decisión o conocimiento es un fragmento.
    """
    id: str
    type: str  # MemoryType
    content: Any
    creator: str  # Qué cerebro lo creó
    timestamp: float
    ttl: Optional[int] = None  # Time-to-live en segundos
    importance: float = 1.0  # 0.0 - 10.0
    associations: List[str] = field(default_factory=list)  # IDs de fragmentos relacionados
    access_count: int = 0
    last_accessed: Optional[float] = None
    brain_signature: Dict[str, Any] = field(default_factory=dict)  # Metadatos del cerebro
    
    def is_expired(self) -> bool:
        """Verifica si el fragmento expiró"""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl
    
    def touch(self):
        """Actualiza contador de acceso"""
        self.access_count += 1
        self.last_accessed = time.time()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "creator": self.creator,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "importance": self.importance,
            "associations": self.associations,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "brain_signature": self.brain_signature
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MemoryFragment":
        return cls(**data)


@dataclass
class WorkingMemorySlot:
    """
    Slot de memoria de trabajo (corto plazo).
    Similar a la RAM de un cerebro - muy rápida, volátil.
    """
    fragment_id: str
    loaded_at: float
    priority: float
    lock_holder: Optional[str] = None  # Qué cerebro lo está usando ahora
    lock_expires: Optional[float] = None
    
    def is_locked(self) -> bool:
        if self.lock_holder is None:
            return False
        if self.lock_expires and time.time() > self.lock_expires:
            return False
        return True


class NeuralMemory:
    """
    Sistema de memoria neural compartida.
    
    Analogía: Es como si los 4 cerebros compartieran el mismo córtex cerebral.
    Pueden leer pensamientos entre sí en tiempo real.
    
    Características:
    - Memoria de trabajo (RAM): ~100 slots
    - Memoria episódica: Persistente en disco
    - Memoria semántica: Grafo de conocimiento
    - Garbage collection automático
    """
    
    def __init__(self, memory_dir: str = ".ai/memory/core/neural"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Memoria de trabajo (corto plazo) - máximo 100 fragmentos activos
        self.working_memory: Dict[str, WorkingMemorySlot] = {}
        self.working_memory_lock = threading.RLock()
        self.MAX_WORKING_MEMORY = 100
        
        # Cache en memoria para acceso rápido
        self._cache: Dict[str, MemoryFragment] = {}
        self._cache_lock = threading.RLock()
        self.CACHE_SIZE = 1000
        
        # Estadísticas
        self.stats = {
            "reads": 0,
            "writes": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Cargar memoria persistente
        self._load_persistent_memory()
    
    def _generate_id(self, content: Any, creator: str) -> str:
        """Genera ID único para fragmento de memoria"""
        content_hash = hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()[:16]
        timestamp = int(time.time())
        return f"mem_{creator}_{timestamp}_{content_hash}"
    
    def _load_persistent_memory(self):
        """Carga memoria episódica y semántica de disco"""
        for memory_file in self.memory_dir.glob("memory_*.json"):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    fragment = MemoryFragment.from_dict(data)
                    if not fragment.is_expired():
                        with self._cache_lock:
                            self._cache[fragment.id] = fragment
            except Exception as e:
                print(f"Error loading memory {memory_file}: {e}")
    
    def store(self, 
              content: Any, 
              memory_type: MemoryType,
              creator: str,
              importance: float = 1.0,
              ttl: Optional[int] = None,
              associations: Optional[List[str]] = None,
              brain_signature: Optional[Dict] = None) -> str:
        """
        Almacena un fragmento en memoria neural.
        
        Args:
            content: Contenido a almacenar
            memory_type: Tipo de memoria
            creator: Cerebro que crea el fragmento
            importance: Importancia (0-10)
            ttl: Tiempo de vida en segundos (None = forever)
            associations: IDs de fragmentos relacionados
            brain_signature: Metadatos adicionales
        
        Returns:
            ID del fragmento creado
        """
        fragment_id = self._generate_id(content, creator)
        
        fragment = MemoryFragment(
            id=fragment_id,
            type=memory_type.value,
            content=content,
            creator=creator,
            timestamp=time.time(),
            ttl=ttl,
            importance=importance,
            associations=associations or [],
            brain_signature=brain_signature or {}
        )
        
        # Guardar en cache
        with self._cache_lock:
            self._cache[fragment_id] = fragment
            self._evict_if_necessary()
        
        # Si es episódica o semántica, persistir
        if memory_type in [MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.CONSENSUS]:
            self._persist_fragment(fragment)
        
        # Si es de trabajo, agregar a working memory
        if memory_type == MemoryType.WORKING:
            self._load_to_working_memory(fragment_id, importance)
        
        self.stats["writes"] += 1
        return fragment_id
    
    def retrieve(self, fragment_id: str, accessor: str) -> Optional[MemoryFragment]:
        """
        Recupera un fragmento de memoria.
        
        Args:
            fragment_id: ID del fragmento
            accessor: Cerebro que accede (para logging)
        
        Returns:
            MemoryFragment o None si no existe/expiró
        """
        # Intentar cache primero
        with self._cache_lock:
            fragment = self._cache.get(fragment_id)
        
        if fragment:
            if fragment.is_expired():
                return None
            fragment.touch()
            self.stats["cache_hits"] += 1
            return fragment
        
        # Intentar cargar de disco
        fragment = self._load_from_disk(fragment_id)
        if fragment:
            with self._cache_lock:
                self._cache[fragment_id] = fragment
            fragment.touch()
            self.stats["cache_misses"] += 1
            return fragment
        
        return None
    
    def query(self, 
              memory_type: Optional[MemoryType] = None,
              creator: Optional[str] = None,
              min_importance: float = 0.0,
              pattern: Optional[str] = None,
              limit: int = 10) -> List[MemoryFragment]:
        """
        Consulta avanzada de memoria.
        
        Args:
            memory_type: Filtrar por tipo
            creator: Filtrar por cerebro creador
            min_importance: Importancia mínima
            pattern: Patrón de búsqueda en contenido
            limit: Máximo de resultados
        
        Returns:
            Lista de fragmentos ordenados por relevancia
        """
        results = []
        
        with self._cache_lock:
            fragments = list(self._cache.values())
        
        for fragment in fragments:
            if fragment.is_expired():
                continue
            
            if memory_type and fragment.type != memory_type.value:
                continue
            
            if creator and fragment.creator != creator:
                continue
            
            if fragment.importance < min_importance:
                continue
            
            if pattern and pattern.lower() not in str(fragment.content).lower():
                continue
            
            results.append(fragment)
        
        # Ordenar por importancia y recencia
        results.sort(key=lambda f: (f.importance, f.timestamp), reverse=True)
        return results[:limit]
    
    def acquire_lock(self, fragment_id: str, brain: str, duration: int = 60) -> bool:
        """
        Adquiere lock sobre un fragmento de memoria.
        Esto permite que un cerebro "piense" con ese fragmento sin interferencia.
        
        Args:
            fragment_id: ID del fragmento
            brain: Cerebro que solicita el lock
            duration: Duración del lock en segundos
        
        Returns:
            True si se adquirió el lock
        """
        with self.working_memory_lock:
            slot = self.working_memory.get(fragment_id)
            if not slot:
                return False
            
            if slot.is_locked() and slot.lock_holder != brain:
                return False
            
            slot.lock_holder = brain
            slot.lock_expires = time.time() + duration
            return True
    
    def release_lock(self, fragment_id: str, brain: str) -> bool:
        """Libera un lock"""
        with self.working_memory_lock:
            slot = self.working_memory.get(fragment_id)
            if slot and slot.lock_holder == brain:
                slot.lock_holder = None
                slot.lock_expires = None
                return True
            return False
    
    def get_working_memory(self, brain: Optional[str] = None) -> List[MemoryFragment]:
        """
        Obtiene los fragmentos en memoria de trabajo.
        
        Args:
            brain: Si se especifica, solo fragmentos que no están lockeados
                   por otros cerebros
        """
        fragments = []
        
        with self.working_memory_lock:
            slots = list(self.working_memory.values())
        
        for slot in slots:
            if brain and slot.is_locked() and slot.lock_holder != brain:
                continue
            
            fragment = self.retrieve(slot.fragment_id, "system")
            if fragment:
                fragments.append(fragment)
        
        return fragments
    
    def create_association(self, fragment_id_1: str, fragment_id_2: str):
        """Crea asociación bidireccional entre fragmentos"""
        f1 = self.retrieve(fragment_id_1, "system")
        f2 = self.retrieve(fragment_id_2, "system")
        
        if f1 and f2:
            if fragment_id_2 not in f1.associations:
                f1.associations.append(fragment_id_2)
            if fragment_id_1 not in f2.associations:
                f2.associations.append(fragment_id_1)
    
    def consolidate(self):
        """
        Consolidación de memoria (类似 sueño en cerebros biológicos).
        - Mueve memoria de trabajo a episódica si es importante
        - Elimina fragmentos expirados
        - Optimiza asociaciones
        """
        # Limpiar working memory
        with self.working_memory_lock:
            to_remove = []
            for frag_id, slot in self.working_memory.items():
                fragment = self.retrieve(frag_id, "system")
                if not fragment or fragment.is_expired():
                    to_remove.append(frag_id)
                elif fragment.importance > 7.0 and fragment.access_count > 3:
                    # Promover a episódica
                    fragment.type = MemoryType.EPISODIC.value
                    self._persist_fragment(fragment)
            
            for frag_id in to_remove:
                del self.working_memory[frag_id]
        
        # Limpiar cache
        with self._cache_lock:
            expired = [fid for fid, f in self._cache.items() if f.is_expired()]
            for fid in expired:
                del self._cache[fid]
    
    def _load_to_working_memory(self, fragment_id: str, priority: float):
        """Carga un fragmento a memoria de trabajo"""
        with self.working_memory_lock:
            # Si está llena, eliminar el de menor prioridad
            if len(self.working_memory) >= self.MAX_WORKING_MEMORY:
                oldest = min(self.working_memory.values(), key=lambda s: s.priority)
                del self.working_memory[oldest.fragment_id]
            
            self.working_memory[fragment_id] = WorkingMemorySlot(
                fragment_id=fragment_id,
                loaded_at=time.time(),
                priority=priority
            )
    
    def _persist_fragment(self, fragment: MemoryFragment):
        """Persiste fragmento a disco"""
        memory_file = self.memory_dir / f"memory_{fragment.id}.json"
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(fragment.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _load_from_disk(self, fragment_id: str) -> Optional[MemoryFragment]:
        """Carga fragmento desde disco"""
        memory_file = self.memory_dir / f"memory_{fragment_id}.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return MemoryFragment.from_dict(data)
            except:
                return None
        return None
    
    def _evict_if_necessary(self):
        """Elimina entradas de cache si excede tamaño"""
        if len(self._cache) > self.CACHE_SIZE:
            # Eliminar los menos accedidos
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1].access_count)
            to_remove = len(self._cache) - self.CACHE_SIZE + 100  # Eliminar 100 extras
            for fragment_id, _ in sorted_items[:to_remove]:
                del self._cache[fragment_id]
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas de uso de memoria"""
        return {
            **self.stats,
            "working_memory_size": len(self.working_memory),
            "cache_size": len(self._cache),
            "persistent_files": len(list(self.memory_dir.glob("memory_*.json")))
        }
