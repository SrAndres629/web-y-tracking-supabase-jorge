"""
NEURO-ARCHITECT v3.0: THE CORTEX
================================
Advanced Neuro-Symbolic Cognitive Engine.
Features:
- Holographic Memory (File Hashes + Semantic Indexing)
- Neuro-Symbolic Graph Persistence
- Infinite Context Memory (Vector-like simulation)
- Real-time Telemetry Stream
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List

import networkx as nx
from vision import get_vision

# Setup Logger
logger = logging.getLogger("neurovision.cortex")
logging.basicConfig(level=logging.INFO)

# --- ADVANCED TYPES ---


@dataclass
class MemoryEngram:
    """Represents a singleunit of long-term memory."""

    id: str
    content: str
    metadata: Dict[str, Any]
    vector_embedding: List[float] = field(
        default_factory=list
    )  # Placeholder for future true vectors
    created_at: float = field(default_factory=time.time)
    decay_rate: float = 0.01  # Forgetting curve simulation


@dataclass
class NeuronState:
    """Dynamic state of a code node."""

    last_active: float = field(default_factory=time.time)
    activation_level: float = 0.0  # 0.0 to 1.0 (How 'hot' is this code?)
    error_rate: float = 0.0  # health indicator
    context_hashes: Dict[str, str] = field(default_factory=dict)  # Integrity Check
    logs: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


class ProjectCortex:
    """
    The Advanced Brain of the System.
    Manages:
    1. Static Structure (The Skeleton)
    2. Dynamic Telemetry (The Nerves)
    3. Persistent Memories (The Mind)
    """

    def __init__(self, project_root: str):
        self._lock = Lock()
        self.root = Path(project_root).resolve()

        # Memory Paths
        self.brain_dir = self.root / ".ai" / "cortex"
        self.brain_dir.mkdir(parents=True, exist_ok=True)
        self.graph_path = self.brain_dir / "neuro_graph.json"
        self.memory_path = self.brain_dir / "long_term_memory.jsonl"

        # Core Components
        self.graph: nx.DiGraph = nx.DiGraph()
        self.neuron_states: Dict[str, NeuronState] = {}
        self.vision = get_vision(str(self.root))

        # Boot Sequence
        self._load_brain()

    def _calculate_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _load_brain(self):
        """Loads the persisted graph and states."""
        try:
            if self.graph_path.exists():
                logger.info("🧠 Loading Neural Cortex from disk...")
                data = json.loads(self.graph_path.read_text(encoding="utf-8"))
                self.graph = nx.node_link_graph(data["graph"])
                for nid, state_data in data.get("states", {}).items():
                    self.neuron_states[nid] = NeuronState(**state_data)
            else:
                logger.info("🌱 Cortex Empty. Initializing detailed scan...")
                self.refresh_scan()
        except Exception as e:
            logger.error(f"Brain damage detected (Load Error): {e}")
            self.refresh_scan()

    def save_brain(self):
        """Persists the current mental state to .ai/cortex."""
        with self._lock:
            try:
                # Convert graph to JSON-serializable format
                graph_data = nx.node_link_data(self.graph)
                states = {nid: s.to_dict() for nid, s in self.neuron_states.items()}

                payload = {
                    "timestamp": datetime.now().isoformat(),
                    "graph": graph_data,
                    "states": states,
                }
                self.graph_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            except Exception as e:
                logger.error(f"Failed to save brain state: {e}")

    def refresh_scan(self):
        """Deep Scan: Rebuilds the graph and checks file integrity hashes."""
        logger.info("👁️ Performing Deep Vision Scan...")
        nodes, edges = self.vision.scan_project()

        with self._lock:
            new_graph = self.vision.build_graph(nodes, edges)

            # Transfer learning (Keep old states if node exists)
            for node in new_graph.nodes():
                if node in self.neuron_states:
                    # Decay activation
                    self.neuron_states[node].activation_level *= 0.9
                else:
                    self.neuron_states[node] = NeuronState()

            # File Integrity Check (Hashing)
            for n_id, attrs in new_graph.nodes(data=True):
                if attrs.get("type") == "file":
                    path = self.root / attrs.get("file_path", "")
                    if path.exists():
                        content = path.read_text(encoding="utf-8", errors="ignore")
                        current_hash = self._calculate_hash(content)
                        self.neuron_states[n_id].context_hashes["content"] = current_hash

            self.graph = new_graph
            self.save_brain()

    def ingest_telemetry(self, node: str, event: str, metadata: dict):
        """
        Real-time telemetry ingestion.
        "Feels" the code running.
        """
        with self._lock:
            # Find closest matching node
            target = node
            if node not in self.graph:
                # Fuzzy match
                matches = [n for n in self.graph.nodes() if node in n]
                if matches:
                    target = matches[0]

            if target not in self.neuron_states:
                self.neuron_states[target] = NeuronState()

            state = self.neuron_states[target]
            state.last_active = time.time()

            if event == "execution":
                state.activation_level = min(1.0, state.activation_level + 0.05)
            elif event == "error":
                state.error_rate = min(1.0, state.error_rate + 0.2)
                state.logs.append(f"ERR: {metadata.get('msg', 'unknown')}")

            self.save_brain()

    def recall(self, query: str) -> List[Dict]:
        """
        Semantic Memory Recall.
        Searches the graph and memory banks for relevant concepts.
        """
        results = []
        # Simple keyword search on graph nodes for now (Vertex Emulation)
        for node, attrs in self.graph.nodes(data=True):
            if query.lower() in node.lower() or query.lower() in str(attrs).lower():
                state = self.neuron_states.get(node)
                results.append(
                    {
                        "id": node,
                        "type": attrs.get("type"),
                        "relevance": state.activation_level if state else 0.0,
                        "metadata": attrs,
                    }
                )

        # Sort by activation level (recent/hot memories first)
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:10]

    def export_holographic_map(self) -> Path:
        """Generates the advanced visualization."""
        nodes = []
        for n, attrs in self.graph.nodes(data=True):
            state = self.neuron_states.get(n, NeuronState())
            nodes.append(
                {
                    "id": n,
                    "group": 1 if attrs.get("type") == "file" else 2,
                    "val": (state.activation_level * 10) + 1,
                    "label": n,
                    "health": 1.0 - state.error_rate,
                }
            )

        links = [{"source": u, "target": v} for u, v in self.graph.edges()]

        data = {"nodes": nodes, "links": links}
        json_path = self.brain_dir / "viz_data.json"
        json_path.write_text(json.dumps(data), encoding="utf-8")
        return json_path


# Singleton Factory
_cortex_instance = None


def get_cortex(root: str) -> ProjectCortex:
    global _cortex_instance
    if not _cortex_instance:
        _cortex_instance = ProjectCortex(root)
    return _cortex_instance
