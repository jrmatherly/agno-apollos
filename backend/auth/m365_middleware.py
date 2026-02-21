"""
M365 Token Propagation Middleware
---------------------------------
Sets the user's Graph token in contextvars for header_provider to read.
Runs after EntraJWTMiddleware (which sets request.state.token).
"""

from __future__ import annotations

import asyncio
import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.tools.m365 import clear_graph_token, set_graph_token

log = logging.getLogger(__name__)


class M365TokenMiddleware(BaseHTTPMiddleware):
    """
    For authenticated requests, resolves the user's Graph token and
    sets it in contextvars so Agno's header_provider can read it.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if getattr(request.state, "authenticated", False):
            user_oid = getattr(request.state, "user_id", None)
            if user_oid:
                from backend.auth.m365_token_service import get_obo_service

                service = get_obo_service()
                # acquire_token_silent: cache hit ~0ms, refresh ~200ms -- run in thread to avoid blocking
                graph_token = await asyncio.to_thread(service.get_graph_token, user_oid)
                if graph_token:
                    set_graph_token(graph_token)

        try:
            response = await call_next(request)
        finally:
            clear_graph_token()

        return response
