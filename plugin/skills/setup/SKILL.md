---
name: setup
description: |
  One-time setup helper for comp-suite. Use right after installing comp-suite, or
  whenever comp-suite or the market MCP returns a 401 / unauthorized / "token not
  set" error, or the user says they need to register or set up their market-data
  token. Produces the exact copy-pasteable terminal command for the user's OS with
  the real install path resolved. Also invoked as /comp-suite:setup.
allowed-tools: Bash
---

# /comp-suite:setup — token setup helper

Your job: give the user the exact command to run **in their terminal** to register
their market-data token, with the real absolute path resolved for their machine —
then the three next steps. You do NOT run the setup script yourself: the token is
entered by the user in a real terminal (hidden input), and the variable is only read
when Claude Code launches.

## Step 1 — Resolve the plugin root and detect the OS

`SKILL_DIR` = the absolute path from the injected "Base directory for this skill:"
preamble above. The plugin root is the nearest ancestor of `SKILL_DIR` that contains
both `_core/` and `_modes/`; the setup scripts live there. Run:

```bash
SKILL_DIR="<absolute path from the 'Base directory for this skill:' preamble>"
ROOT="$SKILL_DIR"
while [ "$ROOT" != "/" ] && ! { [ -d "$ROOT/_core" ] && [ -d "$ROOT/_modes" ]; }; do
  ROOT="$(dirname "$ROOT")"
done
echo "PLUGIN_ROOT=$ROOT"
echo "OS=$(uname -s 2>/dev/null || echo Windows)"
ls "$ROOT/setup.sh" "$ROOT/setup.ps1" 2>/dev/null
```

If the `ls` shows neither script, the plugin did not install cleanly — tell the user
to re-run `/plugin install comp-suite@comp-suite` and try again. Otherwise continue.

## Step 2 — Print the one command for their OS

Use the resolved `PLUGIN_ROOT` literal (never the `<ROOT>` placeholder) and the OS:

- **macOS** (`Darwin`) or **Linux** — they run, in a terminal:
  ```
  bash "PLUGIN_ROOT/setup.sh"
  ```
- **Windows** (`uname` missing, or reports `MINGW`/`MSYS`/`CYGWIN`) — they run, in PowerShell:
  ```
  powershell -ExecutionPolicy Bypass -File "PLUGIN_ROOT\setup.ps1"
  ```
  On Windows convert the resolved path's forward slashes to backslashes.

Print exactly one command — the one matching their OS — with the real path substituted.

## Step 3 — Tell them what happens next (keep it to three lines)

1. Run that command in a **terminal**, not inside Claude Code. It asks for your
   language, then your token — the token stays **hidden** as you type (seeing nothing
   is normal), then it saves it.
2. **Fully quit and reopen Claude Code** afterward — the token is only read at launch.
   On macOS, start it from the Terminal (`claude`), not the Dock, or you will get a 401.
3. Verify by asking comp-suite for a market benchmark. A 401 / unauthorized error means
   the token is wrong — re-run the same command.

Keep the whole reply short: the single command for their OS, then the three steps.
For the full bilingual walkthrough, point them to `INSTALL.md` at the plugin root.
