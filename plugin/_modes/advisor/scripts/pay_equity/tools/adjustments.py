"""Adjustment-calculation tool: calculate_adjustments.

1 of the 19 registered MCP tools.

Spec anchors:
- phase4-final-mcp-architecture.md § 5 Tool 14
- r3-r9-spec-corrections.md § R3 (per-pay-period interest engine — single-principal
  midpoint approximation is FORBIDDEN; CNESST disavows it)
- constraints.md § Per-pay-period interest, § Penalty range $1k–$45k
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from scripts.pay_equity import persistence_gdrive as persistence
from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.computation.interest import (
    DAY_CONVENTION_DEFAULT,
    SIMPLE_INTEREST_RATE_ANNUAL,
    compute_per_pay_period_interest,
)
from scripts.pay_equity.computation.schedule import (
    MAX_INSTALLMENT_YEARS,
    build_payment_schedule,
)
from scripts.pay_equity.errors import MissingDataError, ValidationError
from scripts.pay_equity.models import (
    AdjustmentFile,
    ClassAdjustment,
    CompensationFile,
    InterestBreakdownPeriod,
    JobClassesFile,
    PaymentScheduleYear,
    Predominance,
    RetroactiveEvent,
)


DEFAULT_ANNUAL_HOURS = 1950


@mcp_tool
def calculate_adjustments(
    client_slug: str,
    schedule: str,
    first_payment_date: str,
    num_years: int = 1,
    retroactive_events: Optional[list[dict[str, Any]]] = None,
    day_convention: int = DAY_CONVENTION_DEFAULT,
    interest_rate: float = SIMPLE_INTEREST_RATE_ANNUAL,
    custom_percentages: Optional[list[float]] = None,
) -> dict[str, Any]:
    """Calculate dollar adjustments and payment schedule for all classes with gaps.

    Increase-only direction (Art. 71). Computes simple interest per C.C.Q. art.
    1617 for late or retroactive payments using the per-pay-period engine
    (Σ interest_i over the retroactivity window — never midpoint approximation).
    Multi-year installments cap at 4 years (Art. 76.5.1). Output is flagged
    [UNVERIFIED] until the CNESST Excel spreadsheet is matched.
    """
    if not persistence.engagement_exists(client_slug):
        raise MissingDataError(
            f"engagement.json not found for {client_slug!r}."
        )
    if num_years < 1 or num_years > MAX_INSTALLMENT_YEARS:
        raise ValidationError(
            f"num_years={num_years} outside [1, {MAX_INSTALLMENT_YEARS}] (Art. 76.5.1)."
        )
    try:
        first_pay_date = date.fromisoformat(first_payment_date)
    except ValueError:
        raise ValidationError(
            f"first_payment_date={first_payment_date!r} not ISO format."
        )

    eng_dir = persistence.get_engagement_dir(client_slug)
    comp_path = eng_dir / "compensation.json"
    if not comp_path.exists():
        raise MissingDataError(
            f"compensation.json not found — call compare_compensation first."
        )
    comp_file = persistence.read_json(comp_path, CompensationFile)

    jc_lookup: dict[str, dict[str, Any]] = {}
    jc_path = eng_dir / "job-classes.json"
    if jc_path.exists():
        jc_file = persistence.read_json(jc_path, JobClassesFile)
        for c in jc_file.classes:
            jc_lookup[c.id] = {
                "title": c.title,
                "incumbents": c.total_incumbents,
            }

    incumbents_by_class = {cc.class_id: jc_lookup.get(cc.class_id, {}).get("incumbents", 0) for cc in comp_file.class_compensations}

    # Build per-class adjustments from comparison_results.
    class_adjustments: list[ClassAdjustment] = []
    total_annual_cost = 0.0
    for cmp in comp_file.comparison_results:
        if not cmp.requires_adjustment:
            continue
        cid = cmp.female_class_id
        gap_hourly = max(cmp.gap_hourly, 0.0)
        annual_hours = float(DEFAULT_ANNUAL_HOURS)
        # Pull annual hours from class compensation if hours_worked supplied.
        for cc in comp_file.class_compensations:
            if cc.class_id == cid and cc.hours_worked:
                annual_hours = float(cc.hours_worked.annual_baseline) or annual_hours
                break
        gap_annual = gap_hourly * annual_hours
        annual_adjustment = gap_annual
        incumbents = int(incumbents_by_class.get(cid, 0))
        total_class_cost = annual_adjustment * incumbents
        total_annual_cost += total_class_cost
        class_adjustments.append(
            ClassAdjustment(
                class_id=cid,
                title=jc_lookup.get(cid, {}).get("title", cid),
                gap_hourly=gap_hourly,
                gap_annual=gap_annual,
                annual_adjustment=annual_adjustment,
                total_class_cost=total_class_cost,
                incumbents=incumbents,
                annual_hours=annual_hours,
            )
        )

    # Retroactive events: per-pay-period interest engine.
    is_retroactive = bool(retroactive_events)
    retroactive_models: list[RetroactiveEvent] = []
    total_retroactive_cost = 0.0
    if retroactive_events:
        for ev in retroactive_events:
            try:
                event_date = date.fromisoformat(ev["event_date"])
            except (KeyError, ValueError):
                raise ValidationError(
                    f"retroactive_event missing or malformed event_date: {ev.get('event_date')!r}"
                )
            gap_at_event = float(ev.get("gap_hourly_at_event", 0))
            pay_periods = ev.get("pay_periods", [])
            if not pay_periods:
                raise ValidationError(
                    f"retroactive_event for {ev.get('affected_class_ids')}: "
                    "pay_periods is required (per-pay-period engine — R3)."
                )
            engine = compute_per_pay_period_interest(
                gap_per_hour=gap_at_event,
                pay_periods=pay_periods,
                calc_date=first_pay_date,
                rate=interest_rate,
                day_convention=day_convention,
            )
            breakdown = [
                InterestBreakdownPeriod(
                    period_start=b["period_start"],
                    period_end=b["period_end"],
                    hours_worked=b["hours_worked"],
                    gap_per_hour=b["gap_per_hour"],
                    principal_period=b["principal_period"],
                    days_elapsed=b["days_elapsed"],
                    interest_period=b["interest_period"],
                )
                for b in engine["breakdown"]
            ]
            event_total = engine["total_principal"] + engine["total_interest"]
            total_retroactive_cost += event_total
            retroactive_models.append(
                RetroactiveEvent(
                    event_type=ev.get("event_type", "compensation_change"),
                    event_date=event_date,
                    affected_class_ids=list(ev.get("affected_class_ids", [])),
                    gap_hourly_at_event=gap_at_event,
                    simple_interest_rate=interest_rate,
                    interest_breakdown=breakdown,
                    interest_accrued=engine["total_interest"],
                    total_retroactive_amount=event_total,
                )
            )

    schedule_dicts = build_payment_schedule(
        annual_adjustment_per_employee=sum(a.annual_adjustment for a in class_adjustments) / max(len(class_adjustments), 1)
        if class_adjustments
        else 0.0,
        schedule_type=schedule,
        num_years=num_years,
        first_payment_date=first_pay_date,
        custom_percentages=custom_percentages,
    )
    schedule_models = [PaymentScheduleYear(**s) for s in schedule_dicts]

    total_multi_year_cost = total_annual_cost * (num_years if schedule == "installments" else 1)

    file_payload = AdjustmentFile(
        client_slug=client_slug,
        schedule_type=schedule,  # type: ignore[arg-type]
        num_years=num_years,
        first_payment_date=first_pay_date,
        class_adjustments=class_adjustments,
        payment_schedule=schedule_models,
        total_annual_cost=total_annual_cost,
        total_multi_year_cost=total_multi_year_cost,
        interest_rate=interest_rate,
        day_convention=day_convention,
        is_retroactive=is_retroactive,
        retroactive_events=retroactive_models,
        last_updated=date.today(),
    )
    persistence.write_json(eng_dir / "adjustments.json", file_payload)

    return {
        "class_adjustments": [a.model_dump(mode="json") for a in class_adjustments],
        "payment_schedule": [s.model_dump(mode="json") for s in schedule_models],
        "retroactive_events": [r.model_dump(mode="json") for r in retroactive_models],
        "total_annual_cost": total_annual_cost,
        "total_multi_year_cost": total_multi_year_cost,
        "total_retroactive_cost": total_retroactive_cost,
        "interest_rate": interest_rate,
        "interest_method": "per_pay_period",
        "day_convention": day_convention,
        "data_status": "UNVERIFIED" if is_retroactive else "VERIFIED",
        "data_status_note": (
            "Interest computation uses CNESST per-pay-period method; "
            "tag remains UNVERIFIED until matched against the firewalled CNESST Excel spreadsheet."
        )
        if is_retroactive
        else "",
    }


__all__ = ["calculate_adjustments"]
