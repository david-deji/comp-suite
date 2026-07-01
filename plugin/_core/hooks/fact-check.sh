#!/usr/bin/env bash
# _core/hooks/fact-check.sh
# Stop hook — source-citation check on session-modified deliverables.
# Stop event has different payload shape than PostToolUse — no per-Write file_path.
# Default exit 1 (warn) for first 30 days per SPEC § 9.

set -euo pipefail
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$LIB_DIR/lib.sh"

# Drain stdin (CC sends the Stop payload; we don't need its fields).
cat >/dev/null 2>&1 || true

# State dir resolves via lib.sh ($STATE_ROOT — dev: <repo>/v2/state, plugin:
# <cwd>/comp-state). State is on-disk only and is NOT a git repo
# (close-flow.md:238), so session-modified deliverables are enumerated by
# mtime rather than git status.
STATE_DIR="$STATE_ROOT"
[ -d "$STATE_DIR/_orgs" ] || exit 0  # no engagements yet, nothing to check

# Minutes-back window that counts a deliverable as "session-modified".
# Overridable via COMP_FACTCHECK_WINDOW_MIN; default 120 covers a working session.
window_min="${COMP_FACTCHECK_WINDOW_MIN:-120}"

issues=()

# Enumerate session-modified deliverables by mtime (no git dependency).
while IFS= read -r fpath; do
  [ -z "$fpath" ] && continue
  [ -f "$fpath" ] || continue

  # Source-citation heuristic: scan claim-shape lines, look for citation within ±5 lines
  uncited_lines=()
  while IFS= read -r ln_record; do
    lineno="${ln_record%%:*}"
    ln="${ln_record#*:}"
    [ -z "$lineno" ] && continue
    # Detect claim-shape line
    if grep -qE '\$[0-9]+|[0-9]+%|[0-9]+x|according to|per the|as cited in|reports?|stated|found' <<< "$ln"; then
      start=$((lineno - 5))
      [ "$start" -lt 1 ] && start=1
      end=$((lineno + 5))
      ctx=$(sed -n "${start},${end}p" "$fpath")
      # Citation forms: (Source: ...), [text](http...), ^> blockquote attribution
      if ! grep -qE '\(Source:|\[[^]]+\]\(http|^>' <<< "$ctx"; then
        uncited_lines+=("L${lineno}")
      fi
    fi
  done < <(grep -n '' "$fpath" 2>/dev/null)

  if [ "${#uncited_lines[@]}" -gt 0 ]; then
    rel="${fpath#"$STATE_DIR"/}"
    issues+=("$rel: uncited claims at ${uncited_lines[*]}")
  fi
done < <(find "$STATE_DIR/_orgs" -type f -path '*/engagements/*/deliverables/*.md' -mmin "-${window_min}" 2>/dev/null)

if [ "${#issues[@]}" -gt 0 ]; then
  echo "WARN: fact-check found uncited claims in deliverables:" >&2
  for m in "${issues[@]}"; do
    printf '  - %s\n' "$m" >&2
  done
  emit_friction_event "hook-fired-warn" "hook" "fact-check uncited claims: ${issues[*]}" "low" ""
  exit 1
fi
exit 0
