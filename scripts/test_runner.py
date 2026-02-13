#!/usr/bin/env python3
"""
🧪 Silicon Valley Test Runner

Herramienta profesional para ejecutar tests con diferentes perfiles:
- quick: Tests rápidos para desarrollo (< 5 segundos)
- unit: Tests unitarios completos
- integration: Tests con infraestructura fake
- audit: Tests de arquitectura y gobernanza
- ci: Suite completa para CI/CD
- coverage: Análisis de cobertura

Uso:
    python scripts/test_runner.py quick
    python scripts/test_runner.py unit -v
    python scripts/test_runner.py ci
"""

import argparse
import subprocess
import sys
import time
import os
from pathlib import Path
from typing import List, Tuple

# Colores para output profesional
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def _safe_print(text: str, *, is_error: bool = False) -> None:
    stream = sys.stderr if is_error else sys.stdout
    try:
        print(text, file=stream)
    except UnicodeEncodeError:
        ascii_text = text.encode("ascii", errors="ignore").decode("ascii")
        print(ascii_text, file=stream)


TEST_PROFILES = {
    "quick": {
        "description": "Tests rápidos para desarrollo (< 5s)",
        "paths": ["tests/backend/unit", "tests/backend/architecture", "tests/frontend/rendering"],
        "args": ["-x", "--tb=short"],  # Fail fast, short traceback
        "markers": "not slow",
    },
    "unit": {
        "description": "Tests unitarios completos",
        "paths": ["tests/backend/unit"],
        "args": ["-v", "--tb=short"],
        "markers": None,
    },
    "integration": {
        "description": "Tests de integración con infraestructura fake",
        "paths": ["tests/backend/integration", "tests/platform/infra"],
        "args": ["-v", "--tb=short"],
        "markers": None,
    },
    "architecture": {
        "description": "Tests de arquitectura y gobernanza",
        "paths": ["tests/backend/architecture", "tests/platform/deployment"],
        "args": ["-v", "--tb=long"],
        "markers": None,
    },
    "audit": {
        "description": "Audit completo de infraestructura",
        "paths": ["tests/backend/quality", "tests/backend/security", "tests/platform/cloudflare", "tests/platform/observability"],
        "args": ["-v", "--tb=short"],
        "markers": None,
    },
    "ci": {
        "description": "Suite completa para CI/CD",
        "paths": ["tests/"],
        "args": ["-v", "--tb=short", "--cov=app", "--cov-report=xml", "--cov-report=term"],
        "markers": None,
    },
    "critical": {
        "description": "Tests de caminos críticos de negocio",
        "paths": ["tests/"],
        "args": ["-v", "--tb=short"],
        "markers": "critical",
    },
}


def print_header(text: str) -> None:
    """Imprime un header formateado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD} {text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text: str) -> None:
    """Imprime mensaje de éxito"""
    _safe_print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Imprime mensaje de error"""
    _safe_print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}", is_error=True)


def print_warning(text: str) -> None:
    """Imprime mensaje de advertencia"""
    _safe_print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    """Imprime información"""
    _safe_print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def run_pytest(profile: str, extra_args: List[str]) -> Tuple[int, float]:
    """
    Ejecuta pytest con el perfil especificado.
    
    Returns:
        Tuple of (exit_code, duration_seconds)
    """
    if profile not in TEST_PROFILES:
        print_error(f"Perfil desconocido: {profile}")
        print_info(f"Perfiles disponibles: {', '.join(TEST_PROFILES.keys())}")
        return 1, 0.0
    
    config = TEST_PROFILES[profile]
    
    # Construir comando
    cmd = ["python", "-m", "pytest", "-c", "pytest.ini"] + config["paths"]
    cmd += config["args"]
    
    if config["markers"]:
        cmd += ["-m", config["markers"]]
    
    cmd += extra_args
    
    # Mostrar información
    print_header(f"TEST PROFILE: {profile.upper()}")
    print_info(config["description"])
    print_info(f"Command: {' '.join(cmd)}")
    print()
    
    # Ejecutar
    start_time = time.time()
    result = subprocess.run(cmd)
    duration = time.time() - start_time
    
    return result.returncode, duration


def run_coverage_analysis() -> int:
    """Ejecuta análisis de cobertura"""
    print_header("COVERAGE ANALYSIS")
    
    # Verificar que pytest-cov está instalado
    try:
        import pytest_cov
    except ImportError:
        print_error("pytest-cov no está instalado")
        print_info("Instalar con: pip install pytest-cov")
        return 1
    
    cmd = [
        "python", "-m", "pytest",
        "-c", "pytest.ini",
        "tests/backend/unit", "tests/backend/integration", "tests/frontend",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=80",  # Mínimo 80% de cobertura
    ]
    
    print_info(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print_success("Coverage report generated in htmlcov/")
    
    return result.returncode


def list_tests(pattern: str = None) -> int:
    """Lista todos los tests disponibles"""
    print_header("AVAILABLE TESTS")
    
    cmd = ["python", "-m", "pytest", "-c", "pytest.ini", "tests/", "--collect-only", "-q"]
    
    if pattern:
        cmd.insert(3, pattern)
    
    result = subprocess.run(cmd)
    return result.returncode


def watch_mode(profile: str) -> int:
    """Ejecuta tests en modo watch (re-ejecutar al cambiar archivos)"""
    try:
        import pytest_watch
    except ImportError:
        print_error("pytest-watch no está instalado")
        print_info("Instalar con: pip install pytest-watch")
        return 1
    
    config = TEST_PROFILES.get(profile, TEST_PROFILES["quick"])
    
    cmd = ["ptw", "--runner", "python", "-m", "pytest"] + config["paths"]
    
    print_header(f"WATCH MODE: {profile}")
    print_info("Tests se re-ejecutarán automáticamente al guardar archivos")
    print_info("Presione Ctrl+C para salir")
    print()
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Silicon Valley Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s quick                    # Tests rápidos
  %(prog)s unit -v                  # Tests unitarios verbose
  %(prog)s ci                       # Suite completa CI/CD
  %(prog)s coverage                 # Análisis de cobertura
  %(prog)s list                     # Listar todos los tests
  %(prog)s watch quick              # Modo watch para desarrollo
        """
    )
    
    parser.add_argument(
        "command",
        choices=list(TEST_PROFILES.keys()) + ["coverage", "list", "watch"],
        help="Perfil de tests a ejecutar"
    )
    
    parser.add_argument(
        "extra_args",
        nargs="*",
        help="Argumentos adicionales para pytest"
    )
    
    parser.add_argument(
        "--watch-profile",
        default="quick",
        help="Perfil para modo watch (default: quick)"
    )
    
    args = parser.parse_args()
    
    # Cambiar al directorio del proyecto
    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)
    
    start_time = time.time()
    
    if args.command == "coverage":
        exit_code = run_coverage_analysis()
    elif args.command == "list":
        pattern = args.extra_args[0] if args.extra_args else None
        exit_code = list_tests(pattern)
    elif args.command == "watch":
        profile = args.extra_args[0] if args.extra_args else args.watch_profile
        exit_code = watch_mode(profile)
    else:
        exit_code, duration = run_pytest(args.command, args.extra_args)
        
        # Mostrar resumen
        print()
        print("-" * 70)
        if exit_code == 0:
            print_success(f"All tests passed in {duration:.2f}s")
        else:
            print_error(f"Tests failed after {duration:.2f}s")
        print("-" * 70)
    
    total_duration = time.time() - start_time
    print_info(f"Total execution time: {total_duration:.2f}s")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
