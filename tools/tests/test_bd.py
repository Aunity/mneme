import json
import os
import re
import sys
import subprocess
from pathlib import Path

import pytest

BD = str(Path(__file__).resolve().parents[1] / "bd.py")


def run(args, cwd, stdin=None):
    """Run bd.py as a subprocess; return (returncode, stdout, stderr)."""
    p = subprocess.run(
        [sys.executable, BD, *args],
        cwd=str(cwd), input=stdin, capture_output=True, text=True,
    )
    return p.returncode, p.stdout, p.stderr


def test_init_creates_three_core_files(tmp_path):
    rc, out, err = run(["--project-dir", str(tmp_path), "init",
                        "--north-star", "Ship bd v2",
                        "--milestone", "M1 spec done",
                        "--milestone", "M2 CLI done"], cwd=tmp_path)
    assert rc == 0, err
    bd = tmp_path / "bd"
    assert (bd / "COMPASS.md").is_file()
    assert (bd / "JOURNAL.md").is_file()
    assert (bd / "LESSONS.md").is_file()
    compass = (bd / "COMPASS.md").read_text(encoding="utf-8")
    assert "Ship bd v2" in compass
    assert "M1 spec done" in compass
    assert "M2 CLI done" in compass


def test_init_refuses_when_bd_exists(tmp_path):
    (tmp_path / "bd").mkdir()
    rc, out, err = run(["--project-dir", str(tmp_path), "init"], cwd=tmp_path)
    assert rc != 0
    assert "already exists" in (out + err)


def test_init_quick_uses_placeholders(tmp_path):
    rc, out, err = run(["--project-dir", str(tmp_path), "init", "--quick"], cwd=tmp_path)
    assert rc == 0, err
    compass = (tmp_path / "bd" / "COMPASS.md").read_text(encoding="utf-8")
    assert "<TODO" in compass  # north star placeholder


def _init(tmp_path):
    run(["--project-dir", str(tmp_path), "init",
         "--north-star", "Ship bd v2",
         "--milestone", "M1 spec — spec approved",
         "--milestone", "M2 CLI — bd.py passes tests"], cwd=tmp_path)


def test_resume_prints_compass_and_alignment(tmp_path):
    _init(tmp_path)
    rc, out, err = run(["--project-dir", str(tmp_path), "resume"], cwd=tmp_path)
    assert rc == 0, err
    assert "Ship bd v2" in out          # North Star echoed
    assert "M1 spec" in out             # milestones echoed
    assert "Alignment check" in out     # the prompt line
    assert "▶" in out                   # current milestone surfaced


def test_resume_requires_bd(tmp_path):
    rc, out, err = run(["--project-dir", str(tmp_path), "resume"], cwd=tmp_path)
    assert rc != 0
    assert "No bd/" in (out + err)


def test_save_prepends_entry_and_stamps_compass(tmp_path):
    _init(tmp_path)
    body = "- **advanced**: ▶M2 CLI\n- **did**:\n  - wrote save\n- **next**: run tests"
    rc, out, err = run(["--project-dir", str(tmp_path), "save",
                        "--title", "implement save", "--advanced", "M2 CLI"],
                       cwd=tmp_path, stdin=body)
    assert rc == 0, err
    payload = json.loads(out)
    assert payload["id"].endswith("-001")
    journal = (tmp_path / "bd" / "JOURNAL.md").read_text(encoding="utf-8")
    assert "implement save" in journal
    assert "wrote save" in journal
    # second save same day -> -002, and newest is on top
    rc2, out2, _ = run(["--project-dir", str(tmp_path), "save",
                        "--title", "second"], cwd=tmp_path, stdin="- **did**:\n  - x")
    assert json.loads(out2)["id"].endswith("-002")
    journal2 = (tmp_path / "bd" / "JOURNAL.md").read_text(encoding="utf-8")
    assert journal2.index("second") < journal2.index("implement save")  # newest first
    compass = (tmp_path / "bd" / "COMPASS.md").read_text(encoding="utf-8")
    assert "/bd save" in compass  # Last updated re-stamped


def test_save_rejects_empty_body(tmp_path):
    _init(tmp_path)
    rc, out, err = run(["--project-dir", str(tmp_path), "save", "--title", "x"],
                       cwd=tmp_path, stdin="")
    assert rc != 0
    assert "empty" in (out + err)


def test_check_prints_goal_milestone_action(tmp_path):
    _init(tmp_path)
    rc, out, err = run(["--project-dir", str(tmp_path), "check"], cwd=tmp_path)
    assert rc == 0, err
    assert "North Star: Ship bd v2" in out
    assert "Current milestone:" in out
    assert "▶" in out
    assert "aligned" in out.lower()


def test_lesson_appends_immutably(tmp_path):
    _init(tmp_path)
    rc, out, err = run(["--project-dir", str(tmp_path), "lesson",
                        "--title", "numpy ABI shadowing"], cwd=tmp_path,
                       stdin="- 现象: import 崩\n- 根因: user-site numpy")
    assert rc == 0, err
    first_id = json.loads(out)["id"]
    rc2, out2, _ = run(["--project-dir", str(tmp_path), "lesson",
                        "--title", "second"], cwd=tmp_path, stdin="- 现象: y")
    lessons = (tmp_path / "bd" / "LESSONS.md").read_text(encoding="utf-8")
    # append-only: first entry precedes second (bottom-append, oldest first)
    assert lessons.index("numpy ABI shadowing") < lessons.index("second")
    assert first_id.endswith("-001")
    assert json.loads(out2)["id"].endswith("-002")


def test_branch_creates_recursive_thread(tmp_path):
    _init(tmp_path)
    rc, out, err = run(["--project-dir", str(tmp_path), "branch", "e2e-thrombin",
                        "--goal", "run thrombin round-1 E2E"], cwd=tmp_path)
    assert rc == 0, err
    thread = tmp_path / "bd" / "threads" / "e2e-thrombin"
    assert (thread / "COMPASS.md").is_file()
    assert (thread / "JOURNAL.md").is_file()
    assert (thread / "LESSONS.md").is_file()
    assert "run thrombin round-1 E2E" in (thread / "COMPASS.md").read_text(encoding="utf-8")
    # CLI prints the parent link line for the agent to paste
    assert "threads/e2e-thrombin/" in out


def test_branch_refuses_duplicate(tmp_path):
    _init(tmp_path)
    run(["--project-dir", str(tmp_path), "branch", "dup"], cwd=tmp_path)
    rc, out, err = run(["--project-dir", str(tmp_path), "branch", "dup"], cwd=tmp_path)
    assert rc != 0
    assert "exists" in (out + err)


def test_archive_keeps_newest_n(tmp_path):
    _init(tmp_path)
    for i in range(5):
        run(["--project-dir", str(tmp_path), "save", "--title", f"e{i}"],
            cwd=tmp_path, stdin=f"- **did**:\n  - work {i}")
    rc, out, err = run(["--project-dir", str(tmp_path), "archive", "--keep", "2"],
                       cwd=tmp_path)
    assert rc == 0, err
    journal = (tmp_path / "bd" / "JOURNAL.md").read_text(encoding="utf-8")
    archive = (tmp_path / "bd" / "JOURNAL.archive.md").read_text(encoding="utf-8")
    # newest 2 stay (e4, e3); older 3 moved (e2, e1, e0)
    assert journal.count("### [") == 2
    assert "e4" in journal and "e3" in journal
    assert archive.count("### [") == 3
    assert "e0" in archive and "e2" in archive


def test_archive_noop_when_under_keep(tmp_path):
    _init(tmp_path)
    run(["--project-dir", str(tmp_path), "save", "--title", "only"],
        cwd=tmp_path, stdin="- **did**:\n  - x")
    rc, out, err = run(["--project-dir", str(tmp_path), "archive", "--keep", "2"],
                       cwd=tmp_path)
    assert rc == 0, err
    assert not (tmp_path / "bd" / "JOURNAL.archive.md").exists()


def _make_v1(tmp_path):
    mem = tmp_path / "MEMORY"
    mem.mkdir()
    (mem / "OVERVIEW.md").write_text(
        "# Overview\n\n## Goal\n\nTrain four model families.\n", encoding="utf-8")
    (mem / "STATE.md").write_text(
        "# Current State\n\n## Next Steps\n\n1. wire CLI\n2. ship\n", encoding="utf-8")
    (mem / "SESSIONS.md").write_text(
        "# Sessions\n\n### [2026-06-08-002] — second\n\n- did x\n\n"
        "### [2026-06-08-001] — first\n\n- did y\n", encoding="utf-8")
    (mem / "LESSONS.md").write_text(
        "# Lessons\n\n### [2026-06-01-001] — a gotcha\n\n- root cause\n", encoding="utf-8")


def test_migrate_scaffolds_bd_from_v1(tmp_path):
    _make_v1(tmp_path)
    rc, out, err = run(["--project-dir", str(tmp_path), "migrate"], cwd=tmp_path)
    assert rc == 0, err
    bd = tmp_path / "bd"
    compass = (bd / "COMPASS.md").read_text(encoding="utf-8")
    assert "Train four model families." in compass          # North Star from Goal
    assert "wire CLI" in compass                            # Next Action from Next Steps
    assert "<TODO" in compass and "里程碑" in compass        # milestones placeholder
    journal = (bd / "JOURNAL.md").read_text(encoding="utf-8")
    assert "second" in journal and "first" in journal       # sessions carried over
    lessons = (bd / "LESSONS.md").read_text(encoding="utf-8")
    assert "a gotcha" in lessons
    assert "Milestones" in out  # checklist mentions what agent must fill


def test_migrate_refuses_if_bd_exists(tmp_path):
    _make_v1(tmp_path)
    (tmp_path / "bd").mkdir()
    rc, out, err = run(["--project-dir", str(tmp_path), "migrate"], cwd=tmp_path)
    assert rc != 0


def test_lint_passes_on_fresh_init(tmp_path):
    _init(tmp_path)
    rc, out, err = run(["--project-dir", str(tmp_path), "check", "--lint"], cwd=tmp_path)
    assert rc == 0, out + err
    assert "[ok]   one-current-milestone" in out
    assert "[ok]   next-action-verify" in out


def test_lint_fails_on_two_current_milestones(tmp_path):
    _init(tmp_path)
    compass_path = tmp_path / "bd" / "COMPASS.md"
    txt = compass_path.read_text(encoding="utf-8").replace(
        "2. ⬜ M2 CLI", "2. ▶ M2 CLI")  # now two ▶
    compass_path.write_text(txt, encoding="utf-8")
    rc, out, err = run(["--project-dir", str(tmp_path), "check", "--lint"], cwd=tmp_path)
    assert rc == 1
    assert "[FAIL] one-current-milestone" in out


def test_lint_fails_when_next_action_lacks_verify(tmp_path):
    _init(tmp_path)
    compass_path = tmp_path / "bd" / "COMPASS.md"
    txt = compass_path.read_text(encoding="utf-8")
    # strip the verify clause from the only Next Action line
    txt = re.sub(r" — verify:.*", "", txt)
    compass_path.write_text(txt, encoding="utf-8")
    rc, out, err = run(["--project-dir", str(tmp_path), "check", "--lint"], cwd=tmp_path)
    assert rc == 1
    assert "next-action-verify" in out


def test_lint_warns_on_consecutive_advanced_none(tmp_path):
    _init(tmp_path)
    for i in range(2):
        run(["--project-dir", str(tmp_path), "save", "--title", f"drift{i}"],
            cwd=tmp_path, stdin=f"- **advanced**: none — sidetracked {i}\n- **did**:\n  - x")
    rc, out, err = run(["--project-dir", str(tmp_path), "check", "--lint"], cwd=tmp_path)
    assert rc == 0  # drift is a WARN, not a FAIL
    assert "[warn] no-drift" in out


def test_rollup_folds_old_done_milestones(tmp_path):
    _init(tmp_path)
    compass_path = tmp_path / "bd" / "COMPASS.md"
    txt = compass_path.read_text(encoding="utf-8").replace(
        "1. ▶ M1 spec — spec approved\n2. ⬜ M2 CLI — bd.py passes tests",
        "1. ✅ M1 — out — done 2026-01-01\n"
        "2. ✅ M2 — out — done 2026-02-01\n"
        "3. ▶ M3 — out\n4. ⬜ M4 — out")
    compass_path.write_text(txt, encoding="utf-8")
    rc, out, err = run(["--project-dir", str(tmp_path), "rollup", "--keep-done", "1"],
                       cwd=tmp_path)
    assert rc == 0, out + err
    assert json.loads(out)["rolled_up"] == 1
    result = compass_path.read_text(encoding="utf-8")
    assert "## Milestones (archived)" in result
    active, archived = result.split("## Milestones (archived)")
    assert "M1 — out — done 2026-01-01" in archived   # oldest done moved
    assert "M1 — out — done 2026-01-01" not in active  # gone from active
    assert "M2 — out — done 2026-02-01" in active      # newest done kept inline
    assert "▶ M3" in active                            # current milestone untouched


def test_rollup_noop_when_few_done(tmp_path):
    _init(tmp_path)  # zero done milestones
    rc, out, err = run(["--project-dir", str(tmp_path), "rollup"], cwd=tmp_path)
    assert rc == 0, err
    assert "nothing to roll up" in out
    assert "## Milestones (archived)" not in \
        (tmp_path / "bd" / "COMPASS.md").read_text(encoding="utf-8")


def test_embedded_compass_matches_template_file():
    """The COMPASS template embedded in bd.py must not drift from the .md file."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bd", BD)
    bd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bd)
    tmpl_file = (Path(BD).resolve().parents[1] / "templates" / "bd" /
                 "COMPASS.template.md").read_text(encoding="utf-8")
    # Compare the stable structural lines (section headers) — both must list the
    # same '## ' sections in the same order.
    def headers(t):
        return [l for l in t.splitlines() if l.startswith("## ")]
    assert headers(bd.COMPASS_TEMPLATE) == headers(tmpl_file)
