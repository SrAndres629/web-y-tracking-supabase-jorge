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
            "check": "Vercel Config FIXED. 'api/index.py' explicitly mapped."
        })
    }
