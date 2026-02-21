"""Tests for M365 tool hooks — audit logging and write guard."""

from unittest.mock import MagicMock

import pytest

from backend.tools.hooks import audit_hook, m365_write_guard


def test_audit_hook_calls_function_and_returns_result():
    mock_fn = MagicMock(return_value="result-data")
    ctx = MagicMock()
    ctx.user_id = "test-user"

    result = audit_hook("m365_list_files", mock_fn, {"folder_id": "root"}, ctx)

    assert result == "result-data"
    mock_fn.assert_called_once_with(folder_id="root")


def test_write_guard_blocks_write_operations():
    mock_fn = MagicMock()
    ctx = MagicMock()

    for name in ("m365_send_mail", "m365_create_event", "m365_update_item", "m365_delete_file", "m365_upload_file"):
        with pytest.raises(Exception, match="not permitted"):
            m365_write_guard(name, mock_fn, {}, ctx)

    mock_fn.assert_not_called()


def test_write_guard_allows_read_operations():
    mock_fn = MagicMock(return_value="read-data")
    ctx = MagicMock()

    result = m365_write_guard("m365_list_files", mock_fn, {"path": "/"}, ctx)

    assert result == "read-data"
    mock_fn.assert_called_once_with(path="/")
