import os
import sys

def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    
    body = {
        "status": "success",
        "message": "Pure WSGI is ALIVE",
        "python": sys.version,
        "path": sys.path,
        "cwd": os.getcwd(),
        "env_vercel": os.getenv("VERCEL")
    }
    import json
    return [json.dumps(body).encode('utf-8')]
