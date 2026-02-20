from backend.db.session import get_eval_db, get_postgres_db
from agno.db.postgres import PostgresDb


def test_get_eval_db_returns_postgres_db():
    db = get_eval_db()
    assert isinstance(db, PostgresDb)


def test_get_eval_db_has_eval_table():
    db = get_eval_db()
    # PostgresDb stores eval_table as eval_table_name (defaults to "agno_eval_runs" if not set)
    assert db.eval_table_name == "eval_runs"


def test_get_postgres_db_unchanged():
    db = get_postgres_db()
    assert isinstance(db, PostgresDb)
    # existing function doesn't set eval_table, so it defaults to "agno_eval_runs"
    assert db.eval_table_name == "agno_eval_runs"
