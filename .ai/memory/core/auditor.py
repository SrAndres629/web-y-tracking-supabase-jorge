"""
NEXUS-7 Continuous Auditor
═══════════════════════════════════════════════════════════════════════════════
Sistema de auditoría continua basado en reglas declarativas.

Responsabilidades:
1. Escanear cambios en el codebase
2. Validar contra reglas de arquitectura
3. Generar reportes estructurados
4. (Opcional) Auto-generar tareas de corrección

Diseño:
- Reglas declarativas en registry.yaml
- Auditorías diferenciales (solo cambios)
- Reportes JSON estructurados
- Extensible via plugins

Usage:
    from .ai.core.auditor import Auditor
    
    auditor = Auditor()
    
    # Auditoría completa
    report = auditor.run_full_audit()
    
    # Auditoría diferencial (solo archivos cambiados)
    report = auditor.run_differential_audit(["app/tracking.py"])
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import re
import json
import ast
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import subprocess

from .registry import AgentRegistry

logger = logging.getLogger("nexus7.auditor")


class Severity(Enum):
    """Niveles de severidad de findings"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RuleCategory(Enum):
    """Categorías de reglas de auditoría"""
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    COMPLIANCE = "compliance"


@dataclass
class Finding:
    """Un hallazgo de auditoría"""
    rule_id: str
    rule_name: str
    category: str
    severity: str
    file_path: str
    line_number: Optional[int]
    message: str
    suggestion: Optional[str] = None
    autofix: bool = False
    autofix_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditReport:
    """Reporte completo de auditoría"""
    timestamp: str
    scope: List[str]
    findings: List[Finding]
    summary: Dict[str, int] = field(default_factory=dict)
    duration: float = 0.0
    
    def __post_init__(self):
        if not self.summary:
            self._calculate_summary()
    
    def _calculate_summary(self):
        """Calcula resumen de findings"""
        self.summary = {
            "total": len(self.findings),
            "critical": sum(1 for f in self.findings if f.severity == Severity.CRITICAL.value),
            "error": sum(1 for f in self.findings if f.severity == Severity.ERROR.value),
            "warning": sum(1 for f in self.findings if f.severity == Severity.WARNING.value),
            "info": sum(1 for f in self.findings if f.severity == Severity.INFO.value),
        }
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "scope": self.scope,
            "duration": self.duration,
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings]
        }
    
    def save(self, path: str):
        """Guarda el reporte a disco"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


class AuditRule:
    """
    Regla de auditoría base.
    Las reglas específicas heredan de esta clase.
    """
    
    def __init__(self, rule_id: str, name: str, category: RuleCategory,
                 severity: Severity, autofix: bool = False):
        self.rule_id = rule_id
        self.name = name
        self.category = category
        self.severity = severity
        self.autofix = autofix
    
    def check(self, file_path: str, content: str) -> List[Finding]:
        """
        Ejecuta la regla sobre un archivo.
        
        Args:
            file_path: Ruta al archivo
            content: Contenido del archivo
        
        Returns:
            Lista de findings (vacía si no hay issues)
        """
        raise NotImplementedError


# ═══════════════════════════════════════════════════════════════════════════════
# REGLAS ESPECÍFICAS
# ═══════════════════════════════════════════════════════════════════════════════

class NoCircularImportsRule(AuditRule):
    """Detecta imports circulares"""
    
    def __init__(self):
        super().__init__(
            rule_id="ARCH001",
            name="No Circular Imports",
            category=RuleCategory.ARCHITECTURE,
            severity=Severity.ERROR
        )
    
    def check(self, file_path: str, content: str) -> List[Finding]:
        findings = []
        # TODO: Implementar análisis de imports circulares
        # Esto requiere análisis de AST del proyecto completo
        return findings


class CleanArchitectureRule(AuditRule):
    """Valida cumplimiento de Clean Architecture"""
    
    VIOLATIONS = [
        ("app/interfaces", "app/infrastructure"),  # Interface no debe importar infra
        ("app/application", "app/infrastructure"),  # App no debe importar infra directo
    ]
    
    def __init__(self):
        super().__init__(
            rule_id="ARCH002",
            name="Clean Architecture Compliance",
            category=RuleCategory.ARCHITECTURE,
            severity=Severity.ERROR
        )
    
    def check(self, file_path: str, content: str) -> List[Finding]:
        findings = []
        
        # Detectar imports que violan la arquitectura
        import_pattern = r'^(?:from|import)\s+([\w.]+)'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            match = re.match(import_pattern, line.strip())
            if match:
                imported = match.group(1)
                
                for layer, forbidden in self.VIOLATIONS:
                    if layer in file_path and forbidden in imported:
                        findings.append(Finding(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            category=self.category.value,
                            severity=self.severity.value,
                            file_path=file_path,
                            line_number=line_num,
                            message=f"Layer violation: {layer} imports {forbidden}",
                            suggestion=f"Use dependency injection or move code to proper layer"
                        ))
        
        return findings


class NoHardcodedSecretsRule(AuditRule):
    """Detecta secretos hardcodeados"""
    
    PATTERNS = [
        (r'password\s*=\s*["\'][^"\']+["\']', "Possible hardcoded password"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "Possible hardcoded API key"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "Possible hardcoded secret"),
        (r'token\s*=\s*["\'][^"\']{20,}["\']', "Possible hardcoded token"),
        (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API key pattern"),
        (r'EAAB[a-zA-Z0-9]{20,}', "Meta Access Token pattern"),
    ]
    
    def __init__(self):
        super().__init__(
            rule_id="SEC001",
            name="No Hardcoded Secrets",
            category=RuleCategory.SECURITY,
            severity=Severity.CRITICAL,
            autofix=True
        )
    
    def check(self, file_path: str, content: str) -> List[Finding]:
        findings = []
        
        # Ignorar archivos de configuración de ejemplo
        if '.example' in file_path or 'test' in file_path.lower():
            return findings
        
        for line_num, line in enumerate(content.split('\n'), 1):
            for pattern, message in self.PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Verificar que no sea una variable de entorno
                    if 'os.environ' not in line and 'getenv' not in line:
                        findings.append(Finding(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            category=self.category.value,
                            severity=self.severity.value,
                            file_path=file_path,
                            line_number=line_num,
                            message=message,
                            suggestion="Move to .env file and use os.environ.get()",
                            autofix=True,
                            autofix_code=self._generate_fix(line)
                        ))
        
        return findings
    
    def _generate_fix(self, line: str) -> str:
        """Genera código de fix automático"""
        # Simplificación - en producción sería más sofisticado
        match = re.search(r'(\w+)\s*=\s*["\']([^"\']+)["\']', line)
        if match:
            var_name = match.group(1)
            return f"{var_name} = os.environ.get('{var_name.upper()}')"
        return "# TODO: Move to environment variable"


class AsyncCorrectnessRule(AuditRule):
    """Valida uso correcto de async/await"""
    
    def __init__(self):
        super().__init__(
            rule_id="PERF001",
            name="Async/Await Correctness",
            category=RuleCategory.PERFORMANCE,
            severity=Severity.WARNING
        )
    
    def check(self, file_path: str, content: str) -> List[Finding]:
        findings = []
        
        # Buscar funciones async sin await
        # Esto es una simplificación - análisis real requiere AST
        async_pattern = r'async\s+def\s+(\w+)'
        await_pattern = r'await\s+'
        
        lines = content.split('\n')
        in_async_func = False
        async_func_line = 0
        async_func_name = ""
        has_await = False
        
        for line_num, line in enumerate(lines, 1):
            # Detectar inicio de función async
            match = re.search(async_pattern, line)
            if match:
                # Verificar función anterior
                if in_async_func and not has_await:
                    findings.append(Finding(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        category=self.category.value,
                        severity=self.severity.value,
                        file_path=file_path,
                        line_number=async_func_line,
                        message=f"Async function '{async_func_name}' has no await statements",
                        suggestion="Remove 'async' keyword or add await"
                    ))
                
                in_async_func = True
                async_func_line = line_num
                async_func_name = match.group(1)
                has_await = False
            
            # Detectar await
            if in_async_func and re.search(await_pattern, line):
                has_await = True
            
            # Detectar fin de función (simplificado)
            if in_async_func and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if not has_await:
                    findings.append(Finding(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        category=self.category.value,
                        severity=self.severity.value,
                        file_path=file_path,
                        line_number=async_func_line,
                        message=f"Async function '{async_func_name}' has no await statements",
                        suggestion="Remove 'async' keyword or add await"
                    ))
                in_async_func = False
        
        return findings


class FileSizeRule(AuditRule):
    """Valida tamaño de archivos"""
    
    MAX_LINES = 300
    
    def __init__(self):
        super().__init__(
            rule_id="STYLE001",
            name="File Size Limit",
            category=RuleCategory.STYLE,
            severity=Severity.WARNING
        )
    
    def check(self, file_path: str, content: str) -> List[Finding]:
        findings = []
        
        line_count = len(content.split('\n'))
        if line_count > self.MAX_LINES:
            findings.append(Finding(
                rule_id=self.rule_id,
                rule_name=self.name,
                category=self.category.value,
                severity=self.severity.value,
                file_path=file_path,
                line_number=None,
                message=f"File has {line_count} lines (max recommended: {self.MAX_LINES})",
                suggestion="Consider splitting into smaller modules"
            ))
        
        return findings


# ═══════════════════════════════════════════════════════════════════════════════
# AUDITOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

class Auditor:
    """
    Auditor continuo del sistema NEXUS-7.
    """
    
    DEFAULT_RULES: List[AuditRule] = [
        NoCircularImportsRule(),
        CleanArchitectureRule(),
        NoHardcodedSecretsRule(),
        AsyncCorrectnessRule(),
        FileSizeRule(),
    ]
    
    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or AgentRegistry()
        self.rules: List[AuditRule] = []
        self._load_rules()
    
    def _load_rules(self):
        """Carga reglas desde registry + defaults"""
        # Cargar reglas del registry
        skills = self.registry._config.get("skills", {})
        auditor_skill = skills.get("core.auditor", {})
        
        # TODO: Cargar reglas dinámicas desde config
        
        # Añadir reglas por defecto
        self.rules.extend(self.DEFAULT_RULES)
        
        logger.info(f"Loaded {len(self.rules)} audit rules")
    
    def run_full_audit(self, scope: Optional[List[str]] = None) -> AuditReport:
        """
        Ejecuta auditoría completa del codebase.
        
        Args:
            scope: Lista de paths a auditar (None = todo)
        
        Returns:
            AuditReport con todos los findings
        """
        start_time = datetime.utcnow()
        t0 = time.time()
        
        if scope is None:
            scope = self._discover_python_files()
        
        findings: List[Finding] = []
        
        for file_path in scope:
            try:
                file_findings = self._audit_file(file_path)
                findings.extend(file_findings)
            except Exception as e:
                logger.error(f"Error auditing {file_path}: {e}")
                findings.append(Finding(
                    rule_id="SYSTEM",
                    rule_name="Audit Error",
                    category="system",
                    severity=Severity.ERROR.value,
                    file_path=file_path,
                    line_number=None,
                    message=f"Audit failed: {e}"
                ))
        
        duration = time.time() - t0
        
        report = AuditReport(
            timestamp=start_time.isoformat(),
            scope=scope,
            findings=findings,
            duration=duration
        )
        
        # Guardar reporte
        self._save_report(report)
        
        return report
    
    def run_differential_audit(self, changed_files: List[str]) -> AuditReport:
        """
        Audita solo archivos que han cambiado.
        
        Args:
            changed_files: Lista de archivos modificados
        
        Returns:
            AuditReport con findings de archivos cambiados
        """
        # Filtrar solo archivos Python
        python_files = [f for f in changed_files if f.endswith('.py')]
        
        if not python_files:
            return AuditReport(
                timestamp=datetime.utcnow().isoformat(),
                scope=[],
                findings=[]
            )
        
        return self.run_full_audit(python_files)
    
    def _audit_file(self, file_path: str) -> List[Finding]:
        """Audita un archivo individual"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [Finding(
                rule_id="SYSTEM",
                rule_name="File Read Error",
                category="system",
                severity=Severity.ERROR.value,
                file_path=file_path,
                line_number=None,
                message=f"Cannot read file: {e}"
            )]
        
        # Ejecutar todas las reglas
        for rule in self.rules:
            try:
                rule_findings = rule.check(file_path, content)
                findings.extend(rule_findings)
            except Exception as e:
                logger.error(f"Rule {rule.rule_id} failed on {file_path}: {e}")
        
        return findings
    
    def _discover_python_files(self) -> List[str]:
        """Descubre todos los archivos Python del proyecto"""
        files = []
        
        for pattern in ['app/**/*.py', 'tests/**/*.py', '.ai/**/*.py']:
            files.extend(Path('.').glob(pattern))
        
        # Excluir directorios
        exclude = ['venv', '__pycache__', 'node_modules', '.git']
        files = [
            str(f) for f in files 
            if not any(x in str(f) for x in exclude)
        ]
        
        return files
    
    def _save_report(self, report: AuditReport):
        """Guarda el reporte en .ai/sensory/"""
        report_dir = Path(".ai/sensory")
        report_dir.mkdir(exist_ok=True)
        
        timestamp = int(time.time())
        report_file = report_dir / f"audit_report_{timestamp}.json"
        
        report.save(str(report_file))
        logger.info(f"Audit report saved: {report_file}")
    
    def generate_fix_tasks(self, report: AuditReport) -> List[dict]:
        """
        Genera tareas de corrección para findings con autofix.
        
        Returns:
            Lista de tareas para crear
        """
        tasks = []
        
        for finding in report.findings:
            if finding.autofix and finding.severity in [Severity.CRITICAL.value, Severity.ERROR.value]:
                task = {
                    "agent": "codex",
                    "content": f"""Fix {finding.rule_name} issue in {finding.file_path}

Finding: {finding.message}
Line: {finding.line_number}
Suggestion: {finding.suggestion}

Apply the fix automatically.
""",
                    "permissions": {
                        "read": [finding.file_path],
                        "write": [finding.file_path]
                    }
                }
                tasks.append(task)
        
        return tasks


def main():
    """Entry point para ejecutar auditoría standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NEXUS-7 Auditor")
    parser.add_argument(
        "--scope",
        nargs="+",
        help="Archivos específicos a auditar"
    )
    parser.add_argument(
        "--output",
        default=".ai/sensory/audit_report.json",
        help="Path para guardar el reporte"
    )
    
    args = parser.parse_args()
    
    auditor = Auditor()
    
    if args.scope:
        report = auditor.run_differential_audit(args.scope)
    else:
        report = auditor.run_full_audit()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  AUDIT REPORT")
    print(f"{'='*60}")
    print(f"  Duration: {report.duration:.2f}s")
    print(f"  Files scanned: {len(report.scope)}")
    print(f"  Findings: {report.summary['total']}")
    print(f"    - Critical: {report.summary['critical']}")
    print(f"    - Error: {report.summary['error']}")
    print(f"    - Warning: {report.summary['warning']}")
    print(f"    - Info: {report.summary['info']}")
    print(f"{'='*60}")
    
    # Save
    report.save(args.output)
    print(f"\nReport saved: {args.output}")
    
    # Exit code based on severity
    if report.summary['critical'] > 0:
        exit(2)
    elif report.summary['error'] > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
