"""
Tracing Configuration
---------------------

Dual-layer observability for Apollos AI:

Layer 1 — Built-in trace-to-database: Stores all traces in PostgreSQL
via Agno's setup_tracing(). Always-on when TRACING_ENABLED=true.
Traces queryable programmatically (get_trace, get_spans).

Layer 2 — OTLP multi-exporter: Exports traces to external platforms
(Langfuse, Arize Phoenix, SIEM, or any OTLP backend) via standard
OpenInference instrumentation. Activated when OTLP_ENDPOINTS is set.

Env vars:
    TRACING_ENABLED     Enable trace-to-database (default: false)
    OTLP_ENDPOINTS      Comma-separated OTLP endpoint URLs
    OTLP_AUTH_HEADERS   Comma-separated auth headers (parallel to endpoints)

Future: For complex routing/filtering, add an OTel Collector as a
Docker service and point OTLP_ENDPOINTS at it — zero code changes.
"""

import logging
from os import getenv

logger = logging.getLogger(__name__)


def configure_telemetry() -> None:
    """Set up observability layers.

    Layer 1: Agno trace-to-database (if TRACING_ENABLED=true)
    Layer 2: OTLP multi-export (if OTLP_ENDPOINTS is set)

    Safe to call unconditionally — no-ops when not configured.
    """
    _setup_trace_to_database()
    _setup_otlp_export()


def _setup_trace_to_database() -> None:
    """Layer 1: Store traces in PostgreSQL via Agno's built-in tracing."""
    if getenv("TRACING_ENABLED", "").lower() not in ("true", "1", "yes"):
        return

    from agno.tracing import setup_tracing

    from backend.db import get_postgres_db

    trace_db = get_postgres_db()
    setup_tracing(db=trace_db)
    logger.info("Trace-to-database enabled (PostgreSQL)")


def _setup_otlp_export() -> None:
    """Layer 2: Export traces to external platforms via OTLP.

    Supports multiple simultaneous backends (Langfuse, SIEM, etc.).
    Uses OpenInference instrumentation for Agno-aware span attributes.
    """
    endpoints_raw = getenv("OTLP_ENDPOINTS", "") or getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if not endpoints_raw:
        return

    from openinference.instrumentation.agno import AgnoInstrumentor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    endpoints = [e.strip() for e in endpoints_raw.split(",") if e.strip()]
    headers_raw = getenv("OTLP_AUTH_HEADERS", "")
    headers_list = [h.strip() for h in headers_raw.split(",") if h.strip()] if headers_raw else []

    provider = TracerProvider()

    for i, endpoint in enumerate(endpoints):
        # Parse auth header for this endpoint (if provided)
        exporter_headers: dict[str, str] = {}
        if i < len(headers_list) and headers_list[i]:
            key, _, value = headers_list[i].partition("=")
            if key and value:
                exporter_headers[key] = value

        # Normalize endpoint — append /v1/traces if not already present
        trace_endpoint = endpoint
        if not trace_endpoint.endswith("/v1/traces"):
            trace_endpoint = f"{trace_endpoint.rstrip('/')}/v1/traces"

        exporter = OTLPSpanExporter(endpoint=trace_endpoint, headers=exporter_headers)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("OTLP export configured: %s", endpoint)

    AgnoInstrumentor().instrument(tracer_provider=provider)
    logger.info("OpenInference instrumentation active (%d endpoint(s))", len(endpoints))
