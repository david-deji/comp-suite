# .env Read Authorization

Ask the founder before reading any `.env`, `*.env`, `.envrc`, or other secret-bearing file. Pause; name the specific path and the reason; wait for explicit consent. Censoring rules apply to every operation on the values once permitted — see `.claude/rules/secret-handling-discipline.md`.

## Musts

- Ask before opening. State path + reason.
- Read via in-process helper (python, node) once permitted — never `grep`, `awk`, `sed`, `cat`, `head`, `tail`, or `rg` on the file.
- Surface only redacted forms: length, sha256-first-12, or first 4 chars. Never the value.

## Must-Nots

- Never inspect a secret-bearing file without explicit permission, even for "just checking a key name."
- Never echo, redirect, or print any portion of a value beyond 4 chars / sha256 hash.
- Never re-expand a stored secret into argv of an unrelated command. Use `with-secret.sh` for downstream consumers.

## Why

`.env` files hold TM's highest-impact secrets (JWT_SECRET, postgres passwords, OAuth tokens, derived JWTs). Every read puts the value into agent context, transcripts, and post-compaction recovery — all of which persist beyond the immediate session. Founder authorization is the only gate that scales; structural checks are not exempt because key names alone leak presence.

## See also

- `.claude/rules/secret-handling-discipline.md` — stderr leak vector taxonomy and `with-secret.sh` patterns.
- `.claude/rules/deterministic-api-connections.md` — Infisical as canonical secret source; prefer it over local `.env` reads.
