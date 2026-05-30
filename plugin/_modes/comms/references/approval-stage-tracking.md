# Approval-Stage Tracking

Defines the approval stage chain, field semantics, transition rules, and per-language tracking. Loaded by `draft-protocol.md` (to update stage after draft), `cascade-protocol.md` (to update stages after cascade), and `review-protocol.md` (to surface current stage). Used by `/status` to render the artifact status table.

---

## Design principle

Approval stages are **tracking only** — not gating. The skill records what stage each artifact is in. It does not verify that external approvals actually occurred. Operator is responsible for advancing stages truthfully. This is a deliberate v1 constraint (see SPEC.md § 10). v2 may add `/approve <artifact> <stage>` as a slash command.

---

### 6.1 The 5-stage chain

```
drafted → chro_review → legal_review → ceo_approved → shipped
```

| Stage | Meaning |
|---|---|
| `drafted` | Skill has produced the artifact. No external review has occurred. |
| `chro_review` | Artifact has been sent to the CHRO (or equivalent) for review. |
| `legal_review` | Artifact is in legal review (employment counsel, compliance). |
| `ceo_approved` | CEO (or equivalent authority) has approved the artifact. Content is logically frozen. |
| `shipped` | Artifact has been distributed to the target audience. |

The default chain is configured in `engagement-comms-configs/<slug>.yaml approval_stages:`. Operators may customize the sequence per-engagement. Custom stages are stored as strings and treated as opaque labels — the skill does not validate custom stage names beyond ensuring they are strings.

---

### 6.2 Field location

Per-artifact approval tracking lives in `engagement-comms-configs/<engagement-slug>.yaml` under each artifact entry:

```yaml
artifacts:
  - artifact_type: all-hands-announcement
    languages: [fr-ca, en]
    current_version: 3
    approval_stage:
      fr-ca: ceo_approved          # per-language tracking
      en: chro_review
    last_drafted:
      fr-ca: 2026-04-29
      en: 2026-04-28
    last_drift_check_against_recommendation_revision: <hash>
```

When `languages` has exactly one entry, `approval_stage` and `last_drafted` may be stored as scalar strings rather than maps. When multiple languages are enabled, they must be stored as a map keyed by language code.

---

### 6.3 Stage transitions

**Operator-initiated (v1).** Operator manually edits `engagement-comms-config.yaml` to advance the stage. No slash command in v1.

**Skill-initiated transitions.** The skill automatically sets the stage to `drafted` when it writes a new version of an artifact. No other automatic transitions occur.

**Advancement rules:**
- Stages must advance in the configured chain order — no skipping by default.
- Skip is permitted when operator explicitly edits the config to jump a stage. The skill does not block skips; it does not flag skips in v1 (silent).
- Backward movement (rollback) is permitted; see § 6.5.

---

### 6.4 Lock semantics at `ceo_approved`

When `approval_stage == ceo_approved`:
- The file at `engagements/<slug>/comms/<artifact-slug>-<lang>-v<N>.<ext>` is logically frozen.
- Calling `/draft <artifact-type>` on a `ceo_approved` artifact surfaces: "This artifact is at `ceo_approved`. Drafting will create a new version `v<N+1>` and reset the stage to `drafted`. Continue? (y / n)"
- If confirmed: draft writes `v<N+1>`, sets `approval_stage` back to `drafted`, updates `current_version` to N+1.
- The prior approved version (`v<N>`) is NOT deleted. It remains in `engagements/<slug>/comms/` as the historical record.

When `approval_stage == shipped`:
- Same behavior as `ceo_approved` — logically frozen, any new draft creates `v<N+1>`.

---

### 6.5 Rollback semantics

Rollback means the artifact was at a later stage and needs to return to an earlier one (e.g., CEO rejects after `ceo_approved`).

**v1 process:**
1. Operator manually edits `engagement-comms-config.yaml` to set `approval_stage` back to the target earlier stage (e.g., `chro_review`).
2. Operator calls `/draft <artifact-type>` to produce a new version.
3. The skill creates `v<N+1>`, sets `approval_stage` to `drafted`.
4. The prior version (`v<N>`) remains in `engagements/<slug>/comms/` — not deleted.

There is no `/rollback` command in v1. Rollback is purely an `approval_stage` field edit followed by a new `/draft` call. The skill does not automatically rename or move prior version files.

---

### 6.6 Per-language tracking

FR-CA and EN approval stages are tracked independently. Each language can be at a different stage simultaneously.

Example (from `/status` output):
```
| all-hands-announcement  | fr-ca | v3 | ceo_approved | 2026-04-29 |
| all-hands-announcement  | en    | v2 | chro_review  | 2026-04-28 |
```

Advancing FR-CA to `shipped` does not advance EN. Operator must advance each language independently. There is no "all-languages" shortcut in v1.

---

### 6.7 `/status` output format

The `/status` command reads `engagement-comms-config.artifacts[]` and renders:

```
Engagement: <slug> (cycle: <cycle_name>, effective <cycle_effective_date>)

| Artifact              | Lang  | Version | Stage        | Last drafted |
|-----------------------|-------|---------|--------------|--------------|
| all-hands-announcement | fr-ca | v3     | ceo_approved | 2026-04-29   |
| all-hands-announcement | en    | v2     | chro_review  | 2026-04-28   |
| manager-faq           | fr-ca | v2     | drafted      | 2026-04-29   |
| hrbp-enablement-memo  | fr-ca | v1     | drafted      | 2026-04-27   |
| exec-one-pager        | en    | v3     | ceo_approved | 2026-04-30   |

Anti-patterns active for this engagement: <N>
Drift since last cascade: NONE | DETECTED (if hash differs)
```

If `last_drift_check_against_recommendation_revision` is null for any artifact, report drift as `UNKNOWN` for that artifact.

---

### 6.8 What this file does NOT contain

- Approval gating logic — the skill does not gate writes on approval stage. Tracking only.
- The `/approve` slash command — deferred to v2.
- Per-artifact version file management (creation, deletion) — that lives in `draft-protocol.md`.
- Drift detection mechanics — those live in `compensation-advisor-input-contract.md`.
