# Token Saver Tools

Scripts para ahorrar tokens al editar y leer archivos grandes.

## 1. smart_patch.py
Reemplaza texto en archivos usando patrones exactos.
Uso:
`python3 tools/smart_patch.py <target_file> <search_pattern_file> <replacement_file> [apply]`

## 2. log_strip.py
Lee las últimas N líneas de un archivo y opcionalmente filtra por patrón (grep).
Uso:
`python3 tools/log_strip.py <logfile> <lines> [grep_pattern]`

Ejemplo:
`python3 tools/log_strip.py .ai/uvicorn_test.log 50 "ERROR"`

