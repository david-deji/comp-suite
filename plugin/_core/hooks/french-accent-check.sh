#!/usr/bin/env bash
# _core/hooks/french-accent-check.sh
# PostToolUse:Write production gate — French accent + em-dash check.
# Default exit 1 (warn) for first 30 days per SPEC § 9.

set -euo pipefail
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$LIB_DIR/lib.sh"

path="$(payload_path)"
[ -z "$path" ] && exit 0
is_branded_text "$path" || exit 0
mode_opted_in "french-accent-check" || exit 0

# Resolve language tag — only run on FR-tagged content
lang="$(read_lang_tag "$path")"
case "$lang" in fr|fr-ca) ;; *) exit 0 ;; esac

[ -f "$path" ] || exit 0
content="$(cat "$path")"

issues=()

# Common bare-ASCII forms that should carry accents (FR-CA).
# Conservative list — biased toward false-negatives (better to miss than to nag).
# Tune this list as false-positives are observed (per cost-discipline.md).
declare -a BARE_PATTERNS=(
  "\bdeja\b|déjà"
  "\bcest\b|c'est"
  "\betre\b|être"
  "\btres\b|très"
  "\bmethode\b|méthode"
  "\bmethodes\b|méthodes"
  "\bdonnees\b|données"
  "\bemployes\b|employés"
  "\bemployees\b|employées"
  "\bgenere\b|généré"
  "\bgeneree\b|générée"
  "\brealise\b|réalisé"
  "\bdecide\b|décidé"
  "\bdecision\b|décision"
  "\bdecisions\b|décisions"
)

for pair in "${BARE_PATTERNS[@]}"; do
  bare="${pair%%|*}"
  expected="${pair#*|}"
  if grep -qE -- "$bare" <<< "$content"; then
    issues+=("missing accent: pattern '$bare' should likely be '$expected'")
  fi
done

# Em-dash zero-tolerance in FR (per writing-standards.md)
em_count=$(grep -o '—' <<< "$content" | wc -l | tr -d ' ') || em_count=0
# `set -e` + grep no-match (exit 1) would otherwise kill the hook silently.
[ "$em_count" -gt 0 ] && issues+=("$em_count em-dash(es) present in FR — zero tolerance per writing-standards.md")

if [ "${#issues[@]}" -gt 0 ]; then
  printf 'WARN: FR accent / em-dash issue in %s:\n' "$path" >&2
  for m in "${issues[@]}"; do
    printf '  - %s\n' "$m" >&2
  done
  emit_friction_event "hook-fired-warn" "hook" "french-accent-check: ${issues[*]}" "low" "$path"
  exit 1
fi
exit 0
