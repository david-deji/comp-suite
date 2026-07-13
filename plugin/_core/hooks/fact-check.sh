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
# <cwd>/comp-state). It is itself git-tracked (per-engagement archive flow in
# close-flow.md).
STATE_DIR="$STATE_ROOT"
[ -d "$STATE_DIR/.git" ] || exit 0  # state not yet a sub-repo, nothing to check

issues=()

# Enumerate session-modified deliverables via git status in the state sub-repo.
while IFS= read -r line; do
  [ -z "$line" ] && continue
  status="${line:0:2}"
  file="${line:3}"
  case "$status" in
    " M"|"M "|"MM"|"A "|"AM"|"??") ;;
    *) continue ;;
  esac
  case "$file" in
    _orgs/*/engagements/*/deliverables/*.md) ;;
    *) continue ;;
  esac

  fpath="$STATE_DIR/$file"
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
    issues+=("$file: uncited claims at ${uncited_lines[*]}")
  fi
done < <(git -C "$STATE_DIR" status --porcelain 2>/dev/null)

if [ "${#issues[@]}" -gt 0 ]; then
  echo "WARN: fact-check found uncited claims in deliverables:" >&2
  for m in "${issues[@]}"; do
    printf '  - %s\n' "$m" >&2
  done
  emit_friction_event "hook-fired-warn" "hook" "fact-check uncited claims: ${issues[*]}" "low" ""
  exit 1
fi
exit 0
