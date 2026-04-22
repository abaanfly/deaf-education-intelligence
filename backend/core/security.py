"""Simple header-based admin token guard.

Frontend must send `X-Admin-Token: <value>` matching the `ADMIN_TOKEN` env var
on any mutation of the open dataset. This is intentionally minimal — it is
meant to prevent casual demo-user abuse, not replace proper auth.
"""
from fastapi import Header, HTTPException, status
from core.db import ADMIN_TOKEN


async def require_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    if not ADMIN_TOKEN:
        # Server mis-configured — fail closed.
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Admin token not configured")
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid admin token")
