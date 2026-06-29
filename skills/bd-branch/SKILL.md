---
name: bd-branch
description: Promote a milestone to a recursive sub-thread. Triggers — /bd branch, 拆子任务.
---
# bd-branch

1. Threshold: the sub-task spans multiple sessions AND has its own state/decisions.
   Otherwise keep it as a checklist under the milestone — do NOT branch.
2. `python <bd.py> --project-dir PROJECT_DIR branch <name> --goal "<sub-goal>"`.
3. Paste the printed link line under the relevant parent COMPASS milestone.
4. Inside `bd/threads/<name>/`, use the same bd commands recursively.
5. On finish: close the parent milestone (✅), bubble key LESSONS up to the parent.
