
import hashlib
import logging
from typing import Optional, Dict, Any
from app.database import get_cursor, BACKEND

logger = logging.getLogger(__name__)

class ClientService:
    @staticmethod
    def get_client_by_api_key(api_key: str) -> Optional[Dict[str, Any]]:
        """Look up client by hashed API key."""
        if not api_key:
            return None
            
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        try:
            with get_cursor() as cur:
                query = """
                    SELECT c.id, c.name, c.meta_pixel_id, c.meta_access_token, c.plan
                    FROM clients c
                    JOIN api_keys ak ON c.id = ak.client_id
                    WHERE ak.key_hash = %s AND ak.status = 'active' AND c.status = 'active'
                """
                if BACKEND != "postgres":
                    query = query.replace("%s", "?")
                
                cur.execute(query, (key_hash,))
                row = cur.fetchone()
                if row:
                    # Map row to dict
                    cols = [col[0] for col in cur.description]
                    return dict(zip(cols, row))
            return None
        except Exception as e:
            logger.error(f"Error looking up client by API key: {e}")
            return None

    @staticmethod
    async def create_client(name: str, email: str, company: str, meta_pixel_id: str, meta_access_token: str, plan: str = 'starter') -> Optional[Dict[str, Any]]:
        """Create a new client and return client_id and raw API key."""
        import secrets
        api_key = f"ag_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        try:
            with get_cursor() as cur:
                # 1. Insert Client
                query_client = """
                    INSERT INTO clients (name, email, company, meta_pixel_id, meta_access_token, plan) 
                    VALUES (%s, %s, %s, %s, %s, %s) 
                    RETURNING id
                """
                if BACKEND != "postgres":
                    query_client = "INSERT INTO clients (name, email, company, meta_pixel_id, meta_access_token, plan) VALUES (?, ?, ?, ?, ?, ?)"
                    cur.execute(query_client, (name, email, company, meta_pixel_id, meta_access_token, plan))
                    client_id = cur.lastrowid
                else:
                    cur.execute(query_client, (name, email, company, meta_pixel_id, meta_access_token, plan))
                    client_id = cur.fetchone()[0]

                if not client_id:
                    return None
                
                # 2. Insert API Key
                query_key = "INSERT INTO api_keys (client_id, key_hash, name) VALUES (%s, %s, %s)"
                if BACKEND != "postgres":
                    query_key = query_key.replace("%s", "?")
                
                cur.execute(query_key, (client_id, key_hash, "Default Key"))
            
            return {
                "client_id": client_id,
                "api_key": api_key
            }
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            return None
