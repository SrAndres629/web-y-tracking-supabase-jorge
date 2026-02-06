import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db_connection
import json

def enrich_data():
    services = [
        {
            "id": "microblading",
            "title": "Microblading 3D",
            "subtitle": "Efecto Pelo a Pelo",
            "description": "Técnica pelo a pelo para cejas ultra naturales. Rellena huecos y recupera la forma joven de tu ceja.",
            "icon": "fa-eye-dropper",
            "image": "/static/images/service_brows.webp",
            "rating": "4.9",
            "clients": "+620",
            "badges": ["Más Pedido", "100% Natural", "2-3 años"],
            "benefits": ["2 hrs sesión", "Sin dolor", "Retoque incluido"]
        },
        {
            "id": "eyeliner",
            "title": "Delineado Permanente",
            "subtitle": "Efecto Pestañas",
            "description": "Despierta con una mirada intensa y expresiva. Olvídate de que se corra el maquillaje.",
            "icon": "fa-eye",
            "image": "/static/images/service_eyes.webp",
            "rating": "4.9",
            "clients": "+480",
            "badges": ["Sin Dolor", "Efecto Pestañas", "2-3 años"],
            "benefits": ["1.5 hrs sesión", "Anestesia tópica", "Resultados inmediatos"]
        },
        {
            "id": "lips",
            "title": "Labios Full Color",
            "subtitle": "Corrección y Volumen",
            "description": "Corrige asimetrías y luce una boca jugosa y saludable. Tu color perfecto sin retocarte.",
            "icon": "fa-kiss-wink-heart",
            "image": "/static/images/service_lips.webp",
            "rating": "5.0",
            "clients": "+400",
            "badges": ["Premium", "Color Natural", "1-2 años"],
            "benefits": ["2 hrs sesión", "Corrige volumen", "Efecto rejuvenecedor"]
        }
    ]
    
    contact = {
        "whatsapp": "https://wa.me/59164714751",
        "phone": "+591 64714751",
        "email": "contacto@jorgeaguirreflores.com",
        "location": "Santa Cruz de la Sierra, Bolivia",
        "instagram": "https://instagram.com/jorgeaguirreflores",
        "cta_text": "Hola Jorge, quisiera iniciar mi diagnóstico de diseño facial.",
        "cta_assessment": "Hola Jorge, quiero agendar mi diagnóstico gratuito y ver la geometría de mi rostro."
    }

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE site_content SET value = %s WHERE key = 'services_config'",
                    (json.dumps(services),)
                )
                cur.execute(
                    "UPDATE site_content SET value = %s WHERE key = 'contact_config'",
                    (json.dumps(contact),)
                )
                print("✅ [CMS] Data enriched successfully in Supabase.")
    except Exception as e:
        print(f"❌ [CMS] Error enriching data: {e}")

if __name__ == "__main__":
    enrich_data()
