---
name: bd-init
description: Scaffold a new bd project memory with the near-zero-friction 3-question ritual. Triggers — /bd init, 初始化项目, 起一个项目.
---
# bd-init

0. Resolve `<bd.py>` once: prefer `<WORK_DIR>/.cursor/tools/bd.py`, else the in-place
   repo copy `<bd-repo>/tools/bd.py` (wherever you cloned this repo).
1. Resolve `PROJECT_DIR`; refuse if `PROJECT_DIR/bd/` already exists.
2. Ask the 3 startup questions in ONE round; accept terse answers:
   - ① **North Star** — one sentence: what must this project ultimately achieve,
     and what does *verifiable* success look like?
   - ② The first **2-3 Milestones** — each a *verifiable output*, not an action.
   - ③ The **immediate next step** (becomes Next Action[1]).
3. If the user can't answer now, do the 5-second placeholder start instead:
   `python <bd.py> --project-dir PROJECT_DIR init --quick`.
4. Otherwise scaffold with the answers:
   `python <bd.py> --project-dir PROJECT_DIR init --north-star "<①>" --milestone "<M1> — <verifiable output>" --milestone "<M2> — <…>"`.
5. Open `bd/COMPASS.md`: fill Next Action[1] (with a `verify:` criterion) from ③,
   mark the first milestone `▶`, and stamp Alignment.
6. Validate: `python <bd.py> --project-dir PROJECT_DIR check --lint` — fix every
   FAIL before handing back.
7. **Never auto-start** the work — present COMPASS and wait for the user.
