#!/usr/bin/env python3
"""
Script de ejemplo para ejecutar desde una Skill de Antigravity.
"""

import sys
import json

def main():
    # Leer argumentos de la línea de comandos
    # El primer argumento (sys.argv[0]) es el nombre del script
    # Los argumentos reales empiezan en sys.argv[1]
    args = sys.argv[1:]
    
    # Si no hay argumentos, mostrar ayuda
    if not args:
        print("Uso: python run.py <argumento1> <argumento2> ...")
        print("\nEjemplo: python run.py hola mundo")
        sys.exit(1)
    
    # Procesar argumentos
    result = {
        "input_args": args,
        "message": f"Procesados {len(args)} argumentos",
        "output": [arg.upper() for arg in args]  # Ejemplo: convertir a mayúsculas
    }
    
    # Imprimir resultado en formato JSON
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()