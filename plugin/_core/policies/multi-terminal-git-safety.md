# Multi-Terminal Git Safety

A single git working tree has *one* checked-out branch. When two Claude Code terminals run inside the same monorepo working directory, they share `.git/HEAD` and the on-disk files. Whatever branch one terminal switches to becomes the other terminal's branch too — silently, mid-session.

This rule defines how to detect the collision, recover safely, and prevent it from happening.

**Anchor incident:** 2026-04-30 — a session opened on `main`, but a second terminal was running `/build` for `gpu-broker` *inline* (not in a worktree). The shared HEAD was switched to `build/gpu-broker/main`. The first terminal's edits got captured by a pre-compaction WIP auto-save commit on the build branch, alongside ~2,200 lines of unrelated cross-bureau work. Pushing from the build branch would have shipped a half-done build, plus four other agents' files, to origin. This rule prevents that.

## Detection

Check at session start, after any compaction, and before every `git push`:

| Signal | What it means |
|---|---|
| `git status` shows a branch you didn't switch to | Another terminal switched HEAD under you |
| `git log -1` shows `WIP: pre-compaction auto-save` you didn't author | Your edits are inside another agent's commit |
| Working tree contains files from many bureaus with no unifying theme | Cross-contamination from a shared tree |
| `git worktree list` shows only the monorepo path while branches like `build/*` are checked out there | A `/build` ran inline rather than in a worktree |

Two-line confirmation: `git rev-parse --abbrev-ref HEAD` (current branch) and `git worktree list` (worktree map). If branch ≠ what session-start said, you are affected.

## Musts

- **Never `git checkout` to a different branch in the shared monorepo working tree** when another terminal is active. Switching yanks files out from under the other agent mid-task. WHY: the other terminal's `git status`, `git diff`, edits, and pre-compaction auto-save would all see your branch's files instead of theirs.
- **When you discover you are on the wrong branch**, recover via a fresh worktree on the target branch (recipe below). Do not "fix it" by switching the shared tree.
- **Before `git push`**, run `git rev-parse --abbrev-ref HEAD` and confirm the branch matches what you intend to push. Particularly important when more than one terminal is open.
- **`/build` pipelines must use `git worktree add`** to isolate their build branches into a separate path. The `/build` skill should never `git checkout` in the shared monorepo tree. If you find yourself in a `/build` skill that `checkout`s inline, escalate before continuing.

## Must-Nots

- Never push from a `build/*` branch you did not author. Build-branch lifecycle is owned by the agent running the build; `/build` finishes with a merge commit to `main`, which is the official integration point.
- Never include files in a commit you did not edit yourself. WIP auto-save sweeps everything; that does not authorize you to push everything. Cherry-pick your own files only.
- Never run `git reset --hard` or `git checkout -- .` to "clean up" a working tree shared with another terminal. You will destroy the other agent's uncommitted work. Stash, branch, or worktree out instead.

## Recovery Playbook

When you discover you are on the wrong branch in the shared tree:

```bash
# 1. Sync local copy of the target branch
git fetch origin <target-branch>     # usually: main

# 2. Spin up a SEPARATE worktree for the target branch — does not touch shared tree
git worktree add ~/Projects/.tm-<target>-worktree <target-branch>
cd ~/Projects/.tm-<target>-worktree
git pull --ff-only origin <target-branch>   # if local was behind

# 3. Cherry-pick ONLY your files from the WIP commit on the wrong branch
#    Get the WIP SHA from: git log <wrong-branch> --oneline -5
git checkout <wip-sha> -- path/to/file1 path/to/file2 ...

# 4. Verify staged files match exactly your scope
git status

# 5. Commit cleanly (real message, not WIP) and push
git commit -m "your real commit message"
git push origin <target-branch>

# 6. Clean up worktree from outside it
cd /home/<user>/Projects/telos-machina
git worktree remove ~/Projects/.tm-<target>-worktree
```

The original (wrong-branch) terminal is untouched throughout — it never sees a `git checkout`, so the other agent continues working.

## Communicating to the Other Terminal

When you have cherry-picked files from another agent's WIP commit onto `main`, send a short notice to that terminal so the future merge is unambiguous:

```
Heads-up: I cherry-picked these files from your branch's WIP auto-save
(<wip-sha>) onto main as commit <new-sha>:
  - <file 1>
  - <file 2>
These are now on origin/main. When you eventually merge <branch> back
into main, those files will have identical content in both branches and
should resolve as no-op. No action needed from you. Continue your work.
```

This prevents the other agent from being surprised by a "phantom merge" of files they thought were unchanged, and avoids both terminals trying to push the same content from different branches.

## Escalation Triggers

- **More than one terminal active in the shared tree, AND HEAD just changed.** Pause, identify the other terminal's task, do not edit further until you understand whether your edits will collide with theirs.
- **A WIP auto-save commit you did not author bundled your work with another agent's.** Do the recovery playbook before any `git push` from the wrong branch.
- **A `/build` is running inline (not in a worktree).** Surface to the founder — this is a `/build` skill bug, not a normal state. The `/build` should be using `git worktree add`.

## Why this overrides "just push"

A bare `git push` from a `build/*` branch with mixed-author WIP content can ship four agents' partial work to `origin` simultaneously. The blast radius is high: cross-bureau changes, half-done features, and stale spec assumptions all land on `main` together. The cost of the worktree dance is sixty seconds; the cost of an unwanted `main` push is hours of revert + re-coordination. See also `.claude/rules/multi-repo-git.md` (sibling-repo discipline) and `.claude/rules/session-protocol.md` (pre-compaction WIP auto-save behaviour that creates this hazard).

---

## v2 adapter footer (comp-suite, 2026-05-08)

This rule was ported verbatim from TM `.claude/rules/multi-terminal-git-safety.md` @ commit `4b1dd5d7`.
The TM body above is authoritative — the recovery playbook and detection signals apply identically.

**Path substitutions applied** (TM → comp-suite):
- TM "monorepo" → comp-suite repo at `<your-comp-suite-clone>/`
- TM "sibling repos" — comp-suite has none currently. The single `$STATE_ROOT/.git/` subtree (gitignored from the parent) is its own working tree but is not a sibling repo in the TM sense.
- TM `/build` skill's `git worktree add` pattern — comp-suite has no `/build` skill yet; the analogue is the build branches this very build creates (e.g., `policies-port`, `v2-attempt-2-port`, `build/comp-suite-v2/main`).

**TM-specific references comp-suite ignores:**
- Multi-repo discipline (TM constellation of 11+ repos under apps/ and clients/) — see `multi-repo-git.md` (DROPPED in this port)
- Sibling-repo `.gitignore` exclusions — N/A
- `/build` skill anchor incident (2026-04-30 spacetime-4x cross-contamination)

**Comp-suite anchor:**
- Solo operator with two `/comp` terminal sessions open on the same engagement (e.g., one mid-advisor-draft, one running `/comp doctor`). Both share `comp-suite/.git/HEAD`. If one switches branch (e.g., the doctor session checks out a maintenance branch to patch a primitive), the advisor session's edits land on the maintenance branch silently.
- This very build: `policies-port` branch checked out in this session; if a parallel session runs on `v2-attempt-2-port` and the founder pulls main, the cross-contamination class applies.

**Mitigation in comp-suite**: single working tree, single operator. Discipline > tooling. The 60-second pre-push branch-confirm check (TM rule body) is the cheapest defense and applies identically here.
