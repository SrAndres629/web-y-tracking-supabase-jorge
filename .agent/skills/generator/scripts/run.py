#!/usr/bin/env python3

import json
import subprocess
import sys


def main():
    # 1. Leer la entrada del usuario (stdin)
    # En un entorno real, esto podría ser un JSON complejo.
    # Para este ejemplo, asumimos que el usuario pasa un comando simple.

    # Si no hay argumentos, pedimos uno
    if len(sys.argv) < 2:
        print("Uso: python run.py <comando>")
        sys.exit(1)

    command = sys.argv[1]

    # 2. Ejecutar el comando del sistema
    # Usamos shell=True para simplicidad, pero en producción usaríamos otras rutas.
    try:
        # Ejecutamos el comando y capturamos la salida
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )

        # 3. Devolver el resultado en formato JSON (stdout)
        # El agente leerá esto y lo mostrará al usuario.
        output_data = {
            "status": "success",
            "command_executed": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
        }

        print(json.dumps(output_data, indent=2))

    except subprocess.CalledProcessError as e:
        # Si el comando falla, devolvemos un error JSON
        error_data = {
            "status": "error",
            "command_executed": command,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "return_code": e.returncode,
            "error_message": str(e),
        }
        print(json.dumps(error_data, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
