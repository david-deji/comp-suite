#!/usr/bin/env bash
# _core/hooks/anti-slop.sh
# PostToolUse:Write production gate — anti-slop validation on branded text.
# Default exit 1 (warn) for first 30 days per SPEC § 9 / cost-discipline.md.
#
# Discipline source: _core/policies/writing-standards-comp.md
# (branded-text scope, em-dash limits, never-list categories, first-30-days warn policy).
# The hook is the operational enforcement; the policy is the rationale.

set -euo pipefail
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$LIB_DIR/lib.sh"

# 1. Read payload, get file path
path="$(payload_path)"
[ -z "$path" ] && exit 0

# 2. Path scoping — bail silently if not branded text
is_branded_text "$path" || exit 0

# 3. Mode opt-in — bail silently if mode hasn't opted in
mode_opted_in "anti-slop" || exit 0

# 4. Read file
[ -f "$path" ] || exit 0
content="$(cat "$path")"

# 5. Grep never-list (case-insensitive)
nlist="$LIB_DIR/never-list.txt"
matches=()
if [ -f "$nlist" ]; then
  while IFS= read -r term; do
    [ -z "$term" ] && continue
    case "$term" in '#'*) continue ;; esac
    if grep -qiF -- "$term" <<< "$content"; then
      matches+=("\"$term\"")
    fi
  done < "$nlist"
fi

# 6. Em-dash policy (per writing-standards.md):
#    - FR (fr / fr-ca): zero em-dashes (em-dash is Anglicism + AI-tell)
#    - EN: max 2 em-dashes per piece
em_count=$(grep -o '—' <<< "$content" | wc -l | tr -d ' ') || em_count=0
# `set -e` + grep no-match (exit 1) would otherwise kill the hook before the WARN print.
lang="$(read_lang_tag "$path")"
case "$lang" in
  fr|fr-ca)
    [ "$em_count" -gt 0 ] && matches+=("em-dash count $em_count > 0 in FR (zero tolerance)")
    ;;
  *)
    [ "$em_count" -gt 2 ] && matches+=("em-dash count $em_count > 2 in EN")
    ;;
esac

# 7. Report
if [ "${#matches[@]}" -gt 0 ]; then
  printf 'WARN: anti-slop matched in %s:\n' "$path" >&2
  for m in "${matches[@]}"; do
    printf '  - %s\n' "$m" >&2
  done
  # Emit friction telemetry (best-effort, never blocks; first-30-days gate per lib.sh).
  emit_friction_event "hook-fired-warn" "hook" "anti-slop matched: ${matches[*]}" "low" "$path"
  exit 1
fi
exit 0
