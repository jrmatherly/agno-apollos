"""
Knowledge Loaders
-----------------

Multi-source document loading for the knowledge base.
Supports URL, PDF, and CSV sources with extensible reader support.
"""

import logging
from pathlib import Path

from agno.knowledge.reader.csv_reader import CSVReader
from agno.knowledge.reader.pdf_reader import PDFReader

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Reader Instances
# ---------------------------------------------------------------------------
pdf_reader = PDFReader()
csv_reader = CSVReader()

# ---------------------------------------------------------------------------
# Data Directory
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "docs"


def load_pdf_documents(knowledge: object) -> int:
    """Load all PDF files from data/docs/ into the knowledge base.

    Args:
        knowledge: Knowledge instance with an insert method.

    Returns:
        Number of documents loaded.
    """
    if not DATA_DIR.exists():
        logger.info("Data directory %s does not exist, skipping PDF loading", DATA_DIR)
        return 0

    count = 0
    for pdf_path in sorted(DATA_DIR.glob("*.pdf")):
        try:
            documents = pdf_reader.read(pdf_path)
            for doc in documents:
                knowledge.load_documents(documents=[doc])  # type: ignore[attr-defined]
            count += 1
            logger.info("Loaded PDF: %s", pdf_path.name)
        except Exception:
            logger.exception("Failed to load PDF: %s", pdf_path.name)
    return count


def load_csv_documents(knowledge: object) -> int:
    """Load all CSV files from data/docs/ into the knowledge base.

    Args:
        knowledge: Knowledge instance with an insert method.

    Returns:
        Number of documents loaded.
    """
    if not DATA_DIR.exists():
        logger.info("Data directory %s does not exist, skipping CSV loading", DATA_DIR)
        return 0

    count = 0
    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        try:
            documents = csv_reader.read(csv_path)
            for doc in documents:
                knowledge.load_documents(documents=[doc])  # type: ignore[attr-defined]
            count += 1
            logger.info("Loaded CSV: %s", csv_path.name)
        except Exception:
            logger.exception("Failed to load CSV: %s", csv_path.name)
    return count
