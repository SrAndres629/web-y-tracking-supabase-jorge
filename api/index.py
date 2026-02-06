from main import app
from mangum import Mangum

# Wrap API for Vercel Serverless (AWS Lambda compatibility)
# Vercel-Python Runtime will invoke this 'handler'
handler = Mangum(app)
