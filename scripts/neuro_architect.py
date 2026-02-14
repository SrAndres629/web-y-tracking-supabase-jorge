"""
NEURO-VISION: NEURO-ARCHITECT v2.0
==================================
Graph management and mathematical impact analysis.
"""

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

import networkx as nx
from vision import get_vision

logger = logging.getLogger("neurovision.neuro")

@dataclass
class NeuronState:
    last_active: Optional[datetime] = None
    activation_level: float = 0.0
    error_rate: float = 0.0
    active_variables: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "activation_level": round(self.activation_level, 2),
            "error_rate": round(self.error_rate, 2),
            "active_variables": self.active_variables,
            "logs": self.logs[-5:]
        }

@dataclass
class ImpactPrediction:
    target_node: str
    direct_impact: List[str]
    ripple_effect: List[str]
    risk_score: float

    @property
    def affected_nodes(self) -> List[str]:
        return list(set(self.direct_impact + self.ripple_effect))

    def to_dict(self) -> dict:
        data = asdict(self)
        data["affected_nodes"] = self.affected_nodes
        return data

class NeuroArchitect:
    """The 'Brain' of the MCP - manages the knowledge graph."""

    def __init__(self, project_root: str):
        self._lock = Lock()
        self._graph: nx.DiGraph = nx.DiGraph()
        self._states: Dict[str, NeuronState] = {}
        self._project_root = Path(project_root).resolve()
        self._vision = get_vision(str(self._project_root))
        self._brain_path = self._project_root / ".ai" / "neuro_brain.json"
        self.refresh()

    def refresh(self):
        """Triggers a full re-scan of the project architecture."""
        try:
            logger.info(f"SCANNING ARCHITECTURE: {self._project_root}")
            nodes, edges = self._vision.scan_project()
            with self._lock:
                # Rebuild graph maintaining states where possible
                new_graph = self._vision.build_graph(nodes, edges)
                
                # Cleanup old states not in new graph
                current_nodes = set(new_graph.nodes())
                self._states = {n: s for n, s in self._states.items() if n in current_nodes}
                
                # Initialize new nodes
                for node in current_nodes:
                    if node not in self._states:
                        self._states[node] = NeuronState()
                
                self._graph = new_graph
            
            self.load_state()
            logger.info(f"GRAPH READY: {len(self._graph.nodes())} nodes, {len(self._graph.edges())} edges.")
        except Exception as e:
            logger.error(f"Refresh failed: {e}")

    def save_state(self):
        """Persists the dynamic state (activation, errors) to disk."""
        try:
            with self._lock:
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "states": {node: state.to_dict() for node, state in self._states.items()},
                }
            self._brain_path.parent.mkdir(parents=True, exist_ok=True)
            self._brain_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Save failed: {e}")

    def load_state(self):
        """Loads previous brain state to maintain continuity."""
        if not self._brain_path.exists(): return
        try:
            data = json.loads(self._brain_path.read_text(encoding="utf-8"))
            with self._lock:
                for node_id, s_dict in data.get("states", {}).items():
                    if node_id in self._states:
                        state = self._states[node_id]
                        if s_dict.get("last_active"):
                            state.last_active = datetime.fromisoformat(s_dict["last_active"])
                        state.activation_level = s_dict.get("activation_level", 0.0)
                        state.error_rate = s_dict.get("error_rate", 0.0)
                        state.active_variables = s_dict.get("active_variables", {})
        except Exception as e:
            logger.warning(f"Load failed: {e}")

    def ingest_telemetry(self, node_name: str, event_type: str, payload: Dict[str, Any]):
        """Injects real-time events into the graph neurons."""
        with self._lock:
            # Match node or create dynamic one
            match = node_name
            if node_name not in self._states:
                matches = [n for n in self._graph.nodes() if n.endswith(node_name)]
                match = matches[0] if matches else node_name
                
            if match not in self._states:
                self._graph.add_node(match, node_type="dynamic")
                self._states[match] = NeuronState()

            state = self._states[match]
            state.last_active = datetime.now()
            
            if event_type == "execution":
                state.activation_level = min(1.0, state.activation_level + 0.1)
            elif event_type == "error":
                state.error_rate = min(1.0, state.error_rate + 0.2)
                state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {payload.get('message', 'Err')}")
        
        self.save_state()

    def analyze_impact(self, target_node: str) -> ImpactPrediction:
        """Calculates the mathematical dependency tree for a node."""
        if target_node not in self._graph:
            matches = [n for n in self._graph.nodes() if n.endswith(target_node)]
            if not matches: return ImpactPrediction(target_node, [], [], 0.0)
            target_node = matches[0]

        # Direct depends (who uses me?)
        direct = list(self._graph.predecessors(target_node))
        
        # Deep ripple (transitive dependents)
        ripple = set()
        for d in direct:
            try:
                ripple.update(nx.ancestors(self._graph, d))
            except: pass
        
        ripple_list = [n for n in ripple if n not in direct and n != target_node]
        
        # Mathematical risk scoring: (direct * 15 pts) + (ripple * 5 pts)
        risk = (len(direct) * 15) + (len(ripple_list) * 5)
        
        return ImpactPrediction(target_node, direct, list(ripple_list)[:15], min(100.0, float(risk)))

    def get_brain_state(self) -> Dict[str, Any]:
        """Returns the full graph and neuron data for visualization."""
        nodes = []
        for n, attrs in self._graph.nodes(data=True):
            state = self._states.get(n, NeuronState())
            nodes.append({
                "id": n,
                "label": attrs.get("name", n),
                "type": attrs.get("node_type", "unknown"),
                "state": state.to_dict(),
                "weight": self._graph.in_degree(n) + 1
            })

        links = [{"source": u, "target": v, "type": attrs.get("edge_type")} 
                 for u, v, attrs in self._graph.edges(data=True)]

        return {
            "timestamp": datetime.now().isoformat(),
            "nodes": nodes,
            "links": links,
            "neuron_count": len(nodes),
            "synapse_count": len(links)
        }

    def export_neuro_map(self) -> Path:
        """Generates a standalone HTML 3D visualization."""
        data = self.get_brain_state()
        json_data = json.dumps(data)
        html = f"""
        <!DOCTYPE html><html><head>
        <script src="https://unpkg.com/3d-force-graph"></script>
        <style>body{{margin:0;background:#050505;color:#64ffda;font-family:monospace;}}
        #hud{{position:absolute;top:10px;left:10px;background:rgba(0,10,10,0.8);padding:15px;border:1px solid #64ffda;z-index:10;pointer-events:none;}}</style>
        </head><body>
        <div id="hud">
            <b>NEURO-VISION v2.0</b><br>
            Nodes: {data['neuron_count']}<br>
            Synapses: {data['synapse_count']}<br>
            STATUS: ACTIVE
        </div>
        <div id="graph"></div>
        <script>
            const Graph = ForceGraph3D()(document.getElementById('graph'))
                .graphData({json_data})
                .nodeAutoColorBy('type')
                .nodeVal('weight')
                .nodeLabel(n => `[${{n.type}}] ${{n.id}}`)
                .linkDirectionalParticles(2)
                .linkDirectionalParticleSpeed(d => 0.005);
        </script></body></html>
        """
        out = self._project_root / ".ai" / "visuals" / "neuro_map.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        return out

# Singleton factory
_instance = None
def get_neuro_architect(project_root: str):
    global _instance
    if _instance is None or _instance._project_root != Path(project_root).resolve():
        _instance = NeuroArchitect(project_root)
    return _instance
