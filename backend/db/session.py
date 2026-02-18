"""
Database Session
----------------

PostgreSQL database connection for Apollos AI.
"""

from os import getenv

from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

from backend.db.url import db_url

LITELLM_BASE_URL = getenv("LITELLM_BASE_URL", "http://localhost:4000/v1")
LITELLM_API_KEY = getenv("LITELLM_API_KEY", "")
EMBEDDING_MODEL_ID = getenv("EMBEDDING_MODEL_ID", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(getenv("EMBEDDING_DIMENSIONS", "1536"))

DB_ID = "apollos-db"


def get_postgres_db(contents_table: str | None = None) -> PostgresDb:
    """Create a PostgresDb instance.

    Args:
        contents_table: Optional table name for storing knowledge contents.

    Returns:
        Configured PostgresDb instance.
    """
    if contents_table is not None:
        return PostgresDb(id=DB_ID, db_url=db_url, knowledge_table=contents_table)
    return PostgresDb(id=DB_ID, db_url=db_url)


def create_knowledge(name: str, table_name: str) -> Knowledge:
    """Create a Knowledge instance with PgVector hybrid search.

    Args:
        name: Display name for the knowledge base.
        table_name: PostgreSQL table name for vector storage.

    Returns:
        Configured Knowledge instance.
    """
    return Knowledge(
        name=name,
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(
                id=EMBEDDING_MODEL_ID,
                dimensions=EMBEDDING_DIMENSIONS,
                base_url=LITELLM_BASE_URL,
                api_key=LITELLM_API_KEY,
            ),
        ),
        contents_db=get_postgres_db(contents_table=f"{table_name}_contents"),
    )
