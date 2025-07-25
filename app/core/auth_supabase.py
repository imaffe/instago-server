from typing import Optional, Dict, List, Any
import requests
from jose import jwt, jwk
from jose.utils import base64url_decode
from jose.exceptions import ExpiredSignatureError, JWTError
import json

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


class SupabaseAuthService:
    def __init__(self):
        # Use project ID from env
        self.project_id = settings.SUPABASE_PROJECT_ID
        self.jwks_url = f"https://{self.project_id}.supabase.co/auth/v1/keys"
        self.audience = "authenticated"

        # Cache for JWKS
        self._jwks_cache = None

        logger.info(f"Initialized Supabase auth with JWKS URL: {self.jwks_url}")

    def get_jwks(self) -> List[Dict]:
        """Fetch JWKS from Supabase"""
        try:
            if self._jwks_cache is None:
                # Include service role key in the request headers
                headers = {
                    "apikey": settings.SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
                }
                response = requests.get(self.jwks_url, headers=headers)
                response.raise_for_status()
                self._jwks_cache = response.json()["keys"]
                logger.debug(f"Fetched JWKS: {len(self._jwks_cache)} keys")
            return self._jwks_cache
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            # Clear cache on error
            self._jwks_cache = None
            raise

    def verify_token_with_jwks(self, token: str) -> dict:
        """Verify Supabase JWT token using JWKS (for future migration)"""
        try:
            logger.debug(f"Attempting to verify token with JWKS: {token[:20]}...")

            # Get JWKS
            jwks = self.get_jwks()

            # Get the unverified header to find the key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            # Find the matching key
            key_dict = None
            for key in jwks:
                if key["kid"] == kid:
                    key_dict = key
                    break

            if not key_dict:
                raise ValueError(f"Unable to find a signing key that matches: {kid}")

            # Convert the key to a usable format
            public_key = jwk.construct(key_dict)

            # Decode and verify the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.audience,
                options={"verify_aud": False}
            )

            return payload

        except Exception as e:
            logger.error(f"JWKS verification failed: {e}")
            raise

    def verify_token(self, token: str) -> dict:
        """Verify Supabase JWT token using JWT secret"""
        try:
            logger.debug(f"Attempting to verify token: {token[:20]}...")

            # Decode and verify the token using the JWT secret
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],  # Supabase uses HS256 with the JWT secret
                audience=self.audience,
                options={
                    "verify_aud": False,  # Set to True if you want to check audience
                    "verify_exp": True,
                    "verify_signature": True
                }
            )

            logger.info(f"Token verified successfully for user: {payload.get('sub')}")
            logger.debug(f"Token payload: {payload}")

            return payload

        except ExpiredSignatureError:
            logger.error("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.exception("JWT verification failed")
            logger.error(f"JWT validation error: {e}")
            logger.error(f"Token that failed: {token[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """Get current user from JWT token"""
        logger.debug(f"Authorization header received: {credentials.scheme} {credentials.credentials[:20]}...")

        token = credentials.credentials
        payload = self.verify_token(token)

        user_id = payload.get("sub")
        if not user_id:
            logger.error(f"No user ID found in token payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )

        # Extract user metadata
        user_metadata = payload.get("user_metadata", {})
        app_metadata = payload.get("app_metadata", {})

        user_data = {
            "id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "authenticated"),
            "aud": payload.get("aud"),
            "user_metadata": user_metadata,
            "app_metadata": app_metadata
        }

        logger.info(f"Authenticated user: {user_data['email']} (ID: {user_id})")

        return user_data


# Initialize the service
supabase_auth = SupabaseAuthService()


async def get_current_user_id(
    current_user: dict = Depends(supabase_auth.get_current_user)
) -> str:
    """Dependency to get current user ID"""
    return current_user["id"]


async def get_current_user(
    current_user: dict = Depends(supabase_auth.get_current_user)
) -> dict:
    """Dependency to get full current user data"""
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None

    try:
        return await supabase_auth.get_current_user(credentials)
    except HTTPException:
        return None
