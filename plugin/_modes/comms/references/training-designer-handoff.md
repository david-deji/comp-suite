# Training-Designer Handoff

Optional accelerator. When `engagement-comms-config.training_handoff.enabled == true`, comp-comms-builder reads `comp-training-designer`'s `message-map.yaml` to pre-populate per-audience framing decisions and skip portions of the audience-profile interview.

Loaded by `ingest-protocol.md` at the start of `/ingest` when the handoff is enabled.

---

## Design principle

This handoff is fully optional. comp-comms-builder operates at full capability without comp-training-designer running first. The handoff is an efficiency accelerator when both skills are used in the same cycle — it saves the operator from re-entering audience framing decisions that comp-training-designer already captured.

---

### 8.1 When to enable

Enable when:
- comp-training-designer has already run `/ingest` for the same compensation cycle (same `engagement_slug`).
- The `message-map.yaml` is complete (state: `ingested` in `engagement-training-configs/<slug>.yaml cycles_trained[]`).
- The audience set in comp-training-designer overlaps with the audience set for this comms cycle.

Do not enable when:
- comp-training-designer has not run yet for this cycle.
- The `message-map.yaml` is incomplete or in a partial state.
- The engagement-slug differs between skills (separate engagements cannot share a message-map).

---

### 8.2 Configuration

In `engagement-comms-configs/<slug>.yaml`:

```yaml
training_handoff:
  enabled: true
  message_map_path: cycles/<engagement-slug>/<cycle-slug>/message-map.yaml
```

`message_map_path` is a path relative to the local `$STATE_ROOT` state root. It must point to a file written by comp-training-designer's `/ingest` Workshop synthesis.

If `enabled: true` but `message_map_path` is null: surface a warning and fall back to standard audience-profile interview. Do not abort.

---

### 8.3 What is read from message-map.yaml

The skill reads the following fields from `message-map.yaml` at the start of `/ingest`:

| Field | Used for |
|---|---|
| `messages[].audiences.all_employees.framing` | Pre-populate `key_concerns` for `all_employees` audience profile |
| `messages[].audiences.people_managers.framing` | Pre-populate `key_concerns` for `people_managers` audience profile |
| `messages[].audiences.hrbps.framing` | Pre-populate `key_concerns` for `hrbps` audience profile |
| `messages[].audiences.exec_board.framing` | Pre-populate `key_concerns` for `exec_board` audience profile |
| `messages[].anticipated_objections[]` | Pre-populate `key_objections_anticipated` for the compensation-advisor input contract |
| `messages[].audiences.<audience>.depth` | Informs reading_level calibration (depth 1 → grade-9; depth 2 → grade-12; depth 3-4 → college) |

Fields not present in the message-map schema (comp-training-designer uses `employees`, `managers`, `hrbps`, `execs` as audience keys; comp-comms-builder uses `all_employees`, `people_managers`, `hrbps`, `exec_board`): apply the following mapping:

| comp-training-designer key | comp-comms-builder key |
|---|---|
| `employees` | `all_employees` |
| `managers` | `people_managers` |
| `hrbps` | `hrbps` |
| `execs` | `exec_board` |

---

### 8.4 What portions of /ingest are skipped

When handoff is enabled and `message-map.yaml` is read successfully:

**Skipped:** the audience-profile inference interview section (sub-phase 3 in `ingest-protocol.md`). The `key_concerns` for each audience are pre-populated from `message-map.yaml framing` fields. Operator is shown the pre-populated values and asked to confirm or edit — not re-interviewed from scratch.

**Not skipped:**
- Voice extraction per speaker (sub-phase 2) — message-map.yaml does not contain speaker register data.
- Channel rules detection (sub-phase 4) — message-map.yaml does not contain channel rules.
- Anti-pattern surfacing (sub-phase 5) — always operator-confirmed; not pre-populated from training.
- Brand discovery (sub-phase 6) — not in scope for comp-training-designer.
- Workshop synthesis (sub-phase 7) — always runs.

Time saving: approximately 10–15 minutes from a typical 60-minute `/ingest self` session.

---

### 8.5 Failure handling

If `message_map_path` is set but the file cannot be read (path not found, file malformed, Drive permission issue):
1. Surface warning: "Could not read `<path>`. Proceeding with standard audience-profile interview."
2. Continue `/ingest` with the standard flow (no skip).
3. Do not abort.

The handoff is an accelerator, not a dependency. A read failure falls back gracefully to the standard flow.

---

### 8.6 What this file does NOT contain

- The message-map.yaml schema — that is owned by comp-training-designer (`template_assets/message_map_template.yaml` in that repo).
- The full `/ingest` flow — that lives in `ingest-protocol.md`.
- Audience profile rules — those live in `audience-profile-rules.md`.
- Training-designer artifacts — comp-comms-builder reads from comp-training-designer but does not write to its persistence paths.
