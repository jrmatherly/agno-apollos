import logging

import jwt
from agno.os.scopes import get_accessible_resource_ids, has_required_scopes
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.auth.config import AuthConfig
from backend.auth.database import auth_session_factory
from backend.auth.jwks_cache import JWKSCache
from backend.auth.models import AuthDeniedToken
from backend.auth.scope_mapper import get_required_scopes, roles_to_scopes

logger = logging.getLogger(__name__)

# Routes that never require authentication
EXCLUDED_ROUTES = frozenset(
    [
        "/",
        "/health",
        "/auth/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/docs/oauth2-redirect",
    ]
)


class EntraJWTMiddleware(BaseHTTPMiddleware):
    """
    Custom JWT middleware for Microsoft Entra ID authentication.

    Sets the following request.state fields (from jwt-middleware.mdx reference):
        authenticated, user_id, session_id, scopes, authorization_enabled,
        accessible_resource_ids, token, roles, token_payload, dependencies
    """

    def __init__(self, app: ASGIApp, config: AuthConfig, jwks_cache: JWKSCache) -> None:
        super().__init__(app)
        self.config = config
        self.jwks_cache = jwks_cache

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        # Skip auth for excluded routes
        if request.url.path in EXCLUDED_ROUTES:
            _set_unauthenticated(request)
            return await call_next(request)

        # Skip auth entirely if Entra ID not configured (local dev without Azure)
        if not self.config.enabled:
            _set_unauthenticated(request)
            return await call_next(request)

        # Extract Bearer token
        token = _extract_bearer_token(request)
        if not token:
            return JSONResponse(status_code=401, content={"detail": "Missing authentication token"})

        # Validate JWT
        try:
            payload = await self._validate_token(token)
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail": "Token has expired"})
        except jwt.InvalidAudienceError:
            return JSONResponse(status_code=401, content={"detail": "Invalid audience"})
        except jwt.InvalidTokenError as e:
            logger.warning("JWT validation failed: %s", e)
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        oid = payload.get("oid")
        if not oid:
            return JSONResponse(status_code=401, content={"detail": "Token missing oid claim"})

        # Check deny list
        if await self._is_denied(oid):
            return JSONResponse(status_code=401, content={"detail": "Token revoked"})

        # Map Entra roles to Agno scopes
        roles: list[str] = payload.get("roles", [])
        scopes = roles_to_scopes(roles)

        # Determine accessible resource IDs (for list endpoint filtering)
        # Extract resource type from path (e.g., /agents/* → "agents")
        path_parts = request.url.path.strip("/").split("/")
        resource_type = path_parts[0] if path_parts else ""
        accessible_ids = get_accessible_resource_ids(scopes, resource_type) if resource_type else {"*"}

        # Check route-required scopes
        required = get_required_scopes(request.method, request.url.path)
        if required:  # None = excluded, [] = open, [str...] = check
            resource_id = path_parts[2] if len(path_parts) > 2 else None
            if not has_required_scopes(
                user_scopes=scopes,
                required_scopes=required,
                resource_type=resource_type,
                resource_id=resource_id,
            ):
                return JSONResponse(status_code=403, content={"detail": "Insufficient permissions"})

        # Set all request.state fields per jwt-middleware.mdx reference
        request.state.authenticated = True
        request.state.user_id = oid
        request.state.session_id = payload.get("session_id")
        request.state.scopes = scopes
        request.state.authorization_enabled = True
        request.state.accessible_resource_ids = accessible_ids
        request.state.token = token
        request.state.roles = roles
        request.state.token_payload = payload
        request.state.dependencies = {
            "name": payload.get("name"),
            "email": payload.get("preferred_username"),
            "roles": roles,
            "oid": oid,
            "tid": payload.get("tid"),
        }
        request.state.session_state = {}

        return await call_next(request)

    async def _validate_token(self, token: str) -> dict:  # type: ignore[type-arg]
        """Validate JWT signature and claims against Entra ID JWKS."""
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise jwt.InvalidTokenError("Token missing kid header")

        # Get public key from cache
        public_key = self.jwks_cache.get_key(kid)
        if public_key is None:
            # Key not in cache — attempt throttled re-fetch
            public_key = await self.jwks_cache.fetch_on_miss(kid)
        if public_key is None:
            raise jwt.InvalidTokenError(f"Unknown signing key: {kid}")

        # Validate: RS256 only, audience, issuer, expiry, clock skew tolerance
        payload: dict = jwt.decode(  # type: ignore[type-arg]
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=self.config.audience,
            issuer=self.config.expected_issuer,
            options={
                "verify_exp": True,
                "verify_nbf": True,
                "verify_aud": True,
                "verify_iss": True,
                "require": ["exp", "iss", "aud", "oid"],
            },
            leeway=30,  # 30s clock skew tolerance
        )

        # Validate azp (authorized party) to confirm token issued by our app
        azp = payload.get("azp") or payload.get("appid")
        if azp and azp != self.config.client_id:
            raise jwt.InvalidTokenError("Token not issued for this application")

        return payload

    async def _is_denied(self, oid: str) -> bool:
        """Check token deny list."""
        async with auth_session_factory() as session:
            result = await session.execute(
                select(AuthDeniedToken)
                .where(
                    AuthDeniedToken.oid == oid,
                    AuthDeniedToken.expires_at > func.now(),
                )
                .limit(1)
            )
            return result.scalar_one_or_none() is not None


def _extract_bearer_token(request: Request) -> str | None:
    """Extract JWT from Authorization: Bearer <token> header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def _set_unauthenticated(request: Request) -> None:
    """Set request.state for unauthenticated/passthrough requests."""
    request.state.authenticated = False
    request.state.authorization_enabled = False
