"""
Visual Cortex V2.0 — Cognitive Code Intelligence Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The Central Nervous System for Code Vision.

Features:
  • Proper AST hierarchy (file → class → method)
  • Smart import resolution (sys.path-aware, relative imports, __init__.py chains)
  • Code quality metrics (cyclomatic + cognitive complexity)
  • Temporal memory (scan history + node snapshots)
  • Smell detection (god class, long method, deep nesting, circular imports)
  • Transitive impact analysis (N-depth dependency chains)
"""

import os
import ast
import sqlite3
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime

try:
    from .analyzers import (
        ComplexityAnalyzer, SmellDetector, RiskScorer,
        CircularDependencyDetector, MetricsResult, CodeSmell
    )
except ImportError:
    from analyzers import (
        ComplexityAnalyzer, SmellDetector, RiskScorer,
        CircularDependencyDetector, MetricsResult, CodeSmell
    )

# ─────────────────────────────────────────────────────────────────────────────
# Logger
# ─────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger("visual_cortex")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    ))
    logger.addHandler(handler)


# ─────────────────────────────────────────────────────────────────────────────
# SKIP DIRECTORIES
# ─────────────────────────────────────────────────────────────────────────────
SKIP_DIRS = {
    '.git', '.svn', '__pycache__', 'node_modules', 'venv',
    '.venv', 'env', '.env', '.tox', '.mypy_cache', '.pytest_cache',
    'dist', 'build', 'egg-info', '.ai',  # Skip self
}


class VisualCortex:
    """
    The Central Nervous System for Code Vision.
    Maintains a persistent graph of the codebase in SQLite with
    temporal memory, code metrics, and real-time telemetry support.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = Path(__file__).parent
            db_path = str(base_dir / "cortex.db")

        self.db_path = db_path
        self._init_db()
        self._subscribers: List[Any] = []  # WebSocket event subscribers

    # ═══════════════════════════════════════════════════════════════════════
    # DATABASE INITIALIZATION
    # ═══════════════════════════════════════════════════════════════════════

    def _init_db(self):
        """Initialize the database with the V2.0 schema."""
        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found at {schema_path}")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            with open(schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

    def _get_conn(self) -> sqlite3.Connection:
        """Get a database connection with dict row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    # ═══════════════════════════════════════════════════════════════════════
    # FULL PROJECT SCAN
    # ═══════════════════════════════════════════════════════════════════════

    def scan_project(self, root_dir: str) -> Dict[str, Any]:
        """
        Scans the entire project directory and rebuilds the graph.
        Returns scan statistics.
        """
        root_path = Path(root_dir).resolve()
        if not root_path.exists():
            raise ValueError(f"Root directory {root_dir} does not exist")

        start_time = time.time()
        logger.info(f"🧠 Visual Cortex V2.0 scanning: {root_path}")

        # Create scan history entry
        scan_id = self._create_scan_entry(str(root_path))

        # Collect all nodes and edges
        all_nodes: List[Dict] = []
        all_edges: List[Dict] = []
        all_metrics: List[Dict] = []
        all_smells: List[CodeSmell] = []
        file_count = 0

        # Build import adjacency map for circular dependency detection
        import_adjacency: Dict[str, Set[str]] = {}

        for root, dirs, files in os.walk(str(root_path)):
            # Skip hidden dirs and known non-source dirs
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]

            for file_name in files:
                if not file_name.endswith(".py"):
                    continue

                full_path = Path(root) / file_name
                rel_path = full_path.relative_to(root_path).as_posix()
                file_count += 1

                try:
                    nodes, edges, metrics, smells = self._scan_file(
                        full_path, rel_path, str(root_path)
                    )
                    all_nodes.extend(nodes)
                    all_edges.extend(edges)
                    all_metrics.extend(metrics)
                    all_smells.extend(smells)

                    # Build import adjacency
                    file_imports = {
                        e["target"] for e in edges
                        if e["type"] == "imports" and e["source"] == rel_path
                    }
                    if file_imports:
                        import_adjacency[rel_path] = file_imports

                except Exception as e:
                    logger.error(f"Failed to scan {rel_path}: {e}")

        # Detect circular dependencies
        cycles = CircularDependencyDetector.find_cycles(import_adjacency)
        for cycle in cycles:
            for node_id in cycle[:-1]:  # Last is repeat of first
                all_smells.append(CodeSmell(
                    node_id=node_id,
                    smell_type="circular_import",
                    severity="critical",
                    description=f"Circular import chain: {' → '.join(cycle)}"
                ))

        # Bulk save everything in a transaction
        self._bulk_save(all_nodes, all_edges, all_metrics, all_smells)

        # Compute coupling metrics post-save
        self._compute_coupling_metrics()

        # Compute risk scores
        self._compute_risk_scores()

        # Record scan completion
        duration_ms = int((time.time() - start_time) * 1000)
        self._complete_scan_entry(
            scan_id, duration_ms,
            len(all_nodes), len(all_edges), file_count, len(all_smells)
        )

        # Create node snapshots for temporal tracking
        self._create_snapshots(scan_id, all_nodes)

        stats = {
            "scan_id": scan_id,
            "duration_ms": duration_ms,
            "total_nodes": len(all_nodes),
            "total_edges": len(all_edges),
            "total_files": file_count,
            "total_smells": len(all_smells),
            "circular_imports": len(cycles),
        }
        logger.info(
            f"🧠 Scan complete in {duration_ms}ms | "
            f"Nodes: {stats['total_nodes']} | Edges: {stats['total_edges']} | "
            f"Smells: {stats['total_smells']} | Cycles: {stats['circular_imports']}"
        )

        # Notify subscribers
        self._emit_event("scan_completed", stats)

        return stats

    # ═══════════════════════════════════════════════════════════════════════
    # INCREMENTAL FILE UPDATE
    # ═══════════════════════════════════════════════════════════════════════

    def update_file(self, file_path: str, root_dir: str) -> Dict[str, Any]:
        """Incrementally updates the graph for a single file."""
        try:
            full_path = Path(file_path).resolve()
            root_path = Path(root_dir).resolve()
            rel_path = full_path.relative_to(root_path).as_posix()

            # Delete existing nodes for this file (cascade removes edges, metrics, smells)
            with self._get_conn() as conn:
                conn.execute("DELETE FROM nodes WHERE path = ?", (rel_path,))
                conn.execute("DELETE FROM code_smells WHERE node_id LIKE ?", (f"{rel_path}%",))
                conn.execute("DELETE FROM code_metrics WHERE node_id LIKE ?", (f"{rel_path}%",))

            # Rescan and insert
            nodes, edges, metrics, smells = self._scan_file(full_path, rel_path, str(root_path))
            self._bulk_save(nodes, edges, metrics, smells)
            self._compute_coupling_metrics()
            self._compute_risk_scores()

            logger.info(f"🧠 Updated vision for: {rel_path}")
            self._emit_event("node_updated", {"file": rel_path, "nodes": len(nodes)})

            return {"status": "success", "file": rel_path, "nodes": len(nodes), "edges": len(edges)}

        except Exception as e:
            logger.error(f"Failed to update file {file_path}: {e}")
            return {"status": "error", "message": str(e)}

    # ═══════════════════════════════════════════════════════════════════════
    # FILE SCANNER (Core AST Analysis)
    # ═══════════════════════════════════════════════════════════════════════

    def _scan_file(
        self, full_path: Path, rel_path: str, root_dir: str
    ) -> Tuple[List[Dict], List[Dict], List[Dict], List[CodeSmell]]:
        """
        Parses a single Python file into nodes, edges, metrics, and smells.
        Properly handles class→method hierarchy using AST visitor pattern.
        """
        nodes: List[Dict] = []
        edges: List[Dict] = []
        metrics_list: List[Dict] = []
        smells: List[CodeSmell] = []

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # File Node
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        file_id = rel_path
        line_count = len(content.splitlines())

        nodes.append({
            "id": file_id,
            "type": "file",
            "path": rel_path,
            "name": full_path.name,
            "parent_id": None,
            "start_line": 1,
            "end_line": line_count,
            "content_hash": content_hash,
            "metadata": json.dumps({"size": len(content), "lines": line_count})
        })

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {rel_path}: {e}")
            return nodes, edges, metrics_list, smells

        # Walk top-level definitions (respecting hierarchy)
        self._extract_definitions(
            tree, file_id, rel_path, root_dir,
            nodes, edges, metrics_list, smells
        )

        return nodes, edges, metrics_list, smells

    def _extract_definitions(
        self,
        parent_ast: ast.AST,
        parent_id: str,
        rel_path: str,
        root_dir: str,
        nodes: List[Dict],
        edges: List[Dict],
        metrics_list: List[Dict],
        smells: List[CodeSmell],
        depth: int = 0,
    ):
        """Recursively extract classes and functions with proper hierarchy."""
        file_id = rel_path

        for child in ast.iter_child_nodes(parent_ast):
            # ── Classes ──────────────────────────────────────────────────
            if isinstance(child, ast.ClassDef):
                class_id = f"{parent_id}::{child.name}" if depth > 0 else f"{file_id}::{child.name}"

                bases = []
                for b in child.bases:
                    if isinstance(b, ast.Name):
                        bases.append(b.id)
                    elif isinstance(b, ast.Attribute):
                        bases.append(ast.dump(b))

                nodes.append({
                    "id": class_id,
                    "type": "class",
                    "path": rel_path,
                    "name": child.name,
                    "parent_id": parent_id,
                    "start_line": child.lineno,
                    "end_line": child.end_lineno,
                    "content_hash": "",
                    "metadata": json.dumps({
                        "bases": bases,
                        "decorators": [self._decorator_name(d) for d in child.decorator_list],
                        "docstring": ast.get_docstring(child) or "",
                    })
                })

                # Edge: parent defines class
                edges.append({
                    "source": parent_id,
                    "target": class_id,
                    "type": "defines",
                    "metadata": json.dumps({})
                })

                # Inheritance edges
                for base_name in bases:
                    edges.append({
                        "source": class_id,
                        "target": base_name,
                        "type": "inherits",
                        "metadata": json.dumps({})
                    })

                # Metrics for class
                class_metrics = ComplexityAnalyzer.analyze_class(child)
                metrics_list.append({
                    "node_id": class_id,
                    **class_metrics.to_dict()
                })

                # Smells for class
                class_smells = SmellDetector.detect_all(class_id, "class", class_metrics)
                smells.extend(class_smells)

                # Recurse into class body for methods
                self._extract_definitions(
                    child, class_id, rel_path, root_dir,
                    nodes, edges, metrics_list, smells,
                    depth=depth + 1
                )

            # ── Functions ────────────────────────────────────────────────
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_id = f"{parent_id}::{child.name}" if depth > 0 else f"{file_id}::{child.name}"

                nodes.append({
                    "id": func_id,
                    "type": "function",
                    "path": rel_path,
                    "name": child.name,
                    "parent_id": parent_id,
                    "start_line": child.lineno,
                    "end_line": child.end_lineno,
                    "content_hash": "",
                    "metadata": json.dumps({
                        "async": isinstance(child, ast.AsyncFunctionDef),
                        "args": [a.arg for a in child.args.args],
                        "decorators": [self._decorator_name(d) for d in child.decorator_list],
                        "docstring": ast.get_docstring(child) or "",
                        "returns": ast.dump(child.returns) if child.returns else None,
                    })
                })

                edges.append({
                    "source": parent_id,
                    "target": func_id,
                    "type": "defines",
                    "metadata": json.dumps({})
                })

                # Metrics for function
                func_metrics = ComplexityAnalyzer.analyze_function(child)
                metrics_list.append({
                    "node_id": func_id,
                    **func_metrics.to_dict()
                })

                # Smells for function
                func_smells = SmellDetector.detect_all(func_id, "function", func_metrics)
                smells.extend(func_smells)

            # ── Imports ──────────────────────────────────────────────────
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                self._process_import(
                    child, file_id, root_dir, edges
                )

    # ═══════════════════════════════════════════════════════════════════════
    # IMPORT RESOLUTION V2
    # ═══════════════════════════════════════════════════════════════════════

    def _process_import(
        self,
        node: ast.AST,
        file_id: str,
        root_dir: str,
        edges: List[Dict],
    ):
        """Process import statements with proper resolution."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                resolved = self._resolve_import(alias.name, root_dir)
                if resolved:
                    edges.append({
                        "source": file_id,
                        "target": resolved,
                        "type": "imports",
                        "metadata": json.dumps({
                            "module": alias.name,
                            "alias": alias.asname,
                        })
                    })

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                # Try resolving the full path: module.name
                full_module = f"{module}.{alias.name}" if module else alias.name
                resolved = self._resolve_import(full_module, root_dir)

                if not resolved and module:
                    # Fallback: resolve just the module (it might be a symbol import)
                    resolved = self._resolve_import(module, root_dir)

                if resolved:
                    edges.append({
                        "source": file_id,
                        "target": resolved,
                        "type": "imports",
                        "metadata": json.dumps({
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                        })
                    })

    def _resolve_import(self, module_name: str, root_dir: str) -> Optional[str]:
        """
        Resolves a Python module name to a file path relative to root_dir.

        Strategy:
        1. Convert dots to path separators
        2. Check: module.py, module/__init__.py
        3. Try multiple base paths (root, root/.ai, etc.)
        4. Handle partial matches (e.g., app.core → app/core/__init__.py)
        """
        base_path = module_name.replace(".", "/")
        root = Path(root_dir)

        # Candidate file paths
        candidates = [
            f"{base_path}.py",
            f"{base_path}/__init__.py",
        ]

        # Also try progressively shorter paths for "from X.Y import Z" patterns
        parts = base_path.split("/")
        if len(parts) > 1:
            for i in range(len(parts) - 1, 0, -1):
                partial = "/".join(parts[:i])
                candidates.append(f"{partial}.py")
                candidates.append(f"{partial}/__init__.py")

        # Search roots
        search_roots = [root]
        ai_dir = root / ".ai"
        if ai_dir.exists():
            search_roots.append(ai_dir)

        for search_root in search_roots:
            for cand in candidates:
                full_check = search_root / cand
                if full_check.exists():
                    try:
                        return full_check.relative_to(root).as_posix()
                    except ValueError:
                        return cand

        return None

    # ═══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _decorator_name(dec: ast.AST) -> str:
        """Extract decorator name from AST node."""
        if isinstance(dec, ast.Name):
            return dec.id
        elif isinstance(dec, ast.Attribute):
            return f"{ast.dump(dec)}"
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                return dec.func.id
            elif isinstance(dec.func, ast.Attribute):
                return f"{ast.dump(dec.func)}"
        return str(ast.dump(dec))

    # ═══════════════════════════════════════════════════════════════════════
    # DATABASE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    def _bulk_save(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        metrics: List[Dict],
        smells: List[CodeSmell],
    ):
        """Saves everything to SQLite within a single transaction."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys=ON;")
            cursor = conn.cursor()

            # Nodes
            if nodes:
                cursor.executemany("""
                    INSERT OR REPLACE INTO nodes
                    (id, type, path, name, parent_id, start_line, end_line, content_hash, metadata)
                    VALUES (:id, :type, :path, :name, :parent_id, :start_line, :end_line, :content_hash, :metadata)
                """, nodes)

            # Edges (ignore conflicts for duplicates)
            if edges:
                cursor.executemany("""
                    INSERT OR IGNORE INTO edges (source, target, type, metadata)
                    VALUES (:source, :target, :type, :metadata)
                """, edges)

            # Metrics
            if metrics:
                cursor.executemany("""
                    INSERT OR REPLACE INTO code_metrics
                    (node_id, cyclomatic_complexity, cognitive_complexity, lines_of_code,
                     num_parameters, nesting_depth)
                    VALUES (:node_id, :cyclomatic_complexity, :cognitive_complexity,
                            :lines_of_code, :num_parameters, :nesting_depth)
                """, metrics)

            # Smells
            if smells:
                cursor.executemany("""
                    INSERT INTO code_smells (node_id, smell_type, severity, description)
                    VALUES (:node_id, :smell_type, :severity, :description)
                """, [s.to_dict() for s in smells])

    def _compute_coupling_metrics(self):
        """Compute coupling_in and coupling_out from the edges table."""
        with self._get_conn() as conn:
            # Coupling IN: how many nodes import/depend on this node
            conn.execute("""
                UPDATE code_metrics SET coupling_in = (
                    SELECT COUNT(DISTINCT source) FROM edges
                    WHERE edges.target = code_metrics.node_id AND edges.type = 'imports'
                )
            """)
            # Coupling OUT: how many nodes this node imports/depends on
            conn.execute("""
                UPDATE code_metrics SET coupling_out = (
                    SELECT COUNT(DISTINCT target) FROM edges
                    WHERE edges.source = code_metrics.node_id AND edges.type = 'imports'
                )
            """)

    def _compute_risk_scores(self):
        """Compute risk scores for all nodes with metrics."""
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM code_metrics").fetchall()

            for row in rows:
                m = MetricsResult(
                    cyclomatic_complexity=row["cyclomatic_complexity"],
                    cognitive_complexity=row["cognitive_complexity"],
                    lines_of_code=row["lines_of_code"],
                    num_parameters=row["num_parameters"],
                    nesting_depth=row["nesting_depth"],
                )
                risk = RiskScorer.compute(m, row["coupling_in"], row["coupling_out"])

                conn.execute(
                    "UPDATE code_metrics SET risk_score = ? WHERE node_id = ?",
                    (risk.risk_score, row["node_id"])
                )

    # ═══════════════════════════════════════════════════════════════════════
    # SCAN HISTORY (Temporal Memory)
    # ═══════════════════════════════════════════════════════════════════════

    def _create_scan_entry(self, project_root: str) -> int:
        """Create a new scan history entry. Returns scan_id."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO scan_history (project_root) VALUES (?)",
                (project_root,)
            )
            return cursor.lastrowid

    def _complete_scan_entry(
        self, scan_id: int, duration_ms: int,
        total_nodes: int, total_edges: int, total_files: int, total_smells: int
    ):
        """Mark a scan as completed with statistics."""
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE scan_history SET
                    completed_at = CURRENT_TIMESTAMP,
                    duration_ms = ?,
                    total_nodes = ?,
                    total_edges = ?,
                    total_files = ?,
                    total_smells = ?,
                    status = 'completed'
                WHERE id = ?
            """, (duration_ms, total_nodes, total_edges, total_files, total_smells, scan_id))

    def _create_snapshots(self, scan_id: int, nodes: List[Dict]):
        """Create node snapshots for temporal diff tracking."""
        with self._get_conn() as conn:
            # Get previous hashes for diff detection
            prev_hashes = {}
            for row in conn.execute("SELECT id, content_hash FROM nodes"):
                prev_hashes[row["id"]] = row["content_hash"]

            snapshots = []
            for node in nodes:
                prev_hash = prev_hashes.get(node["id"])
                if prev_hash is None:
                    change_type = "added"
                elif prev_hash != node.get("content_hash", ""):
                    change_type = "modified"
                else:
                    change_type = "unchanged"

                snapshots.append({
                    "scan_id": scan_id,
                    "node_id": node["id"],
                    "content_hash": node.get("content_hash", ""),
                    "change_type": change_type,
                })

            if snapshots:
                conn.executemany("""
                    INSERT INTO node_snapshots (scan_id, node_id, content_hash, change_type)
                    VALUES (:scan_id, :node_id, :content_hash, :change_type)
                """, snapshots)

    # ═══════════════════════════════════════════════════════════════════════
    # QUERY API — Impact Analysis
    # ═══════════════════════════════════════════════════════════════════════

    def query_impact(self, node_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Transitive impact analysis: what breaks if this node changes?
        Returns N-depth dependency chain with risk scores.
        """
        target = node_id.replace("\\", "/")

        with self._get_conn() as conn:
            # BFS for transitive dependents
            visited: Set[str] = set()
            queue = [(target, 0)]
            dependents: List[Dict] = []

            while queue:
                current, depth = queue.pop(0)
                if current in visited or depth > max_depth:
                    continue
                visited.add(current)

                rows = conn.execute("""
                    SELECT e.source, e.type, e.metadata, m.risk_score
                    FROM edges e
                    LEFT JOIN code_metrics m ON m.node_id = e.source
                    WHERE e.target = ? AND e.type = 'imports'
                """, (current,)).fetchall()

                for row in rows:
                    dep = {
                        "node_id": row["source"],
                        "edge_type": row["type"],
                        "depth": depth + 1,
                        "risk_score": row["risk_score"] or 0.0,
                    }
                    dependents.append(dep)
                    queue.append((row["source"], depth + 1))

            # Aggregate risk
            total_risk = sum(d["risk_score"] for d in dependents) / max(len(dependents), 1)

            return {
                "target": target,
                "max_depth": max_depth,
                "total_dependents": len(dependents),
                "aggregate_risk": round(total_risk, 1),
                "dependents": dependents,
            }

    def query_references(self, symbol_name: str) -> List[Dict]:
        """Finds all nodes matching a symbol name."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM nodes WHERE name = ? OR id LIKE ?",
                (symbol_name, f"%::{symbol_name}")
            ).fetchall()
            return [dict(r) for r in rows]

    def query_metrics(self, node_id: str) -> Optional[Dict]:
        """Get code quality metrics for a specific node."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM code_metrics WHERE node_id = ?", (node_id,)
            ).fetchone()
            return dict(row) if row else None

    def query_smells(self, severity: Optional[str] = None) -> List[Dict]:
        """Get all detected code smells, optionally filtered by severity."""
        with self._get_conn() as conn:
            if severity:
                rows = conn.execute(
                    "SELECT * FROM code_smells WHERE severity = ? ORDER BY detected_at DESC",
                    (severity,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM code_smells ORDER BY severity DESC, detected_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]

    def query_history(self, limit: int = 10) -> List[Dict]:
        """Get recent scan history."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM scan_history ORDER BY started_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def query_search(self, query: str, node_type: Optional[str] = None) -> List[Dict]:
        """Semantic search across nodes."""
        with self._get_conn() as conn:
            if node_type:
                rows = conn.execute(
                    "SELECT * FROM nodes WHERE (name LIKE ? OR id LIKE ?) AND type = ?",
                    (f"%{query}%", f"%{query}%", node_type)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM nodes WHERE name LIKE ? OR id LIKE ?",
                    (f"%{query}%", f"%{query}%")
                ).fetchall()
            return [dict(r) for r in rows]

    # ═══════════════════════════════════════════════════════════════════════
    # TELEMETRY
    # ═══════════════════════════════════════════════════════════════════════

    def record_telemetry(
        self, node_id: str, event_type: str,
        metadata: Optional[Dict] = None, session_id: Optional[str] = None
    ) -> int:
        """Record a real-time telemetry event."""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                INSERT INTO telemetry_events (node_id, event_type, metadata, session_id)
                VALUES (?, ?, ?, ?)
            """, (node_id, event_type, json.dumps(metadata or {}), session_id))

            self._emit_event("telemetry_received", {
                "node_id": node_id,
                "event_type": event_type,
                "metadata": metadata,
            })

            return cursor.lastrowid

    def query_telemetry(
        self, node_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict]:
        """Get recent telemetry events."""
        with self._get_conn() as conn:
            if node_id:
                rows = conn.execute(
                    "SELECT * FROM telemetry_events WHERE node_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (node_id, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM telemetry_events ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [dict(r) for r in rows]

    # ═══════════════════════════════════════════════════════════════════════
    # GRAPH EXPORT (D3/Vis.js compatible)
    # ═══════════════════════════════════════════════════════════════════════

    def get_graph_json(self) -> Dict[str, Any]:
        """Returns the full graph in D3-compatible JSON with metrics overlay."""
        with self._get_conn() as conn:
            # Nodes with metrics
            nodes_raw = conn.execute("""
                SELECT n.*, m.cyclomatic_complexity, m.cognitive_complexity,
                       m.lines_of_code, m.risk_score, m.coupling_in, m.coupling_out
                FROM nodes n
                LEFT JOIN code_metrics m ON m.node_id = n.id
            """).fetchall()

            nodes = []
            for row in nodes_raw:
                node = dict(row)
                node["metrics"] = {
                    "cyclomatic_complexity": node.pop("cyclomatic_complexity", 0) or 0,
                    "cognitive_complexity": node.pop("cognitive_complexity", 0) or 0,
                    "lines_of_code": node.pop("lines_of_code", 0) or 0,
                    "risk_score": node.pop("risk_score", 0) or 0,
                    "coupling_in": node.pop("coupling_in", 0) or 0,
                    "coupling_out": node.pop("coupling_out", 0) or 0,
                }
                nodes.append(node)

            edges = [dict(r) for r in conn.execute("SELECT * FROM edges").fetchall()]

            # Summary stats
            smell_count = conn.execute("SELECT COUNT(*) as c FROM code_smells").fetchone()["c"]
            scan = conn.execute(
                "SELECT * FROM scan_history ORDER BY started_at DESC LIMIT 1"
            ).fetchone()

            return {
                "nodes": nodes,
                "links": edges,
                "stats": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "total_smells": smell_count,
                    "last_scan": dict(scan) if scan else None,
                },
            }

    # ═══════════════════════════════════════════════════════════════════════
    # PROJECT HEALTH SCORE
    # ═══════════════════════════════════════════════════════════════════════

    def get_health_report(self) -> Dict[str, Any]:
        """Aggregate project health report."""
        with self._get_conn() as conn:
            # Node counts by type
            type_counts = {}
            for row in conn.execute("SELECT type, COUNT(*) as c FROM nodes GROUP BY type"):
                type_counts[row["type"]] = row["c"]

            # Smell counts by severity
            smell_counts = {}
            for row in conn.execute("SELECT severity, COUNT(*) as c FROM code_smells GROUP BY severity"):
                smell_counts[row["severity"]] = row["c"]

            # Average risk
            avg_risk = conn.execute(
                "SELECT AVG(risk_score) as avg_risk FROM code_metrics"
            ).fetchone()

            # Top 10 riskiest nodes
            risky_nodes = conn.execute("""
                SELECT m.node_id, m.risk_score, m.cyclomatic_complexity,
                       m.cognitive_complexity, n.type, n.name
                FROM code_metrics m
                JOIN nodes n ON n.id = m.node_id
                ORDER BY m.risk_score DESC LIMIT 10
            """).fetchall()

            return {
                "node_counts": type_counts,
                "smell_counts": smell_counts,
                "average_risk": round(avg_risk["avg_risk"] or 0, 1),
                "top_risky_nodes": [dict(r) for r in risky_nodes],
                "health_score": max(0, round(100 - (avg_risk["avg_risk"] or 0), 1)),
            }

    # ═══════════════════════════════════════════════════════════════════════
    # EVENT SYSTEM (for WebSocket subscribers)
    # ═══════════════════════════════════════════════════════════════════════

    def subscribe(self, callback):
        """Register a callback for events."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback):
        """Remove an event callback."""
        self._subscribers = [s for s in self._subscribers if s != callback]

    def _emit_event(self, event_type: str, data: Any):
        """Emit an event to all subscribers."""
        event = {"type": event_type, "data": data, "timestamp": datetime.utcnow().isoformat()}
        for sub in self._subscribers:
            try:
                sub(event)
            except Exception as e:
                logger.error(f"Event subscriber error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    cortex = VisualCortex()
    stats = cortex.scan_project(root)
    print(json.dumps(stats, indent=2))

    # Print health report
    health = cortex.get_health_report()
    print("\n🏥 Health Report:")
    print(json.dumps(health, indent=2))
