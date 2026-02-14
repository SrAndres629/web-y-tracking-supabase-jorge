"""
🤖 AI-Powered Technical Debt & Placeholder Detector
Jorge Aguirre Flores Web - Silicon Valley Protocol

Este script permite a un agente de IA auditar la "salud" del código buscando:
1. Placeholders (TODO, FIXME, PLACEHOLDER)
2. Deuda técnica etiquetada (HACK, LEGACY, REFACTOR)
3. Hardcoded values (En áreas sensibles)
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

# --- CONFIGURACIÓN ---
IGNORE_DIRS = {'.git', 'venv', '__pycache__', 'static', 'node_modules', 'htmlcov'}
DEBT_TAGS = ['TODO', 'FIXME', 'PLACEHOLDER', 'HACK', 'LEGACY', 'REFACTOR']
SENSITIVE_FILES = ['main.py', 'database.py', 'settings.py', 'config.py']

class DebtAuditor:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.debt_found = []

    def scan(self):
        """Escanea recursivamente el proyecto por etiquetas de deuda."""
        print(f"🔍 AI Debugger: Escaneando technical debt en {self.root_dir}...")
        
        for root, dirs, files in os.walk(self._root_dir_str()):
            # Filtrar directorios ignorados
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file.endswith('.py') or file.endswith('.html') or file.endswith('.md'):
                    self._audit_file(Path(root) / file)
        
        return self.debt_found

    def _root_dir_str(self):
        return str(self.root_dir)

    def _audit_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    for tag in DEBT_TAGS:
                        if tag in line.upper():
                            # Extraer comentario
                            match = re.search(f"{tag}:? (.*)", line, re.IGNORECASE)
                            comment = match.group(1) if match else "No details"
                            
                            self.debt_found.append({
                                'file': str(file_path.relative_to(self.root_dir)),
                                'line': i + 1,
                                'tag': tag,
                                'content': comment.strip()
                            })
        except Exception as e:
            print(f"⚠️ Error leyendo {file_path}: {e}")

    def report(self):
        """Genera un reporte legible para el agente de IA."""
        if not self.debt_found:
            print("✅ Clean Code: No se encontró deuda técnica explícita ni placeholders.")
            return

        print(f"\n📊 REPORT: {len(self.debt_found)} DEBT ITEMS FOUND\n")
        print("| File | Line | Tag | Content |")
        print("| :--- | :--- | :--- | :--- |")
        
        # Ordenar por criticidad (FIXME/HACK > TODO > LEGACY)
        priority = {'FIXME': 0, 'HACK': 1, 'PLACEHOLDER': 2, 'TODO': 3, 'LEGACY': 4, 'REFACTOR': 5}
        sorted_debt = sorted(self.debt_found, key=lambda x: priority.get(x['tag'], 99))

        for item in sorted_debt:
            print(f"| {item['file']} | {item['line']} | **{item['tag']}** | {item['content']} |")

if __name__ == "__main__":
    # Si se ejecuta como script, analizar desde el root
    root = Path(__file__).parent.parent.parent
    auditor = DebtAuditor(root)
    auditor.scan()
    auditor.report()
