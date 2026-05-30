"""In-skill function registry for the 22 ported pay-equity tools.

Replaces the FastMCP server pattern (the original `pay_equity_mcp.app` module).
Each tool function is registered by name into TOOL_REGISTRY at import time.
The skill orchestration code in `references/pay-equity-qc-protocol.md` calls
tools by name via call_tool().
"""
from __future__ import annotations

from typing import Any, Callable

TOOL_REGISTRY: dict[str, Callable[..., Any]] = {}


def tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: register a function in TOOL_REGISTRY by its name.

    Replaces the FastMCP `@mcp.tool()` decorator. Used as `@mcp_tool` (no parens).
    """
    TOOL_REGISTRY[func.__name__] = func
    return func


def call_tool(name: str, **kwargs: Any) -> Any:
    """Invoke a registered tool by name. Raises KeyError if not registered."""
    if name not in TOOL_REGISTRY:
        raise KeyError(
            f"Tool {name!r} not registered (known: {sorted(TOOL_REGISTRY)})"
        )
    return TOOL_REGISTRY[name](**kwargs)


# Importing each tools submodule triggers @tool() registration via the @mcp_tool
# alias each tools/*.py installs (`from scripts.pay_equity.app import tool as mcp_tool`).
from scripts.pay_equity.tools import engagement      # noqa: E402, F401
from scripts.pay_equity.tools import job_classes     # noqa: E402, F401
from scripts.pay_equity.tools import evaluation      # noqa: E402, F401
from scripts.pay_equity.tools import compensation    # noqa: E402, F401
from scripts.pay_equity.tools import adjustments     # noqa: E402, F401
from scripts.pay_equity.tools import maintenance     # noqa: E402, F401
from scripts.pay_equity.tools import observations    # noqa: E402, F401
from scripts.pay_equity.tools import render          # noqa: E402, F401


__all__ = ["TOOL_REGISTRY", "tool", "call_tool"]
