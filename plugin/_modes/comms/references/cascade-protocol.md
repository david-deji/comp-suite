# /cascade Protocol

`/cascade <engagement-slug>` renders the full comms bundle for a single engagement — every artifact in `engagement-comms-config.artifacts[]` in dependency order. It is a wrapper that calls the `/draft` pipeline per-artifact with bundle-level coordination.

Loaded by SKILL.md when intent-router classifies as `/cascade`. Loads: same references as `/draft` (meta-protocol, draft-protocol, artifact-catalog, valid-combinations-rules, bilingual-rules, compensation-advisor-input-contract, production-and-qa, template-master, brand-kit-protocol, all mirrored where applicable) plus `cascade-protocol.md` (this file).

---

## Mode-keyed step routing

This protocol assumes `engagement_mode: full-cascade` by default. When the
engagement-comms-config declares a different mode, apply the routing below.

**Mode resolution at session start:**

1. Read `engagement_mode` from `engagement-comms-config.yaml` for this slug.
2. Look up the mode's step routing from `references/engagement-modes.md`.
3. Apply the routing for this session.
4. Write the mode declaration into every artifact's frontmatter.

**Per-mode routing for /cascade:**

| Mode | Cascade routing |
|---|---|
| `full-cascade` | Run the full dependency chain: exec-one-pager → all-hands-announcement → manager-faq → hrbp-enablement-memo. All 4 artifacts, dependency order enforced. |
| `single-artifact` | /cascade is not invoked — single-artifact mode routes to /draft directly. If /cascade is called with single-artifact config, surface: "Config declares single-artifact mode. Run `/draft <type>` instead?" |
| `bilingual-co-draft` | Full cascade dependency chain applies. Each artifact runs FR-first co-draft. FR render completes before EN render begins per artifact (not across artifacts). |
| `revision-only` | /cascade is not invoked — revision-only routes to /review. If /cascade is called with revision-only config, surface: "Config declares revision-only mode. Run `/review <artifact>` instead?" |
| `voice-extraction-only` | /cascade is not invoked. Route to /ingest. |
| `glossary-merge` | /cascade is not invoked. Route to /glossary add. |

**Cascade-mode dependency chain (full-cascade):**

```
exec-one-pager          (establishes governing narrative framing)
  → all-hands-announcement  (draws headline from exec framing)
    → manager-faq           (anticipates employee questions from all-hands)
      → hrbp-enablement-memo    (provides escalation paths for manager FAQ)
```

Each artifact reads the preceding artifact's key framing claims to maintain
consistency. Rendering out of order risks circular inconsistency — order is
enforced and not configurable.

If `engagement_mode` is missing from the config, default to `full-cascade`
and log `decision_type: mode_defaulted_silently` before proceeding.

---

## 1. Cascade pre-flight checklist

Before dispatching any individual artifact render, run these checks:

1. **Config exists** — `engagement-comms-configs/<engagement-slug>.yaml` loadable from Drive. If not, surface: "No engagement config for `<engagement-slug>`. Run `/init` first." Abort.
2. **Source recommendation accessible** — read-test the recommendation source (same as draft-protocol Step 4). If required fields are missing, list them all at once and abort. Do not start the cascade and fail mid-run.
3. **Drive write permissions** — verify the Drive folder accepts writes (from Phase 0 persistence test). If in paste-mode, confirm: "Cascade will produce up to 16 artifacts. In paste-mode, each will be surfaced in chat. Confirm to proceed."
4. **Artifacts enabled** — surface the planned artifact list with expected languages and formats:

```
Cascade plan for `<engagement-slug>`:

Dependency order:
  1. exec-one-pager          EN       PPTX      (1-3 slides)
  2. all-hands-announcement  FR-CA    HTML + PDF
     all-hands-announcement  EN       HTML + PDF
  3. manager-faq             FR-CA    DOCX
  4. hrbp-enablement-memo    FR-CA    DOCX
     hrbp-enablement-memo    EN       DOCX

Total artifacts: 4   Total file writes: up to <N>
Anti-patterns active: <N>

Proceed? (y / abort)
```

Wait for explicit `y`. Do not start cascade without confirmation.

---

## 2. Dependency order (non-negotiable)

Artifacts run in this order:

```
1. exec-one-pager
2. all-hands-announcement
3. manager-faq
4. hrbp-enablement-memo
```

**Why this order matters:** the exec one-pager establishes the governing decision framing (narrative headline, key numbers, governance note). The all-hands draws its headline from the same framing — it must be consistent. The manager FAQ anticipates the employee questions the all-hands will generate. The HRBP memo provides the escalation paths the manager FAQ references.

Rendering out of order risks circular inconsistency — e.g., the all-hands references "the board has approved" before the exec one-pager has confirmed that language. Order is enforced and not configurable.

---

## 3. Per-artifact render sequence

For each artifact in dependency order:

### 3.1 Header announcement

Before each artifact starts, surface:

```
[<N> of <total>] Rendering `<artifact-type>` (<lang>) — <format>...
Anti-patterns from prior cycles for this artifact:
  - "<phrase>" → use "<use_instead>" instead
  ...
Acknowledge and proceed? (y / n)
```

Wait for acknowledgment. If `n` on any artifact: offer "skip this artifact and continue cascade" or "abort cascade".

### 3.2 Individual draft pipeline

Run `/draft` pipeline steps 1-10 (from `references/draft-protocol.md`) for this artifact. The cascade passes the following context carried forward from prior artifacts:

**From exec-one-pager into all-hands-announcement:**
- `headline_decision`: the exact decision headline phrase used in the exec one-pager. The all-hands MUST use the identical headline — cross-artifact consistency.
- `effective_date_phrasing`: the exact "effective [date]" phrasing used in the exec one-pager.

**From all-hands-announcement into manager-faq:**
- `employee_questions_anticipated`: the key concerns from the all-hands audience profile, used to seed the FAQ question set. Manager FAQ should anticipate what employees will ask AFTER reading the all-hands.

**From all-hands-announcement + manager-faq into hrbp-enablement-memo:**
- `escalation_trigger_phrases`: edge-case scenarios the manager FAQ flagged for escalation. The HRBP memo's escalation-paths section must address each one.

Carry-forward fields are passed as render context — they constrain content, not replace it. The HRBP memo still has its own full render; it is not a summary of the manager FAQ.

### 3.3 Language iteration

For each artifact in the cascade plan, language order:

1. Render primary language (default `fr-ca`) first.
2. Render secondary language (if enabled for this artifact) second.

Each language gets its own file write. The primary language draft informs the carry-forward context; the secondary does not.

### 3.4 Progress reporting

After each artifact completes all its file writes:

```
✓ exec-one-pager        EN         PPTX        → engagements/<slug>/comms/exec-one-pager-en-v<N>.pptx
✓ all-hands-announcement FR-CA     HTML + PDF  → engagements/<slug>/comms/all-hands-announcement-fr-ca-v<N>.html
                                               → engagements/<slug>/comms/all-hands-announcement-fr-ca-v<N>.pdf
...
```

Surface failures immediately. Do not continue to the next artifact if a write fails — pause and prompt for operator decision.

---

## 4. Multi-file write ordering

Per `persistence-and-ledger.md` (mirrored) multi-file write ordering rule:

1. Write primary language files for each artifact before secondary language files.
2. Within a (language × format) pair, write the artifact file before updating `engagement-comms-config.yaml`.
3. Update `engagement-comms-config.yaml` once after ALL artifact files for that artifact are confirmed written — not per-file.
4. Write `engagement-comms-config.yaml` once at the END of the full cascade for all version increments, not after each artifact.

This reduces config write frequency and prevents partial-state inconsistency if a write fails mid-cascade.

---

## 5. File output table (full cascade, 4-artifact example)

The table below shows the maximum expected output for a FR-CA + EN cascade with PDF path confirmed:

| Artifact | Lang | Format | Path |
|---|---|---|---|
| exec-one-pager | en | pptx | `engagements/<slug>/comms/exec-one-pager-en-v<N>.pptx` |
| all-hands-announcement | fr-ca | html | `engagements/<slug>/comms/all-hands-announcement-fr-ca-v<N>.html` |
| all-hands-announcement | fr-ca | pdf | `engagements/<slug>/comms/all-hands-announcement-fr-ca-v<N>.pdf` |
| all-hands-announcement | en | html | `engagements/<slug>/comms/all-hands-announcement-en-v<N>.html` |
| all-hands-announcement | en | pdf | `engagements/<slug>/comms/all-hands-announcement-en-v<N>.pdf` |
| manager-faq | fr-ca | docx | `engagements/<slug>/comms/manager-faq-fr-ca-v<N>.docx` |
| hrbp-enablement-memo | fr-ca | docx | `engagements/<slug>/comms/hrbp-enablement-memo-fr-ca-v<N>.docx` |
| hrbp-enablement-memo | en | docx | `engagements/<slug>/comms/hrbp-enablement-memo-en-v<N>.docx` |

**With PDF path available for DOCX→PDF conversion (if verified at Phase 0):**

| Artifact | Lang | Format | Path |
|---|---|---|---|
| manager-faq | fr-ca | pdf | `engagements/<slug>/comms/manager-faq-fr-ca-v<N>.pdf` |
| hrbp-enablement-memo | fr-ca | pdf | `engagements/<slug>/comms/hrbp-enablement-memo-fr-ca-v<N>.pdf` |
| hrbp-enablement-memo | en | pdf | `engagements/<slug>/comms/hrbp-enablement-memo-en-v<N>.pdf` |

Maximum total with full PDF path: 11 artifact files + 1 config update = 12 Drive writes. Without PDF path: 8 + 1 = 9.

The "up to 16" figure from SPEC.md § 6.5 is the theoretical maximum (4 artifacts × 2 languages × 2 formats). Actual count depends on which languages and formats are enabled per engagement.

---

## 6. Cascade completion summary

After all artifacts complete:

```
Cascade complete for `<engagement-slug>` (cycle: <cycle-name>)

Artifacts written:
  exec-one-pager         en    v<N>   PPTX
  all-hands-announcement fr-ca v<N>   HTML + PDF
  all-hands-announcement en    v<N>   HTML + PDF
  manager-faq            fr-ca v<N>   DOCX
  hrbp-enablement-memo   fr-ca v<N>   DOCX
  hrbp-enablement-memo   en    v<N>   DOCX

All approval stages reset to: drafted
Run `/review <artifact-slug>` on each to diff vs prior version before sharing for review.
```

---

## 7. Partial cascade (skip-and-continue)

If an artifact fails or the operator skips it, the cascade continues with the remaining artifacts. Carry-forward context from the skipped artifact is absent; downstream artifacts that depended on it receive a warning:

> "`exec-one-pager` was skipped. `all-hands-announcement` will be drafted without the headline consistency check. Proceed? (y / abort)"

Partial cascade is valid — operator may want to re-run one artifact separately later.

---

## 8. What this protocol does NOT contain

- Individual artifact render steps — those live in `draft-protocol.md`.
- Artifact content sections, length caps, format specs — those live in `artifact-catalog.md`.
- Valid combination registry — that lives in `valid-combinations-rules.md` + `template_assets/valid-combinations.yaml`.
- Multi-file write ordering contract — that lives in `persistence-and-ledger.md` (mirrored).
- Bilingual co-draft mechanics — those live in `bilingual-rules.md`.
- Compensation-advisor required fields — those live in `compensation-advisor-input-contract.md`.
