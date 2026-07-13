"""Adjustment input validation: validate_adjustment_inputs.

Pure pre-call validation for the pay-equity orchestrator. The interest +
schedule math (per-pay-period engine, installment scheduling) is server-side
(`payequity_compute_adjustments`, W-A A1 verbatim port). This module keeps only
the statutory input guards that must survive client-side as structured refusals.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tool 14
- r3-r9-spec-corrections.md § R3 (per-pay-period interest engine — single-principal
  midpoint approximation is FORBIDDEN; CNESST disavows it)
- p4b-cutover-contract.md § OR-6 (Art. 76.5.1 installment guard + retroactive
  pay_periods-required hard error stay client-side as pre-call validation)
"""
from __future__ import annotations

from typing import Any, Optional

from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.errors import ValidationError

# Art. 76.5.1 — 4-year installment cap. Inlined from the retired computation/schedule.py:
# build_payment_schedule + the whole computation/ package are server-side now
# (payequity_compute_adjustments); only this statutory guard constant survives client-side,
# used by validate_adjustment_inputs below as a pre-call refusal.
MAX_INSTALLMENT_YEARS = 4


@mcp_tool
def validate_adjustment_inputs(
    num_years: int,
    retroactive_events: Optional[list[dict[str, Any]]] = None,
) -> None:
    """Validate adjustment inputs BEFORE `payequity_compute_adjustments`.

    Raises ValidationError on:
      - Art. 76.5.1: num_years outside [1, MAX_INSTALLMENT_YEARS] (4-year installment cap).
      - R3: any retroactive_event missing the `pay_periods` field — the per-pay-period
        interest engine requires it; midpoint approximation is forbidden.

    Returns None when all inputs are valid.
    """
    if num_years < 1 or num_years > MAX_INSTALLMENT_YEARS:
        raise ValidationError(
            f"num_years={num_years} outside [1, {MAX_INSTALLMENT_YEARS}] (Art. 76.5.1)."
        )

    if retroactive_events:
        for ev in retroactive_events:
            if not ev.get("pay_periods"):
                raise ValidationError(
                    f"retroactive_event for {ev.get('affected_class_ids')}: "
                    "pay_periods is required (per-pay-period engine — R3)."
                )


__all__ = ["validate_adjustment_inputs"]
