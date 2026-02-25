import hashlib
import base64
import logging
from typing import Optional, List

from fastapi import HTTPException
from jose import jwt, JWTError

from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

def verify_qstash_signature(token: str, body: bytes, url: str) -> None:
    """
    Verifies the QStash signature (JWT) against the request body and URL.

    Args:
        token: The 'Upstash-Signature' header value (JWT).
        body: The raw request body bytes.
        url: The full URL of the request (e.g. https://.../hooks/process-event).

    Raises:
        HTTPException(401) if verification fails.
    """
    current_key = settings.external.qstash_current_signing_key
    next_key = settings.external.qstash_next_signing_key

    if not current_key and not next_key:
        logger.error("❌ QStash signing keys are missing in configuration.")
        # If keys are missing, we cannot verify, so fail closed (500 or 401).
        # Assuming if keys are missing we are misconfigured.
        raise HTTPException(status_code=500, detail="Configuration error: Missing signing keys")

    keys: List[str] = []
    if current_key:
        keys.append(current_key)
    if next_key:
        keys.append(next_key)

    last_exception = None
    success = False

    for key in keys:
        try:
            # decode checks signature and standard claims (exp, nbf)
            # We also verify 'iss' and 'sub'
            claims = jwt.decode(
                token,
                key,
                algorithms=["HS256"],
                issuer="Upstash",
                subject=url,
                options={"verify_aud": False}
            )

            # Verify body hash
            # Calculate SHA256 of the body
            body_hash = hashlib.sha256(body).digest()
            # Try Base64URL first (standard for JWT)
            calculated_hash_b64url = base64.urlsafe_b64encode(body_hash).rstrip(b"=").decode("utf-8")

            claim_body_hash = claims.get("body")

            if claim_body_hash == calculated_hash_b64url:
                success = True
                break

            # If not matching, try standard Base64
            calculated_hash_std = base64.b64encode(body_hash).decode("utf-8")
            if claim_body_hash == calculated_hash_std:
                success = True
                break

            # If not matching, try Hex
            calculated_hash_hex = hashlib.sha256(body).hexdigest()
            if claim_body_hash == calculated_hash_hex:
                success = True
                break

            raise JWTError(f"Body hash mismatch. Claim: {claim_body_hash}, Calc: {calculated_hash_b64url}")

        except JWTError as e:
            last_exception = e
            continue
        except Exception as e:
            logger.warning(f"Unexpected error verifying signature with key: {e}")
            last_exception = e
            continue

    if not success:
        logger.warning(f"⚠️ QStash signature verification failed: {last_exception}")
        raise HTTPException(status_code=401, detail="Invalid signature")
