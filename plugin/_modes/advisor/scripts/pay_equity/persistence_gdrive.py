"""Persistence layer — sandbox-FS read/write + Google Drive staging contract.

Replaces the original `pay_equity_mcp.persistence` module. Mirrors that module's
public API exactly so the 22 ported tools work unchanged.

## How Google Drive integration works

The in-skill Python (this module) writes files to the sandbox filesystem.
The skill orchestration layer in `references/pay-equity-qc-protocol.md` is
responsible for syncing the resulting files to the Google Drive (Claude.ai
connector)-backed persistence folder and seeding the sandbox at session start
by reading the folder.

In other words: this module knows nothing about Google Drive. It writes plain
files atomically. The orchestration layer treats the sandbox as a working tree
and the Drive folder as the source of truth.

## Engagement directory layout

Each engagement lives under ENGAGEMENTS_ROOT/<client-slug>/. ENGAGEMENTS_ROOT
defaults to `./engagements` (relative to the sandbox cwd) and can be overridden
via the PAY_EQUITY_ENGAGEMENTS_ROOT environment variable for tests or for a
fixed sandbox layout.

Per-engagement files (suffix retained as `.json` for v1 — see "JSON vs YAML"
below):

    engagement.json
    job-classes.json
    evaluation-grid.json
    evaluation-grid-meta.json
    compensation.json
    adjustments.json
    retention-policy.json
    retention-policy-decisions.json    (append-only audit log)
    participation-session.json         (when applicable)
    prior-exercise.json                (maintenance audits only)
    maintenance-committee.json         (100+ only)
    operator-decisions.json            (skill-layer write)
    observations.json                  (consultation observations)

## State invalidation DAG

    job-classes.json         → evaluation-grid.json, evaluation-grid-meta.json,
                               compensation.json, adjustments.json
    evaluation-grid.json     → evaluation-grid-meta.json, compensation.json,
                               adjustments.json
    evaluation-grid-meta.json → compensation.json, adjustments.json
    compensation.json        → adjustments.json

Stale files are not deleted; engagement.json `stale_files` and `stale_reasons`
fields flag downstream files. The next read returns stale data with a warning.
The skill orchestration code surfaces stale warnings to the operator and
prompts to either re-run the upstream phase or proceed with stale data
acknowledged.

## JSON vs YAML

The original spec (§ 4) called for a JSON→YAML format swap on engagement
files. v1 ships JSON to keep the port to a single mechanical pass. The
extensive raw `json.loads/json.dump` calls scattered through tool code (12+
sites in evaluation.py / maintenance.py / engagement.py) bypass this module's
write_json/read_json helpers — converting them to YAML would require touching
every site with material risk of corruption. v1.1 can do the YAML swap as a
focused refactor across all callers in one pass.

Files synced to the Google Drive folder are JSON. Operators do not read these
files directly — they interact with the skill, which renders affichages and
other deliverables as Markdown.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

from scripts.pay_equity.errors import ValidationError

if TYPE_CHECKING:
    from pydantic import BaseModel


# ENGAGEMENTS_ROOT defaults to a relative path inside the sandbox cwd. Tests
# override via the env var to point at tmp_path. Skill orchestration in
# Claude.ai web sandbox can also override per session.
ENGAGEMENTS_ROOT = Path(
    os.environ.get("PAY_EQUITY_ENGAGEMENTS_ROOT", "engagements")
)


# --- Slug / identifier validation ------------------------------------------

# Lowercase alnum + hyphens, 1-64 chars, starts with alnum. Blocks `..`,
# leading hyphens, slashes, dots, null bytes. Same regex as the original
# persistence module — both client_slug and template_id flow through this.
_SAFE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def validate_safe_identifier(value: str, *, field: str = "identifier") -> str:
    """Reject values that could escape a directory via traversal or absolute paths."""
    if not isinstance(value, str) or not _SAFE_ID_RE.match(value):
        raise ValidationError(
            f"Invalid {field}: must match [a-z0-9][a-z0-9-]{{0,63}}",
            data={"field": field, "value_kind": type(value).__name__},
        )
    return value


# --- Invalidation DAG -------------------------------------------------------

DOWNSTREAM: dict[str, list[str]] = {
    "job-classes.json": [
        "evaluation-grid.json",
        "evaluation-grid-meta.json",
        "compensation.json",
        "adjustments.json",
    ],
    "evaluation-grid.json": [
        "evaluation-grid-meta.json",
        "compensation.json",
        "adjustments.json",
    ],
    # Sub-factor weights live in evaluation-grid-meta.json. Mutating that
    # sidecar invalidates compensation/adjustments because rule-5 validation
    # depends on those weights.
    "evaluation-grid-meta.json": [
        "compensation.json",
        "adjustments.json",
    ],
    "compensation.json": [
        "adjustments.json",
    ],
}


# --- Path helpers -----------------------------------------------------------

def get_engagement_dir(client_slug: str) -> Path:
    """Return the engagement directory path for a client slug.

    Raises ValidationError if the slug is shaped to escape the engagements root.
    """
    validate_safe_identifier(client_slug, field="client_slug")
    root_resolved = ENGAGEMENTS_ROOT.resolve()
    candidate = (ENGAGEMENTS_ROOT / client_slug).resolve()
    if not candidate.is_relative_to(root_resolved):
        raise ValidationError(
            "client_slug resolves outside engagements root",
            data={"field": "client_slug"},
        )
    return ENGAGEMENTS_ROOT / client_slug


def engagement_exists(client_slug: str) -> bool:
    """True iff the engagement directory and engagement.json both exist."""
    return (get_engagement_dir(client_slug) / "engagement.json").exists()


# --- Atomic read/write ------------------------------------------------------

def write_json(path: Path, model: "BaseModel") -> None:
    """Atomic JSON write: temp file in same directory, then rename.

    POSIX `os.replace` is atomic so readers never observe a partial file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(model.model_dump_json(indent=2))
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


def read_json(path: Path, model_class: type) -> object:
    """Read a JSON file and validate against the supplied Pydantic v2 model."""
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    return model_class.model_validate_json(path.read_text(encoding="utf-8"))


def append_audit_entry(path: Path, entry: dict[str, Any]) -> None:
    """Append-only write for audit logs (e.g. retention-policy-decisions.json,
    operator-decisions.json).

    Reads the existing list (or starts an empty list), appends the entry, writes
    the file back atomically. Tools may also do this inline with their own
    `_atomic_write_json` helpers; this is the canonical helper for any future
    audit-log additions.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, Any]] = []
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                existing = loaded
            else:
                existing = [loaded]
        except json.JSONDecodeError:
            existing = []
    existing.append(entry)

    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False, default=str)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


# --- Invalidation -----------------------------------------------------------

def invalidate_downstream(engagement_dir: Path, mutated_file: str) -> list[str]:
    """Mark downstream files stale in engagement.json after an upstream mutation.

    Returns the list of file names (relative to engagement_dir) marked stale.
    """
    downstream = DOWNSTREAM.get(mutated_file, [])
    if not downstream:
        return []

    eng_path = engagement_dir / "engagement.json"
    if not eng_path.exists():
        return []

    data = json.loads(eng_path.read_text(encoding="utf-8"))
    stale_files = data.setdefault("stale_files", [])
    stale_reasons = data.setdefault("stale_reasons", {})
    for f in downstream:
        if f not in stale_files:
            stale_files.append(f)
            stale_reasons[f] = f"upstream {mutated_file} modified"

    fd, tmp_path = tempfile.mkstemp(dir=str(engagement_dir), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        os.replace(tmp_path, eng_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise

    return downstream


__all__ = [
    "ENGAGEMENTS_ROOT",
    "DOWNSTREAM",
    "validate_safe_identifier",
    "get_engagement_dir",
    "engagement_exists",
    "write_json",
    "read_json",
    "append_audit_entry",
    "invalidate_downstream",
]
