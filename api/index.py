from main import app

# Vercel serverless function entrypoint
# Alias 'app' to 'handler' just in case the runtime looks for it
handler = app
