def handler(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    return [b'{"status": "wsgi_success", "message": "Python Runtime is HEALTHY"}']

# Alias app to handler just in case
app = handler
