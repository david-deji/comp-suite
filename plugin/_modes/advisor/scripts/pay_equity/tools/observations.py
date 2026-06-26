"""Tools 20-21: Observation logging and response during consultation periods.

Employees may submit observations during the 60-day consultation period
following a posting. These tools record and respond to those observations.

Pure compute. The orchestrator passes the current observations file (or None)
in — fetched via payequity_get_observations — and persists the returned
observations_file via payequity_put_observation. No persistence lives here.
"""

from datetime import date
from typing import Optional

from scripts.pay_equity.app import tool as mcp_tool
from scripts.pay_equity.errors import ValidationError
from scripts.pay_equity.models.observation import (
    Observation,
    ObservationsFile,
)


VALID_CATEGORIES = {"question", "comment", "objection", "correction_request"}


def _coerce_observations(
    observations: Optional[dict], client_slug: str
) -> ObservationsFile:
    """Validate a passed-in observations dict, or build an empty ObservationsFile."""
    if observations is None:
        return ObservationsFile(client_slug=client_slug)
    return ObservationsFile.model_validate(observations)


def _next_obs_id(observations: list[Observation]) -> str:
    """Generate the next OBS-NNN id."""
    max_num = 0
    for obs in observations:
        if obs.id.startswith("OBS-"):
            try:
                num = int(obs.id[4:])
                max_num = max(max_num, num)
            except ValueError:
                pass
    return f"OBS-{max_num + 1:03d}"


def _parse_iso_date(value: str, *, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError(
            f"Invalid {field}: must be ISO 8601 (YYYY-MM-DD)",
            data={"field": field},
        )


@mcp_tool
def log_observation(
    observations: Optional[dict],
    client_slug: str,
    posting_type: str,
    observer_description: str,
    observation_text: str,
    received_date: str,
    category: Optional[str] = None,
) -> dict:
    """Record an employee observation received during the 60-day consultation period (pure).

    observations: the current observations file (or None on first observation),
        fetched by the orchestrator via payequity_get_observations.
    posting_type: which posting this observation relates to.
    observer_description: who submitted (e.g. "Groupe d'employees du service comptable").
    category: optional, one of question, comment, objection, correction_request.

    Appends the new observation, computes the next id, and returns the full
    updated observations_file for the orchestrator to persist via
    payequity_put_observation.
    """
    if category is not None and category not in VALID_CATEGORIES:
        raise ValidationError(
            f"Invalid category '{category}'. "
            f"Valid values: {', '.join(sorted(VALID_CATEGORIES))}"
        )

    received = _parse_iso_date(received_date, field="received_date")

    data = _coerce_observations(observations, client_slug)
    data.client_slug = client_slug

    obs_id = _next_obs_id(data.observations)

    observation = Observation(
        id=obs_id,
        posting_type=posting_type,
        observer_description=observer_description,
        observation_text=observation_text,
        received_date=received,
        category=category,
    )

    data.observations.append(observation)
    data.last_updated = date.today()

    return {
        "observations_file": data.model_dump(mode="json"),
        "observation_id": obs_id,
        "summary": {
            "client_slug": client_slug,
            "observation_id": obs_id,
            "posting_type": posting_type,
            "received_date": received.isoformat(),
            "total_observations": len(data.observations),
        },
    }


@mcp_tool
def respond_to_observation(
    observations: dict,
    observation_id: str,
    response_text: str,
) -> dict:
    """Record a response to an employee observation (pure).

    observations: the current observations file, fetched by the orchestrator via
        payequity_get_observations.

    Updates the observation's response and response_date fields and returns the
    full updated observations_file (for payequity_put_observation) plus the
    updated_observation.
    """
    data = _coerce_observations(observations, "")

    target: Optional[Observation] = None
    for obs in data.observations:
        if obs.id == observation_id:
            target = obs
            break

    if target is None:
        raise ValidationError(
            f"Observation '{observation_id}' not found for engagement "
            f"'{data.client_slug}'."
        )

    target.response = response_text
    target.response_date = date.today()
    data.last_updated = date.today()

    return {
        "observations_file": data.model_dump(mode="json"),
        "updated_observation": target.model_dump(mode="json"),
    }
