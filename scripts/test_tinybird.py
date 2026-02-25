import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TINYBIRD_ADMIN_TOKEN = os.getenv("TINYBIRD_ADMIN_TOKEN")
TINYBIRD_API_URL = os.getenv("TINYBIRD_API_URL", "https://api.northamerica-northeast2.gcp.tinybird.co")

async def test_connection():
    if not TINYBIRD_ADMIN_TOKEN:
        print("❌ Error: TINYBIRD_ADMIN_TOKEN not found in .env")
        return

    print(f"🔍 Testing connection to Tinybird at {TINYBIRD_API_URL}...")
    headers = {
        "Authorization": f"Bearer {TINYBIRD_ADMIN_TOKEN}"
    }

    async with httpx.AsyncClient() as client:
        try:
            # Try to list data sources
            response = await client.get(f"{TINYBIRD_API_URL}/v0/datasources", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print("✅ Connection Successful!")
                print(f"Found {len(data.get('datasources', []))} datasources.")
                for ds in data.get('datasources', [])[:5]:
                    print(f" - {ds.get('name')}")
            else:
                print(f"❌ Connection Failed ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connection())
