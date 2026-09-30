from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any

try:
    from langfuse import get_client, observe as _langfuse_observe, propagate_attributes

    LANGFUSE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - chỉ dùng khi chưa cài requirements
    LANGFUSE_SDK_AVAILABLE = False
    _langfuse_observe = None

    class _DummyClient:
        def update_current_span(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

    def get_client():
        return _DummyClient()

    @contextmanager
    def propagate_attributes(**kwargs: Any):
        yield


def get_langfuse_client():
    return get_client()


def tracing_enabled() -> bool:
    return LANGFUSE_SDK_AVAILABLE and bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )


def observe(*args: Any, **kwargs: Any):
    """Use Langfuse instrumentation only when credentials are configured."""
    if not tracing_enabled():
        def decorator(func):
            return func

        return decorator
    return _langfuse_observe(*args, **kwargs)
