---
name: bd-log
description: Append a single LESSON to bd memory. Triggers — /bd lesson, 记教训, 记踩坑.
---
# bd-log

1. Resolve `PROJECT_DIR`; require `PROJECT_DIR/bd/`.
2. Threshold: only a failed path or a non-obvious gotcha with reuse value.
   Decisions go inline in the JOURNAL entry as `[decision]`, not here.
3. Draft body (现象 / 触发条件 / 根因 / 解决 / 复用提示) — WHY, not HOW.
4. `printf '%s' "<body>" | python <bd.py> --project-dir PROJECT_DIR lesson --title "<one-line>"`.
