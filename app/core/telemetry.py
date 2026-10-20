"""OpenTelemetry observability and GenAI tracing for SlothPilot multi-agent runs with zero-dependency fallback."""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

_RECORDED_SPANS: List[Dict[str, Any]] = []

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    HAS_OTEL_SDK = True
except ImportError:
    HAS_OTEL_SDK = False


class _FallbackSpan:
    """Lightweight span context manager when opentelemetry-sdk is not installed."""
    def __init__(self, name: str, tracer: _FallbackTracer):
        self.name = name
        self.tracer = tracer
        self.attributes: Dict[str, Any] = {}
        self.start_time = 0.0
        self.trace_id = uuid.uuid4().hex
        self.span_id = uuid.uuid4().hex[:16]

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def __enter__(self) -> _FallbackSpan:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        _RECORDED_SPANS.append({
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "duration_ms": round(duration_ms, 2),
            "attributes": dict(self.attributes),
            "status": "ERROR" if exc_type else "OK",
        })


class _FallbackTracer:
    """Lightweight tracer when opentelemetry-sdk is not installed."""
    def start_as_current_span(self, name: str) -> _FallbackSpan:
        return _FallbackSpan(name, self)


_SPAN_EXPORTER: Any = None
_TRACER: Any = None


def init_telemetry() -> Any:
    """Initializes OpenTelemetry tracer with in-memory storage or zero-dependency fallback."""
    global _SPAN_EXPORTER, _TRACER

    if HAS_OTEL_SDK:
        if _TRACER is not None and _SPAN_EXPORTER is not None:
            return _TRACER
        provider = TracerProvider()
        _SPAN_EXPORTER = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(_SPAN_EXPORTER))
        trace.set_tracer_provider(provider)
        _TRACER = trace.get_tracer("slothpilot.agent_pipeline", "0.1.0")
        return _TRACER
    else:
        _TRACER = _FallbackTracer()
        return _TRACER


def get_tracer() -> Any:
    """Returns the active tracer."""
    global _TRACER
    if _TRACER is None:
        return init_telemetry()
    return _TRACER


def get_recorded_spans() -> List[Dict[str, Any]]:
    """Retrieves formatted span records for the morning dashboard."""
    global _SPAN_EXPORTER, _RECORDED_SPANS

    if HAS_OTEL_SDK and _SPAN_EXPORTER is not None:
        spans = _SPAN_EXPORTER.get_finished_spans()
        formatted = []
        for s in spans:
            duration_ms = (s.end_time - s.start_time) / 1_000_000.0 if s.end_time and s.start_time else 0.0
            formatted.append({
                "name": s.name,
                "trace_id": format(s.context.trace_id, "032x"),
                "span_id": format(s.context.span_id, "016x"),
                "duration_ms": round(duration_ms, 2),
                "attributes": dict(s.attributes or {}),
                "status": s.status.status_code.name,
            })
        return formatted

    return list(_RECORDED_SPANS)
