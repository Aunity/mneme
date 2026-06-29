---
name: bd-save
description: Persist a work session into bd memory. Triggers — /bd save, 交接一下, save progress.
---
# bd-save

1. Resolve `PROJECT_DIR`; require `PROJECT_DIR/bd/`.
2. Draft the JOURNAL entry body (advanced / did / [decision]? / [gotcha]? / produced / next).
3. Pipe it: `printf '%s' "<body>" | python <bd.py> --project-dir PROJECT_DIR save --title "<title>" --advanced "<milestone>"`.
4. Read the printed `alignment_reminder`. Then **rewrite** `bd/COMPASS.md`:
   `Current Frontier`, `Next Action` (each with `verify:`), and stamp `Alignment`.
   Close any finished milestone (✅ + one-line rollup) and mark the new ▶.
5. If a genuine reusable gotcha appeared, also run `bd lesson` (see bd-log).
6. Validate the rewrite with `python <bd.py> --project-dir PROJECT_DIR check --lint`.
7. If `JOURNAL.md` has grown large, suggest `bd archive --keep N`; if many
   milestones are ✅, suggest `bd rollup` to keep the spine short.
