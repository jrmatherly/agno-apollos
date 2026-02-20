from dataclasses import dataclass, field
from os import getenv


@dataclass
class AuthConfig:
    tenant_id: str = field(default_factory=lambda: getenv("AZURE_TENANT_ID", ""))
    client_id: str = field(default_factory=lambda: getenv("AZURE_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: getenv("AZURE_CLIENT_SECRET", ""))
    audience: str = field(default_factory=lambda: getenv("AZURE_AUDIENCE", ""))
    frontend_url: str = field(default_factory=lambda: getenv("FRONTEND_URL", "http://localhost:3000"))
    jwks_refresh_interval: int = field(default_factory=lambda: int(getenv("JWKS_REFRESH_INTERVAL", "3600")))
    jwks_miss_cooldown: int = field(default_factory=lambda: int(getenv("JWKS_MISS_COOLDOWN", "300")))
    group_sync_interval: int = field(default_factory=lambda: int(getenv("GROUP_SYNC_INTERVAL", "900")))

    @property
    def enabled(self) -> bool:
        """Auth is enabled when all required Azure env vars are set."""
        return bool(self.tenant_id and self.client_id and self.audience)

    @property
    def oidc_discovery_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/v2.0/.well-known/openid-configuration"

    @property
    def expected_issuer(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"

    @property
    def graph_base_url(self) -> str:
        return "https://graph.microsoft.com/v1.0"


# Module-level singleton — all auth modules import this instance, not the class
auth_config = AuthConfig()
