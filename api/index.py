import json

def app(environ, start_response):
    """
    Standard WSGI Application (Guaranteed for @vercel/python)
    """
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    
    body = {
        "status": "alive",
        "message": "Hello from Minimal WSGI App",
        "check": "Vercel Config & Runtime are OK.",
        "env": str(environ.get('VERCEL_ENV', 'unknown'))
    }
    return [json.dumps(body).encode('utf-8')]
