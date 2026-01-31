from mangum import Mangum
from main import app

# Bridge for Vercel Serverless (AWS Lambda)
handler = Mangum(app)
