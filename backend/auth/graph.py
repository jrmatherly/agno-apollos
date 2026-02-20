import asyncio

import httpx


class GraphClient:
    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_user_groups_delegated(self, user_token: str) -> list[dict]:  # type: ignore[type-arg]
        """Login-time sync: get user's groups using their delegated token."""
        return await self._get_groups_paginated(
            f"{self.BASE_URL}/me/transitiveMemberOf",
            headers={"Authorization": f"Bearer {user_token}"},
        )

    async def get_user_groups_app(self, user_oid: str) -> list[dict]:  # type: ignore[type-arg]
        """Background sync: get user's groups using client credentials app token."""
        app_token = await self._get_app_token()
        return await self._get_groups_paginated(
            f"{self.BASE_URL}/users/{user_oid}/transitiveMemberOf",
            headers={"Authorization": f"Bearer {app_token}"},
        )

    async def get_user_info(self, user_oid: str) -> dict | None:  # type: ignore[type-arg]
        """Get basic user info from Graph (for sync)."""
        app_token = await self._get_app_token()
        resp = await self._client.get(
            f"{self.BASE_URL}/users/{user_oid}",
            headers={"Authorization": f"Bearer {app_token}"},
            params={"$select": "id,displayName,mail,userPrincipalName,accountEnabled"},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]

    async def _get_groups_paginated(self, url: str, headers: dict) -> list[dict]:  # type: ignore[type-arg]
        """Fetch all groups with pagination and 429 retry handling."""
        groups: list[dict] = []  # type: ignore[type-arg]
        next_link: str | None = url
        params: dict | None = {"$select": "id,displayName", "$top": "999"}  # type: ignore[type-arg]

        while next_link:
            resp = None
            for attempt in range(4):
                resp = await self._client.get(next_link, headers=headers, params=params if "?" not in next_link else None)
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 2**attempt))
                    await asyncio.sleep(retry_after)
                    continue
                resp.raise_for_status()
                break

            if resp is None:
                break

            data = resp.json()
            for item in data.get("value", []):
                if item.get("@odata.type") == "#microsoft.graph.group":
                    groups.append(item)
            next_link = data.get("@odata.nextLink")
            params = None  # next_link already has params embedded

        return groups

    async def _get_app_token(self) -> str:
        """Acquire app-only token via client credentials flow."""
        resp = await self._client.post(
            f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": "https://graph.microsoft.com/.default",
            },
        )
        resp.raise_for_status()
        return str(resp.json()["access_token"])

    async def close(self) -> None:
        await self._client.aclose()
