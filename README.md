# comp-suite

A Claude Code plugin for compensation work — market benchmarks, pay-equity analysis,
decision documents, and branded decks. Four modes: advisor, comms, training, transformer.
Quebec CNESST pay-equity tooling, bilingual FR-CA.

A personal power-tool, shared as a plugin.

## Install

```
/plugin marketplace add david-deji/comp-suite
/plugin install comp-suite@comp-suite
```

Then run the bundled setup script **once** to register your market-data token, and restart
Claude Code:

- **macOS / Linux**: `bash setup.sh` (in the plugin folder)
- **Windows**: right-click `setup.ps1` → **Run with PowerShell**

Full walkthrough, FR + EN: [`plugin/INSTALL.md`](plugin/INSTALL.md).

Verify with `/comp-suite:comp` — e.g. ask it to *benchmark a software developer in Quebec*.

## What's in this repo

| Path | What |
|---|---|
| `plugin/` | The plugin itself — agents, skills, modes, hooks, `.mcp.json`, and the per-OS setup scripts. |
| `.claude-plugin/marketplace.json` | Single-plugin marketplace manifest so `/plugin marketplace add` resolves this repo. |

The plugin is built from a private source tree and committed here as a self-contained
artifact. Updates are versioned via `plugin/.claude-plugin/plugin.json` — your install only
changes when that version changes.

## Notes

- The only thing you configure is a market-data token (set by `setup.sh` / `setup.ps1`). Web
  research works out of the box via Claude Code's built-in search.
- Your token lives only in your own computer's user environment — never written into the
  plugin or sent anywhere except the market server you query. No personal data in comp-suite.
