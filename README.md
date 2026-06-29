# bd (北斗) — Goal-Spine Project Memory

**English** | [中文](README.zh-CN.md)

> A **goal-driven** memory workflow for AI collaboration: it flips project memory
> from *"record for the archive"* to *"record to advance the goal."*
> One spine per project (COMPASS) + two append-only logs (JOURNAL / LESSONS),
> a single always-on rule, and a pure-stdlib CLI.

## The 4 pain points it solves

1. **Cross-session amnesia** — `bd resume` prints the spine + recent log + an alignment prompt in one shot.
2. **Deep-dives polluting the main session** — `bd branch` splits a sub-task into a recursive spine under `bd/threads/<name>/`.
3. **Pre-compaction anxiety** — memory lives on disk and doesn't consume context; when you near the limit, do an `[emergency-save]`.
4. **The record dilemma** — 3 core documents; decisions are inlined with a `[decision]` tag instead of being sorted into separate files.

## Core model: 1 spine + 2 logs

| Document | Nature | Lifecycle |
|---|---|---|
| `bd/COMPASS.md` | Spine: North Star / Constraints / **Milestones** / Frontier / **Next Action (verify)** / **Alignment** | Everything below "Frontier" is rewritten on each save; the goal rarely changes |
| `bd/JOURNAL.md` | append-only, newest-first, one entry per save | immutable; decisions inlined as `[decision]` |
| `bd/LESSONS.md` | append-only, never-lose-it gotchas | immutable |

Invariants: Milestones must be non-empty; every Next Action carries a `verify:`;
each save stamps an Alignment (including an `advanced:` field — a run of `none`
is a drift warning).

## CLI (`tools/bd.py`, pure Python 3 stdlib, zero dependencies)

| Command | Purpose |
|---|---|
| `bd init [--quick]` | Start a project (3-question ritual, or a 5-second placeholder) |
| `bd resume` | Print the spine + the latest N journal entries + an alignment prompt |
| `bd save --title … --advanced …` | Read JOURNAL body from stdin → stamp an id, prepend, refresh the stamp + alignment prompt |
| `bd check [--lint]` | Drift self-check; `--lint` validates COMPASS invariants (non-zero exit on FAIL) |
| `bd lesson --title …` | Append a LESSONS entry |
| `bd branch <name>` | Promote a Milestone to a recursive sub-thread under `bd/threads/<name>/` |
| `bd rollup [--keep-done N]` | Fold old ✅ milestones into `## Milestones (archived)` to keep the spine short |
| `bd archive [--keep N]` | Move old JOURNAL entries into `JOURNAL.archive.md` |

Mechanical vs. semantic split: the CLI only does ids / placement / scaffold
rewrites / printing alignment; the semantics (entry bodies, whether a milestone
should close, alignment conclusions) come from the agent.

## Install

There's no installer to run — copy three things into your agent's config dir
(`.cursor/` for Cursor; see [Using bd outside Cursor](#using-bd-outside-cursor) for other frameworks):

| Source | Destination |
|---|---|
| `rules/bd.mdc` | `<config>/rules/bd.mdc` — the single always-on rule (~1 page) |
| `skills/bd-{init,resume,save,log,branch}/` | `<config>/skills/` |
| `tools/bd.py` | `<config>/tools/bd.py` (or just run it in-place) |

Then start a project:

```bash
python tools/bd.py --project-dir /path/to/project init
```

## Trigger cheat-sheet

| Trigger | Behavior |
|---|---|
| `/bd init` | 3-question ritual, creates the `bd/` skeleton |
| `/bd resume` | Read spine + recent log + alignment prompt (read-only; does not auto-start work) |
| `/bd save` | Prepend a JOURNAL entry + rewrite COMPASS Frontier/Next/Alignment |
| `/bd lesson` | Append a LESSONS entry |
| `/bd branch` | Promote a Milestone into a recursive sub-thread |

## Using bd outside Cursor

bd splits into a portable **engine** and a thin **integration layer**:

- **Engine** — `tools/bd.py` (pure stdlib) + the plain-markdown `bd/` files. It has
  zero Cursor dependencies and runs identically under any agent, or in a bare terminal.
- **Integration layer** — only how the agent auto-loads the always-on rule and
  discovers the skills. This is the only part that changes per framework.

To port, drop the body of `rules/bd.mdc` into the host framework's always-on
instructions file, and put the skills where that framework looks for them:

| Framework | Always-on rule → | Skills / commands |
|---|---|---|
| Cursor | `.cursor/rules/bd.mdc` | `.cursor/skills/` |
| Claude Code | `CLAUDE.md` | `.claude/skills/` + `.claude/commands/` |
| Codex | `AGENTS.md` | no skill system — inline the procedures or lean on the CLI |
| Gemini CLI | `GEMINI.md` | `activate_skill` |

The CLI itself is unchanged everywhere (`python tools/bd.py …`); the `/bd …`
slash-triggers just become ordinary prompts.

**One caveat:** frameworks without a skills mechanism (e.g. Codex / `AGENTS.md`)
can't lazy-load the `bd-*` procedures on demand — either inline the short
procedures into the always-on file, or rely on the CLI being self-documenting
(`bd resume` prints the spine + log + alignment; `bd save` prints the alignment reminder).

## License

[MIT](LICENSE)
