"""JSON-RPC error code mapping for the pay-equity MCP server.

Three error categories per phase4 spec § 8:

| Category         | Code   | When                                              |
|------------------|--------|---------------------------------------------------|
| Validation       | -32602 | Input fails schema or business rule               |
| Missing data     | -32001 | Tool requires data from a prior step              |
| Computation      | -32002 | Math fails (e.g., regression with <2 male classes)|

FastMCP surfaces these via standard exception types. Phase 2 wires the exception
classes here into FastMCP's error handling.

# TODO[Phase 2]: implement F006 — wire exceptions to FastMCP error handler
"""
from __future__ import annotations


# --- Error codes ------------------------------------------------------------

VALIDATION_ERROR = -32602
MISSING_DATA_ERROR = -32001
COMPUTATION_ERROR = -32002


# --- Exception classes ------------------------------------------------------

class PayEquityError(Exception):
    """Base exception for all pay-equity MCP errors."""

    code: int = -32000

    def __init__(self, message: str, *, data: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.data = data or {}


class ValidationError(PayEquityError):
    """Input validation failure (schema or business rule)."""

    code = VALIDATION_ERROR


class MissingDataError(PayEquityError):
    """Required upstream data is missing for this tool to run."""

    code = MISSING_DATA_ERROR


class EngagementNotFoundError(MissingDataError):
    """The engagement directory does not exist for the given client_slug.

    Subclass of MissingDataError — reported with the same JSON-RPC code (-32001).
    Used by tools that require an existing engagement (e.g. observations,
    operator actions on a previously-created engagement).
    """


class ComputationError(PayEquityError):
    """Computation cannot proceed (insufficient data, divide-by-zero, etc.)."""

    code = COMPUTATION_ERROR


def to_jsonrpc(exc: PayEquityError) -> dict:
    """Map a PayEquityError into the JSON-RPC error object shape."""
    return {
        "code": exc.code,
        "message": exc.message,
        "data": dict(exc.data),
    }


__all__ = [
    "VALIDATION_ERROR",
    "MISSING_DATA_ERROR",
    "COMPUTATION_ERROR",
    "PayEquityError",
    "ValidationError",
    "MissingDataError",
    "EngagementNotFoundError",
    "ComputationError",
    "to_jsonrpc",
]
