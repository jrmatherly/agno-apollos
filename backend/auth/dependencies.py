from fastapi import Depends, HTTPException, Request

from agno.os.scopes import has_required_scopes


def get_current_user(request: Request) -> dict:  # type: ignore[type-arg]
    """Require an authenticated user. Returns token payload."""
    if not getattr(request.state, "authenticated", False):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.token_payload  # type: ignore[no-any-return]


def require_scope(scope: str):  # type: ignore[return]
    """FastAPI dependency factory: require a specific scope."""

    def _check(request: Request) -> None:
        scopes: list[str] = getattr(request.state, "scopes", [])
        if not has_required_scopes(user_scopes=scopes, required_scopes=[scope]):
            raise HTTPException(status_code=403, detail=f"Requires scope: {scope}")

    return Depends(_check)
