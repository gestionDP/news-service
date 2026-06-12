"""BasicAuth for UI routes."""
import base64
from fastapi import Request, HTTPException, status
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection

from app.config import settings


def _check_basic_auth(authorization: str) -> bool:
    """Verify Basic auth credentials."""
    if not settings.UI_USER or not settings.UI_PASS:
        return True  # No auth configured
    try:
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() != "basic":
            return False
        decoded = base64.b64decode(credentials).decode("utf-8")
        user, _, password = decoded.partition(":")
        return user == settings.UI_USER and password == settings.UI_PASS
    except Exception:
        return False


async def admin_api_key_dependency(request: Request):
    """
    Dependency for destructive admin endpoints (delete/clean).

    Enforced only when ADMIN_API_KEY is configured — without it the
    endpoints behave exactly as before (open), so enabling the key is a
    zero-downtime opt-in. Clients must send `X-Admin-Api-Key`; the Althara
    frontend proxy injects it from NEWS_ADMIN_API_KEY.
    (Audit 2026-06-12: the delete endpoints previously had no auth at all.)
    """
    if not settings.ADMIN_API_KEY:
        return
    provided = request.headers.get("X-Admin-Api-Key")
    if not hmac.compare_digest(provided or "", settings.ADMIN_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key",
        )


async def basic_auth_dependency(request: Request):
    """Dependency for UI routes: require BasicAuth when configured."""
    if not settings.UI_USER or not settings.UI_PASS:
        return
    auth = request.headers.get("Authorization")
    if not auth or not _check_basic_auth(auth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic realm=\"News Studio\""},
        )
