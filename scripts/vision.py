"""
NEURO-VISION: VISION ENGINE v2.0
================================
Static analysis engine with AST parsing for internal project mapping.
"""

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import networkx as nx

logger = logging.getLogger("neurovision.vision")

@dataclass
class DependencyNode:
    id: str
    name: str
    node_type: str
    file_path: str

@dataclass
class DependencyEdge:
    source: str
    target: str
    edge_type: str

class VisionArchitect:
    """The 'Eyes' - performs static analysis to build the architectural graph."""

    def __init__(self, project_root: str):
        self._project_root = Path(project_root).resolve()
        # Ensure project exists
        if not self._project_root.exists():
            raise FileNotFoundError(f"Project root {project_root} not found.")

    def scan_project(self) -> Tuple[List[DependencyNode], List[DependencyEdge]]:
        """Scans the codebase and returns raw nodes and edges."""
        nodes: Dict[str, DependencyNode] = {}
        edges: List[DependencyEdge] = []
        
        # Optimized exclusions for WSL performance
        exclude = {".git", ".ai", "__pycache__", "node_modules", ".venv", "venv", "dist", "static", "assets"}

        for py_file in self._project_root.rglob("*.py"):
            # Check if any path component is in exclusions
            if any(p in py_file.parts for p in exclude):
                continue
            
            try:
                rel_path = str(py_file.relative_to(self._project_root))
                file_id = rel_path
                nodes[file_id] = DependencyNode(file_id, py_file.stem, "file", rel_path)
                
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    # 1. Imports -> Dependencies
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        # Capture more specific dependencies
                        modules = []
                        if isinstance(node, ast.Import):
                            modules = [n.name for n in node.names]
                        elif node.module:
                            modules = [node.module]
                        
                        for mod in modules:
                            # Normalize: app.database -> app/database.py
                            mod_path = mod.replace('.', '/')
                            if self._is_internal_module(mod_path):
                                edges.append(DependencyEdge(file_id, mod_path + ".py", "import"))
                            elif self._is_internal_module(mod.split('.')[0]):
                                # Fallback to top-level module
                                edges.append(DependencyEdge(file_id, mod.split('.')[0], "import"))
                    
                    # 2. Classes -> Internal Nodes
                    elif isinstance(node, ast.ClassDef):
                        class_id = f"{rel_path}:{node.name}"
                        nodes[class_id] = DependencyNode(class_id, node.name, "class", rel_path)
                        edges.append(DependencyEdge(file_id, class_id, "contains"))
                        
                        # Inheritance
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                edges.append(DependencyEdge(class_id, base.id, "inherits"))
                    
                    # 3. Functions -> Internal Nodes
                    elif isinstance(node, ast.FunctionDef):
                        func_id = f"{rel_path}:{node.name}"
                        nodes[func_id] = DependencyNode(func_id, node.name, "function", rel_path)
                        
                        # Detect if it's a method
                        parent_class = self._find_parent_class(node, tree)
                        if parent_class:
                           class_id = f"{rel_path}:{parent_class.name}"
                           edges.append(DependencyEdge(class_id, func_id, "method"))
                        else:
                           edges.append(DependencyEdge(file_id, func_id, "contains"))
                           
            except Exception as e:
                logger.debug(f"Scan error in {py_file.name}: {e}")
            
        return list(nodes.values()), edges

    def _is_internal_module(self, module_path: str) -> bool:
        # Check if module exists as a directory or a .py file
        return (self._project_root / module_path).is_dir() or (self._project_root / f"{module_path}.py").exists()

    def _find_parent_class(self, func_node: ast.FunctionDef, tree: ast.AST) -> Optional[ast.ClassDef]:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if func_node in node.body:
                    return node
        return None

    def build_graph(self, nodes: List[DependencyNode], edges: List[DependencyEdge]) -> nx.DiGraph:
        """Constructs a NetworkX directed graph with mathematical integrity."""
        G = nx.DiGraph()
        for n in nodes:
            G.add_node(n.id, name=n.name, node_type=n.node_type, file_path=n.file_path)
        
        for e in edges:
            if G.has_node(e.source) and G.has_node(e.target):
                G.add_edge(e.source, e.target, edge_type=e.edge_type)
            elif G.has_node(e.source):
                # Handle external dependencies as distinct nodes
                if not G.has_node(e.target):
                    G.add_node(e.target, node_type="module", name=e.target)
                G.add_edge(e.source, e.target, edge_type=e.edge_type)
        return G

# Singleton factory
_instance = None
def get_vision(project_root: str):
    global _instance
    if _instance is None or _instance._project_root != Path(project_root).resolve():
        _instance = VisionArchitect(project_root)
    return _instance
