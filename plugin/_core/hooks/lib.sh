#!/usr/bin/env bash
# _core/hooks/lib.sh — shared helpers for production-gate hooks.
# Sourced by anti-slop.sh, french-accent-check.sh, fact-check.sh.

# --- Path resolution (portable: dev repo OR installed plugin) ---------------
# Hooks run as separate processes in the session cwd with no orchestrator vars,
# so resolve roots from this script's own location. lib.sh lives at
# <ASSET_ROOT>/_core/hooks/lib.sh, so ASSET_ROOT is two dirs up.
_COMP_HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSET_ROOT="$(dirname "$(dirname "$_COMP_HOOK_DIR")")"
if [ -n "${COMP_STATE_DIR:-}" ]; then
  STATE_ROOT="$COMP_STATE_DIR"
elif [ -d "$ASSET_ROOT/.claude" ]; then
  STATE_ROOT="$ASSET_ROOT/state"      # dev layout (v2/ has .claude/)
else
  STATE_ROOT="$PWD/comp-state"        # plugin: colleague's working dir
fi

# Read CC hook JSON payload from stdin, return file_path field via jq.
# Returns empty string if jq missing or payload malformed (caller exits 0).
payload_path() {
  command -v jq >/dev/null 2>&1 || { echo "" ; return 0; }
  jq -r '.tool_input.file_path // empty' 2>/dev/null
}

# Returns 0 if path is branded text (hook should run), 1 otherwise.
# State-root-relative: works whether the state dir is named `state/` (dev) or
# `comp-state/` (plugin). Mode-specific working dirs are discovered from
# `$ASSET_ROOT/_modes/*/` at call time, so adding a 5th mode needs no edit here.
is_branded_text() {
  local p="$1" abs sroot rel modes_dir mode_name
  # Normalize candidate + state root to absolute for reliable prefix matching.
  case "$p" in /*) abs="$p" ;; *) abs="$PWD/$p" ;; esac
  case "$STATE_ROOT" in /*) sroot="$STATE_ROOT" ;; *) sroot="$PWD/$STATE_ROOT" ;; esac

  # Skip non-branded file shapes.
  case "$abs" in
    *.yaml|*.json|*.jsonl) return 1 ;;
  esac

  # Only writes under STATE_ROOT can be branded deliverables. Check this BEFORE
  # any asset-tree skip: in dev STATE_ROOT (v2/state) is nested under ASSET_ROOT
  # (v2), so a naive "under ASSET_ROOT -> skip" would wrongly drop dev
  # deliverables. Anything not under STATE_ROOT (incl. the asset tree) -> 1.
  case "$abs" in
    "$sroot"/*) rel="${abs#"$sroot"/}" ;;
    *) return 1 ;;
  esac

  # Skip non-deliverable state shapes; match deliverables.
  case "$rel" in
    ledger/*) return 1 ;;
    _orgs/*/engagements/*/council/*) return 1 ;;
    _orgs/*/engagements/*/close-validation-errors.md) return 1 ;;
    _orgs/*/engagements/*/deliverables/*.md) return 0 ;;
  esac

  # Dynamic mode-dir patterns: <state>/_orgs/*/engagements/*/<mode>/*.md
  modes_dir="$ASSET_ROOT/_modes"
  [ -d "$modes_dir" ] || return 1
  for mode_name in "$modes_dir"/*/; do
    [ -d "$mode_name" ] || continue
    mode_name="$(basename "$mode_name")"
    case "$rel" in
      _orgs/*/engagements/*/"$mode_name"/*.md) return 0 ;;
    esac
  done
  return 1
}

# Check if active mode opted into a hook. Returns 0 if opted in.
# If COMP_ACTIVE_MODE unset (dev/test write), default to "run all hooks".
mode_opted_in() {
  local hook="$1"
  [ -z "${COMP_ACTIVE_MODE:-}" ] && return 0
  local hooks_yaml
  hooks_yaml="$ASSET_ROOT/_modes/${COMP_ACTIVE_MODE}/hooks.yaml"
  [ -f "$hooks_yaml" ] || return 0  # missing file = default-on
  command -v yq >/dev/null 2>&1 || return 0  # no yq = default-on
  yq ".opt_in[]" "$hooks_yaml" 2>/dev/null | tr -d '"' | grep -qx "$hook"
}

# Resolve language tag for a file. Echoes "fr", "fr-ca", "en", or empty.
read_lang_tag() {
  local f="$1"
  # 1. Filename suffix
  case "$f" in
    *-fr.md|*.fr.md) echo "fr"; return 0 ;;
    *-fr-ca.md|*.fr-ca.md) echo "fr-ca"; return 0 ;;
    *-en.md|*.en.md) echo "en"; return 0 ;;
  esac
  # 2. Frontmatter (first 20 lines)
  if [ -f "$f" ]; then
    local lang
    lang=$(head -20 "$f" 2>/dev/null | grep -oE '^language:[[:space:]]*[a-z-]+' | head -1 | awk '{print $2}')
    [ -n "$lang" ] && { echo "$lang"; return 0; }
  fi
  # 3. Mode default (if COMP_ACTIVE_MODE set)
  if [ -n "${COMP_ACTIVE_MODE:-}" ]; then
    local mode_yaml
    mode_yaml="$ASSET_ROOT/_modes/${COMP_ACTIVE_MODE}/mode.yaml"
    if [ -f "$mode_yaml" ] && command -v yq >/dev/null 2>&1; then
      local default_lang
      default_lang=$(yq '.default_language // ""' "$mode_yaml" 2>/dev/null | tr -d '"')
      [ -n "$default_lang" ] && [ "$default_lang" != "null" ] && { echo "$default_lang"; return 0; }
    fi
  fi
  echo ""
}

# Append a friction event to <STATE_ROOT>/harness/friction.jsonl.
# See SPEC-learn.md § 6 + _core/primitives/friction-aggregator.md.
# Args:
#   $1: signal_type (required, must match schema enum)
#   $2: target_class (required, must match schema enum)
#   $3: description (required)
#   $4: severity (optional, default "medium")
#   $5: target_path (optional, default empty -> null)
# Honors first-30-days window for hook-fired-warn signal_type.
# Always returns 0 — never blocks the caller's own exit. Disk full, missing
# python3, jq, or any other failure is silently absorbed (telemetry must
# never break primary functionality).
emit_friction_event() {
  local signal_type="$1" target_class="$2" description="$3"
  local severity="${4:-medium}" target_path="${5:-}"
  local harness_dir install_date_file install_date today_iso days_in
  command -v python3 >/dev/null 2>&1 || return 0
  harness_dir="$STATE_ROOT/harness"
  mkdir -p "$harness_dir" 2>/dev/null || return 0
  install_date_file="$harness_dir/.install-date"
  today_iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  if [ ! -f "$install_date_file" ]; then
    date -u +%Y-%m-%d > "$install_date_file" 2>/dev/null || return 0
  fi
  # First-30-days gate for hook-fired-warn only. Other signal types always emit.
  if [ "$signal_type" = "hook-fired-warn" ]; then
    install_date="$(cat "$install_date_file" 2>/dev/null)"
    [ -z "$install_date" ] && return 0
    days_in=$(( ( $(date -u +%s) - $(date -u -d "$install_date" +%s 2>/dev/null || echo 0) ) / 86400 ))
    [ "$days_in" -ge 30 ] && return 0
  fi
  # JSON-encode strings via python3 (handles quotes, backslashes, newlines, unicode).
  python3 - "$signal_type" "$target_class" "$description" "$severity" "$target_path" \
    "${COMP_ENGAGEMENT_ID:-}" "${COMP_ACTIVE_MODE:-}" "$today_iso" "$harness_dir/friction.jsonl" \
    <<'PYEOF' 2>/dev/null || return 0
import sys, json
sig, tcls, desc, sev, tpath, eng, mode, ts, out = sys.argv[1:10]
event = {
  "ts": ts,
  "source": "auto",
  "severity": sev,
  "target_class": tcls,
  "target_path": tpath if tpath else None,
  "description": desc,
  "context_engagement_id": eng if eng else None,
  "context_mode": mode if mode else None,
  "signal_type": sig,
}
with open(out, "a") as f:
    f.write(json.dumps(event, ensure_ascii=False) + "\n")
PYEOF
  return 0
}
