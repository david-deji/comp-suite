# master-yaml-ops

Comp-suite v2 primitive. All reads and writes to `master.yaml` flow through these functions.
No other primitive or mode writes master.yaml directly.

## Contract

| | |
|---|---|
| **Inputs** | Varies per function — see signatures below |
| **Outputs** | Validated dict, void, or error list |
| **DAG position** | 2 — consumes engagement-loader output; feeds all other primitives |
| **Functions** | `find_or_create_org`, `read_master`, `write_master_section`, `append_decision_log`, `walk_sibling_assets`, `render_tree_view` |

Schema files are in `$ASSET_ROOT/_core/schemas/`. Validate via `python3 -c "import jsonschema, json, yaml; ..."` inline.

---

## `find_or_create_org(slug)`

Reads `$STATE_ROOT/_orgs/index.yaml`. If `slug` is in `orgs[]`, returns the record.
If not found, performs a fuzzy near-miss check and surface options before creating.

```python
import re, yaml, os

SLUG_RE = re.compile(r'^[a-z][a-z0-9-]{1,40}$')

def find_or_create_org(slug):
    index_path = f"{STATE_ROOT}/_orgs/index.yaml"

    if not os.path.exists(index_path):
        # Bootstrap: first-ever org
        index = {"schema_version": "1.0.0", "orgs": []}
    else:
        with open(index_path) as f:
            index = yaml.safe_load(f) or {"orgs": []}

    existing = {o["org_slug"]: o for o in index.get("orgs", [])}

    if slug in existing:
        return existing[slug]

    # Slug validation
    if not SLUG_RE.match(slug):
        raise ValueError(f"'{slug}' is not a valid slug (must match ^[a-z][a-z0-9-]{{1,40}}$)")

    # Near-miss check (Levenshtein distance ≤ 2)
    near_misses = [s for s in existing if _levenshtein(slug, s) <= 2]
    if near_misses:
        # Surface near-miss prompt to orchestrator; do not auto-create
        return {"near_misses": near_misses, "action_required": "confirm_create_or_use_existing"}

    # Create new org
    new_entry = {
        "org_slug":         slug,
        "created_date":     _today_iso(),
        "status":           "active",
        "display_name":     slug,
    }
    index["orgs"].append(new_entry)

    os.makedirs(f"{STATE_ROOT}/_orgs", exist_ok=True)
    with open(index_path, "w") as f:
        yaml.safe_dump(index, f, allow_unicode=True, sort_keys=False)

    # Scaffold master.yaml skeleton for new org
    org_dir = f"{STATE_ROOT}/_orgs/{slug}"
    os.makedirs(f"{org_dir}/engagements", exist_ok=True)
    _write_master_skeleton(slug, org_dir)

    return new_entry


def _levenshtein(a, b):
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[:]
        dp[0] = i
        for j in range(1, n + 1):
            dp[j] = prev[j-1] if a[i-1] == b[j-1] else 1 + min(prev[j], dp[j-1], prev[j-1])
    return dp[n]


def _today_iso():
    from datetime import date
    return date.today().isoformat()


def _write_master_skeleton(slug, org_dir):
    skeleton = {
        "schema_version": "2.1.0",
        "header": {
            "org_slug":              slug,
            "display_name":          slug,
            "created_date":          _today_iso(),
            "created_by_skill":      "comp",        # required by master-shared-header schema
            "last_touched_date":     _today_iso(),
            "last_touched_by_skill": "comp",
            "primary_language":      "fr-ca",       # required; default per Bill 96 / Quebec posture
            "active_skills":         [],
            "industry":              None,
        },
        "cycles":       [],
        "decision_log": [],
    }
    master_path = f"{org_dir}/master.yaml"
    with open(master_path, "w") as f:
        yaml.safe_dump(skeleton, f, allow_unicode=True, sort_keys=False)
```

---

## `read_master(org_slug)`

Reads master.yaml, validates shared header + decision_log, returns dict or error list.

```python
import yaml, json, subprocess, os

SCHEMAS_DIR = f"{ASSET_ROOT}/_core/schemas"

def read_master(org_slug):
    master_path = f"{STATE_ROOT}/_orgs/{org_slug}/master.yaml"

    if not os.path.exists(master_path):
        return {"error": f"master.yaml not found for org '{org_slug}'"}

    with open(master_path) as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return {"error": f"YAML parse failure: {e}"}

    if data is None:
        return {"error": "master.yaml is empty; re-initialize the org"}

    # Validate shared header
    errors = _validate(data, f"{SCHEMAS_DIR}/master-shared-header.schema.json")
    if errors:
        # Surface errors; return the dict anyway for read-only access (/comp doctor repairs)
        return {"data": data, "validation_errors": errors, "read_only": True}

    # Validate each decision_log entry
    dl_schema = f"{SCHEMAS_DIR}/decision-log-entry.schema.json"
    for i, entry in enumerate(data.get("decision_log", [])):
        dl_errors = _validate(entry, dl_schema)
        if dl_errors:
            errors.extend([f"decision_log[{i}]: {e}" for e in dl_errors])

    # Validate each mode section against its schema (warn only on sibling sections)
    mode_section_map = _discover_section_schemas()
    for section_name, schema_file in mode_section_map.items():
        if section_name in data:
            sec_errors = _validate(data[section_name], f"{SCHEMAS_DIR}/{schema_file}")
            if sec_errors:
                errors.extend([f"section '{section_name}': {e}" for e in sec_errors])

    if errors:
        return {"data": data, "validation_errors": errors, "read_only": True}

    return {"data": data}


def _validate(data, schema_path):
    """Returns list of error strings, empty if valid.

    FAILS LOUD on missing `jsonschema` import — silent no-ops are worse than
    crashes when validation is the safety contract. See README § Setup for
    install (Arch/PEP 668 needs `pacman -S python-jsonschema` or a venv).
    """
    script = (
        "import sys, json, yaml; "
        "try:\n    import jsonschema\nexcept ImportError as e:\n"
        "    sys.stderr.write('FATAL: jsonschema not installed — see v2/README.md § Setup\\n'); "
        "    sys.exit(2)\n"
        f"schema = json.load(open({repr(schema_path)})); "
        "data = yaml.safe_load(sys.stdin); "
        "v = jsonschema.Draft7Validator(schema); "
        "errors = sorted(v.iter_errors(data), key=lambda e: list(e.path)); "
        "[print(str(e.message)) for e in errors]"
    )
    import subprocess, json as _json, yaml as _yaml
    result = subprocess.run(
        ["python3", "-c", script],
        input=_yaml.dump(data),
        capture_output=True, text=True
    )
    if result.returncode == 2:
        raise RuntimeError(result.stderr.strip() or "jsonschema unavailable")
    if result.returncode != 0:
        raise RuntimeError(f"validator crashed: rc={result.returncode} stderr={result.stderr.strip()}")
    return [l.strip() for l in result.stdout.splitlines() if l.strip()]
```

---

## `write_master_section(org_slug, section_name, data)`

Validates section, then writes atomically. MUST use glob discovery — no hardcoded section list.

```python
import glob, yaml, os, shutil

def write_master_section(org_slug, section_name, section_data):
    # Validate section_name via glob discovery (SPEC § 5.1 — mode-plugin requirement)
    valid_sections = _discover_section_names()
    if section_name not in valid_sections:
        raise ValueError(
            f"'{section_name}' is not a registered master_yaml_section. "
            f"Known sections: {sorted(valid_sections)}. "
            "Add a mode.yaml with master_yaml_section: <name> to register a new section."
        )

    # Validate section_data against the mode's declared schema
    mode_schemas = _discover_section_schemas()
    schema_file  = mode_schemas.get(section_name)
    if schema_file:
        errors = _validate(section_data, f"{ASSET_ROOT}/_core/schemas/{schema_file}")
        if errors:
            raise ValueError(f"Section '{section_name}' schema validation failed:\n" + "\n".join(errors))

    master_path     = f"{STATE_ROOT}/_orgs/{org_slug}/master.yaml"
    master_path_new = master_path + ".new"

    # Read current state fresh before every write
    result = read_master(org_slug)
    if "error" in result:
        raise RuntimeError(f"Cannot write: {result['error']}")
    master = result["data"]

    # Merge section
    master[section_name] = section_data

    # Update advisory header fields
    master.setdefault("header", {})
    master["header"]["last_touched_date"]     = _today_iso()
    master["header"]["last_touched_by_skill"] = "comp"

    # Atomic write: new → rename
    with open(master_path_new, "w") as f:
        yaml.safe_dump(master, f, allow_unicode=True, sort_keys=False)
    os.replace(master_path_new, master_path)


def _discover_section_names():
    """Returns set of valid master_yaml_section values from all mode.yamls."""
    paths = glob.glob(f"{ASSET_ROOT}/_modes/*/mode.yaml")
    sections = set()
    for p in paths:
        with open(p) as f:
            m = yaml.safe_load(f)
        val = m.get("master_yaml_section")
        if val:
            sections.add(val)
    return sections


def _discover_section_schemas():
    """Returns {section_name: schema_filename} for all mode.yamls that declare both."""
    paths = glob.glob(f"{ASSET_ROOT}/_modes/*/mode.yaml")
    mapping = {}
    for p in paths:
        with open(p) as f:
            m = yaml.safe_load(f)
        section = m.get("master_yaml_section")
        schema  = m.get("schema")
        if section and schema:
            mapping[section] = schema
    return mapping
```

---

## `append_decision_log(org_slug, entry)`

Appends one entry to `decision_log[]`. Idempotent on `entry.id`.

```python
def append_decision_log(org_slug, entry):
    master_path     = f"{STATE_ROOT}/_orgs/{org_slug}/master.yaml"
    master_path_new = master_path + ".new"

    result = read_master(org_slug)
    if "error" in result:
        raise RuntimeError(f"Cannot append: {result['error']}")
    master = result["data"]

    dl = master.setdefault("decision_log", [])

    # Idempotency: skip if id already present
    existing_ids = {e.get("id") for e in dl if "id" in e}
    if entry.get("id") and entry["id"] in existing_ids:
        return  # already appended; no-op

    # Validate entry
    errors = _validate(entry, f"{ASSET_ROOT}/_core/schemas/decision-log-entry.schema.json")
    if errors:
        raise ValueError(f"Decision log entry validation failed:\n" + "\n".join(errors))

    # Assign monotonic id if not provided
    if not entry.get("id"):
        next_n = len(dl) + 1
        entry = dict(entry)
        entry["id"] = f"dl-{next_n:03d}"

    dl.append(entry)
    master["decision_log"] = dl
    master.setdefault("header", {})["last_touched_date"] = _today_iso()

    with open(master_path_new, "w") as f:
        yaml.safe_dump(master, f, allow_unicode=True, sort_keys=False)
    os.replace(master_path_new, master_path)
```

---

## `walk_sibling_assets(org_slug, engagement_id)`

Walks the engagement directory tree and returns a structured asset list.
Local FS only — no Drive, no MIME-type checks.

```python
import os
import glob as _glob
from datetime import datetime

# Static asset dirs + every registered mode under $ASSET_ROOT/_modes/. Glob discovery
# keeps SPEC § 5.1's promise: adding a 5th mode requires no edits here.
def _discover_asset_dirs():
    static = ["inputs", "deliverables"]
    mode_dirs = sorted(
        os.path.basename(p.rstrip("/"))
        for p in _glob.glob(f"{ASSET_ROOT}/_modes/*/")
        if os.path.isfile(os.path.join(p, "mode.yaml"))
    )
    return static + mode_dirs

def walk_sibling_assets(org_slug, engagement_id):
    base = f"{STATE_ROOT}/_orgs/{org_slug}/engagements/{engagement_id}"
    results = []

    for dir_name in _discover_asset_dirs():
        dir_path = os.path.join(base, dir_name)
        if not os.path.isdir(dir_path):
            continue
        for root, _, files in os.walk(dir_path):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                rel   = os.path.relpath(fpath, base)
                mtime = os.path.getmtime(fpath)
                results.append({
                    "path":          rel,
                    "kind":          dir_name,
                    "last_modified": datetime.utcfromtimestamp(mtime).strftime("%Y-%m-%dT%H:%M:%SZ"),
                })

    return results
```

---

## `render_tree_view(asset_walk_result)`

Produces a human-readable markdown block from `walk_sibling_assets` output.

```python
def render_tree_view(asset_walk_result):
    from collections import defaultdict
    by_kind = defaultdict(list)
    for asset in asset_walk_result:
        by_kind[asset["kind"]].append(asset)

    lines = ["### Engagement assets\n"]
    for kind in ASSET_DIRS:
        items = by_kind.get(kind, [])
        if not items:
            lines.append(f"  {kind}/  (empty)")
        else:
            lines.append(f"  {kind}/")
            for item in items:
                fname = os.path.basename(item["path"])
                lines.append(f"    ├── {fname}  ({item['last_modified'][:10]})")
    return "\n".join(lines)
```

## Freshness convention

Freshness is computed from `last_updated` timestamps in master.yaml sections:

| Emoji | Age | Meaning |
|---|---|---|
| 🟢 | < 6 months | Fresh |
| 🟡 | 6–18 months | Aging |
| 🔴 | > 18 months | Stale |

## Constraints

- `write_master_section` uses glob discovery against `$ASSET_ROOT/_modes/*/mode.yaml` — no hardcoded section whitelist. Adding mode #5 requires only a new `mode.yaml` with `master_yaml_section` set.
- All writes: produce to `master.yaml.new`, then `os.replace` (atomic on POSIX).
- If validation fails on read, return error list + `read_only: True`. Do not crash.
- `append_decision_log` is idempotent on `entry.id` — safe to re-run after crash.
- Section writes are section-locked: only the active mode may write its own section key.
- Pull notifications (`check_pull_notifications`) from v1 are handled inline by the orchestrator reading `decision_log`; they are not a separate primitive function in v2.
