---
name: bd-resume
description: Load bd project memory at session start. Triggers — /bd resume, 接手, 继续上次的, load compass.
---
# bd-resume

0. Resolve `<bd.py>` once: prefer the installed copy `<WORK_DIR>/.cursor/tools/bd.py`;
   if absent, use the in-place repo copy `<bd-repo>/tools/bd.py` (wherever you cloned
   this repo). Use that absolute path for every `python <bd.py> …` call in the bd skills.
1. Resolve `PROJECT_DIR` (ask if unknown; must be inside `WORK_DIR`).
2. If `PROJECT_DIR/bd/` is missing, suggest `bd init`. Do not scaffold without the user.
3. Run `python <bd.py> --project-dir PROJECT_DIR resume`.
4. Report back, in this order: North Star, current ▶ milestone + what's left,
   Next Action[1] and whether it is aligned, then the recent journal tail.
5. **Never auto-start** the Next Action — present and wait for the user.
