from main import app
from mangum import Mangum

# Wrap API for Vercel Serverless (AWS Lambda compatibility)
handler = Mangum(app)
