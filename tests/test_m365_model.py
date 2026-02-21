"""Tests for M365Connection SQLAlchemy model."""

from backend.auth.models import AuthBase


def test_m365_connection_uses_auth_base():
    from backend.auth.models import M365Connection

    assert issubclass(M365Connection, AuthBase)


def test_m365_connection_tablename():
    from backend.auth.models import M365Connection

    assert M365Connection.__tablename__ == "auth_m365_connections"


def test_m365_connection_columns():
    from backend.auth.models import M365Connection

    cols = {c.name for c in M365Connection.__table__.columns}
    expected = {"id", "user_id", "connected_at", "last_refreshed", "scopes", "cache_state", "is_active"}
    assert expected.issubset(cols)
    # No raw token columns
    assert "access_token" not in cols
    assert "refresh_token" not in cols


def test_m365_connection_user_id_fk():
    """FK must reference auth_users.id (UUID), not auth_users.oid."""
    from backend.auth.models import M365Connection

    user_id_col = M365Connection.__table__.c.user_id
    fk = list(user_id_col.foreign_keys)
    assert len(fk) == 1
    assert str(fk[0].column) == "auth_users.id"
