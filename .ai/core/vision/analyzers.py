"""
Code Quality Analyzers — MCP Vision Neuronal V2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Production-grade static analysis: complexity scoring, smell detection, risk engine.
"""

import ast
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger("visual_cortex.analyzers")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MetricsResult:
    """Code quality metrics for a single node."""
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    num_parameters: int = 0
    nesting_depth: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CodeSmell:
    """A detected code quality issue."""
    node_id: str
    smell_type: str       # god_class | long_method | deep_nesting | high_coupling | circular_import
    severity: str          # info | warning | critical
    description: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskAssessment:
    """Aggregate risk assessment for a node."""
    node_id: str
    risk_score: float      # 0.0 - 100.0
    factors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLEXITY ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

class ComplexityAnalyzer:
    """
    Computes McCabe cyclomatic complexity and cognitive complexity for AST nodes.

    Cyclomatic = number of independent paths through code
    Cognitive  = how hard it is for a human to understand (penalizes nesting)
    """

    # AST nodes that create a new branch (cyclomatic)
    BRANCH_NODES = (
        ast.If, ast.For, ast.While, ast.ExceptHandler,
        ast.With, ast.Assert, ast.BoolOp,
    )

    @staticmethod
    def analyze_function(node: ast.AST) -> MetricsResult:
        """Analyze a function/method AST node for complexity metrics."""
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return MetricsResult()

        metrics = MetricsResult()
        metrics.lines_of_code = (node.end_lineno or node.lineno) - node.lineno + 1
        metrics.num_parameters = len(node.args.args)

        # Cyclomatic: start at 1 (the function itself is one path)
        cyclomatic = 1
        cognitive = 0
        max_depth = 0

        def _walk_cognitive(n: ast.AST, depth: int = 0) -> None:
            nonlocal cyclomatic, cognitive, max_depth
            max_depth = max(max_depth, depth)

            for child in ast.iter_child_nodes(n):
                increment = 0

                # Branches add to cyclomatic complexity
                if isinstance(child, ComplexityAnalyzer.BRANCH_NODES):
                    cyclomatic += 1
                    increment = 1

                # Cognitive: nesting penalizes more
                if isinstance(child, (ast.If, ast.For, ast.While)):
                    cognitive += increment + depth  # nested = harder to understand
                    _walk_cognitive(child, depth + 1)
                elif isinstance(child, (ast.ExceptHandler, ast.With)):
                    cognitive += increment
                    _walk_cognitive(child, depth + 1)
                elif isinstance(child, ast.BoolOp):
                    # Each boolean operator in a chain adds
                    cognitive += len(child.values) - 1
                    cyclomatic += len(child.values) - 1
                    _walk_cognitive(child, depth)
                elif isinstance(child, ast.Lambda):
                    cognitive += 1  # Lambda is a cognitive cost
                    _walk_cognitive(child, depth)
                elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                    cognitive += 1 + depth  # Comprehensions nested = complex
                    _walk_cognitive(child, depth + 1)
                else:
                    _walk_cognitive(child, depth)

        _walk_cognitive(node)
        metrics.cyclomatic_complexity = cyclomatic
        metrics.cognitive_complexity = cognitive
        metrics.nesting_depth = max_depth

        return metrics

    @staticmethod
    def analyze_class(class_node: ast.ClassDef) -> MetricsResult:
        """Analyze a class as the sum of its methods."""
        total = MetricsResult()
        total.lines_of_code = (class_node.end_lineno or class_node.lineno) - class_node.lineno + 1

        method_count = 0
        for child in ast.iter_child_nodes(class_node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_count += 1
                m = ComplexityAnalyzer.analyze_function(child)
                total.cyclomatic_complexity += m.cyclomatic_complexity
                total.cognitive_complexity += m.cognitive_complexity
                total.nesting_depth = max(total.nesting_depth, m.nesting_depth)

        total.num_parameters = method_count  # For classes, this means method count
        return total


# ═══════════════════════════════════════════════════════════════════════════════
# SMELL DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class SmellDetector:
    """Detects common code smells based on metrics and structural patterns."""

    # Thresholds (configurable)
    GOD_CLASS_METHOD_THRESHOLD = 20
    LONG_METHOD_LINES_THRESHOLD = 50
    DEEP_NESTING_THRESHOLD = 4
    HIGH_COMPLEXITY_THRESHOLD = 15
    MANY_PARAMS_THRESHOLD = 7

    @classmethod
    def detect_all(
        cls,
        node_id: str,
        node_type: str,
        metrics: MetricsResult,
    ) -> List[CodeSmell]:
        """Run all smell detectors on a node."""
        smells: List[CodeSmell] = []

        if node_type == "class":
            if metrics.num_parameters >= cls.GOD_CLASS_METHOD_THRESHOLD:
                smells.append(CodeSmell(
                    node_id=node_id,
                    smell_type="god_class",
                    severity="critical",
                    description=f"Class has {metrics.num_parameters} methods (threshold: {cls.GOD_CLASS_METHOD_THRESHOLD})"
                ))

        if node_type == "function":
            if metrics.lines_of_code >= cls.LONG_METHOD_LINES_THRESHOLD:
                smells.append(CodeSmell(
                    node_id=node_id,
                    smell_type="long_method",
                    severity="warning",
                    description=f"Function has {metrics.lines_of_code} lines (threshold: {cls.LONG_METHOD_LINES_THRESHOLD})"
                ))

            if metrics.nesting_depth >= cls.DEEP_NESTING_THRESHOLD:
                smells.append(CodeSmell(
                    node_id=node_id,
                    smell_type="deep_nesting",
                    severity="warning",
                    description=f"Nesting depth of {metrics.nesting_depth} (threshold: {cls.DEEP_NESTING_THRESHOLD})"
                ))

            if metrics.cyclomatic_complexity >= cls.HIGH_COMPLEXITY_THRESHOLD:
                smells.append(CodeSmell(
                    node_id=node_id,
                    smell_type="high_complexity",
                    severity="critical",
                    description=f"Cyclomatic complexity of {metrics.cyclomatic_complexity} (threshold: {cls.HIGH_COMPLEXITY_THRESHOLD})"
                ))

            if metrics.num_parameters >= cls.MANY_PARAMS_THRESHOLD:
                smells.append(CodeSmell(
                    node_id=node_id,
                    smell_type="many_parameters",
                    severity="info",
                    description=f"Function has {metrics.num_parameters} parameters (threshold: {cls.MANY_PARAMS_THRESHOLD})"
                ))

        return smells


# ═══════════════════════════════════════════════════════════════════════════════
# RISK SCORER
# ═══════════════════════════════════════════════════════════════════════════════

class RiskScorer:
    """
    Combines code metrics + coupling data into a 0-100 risk score.

    Higher score = more risky to modify.
    """

    # Weight factors for risk calculation
    WEIGHTS = {
        "cyclomatic_complexity": 3.0,
        "cognitive_complexity": 2.0,
        "lines_of_code": 0.2,
        "nesting_depth": 5.0,
        "coupling_in": 4.0,   # Many dependents = high risk
        "coupling_out": 1.5,
        "num_parameters": 1.0,
    }

    @classmethod
    def compute(
        cls,
        metrics: MetricsResult,
        coupling_in: int = 0,
        coupling_out: int = 0,
    ) -> RiskAssessment:
        """Compute aggregate risk score from metrics and coupling."""
        raw_score = 0.0
        factors: List[str] = []

        # Cyclomatic
        cc = metrics.cyclomatic_complexity
        raw_score += min(cc * cls.WEIGHTS["cyclomatic_complexity"], 30)
        if cc >= 15:
            factors.append(f"High cyclomatic complexity ({cc})")

        # Cognitive
        cog = metrics.cognitive_complexity
        raw_score += min(cog * cls.WEIGHTS["cognitive_complexity"], 20)
        if cog >= 20:
            factors.append(f"High cognitive complexity ({cog})")

        # LOC
        loc = metrics.lines_of_code
        raw_score += min(loc * cls.WEIGHTS["lines_of_code"], 10)
        if loc >= 50:
            factors.append(f"Long code ({loc} lines)")

        # Nesting
        nd = metrics.nesting_depth
        raw_score += min(nd * cls.WEIGHTS["nesting_depth"], 15)
        if nd >= 4:
            factors.append(f"Deep nesting ({nd} levels)")

        # Coupling
        raw_score += min(coupling_in * cls.WEIGHTS["coupling_in"], 20)
        if coupling_in >= 5:
            factors.append(f"High fan-in ({coupling_in} dependents)")

        raw_score += min(coupling_out * cls.WEIGHTS["coupling_out"], 10)
        if coupling_out >= 10:
            factors.append(f"High fan-out ({coupling_out} dependencies)")

        # Params
        nparams = metrics.num_parameters
        raw_score += min(nparams * cls.WEIGHTS["num_parameters"], 5)

        # Clamp to 0-100
        final_score = min(max(raw_score, 0.0), 100.0)

        return RiskAssessment(
            node_id="",  # Caller sets this
            risk_score=round(final_score, 1),
            factors=factors,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CIRCULAR DEPENDENCY DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class CircularDependencyDetector:
    """Detects circular import chains in the dependency graph."""

    @staticmethod
    def find_cycles(adjacency: Dict[str, Set[str]]) -> List[List[str]]:
        """
        Find all import cycles using DFS.

        Args:
            adjacency: {file_id: set_of_imported_file_ids}

        Returns:
            List of cycles, each as a list of node IDs forming the cycle.
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []
        path: List[str] = []

        def _dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adjacency.get(node, set()):
                if neighbor not in visited:
                    _dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle — extract it
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.discard(node)

        for node in adjacency:
            if node not in visited:
                _dfs(node)

        return cycles
