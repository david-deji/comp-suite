# Secret Handling Discipline

When an agent handles a secret in a shell context, the secret must never reach a position where the shell could echo its expanded value to stderr. Claude Code captures stderr `2>&1` into the persistent transcript; every leak is rotation-grade.

Anchor incidents (all 2026):
- 04-30 — `bash -x fetch-key.sh` xtraced 3 secrets to stderr → transcript.
- 05-02 (a) — `PSQL="docker -e PASS=$VAR ..."` then `$PSQL ...`; zsh `command not found:` echoed the expanded line including the cleartext password → transcript.
- 05-02 (b) — `grep -nE '^(ANON_KEY|SERVICE_ROLE_KEY)=' /home/<user>/db/.env` printed both JWT values directly to the transcript. Inspecting an env file with grep returns the matched lines including their cleartext values. The full rotation cascade (JWT_SECRET + derived JWTs + 9 primitives) was triggered as a result.
- 05-02 (c) — `docker compose config` (run inside `~/supabase`) printed the resolved YAML with `${VAR}` interpolations expanded, leaking `JWT_SECRET` + `SUPABASE_DB_URL` (postgres password) + `SUPABASE_ANON_KEY` + `SUPABASE_SERVICE_ROLE_KEY` to the transcript. `docker compose config` is documented to resolve and print the merged config — when `.env` interpolations are used (the upstream Supabase pattern), every value is emitted in cleartext. Same class as `grep`: any tool that prints the resolved content of an env-bearing file leaks values.

The shell has at least 9 confirmed paths that can emit a variable's expansion to stderr (xtrace, ERR/DEBUG traps, unquoted `$VAR` as argv[0], zsh `command_not_found_handler`, `set -e` errexit messages, history `!`, `eval` syntax errors, brace expansion errors, zsh `PRINT_EXIT_VALUE`). Full taxonomy: `research-bureau/output/2026-05-02-shell-secret-leak-prevention-ai-coding-agents-stderr.md`. Behavioral rules block one path at a time; only structural isolation blocks the class.

## The Default — `with-secret`

Use `scripts/api-keys/with-secret.sh` for every shell consumption of a fetched secret. It pipes the secret through stdin so the value never enters argv, env, or a shell variable.

```bash
bash scripts/api-keys/with-secret.sh supabase-postgres-password -- \
  docker run --rm -i postgres:16 sh -c \
  'PGPASSWORD=$(cat) psql -h <db-host> -p 54329 -U postgres -c "SELECT 1"'
```

When `with-secret.sh` does not fit, use the env-prefix form on a single command — `PGPASSWORD="$(bash scripts/api-keys/fetch-key.sh pg-pass)" psql -h ...`. The value scopes to one command's environment and the parent shell never holds it.

Other safe patterns (`--env-file` + EXIT trap, Docker BuildKit `--secret`) are documented in the research synthesis. Use only when the canonical patterns above do not fit.

## Musts

- Use `with-secret.sh` for any shell command that consumes a fetched secret. Drift requires a one-line note in the issue log.
- Quote every parameter expansion that involves a secret-typed variable. `"$VAR"`, never `$VAR`. Quoting prevents `command_not_found_handler` from receiving the expanded argv.
- Debug secret-handling scripts with `fetch-key.sh --debug`. It prints redacted diagnostics (length, first 4 chars).
- Run `bash scripts/audit-secret-shell.sh` before committing new secret-handling shell. Review every match.

## Must-Nots

- Never store a secret in a shell variable that you will re-expand into another command string. Pipe through `with-secret.sh` instead.
- Never invoke `$VAR` unquoted as argv[0], even with non-secret values. The habit ships into a secret-handling site eventually. Use functions or quote.
- Never use `bash -x`, `set -x`, or any xtrace flag on a script that fetches or consumes secrets. Use `--debug` instead.
- Never set an `ERR` or `DEBUG` trap that prints `$BASH_COMMAND` in any context that may handle secrets.
- Never `eval` a string that interpolates a secret. eval expands then parses; syntax errors emit the expanded source.
- Never `setopt PRINT_EXIT_VALUE` (zsh) globally in a shell that handles secrets.
- Never paste a secret into chat. If a founder offers one, refuse and redirect to Infisical.
- Never inspect a `.env` file or other secret-bearing file with a tool that prints matched lines (`grep`, `awk '/.../'`, `sed -n '/.../p'`, `rg`, `head`, `tail`, `cat`). To check which keys are present without leaking values, use a name-only filter: `grep -E '^[A-Z_]+=' file | cut -d= -f1`, or read the value into a variable and print only its length: `len=$(grep '^KEY=' file | cut -d= -f2- | wc -c); echo "KEY length: $len"`. WHY: agent transcripts capture stdout AND stderr; any tool that emits the matched line emits the value.
- Never run `docker compose config` (or `podman-compose config`, `helm template`, `kustomize build`, or any other config-resolving renderer) on a stack whose values come from `.env` interpolation — these tools print the merged, fully-expanded YAML/manifest including every `${VAR}` value in cleartext. Inspect the source compose file with `cat docker-compose.yml` (placeholders only, safe), or query specific resolved fields via the running container: `docker inspect <container> --format '{{ index .Config.Env 0 }}'` is also unsafe — every `Env` entry contains cleartext. To verify a secret is present without printing it: `docker exec <container> sh -c 'test -n "$VAR" && echo "VAR set, length: ${#VAR}"'`. WHY: same class as grep — config-resolving tools render cleartext interpolations to stdout.

## Lint Backstop

`.semgrep/secret-shell.yml` catches three committed-shell anti-patterns at WARNING severity. `scripts/audit-secret-shell.sh` runs the same checks via grep without Semgrep. Both catch *committed* code only — they do not catch agent-improvised inline shell, which is the dominant leak class. The default pattern above is the primary defence; lint is the backstop.

Promote Semgrep severity from WARNING to ERROR after 30 days of false-positive observation per `.claude/rules/cost-discipline.md`.

## Escalation Triggers

- Any secret value visible in a Claude Code transcript → P0 rotation issue (template: 0356-OPS), do not "wait and see."
- A new stderr echo vector discovered that is not in the synthesis taxonomy → add it to the taxonomy and the audit script, file an issue.
- A founder pastes a secret in chat → refuse the value, redirect to Infisical.
- An audit reveals a committed script with the var-as-cmd or xtrace+secret-fetcher anti-pattern → near-miss; refactor to `with-secret.sh`.

## See Also

- `.claude/rules/dotenv-read-authorization.md` — ask-before-reading rule for `.env` and other secret-bearing files (companion rule).
- `.claude/rules/deterministic-api-connections.md` — fetch-key.sh discipline and the bash -x prohibition (companion rule).
- `scripts/api-keys/with-secret.sh`, `.semgrep/secret-shell.yml`, `scripts/audit-secret-shell.sh` — the enforcement artifacts this rule references.
- `research-bureau/output/2026-05-02-shell-secret-leak-prevention-ai-coding-agents-stderr.md` — full vector taxonomy, 4 safe patterns, sources.
- `internal-ops-bureau/issues/0357-OPS-...md` — the issue this rule resolves.

---

## v2 adapter footer (comp-suite, 2026-05-08)

This rule was ported verbatim from TM `.claude/rules/secret-handling-discipline.md` @ commit `4b1dd5d7`.
The TM body above is authoritative — the 9 stderr leak vectors and the 4 safe shell patterns apply universally.

**Path substitutions applied** (TM → comp-suite):
- TM `scripts/api-keys/with-secret.sh` → comp-suite has NO equivalent yet. If a future MCP wrapper or script in `v2/scripts/` needs to consume a fetched secret beyond the env-var-at-startup pattern, port `with-secret.sh` then; do not improvise.
- TM `scripts/api-keys/fetch-key.sh` → comp-suite uses environment-variable-at-MCP-startup (set by Claude Code from `.claude/settings.json` or the user's session). Future `fetch-key.sh` analogue is out of scope until a credential-rotation workflow materializes.
- TM `.semgrep/secret-shell.yml` and `scripts/audit-secret-shell.sh` → not ported. If shell secret-handling code grows in comp-suite, port the audit script then.

**TM-specific references comp-suite ignores:**
- Infisical CLI authentication (`infisical login`, machine-identity in `~/.config/telos-machina/infisical.env`)
- TM-bureau issue references (0356-OPS, 0357-OPS) — anchor incidents documenting TM rotations
- TM secret register at `scripts/api-keys/register.yaml`

**Comp-suite anchor:**
- MCP wrapper scripts at `scripts/mcp-wrappers/*.sh` (perplexity.sh; market uses HTTP transport, no local wrapper) launch MCP servers with env-vars set by Claude Code's settings.json — they do NOT currently fetch secrets via shell. If any wrapper grows a secret-fetch step, the 4 safe patterns above (with-secret pipe-through-stdin, env-prefix scoped to one command, --env-file + EXIT trap, Docker BuildKit --secret) are the contract.
- The 9 stderr leak vectors apply to any inline shell the orchestrator improvises during `/comp` dispatch — especially `bash -x` and unquoted `$VAR` as argv[0].

**Companion rule**: `dotenv-read-authorization.md` (also ported verbatim) covers the ask-before-reading discipline for `.env` and other secret-bearing files.
