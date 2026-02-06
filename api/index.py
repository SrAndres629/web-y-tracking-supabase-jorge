import json

def handler(request):
    """
    MINIMAL TEST HANDLER (No Dependencies)
    """
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "alive",
            "message": "Hello from Minimal Python Handler",
            "check": "If you see this, Vercel Config is OK. App Dependencies are the problem."
        })
    }
