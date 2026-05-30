# /glossary Protocol

`/glossary add` appends a comms-specific FR-CA term to the engagement-level additions file. Promotion to the canonical shared glossary is delegated to compensation-advisor's `/glossary promote`.

Loaded by SKILL.md when intent-router classifies as `/glossary add`. Loads `glossary-protocol.md` (this file) only.

---

## 1. Scope

comp-comms-builder's glossary role is narrow:

| Action | Owner |
|---|---|
| Add comms-specific term to engagement-level additions | comp-comms-builder `/glossary add` |
| Promote engagement-level additions to canonical `vocabulary/fr-ca-glossary.yaml` | compensation-advisor `/glossary promote` |
| Read canonical glossary at draft time | comp-comms-builder (via `bilingual-rules.md`) |

comp-comms-builder does NOT write directly to `vocabulary/fr-ca-glossary.yaml`. It writes only to `engagements/<slug>/comms/fr-ca-additions.yaml`. The separation ensures no two sibling skills write to the canonical glossary concurrently.

---

## 2. Command syntax

```
/glossary add "<EN term>" "<FR-CA translation>"
```

Examples:
```
/glossary add "wage scale increase" "augmentation de l'échelle salariale"
/glossary add "all-hands announcement" "annonce à tous les employés"
/glossary add "HRBP enablement memo" "mémo d'activation RHBP"
```

---

## 3. Add sequence

1. **Parse the command.** Extract EN term and FR-CA translation from the command string. If either is missing, prompt:
   > "Usage: `/glossary add \"<EN term>\" \"<FR-CA translation>\"`"

2. **Load existing additions file** (if present): `engagements/<slug>/comms/fr-ca-additions.yaml`.

3. **Duplicate check.** If the EN term already exists in the additions file, surface:
   > "Term `<EN term>` is already in additions with translation `<current FR-CA value>`. Update it? (y / n)"
   If yes, update in-place. If no, abort.

4. **Duplicate check against canonical glossary** (read `vocabulary/fr-ca-glossary.yaml` if accessible). If the EN term is already in the canonical glossary with a different translation, surface:
   > "Term `<EN term>` exists in the canonical glossary with translation `<canonical value>`. Adding a comms-specific override. Continue? (y / n)"
   If yes, proceed — the comms-specific translation takes precedence in comms artifacts per `bilingual-rules.md`.

5. **Append the entry** to `fr-ca-additions.yaml`:

```yaml
- en: "<EN term>"
  fr_ca: "<FR-CA translation>"
  usage_tag: comms
  added: YYYY-MM-DD
  engagement: <engagement-slug>
  added_by: operator
```

6. **Write** `engagements/<slug>/comms/fr-ca-additions.yaml` to Drive. If file is new: create with schema header. If existing: append to the `additions:` array.

7. **Surface confirmation:**
   > "Added: `<EN term>` → `<FR-CA translation>` (`usage_tag: comms`) to `<engagement-slug>` additions.
   > To promote to canonical: run compensation-advisor's `/glossary promote` (reads all `fr-ca-additions.yaml` files across comp-* skills)."

---

## 4. fr-ca-additions.yaml schema

```yaml
# engagements/<slug>/comms/fr-ca-additions.yaml
# Engagement-level FR-CA glossary additions for comms artifacts
# Promote to canonical via compensation-advisor /glossary promote
# Schema version: 1

schema_version: 1
engagement: <engagement-slug>
last_updated: YYYY-MM-DD

additions:
  - en: "wage scale increase"
    fr_ca: "augmentation de l'échelle salariale"
    usage_tag: comms
    added: 2026-05-03
    engagement: pharmacy-fy26
    added_by: operator
```

`usage_tag: comms` is non-negotiable on all entries from this skill. It allows `/glossary promote` to route comms-specific terms correctly and avoids polluting the general compensation vocabulary.

---

## 5. Promotion path (not owned here)

When the founder or CHRO runs compensation-advisor's `/glossary promote`, it:

1. Reads all `engagements/*/comms/fr-ca-additions.yaml` files
2. Merges entries not yet in `vocabulary/fr-ca-glossary.yaml`
3. Carries `usage_tag: comms` on the promoted entries for traceability
4. Writes the merged entries to the canonical glossary

comp-comms-builder never calls `/glossary promote` — that is strictly compensation-advisor's tool. The separation is intentional: promotion touches a shared file that all comp-* skills read; it requires a deliberate cross-skill action, not an automatic merge.

---

## 6. What this protocol does NOT contain

- Bilingual co-draft mechanics, how the glossary is used at render time — those live in `bilingual-rules.md`.
- Canonical glossary schema — that lives in `vocabulary/fr-ca-glossary.yaml` (Drive, shared).
- Promotion mechanics — those live in compensation-advisor's glossary-promote protocol.
- FR-CA grammar rules — those live in `bilingual-rules.md`.
