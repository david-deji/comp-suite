# /review Protocol

`/review <artifact>` surfaces a diff between the current and prior version of an artifact, re-surfaces the anti-pattern checklist, runs a FR-CA glossary check, and displays the current approval-stage status. Output is chat-only — no file writes.

Loaded by SKILL.md when intent-router classifies as `/review`. Loads: `review-protocol.md` (this file) + `bilingual-rules.md`.

---

## 1. Artifact resolution

The operator passes the artifact slug, optionally with version and language:

- `/review all-hands-announcement` — review the most recent version of all-hands-announcement across all enabled languages
- `/review all-hands-announcement-fr-ca` — review the most recent FR-CA version
- `/review all-hands-announcement-fr-ca-v2` — review v2 specifically

If the artifact slug is ambiguous (multiple artifacts match), prompt: "Which artifact? Matches found: <list>. Pick one."

If the requested version does not exist: "Version `<N>` of `<artifact-slug>` not found. Most recent is v<M>. Review v<M>?"

---

## 2. Comparison baseline

`/review` diffs against the **immediately-prior version**, not the last approved version. This is intentional — the operator needs to see what just changed between their most recent edit and the one before it.

- v(N) is the current version (most recently drafted)
- v(N-1) is the immediately-prior version

If v(N-1) does not exist (v1 is the first draft), surface:

> "No prior version to diff — `<artifact-slug>` v1 is the first draft. Showing the artifact content only."

---

## 3. Review output (chat-only; no file write)

All output is surfaced in chat. Structure:

### 3.1 Diff summary

```
/review: `<artifact-slug>-<lang>` v(N-1) → v(N)

Changed sections:
  Section: <section-name>
    - REMOVED: "<old text excerpt>"
    + ADDED:   "<new text excerpt>"

  Section: <section-name>
    - REMOVED: "<old text>"
    + ADDED:   "<new text>"

Unchanged sections: <list of section names with no changes>
```

Diff is paragraph-level — not character-level. Surface the first meaningful changed phrase in each changed section, not every word. If a section was rewritten entirely, surface: "REWRITTEN — show full section? (y / n)".

### 3.2 Anti-pattern checklist re-surface

Re-run the same pre-draft anti-pattern check against the current version (v(N)) content. This catches cases where the anti-pattern guard at draft time was acknowledged but the operator wrote around it improperly.

```
Anti-pattern check on v(N):
  ✓ "merit increase" — not found
  ✗ "transformation journey" — found in Section 2, paragraph 3
    Suggestion: replace with "the changes this year"
    (first flagged in FY25, CHRO explicit rejection)
  ✓ "employees should" — not found
```

Green checkmarks for clean. Red flags for violations found. Operator is responsible for correcting — the review does not auto-correct.

### 3.3 FR-CA glossary check (if primary or secondary language is fr-ca)

Scan v(N) content for FR-CA terms not yet in `vocabulary/fr-ca-glossary.yaml`. Surface:

```
FR-CA glossary check:
  Terms in this draft not yet in canonical glossary:
    - "augmentation de l'échelle salariale" — not in glossary
      Add via: /glossary add "wage scale increase" "augmentation de l'échelle salariale"
    - "mémo d'activation RHBP" — not in glossary
      Add via: /glossary add "HRBP enablement memo" "mémo d'activation RHBP"

  Terms confirmed in canonical glossary:
    - "rémunération" ✓
    - "régime d'avantages sociaux" ✓
```

If no unrecognized terms: "FR-CA glossary check: all FR terms in this draft are in the canonical glossary."

Glossary check is informational — it does not block review or require operator acknowledgment. Action items are surfaced with the `/glossary add` command ready to copy-paste.

### 3.4 Approval-stage status

```
Approval stage: <artifact-slug> (<lang>)
  Current stage:  <chro_review>
  Next stage:     <legal_review>
  Full chain:     drafted → chro_review → legal_review → ceo_approved → shipped
  Last drafted:   <YYYY-MM-DD>

To advance stage: edit `engagement-comms-config.artifacts[].approval_stage` in the engagement config.
Lock semantics: advancing to `ceo_approved` freezes this version. Next `/draft` will create v(N+1).
```

If all languages of an artifact are at the same stage, display once. If languages are at different stages (e.g., FR-CA at `legal_review`, EN at `chro_review`), display per-language.

---

## 4. Behavior constraints

- **No file write** — `/review` is strictly chat-only. Even if the operator says "fix it", the response is: "I can flag the issue for you, but `/review` is read-only. Run `/draft` to create a new version with corrections."
- **No auto-correction** — surfacing an anti-pattern violation does not auto-fix it. The operator decides whether to re-draft.
- **No approval advancement** — `/review` does not advance the approval stage. That requires manual config edit (v1) or `/approve` (v2).
- **Always produces all four sections** — do not skip any section even if there are no changes (diff can be empty) or no FR-CA terms (glossary check returns clean).

---

## 5. What this protocol does NOT contain

- Anti-pattern registry — that lives in `org-comms-profiles/<org-slug>.yaml` + `template_assets/anti-patterns.yaml`.
- Bilingual co-draft mechanics, glossary-promote integration — those live in `bilingual-rules.md`.
- Approval-stage transitions, lock semantics — those live in `approval-stage-tracking.md`.
- File write operations — this protocol has none. `/draft` owns writes.
- Drift detection — that is a `/draft` pre-render check. `/review` shows what changed between versions, not whether the recommendation source drifted.
