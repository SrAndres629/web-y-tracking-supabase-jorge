"""
🧬 High-Fidelity Code Health Audit
Silicon Valley Grade Autonomous Diagnostics

Este test no verifica comportamiento, sino la SALUD ESTRUCTURAL del código.
Permite que un agente de IA detecte degradación de calidad automáticamente.
"""

import subprocess
import pytest
import os
from pathlib import Path

# --- CONFIGURACIÓN DE UMBRALES ---
MAX_CYCLOMATIC_COMPLEXITY = 15  # Máxima complejidad permitida para un solo bloque
MIN_VULTURE_CONFIDENCE = 80     # Confianza mínima para reportar código muerto
PROJECT_ROOT = Path(__file__).resolve().parents[3]

def test_cyclomatic_complexity_audit():
    """
    DIAGNOSTIC: Radon analiza la complejidad ciclomática.
    Si un archivo es 'spaghetti' (Complejidad > MAX), el test falla.
    """
    # Radon cc app -a (total complexity)
    result = subprocess.run(
        [sys.executable, "-m", "radon", "cc", "app", "--min", "C", "--show-complexity"],
        capture_output=True, text=True
    )
    
    # Si hay bloques con complejidad C o superior, imprimimos y fallamos
    if result.stdout.strip():
        # Filtrar por bloques que excedan nuestro límite específico
        complex_blocks = []
        for line in result.stdout.split('\n'):
            if '(' in line and ')' in line:
                try:
                    score = int(line.split()[-1].strip('[]'))
                    if score > MAX_CYCLOMATIC_COMPLEXITY:
                        complex_blocks.append(line)
                except (ValueError, IndexError):
                    continue
        
        if complex_blocks:
            pytest.fail(
                f"🔥 High Complexity Debt Detected!\n"
                f"Blocks exceeding CC={MAX_CYCLOMATIC_COMPLEXITY}:\n"
                + "\n".join(complex_blocks)
            )

def test_dead_code_audit():
    """
    DIAGNOSTIC: Vulture busca código 'zombie' que no se usa.
    Un agente de IA puede usar el output de este test para podar el código.
    """
    # Vulture app/ --min-confidence 80
    result = subprocess.run(
        [sys.executable, "-m", "vulture", "app/", "--min-confidence", str(MIN_VULTURE_CONFIDENCE)],
        capture_output=True, text=True
    )
    
    # Vulture retorna exit code 1 si encuentra código muerto
    if result.returncode != 0:
        # Generamos un warning detallado en lugar de fallo total para permitir 
        # que el agente lea la lista sin detener el pipeline de despliegue si es menor.
        # Pero para Silicon Valley Grade, si el volumen es alto, debe ser crítico.
        report = result.stdout.strip()
        zombie_count = len(report.split('\n'))
        
        if zombie_count > 5:
            pytest.fail(f"🧟 High Dead Code Volume ({zombie_count} items found):\n{report}")
        else:
            print(f"⚠️ Minor Dead Code Detected:\n{report}")

def test_security_vulnerability_audit():
    """
    DIAGNOSTIC: Bandit busca vulnerabilidades comunes y placeholders peligrosos.
    """
    result = subprocess.run(
        [sys.executable, "-m", "bandit", "-r", "app", "-ll"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        pytest.fail(f"🛡️ Security Debt Found by Bandit:\n{result.stdout}")

import sys
