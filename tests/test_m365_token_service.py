"""Tests for OBOTokenService — uses MSAL mock to avoid real Entra calls."""

from unittest.mock import MagicMock, patch


def test_module_importable():
    """Service must import without real credentials (lazy init)."""
    from backend.auth.m365_token_service import OBOTokenService

    assert OBOTokenService is not None


def test_get_graph_token_none_when_not_connected():
    """Returns None for user with no cached tokens."""
    from backend.auth.m365_token_service import OBOTokenService

    service = OBOTokenService.__new__(OBOTokenService)
    service._user_apps = {}
    result = service.get_graph_token("non-existent-oid")
    assert result is None


def test_connect_returns_token_on_success():
    """connect() must return access_token on successful OBO exchange."""
    from backend.auth.m365_token_service import OBOTokenService

    service = OBOTokenService.__new__(OBOTokenService)
    service._user_apps = {}
    service._user_locks = {}
    service._tenant_id = "fake-tenant"
    service._client_id = "fake-client"
    service._client_secret = "fake-secret"
    service._authority = "https://login.microsoftonline.com/fake-tenant"

    with patch("msal.ConfidentialClientApplication") as MockApp:
        mock_instance = MockApp.return_value
        mock_instance.acquire_token_on_behalf_of.return_value = {
            "access_token": "graph-token-123",
            "scope": "Mail.Read Calendars.Read",
        }
        mock_instance.get_accounts.return_value = [{"username": "user@org.com"}]

        result = service.connect("test-oid", "fake-jwt")
        assert result["connected"] is True
        assert "access_token" not in result  # never expose token to client


def test_get_graph_token_uses_silent_first():
    """get_graph_token() must try acquire_token_silent before OBO."""
    from backend.auth.m365_token_service import OBOTokenService

    service = OBOTokenService.__new__(OBOTokenService)
    service._user_locks = {}

    mock_app = MagicMock()
    mock_app.get_accounts.return_value = [{"username": "user@org.com"}]
    mock_app.acquire_token_silent.return_value = {"access_token": "cached-token"}
    service._user_apps = {"test-oid": mock_app}

    token = service.get_graph_token("test-oid")
    assert token == "cached-token"
    mock_app.acquire_token_silent.assert_called_once()
    mock_app.acquire_token_on_behalf_of.assert_not_called()


def test_disconnect_removes_user():
    """disconnect() clears all per-user state."""
    from backend.auth.m365_token_service import OBOTokenService

    service = OBOTokenService.__new__(OBOTokenService)
    service._user_apps = {"test-oid": MagicMock()}
    service._user_locks = {"test-oid": MagicMock()}

    service.disconnect("test-oid")
    assert "test-oid" not in service._user_apps
    assert "test-oid" not in service._user_locks


def test_status_not_connected():
    """status() returns connected=False for unknown user."""
    from backend.auth.m365_token_service import OBOTokenService

    service = OBOTokenService.__new__(OBOTokenService)
    service._user_apps = {}

    result = service.status("unknown-oid")
    assert result["connected"] is False


def test_encrypt_decrypt_roundtrip():
    """Fernet encryption roundtrips correctly."""
    import os

    os.environ["M365_CACHE_KEY"] = ""
    os.environ["AZURE_CLIENT_SECRET"] = "test-secret-for-derivation"

    # Reset cached key
    import backend.auth.m365_token_service as mod

    mod._CACHE_KEY = None

    plaintext = '{"token_cache": "data"}'
    encrypted = mod.encrypt_cache(plaintext)
    assert isinstance(encrypted, bytes)
    assert encrypted != plaintext.encode()
    decrypted = mod.decrypt_cache(encrypted)
    assert decrypted == plaintext
