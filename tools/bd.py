#!/usr/bin/env python3
"""bd.py — deterministic mechanics for the 北斗 (bd) goal-spine memory workflow.

Owns ONLY mechanical work for a PROJECT_DIR/bd/ directory: scaffolding (init),
id allocation + entry placement (save/lesson), COMPASS stamping, and
parsing/printing for resume/check. All SEMANTIC content (entry bodies, whether
a milestone is done, alignment conclusions) stays with the agent.

Pure Python 3 standard library — no third-party deps. Templates are embedded
below so the tool is fully self-contained and portable.

Subcommands: init / resume / save / check / lesson / branch / archive / rollup / migrate
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys

BD_DIRNAME = "bd"
CORE = ("COMPASS.md", "JOURNAL.md", "LESSONS.md")
ENTRY_RE = re.compile(r"^### \[(\d{4}-\d{2}-\d{2})-(\d{3})\]")
RESUME_TAIL_N = 3

# --- embedded templates (canonical copies live in templates/bd/*.md) -------

COMPASS_TEMPLATE = """\
<!-- bd 脊柱模板。`bd save` 每次重写 "Current Frontier" 及其以下；North Star / Constraints /
     Milestones 很少动。每个 session 起手必读（或跑 `bd resume`）。小节顺序稳定，不要重排。 -->
# Compass — {project}

## North Star   (目标 · 少动)

{north_star}

## Constraints   (硬约束 · 少动 · 可空)

{constraints}

## Milestones   (路径 · 目标的有序分解 · 强制非空)

{milestones}

## Current Frontier   (前沿 · 每次 save 重写)

- 在 ▶{first_milestone}；距达成还差：<待填>

## Next Action   (下一步 · 每次 save 重写 · 只列最高杠杆 1-3 个)

1. {next_action} — verify: <判据>

## Alignment   (对齐自检 · save / check 时盖章)

- Next Action[1] 是否服务于当前 Milestone？ <yes / 已修正：…> — checked {today}

## Open / Blocked   (可空)

## Last updated

{stamp} by /bd init
"""

JOURNAL_HEADER = (
    "<!-- JOURNAL.md — newest entry on top. Append-only / immutable: never edit "
    "existing entries; corrections append a new entry referencing the old id. -->\n"
    "# Journal\n"
)

LESSONS_HEADER = (
    "<!-- LESSONS.md — append-only / immutable. 门槛 = failed path 或 non-obvious "
    "gotcha；关心 WHY，不写 HOW。 -->\n# Lessons\n"
)

# --- helpers ---------------------------------------------------------------

def _now():
    return _dt.datetime.now()

def _today():
    return _now().strftime("%Y-%m-%d")

def _stamp():
    return _now().strftime("%Y-%m-%d %H:%M")

def _die(msg, code=2):
    print(f"bd: {msg}", file=sys.stderr)
    sys.exit(code)

def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()

def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

def _bd_dir(project_dir):
    return os.path.join(project_dir, BD_DIRNAME)

def _require_bd(project_dir):
    bd = _bd_dir(project_dir)
    if not os.path.isdir(bd):
        _die(f"No bd/ at {bd}. Run `bd init` or `bd migrate` first.")
    return bd

def _parse_entries(path):
    if not os.path.isfile(path):
        return []
    return [(m.group(1), int(m.group(2)))
            for line in _read(path).splitlines()
            for m in [ENTRY_RE.match(line)] if m]

def _next_id(path):
    today = _today()
    todays = [n for (d, n) in _parse_entries(path) if d == today]
    nnn = (max(todays) + 1) if todays else 1
    return f"{today}-{nnn:03d}"

# --- COMPASS section parsing (shared by resume / check) --------------------

def _split_sections(text):
    """Return (preamble_lines, [(header_line, body_lines)]). Headers start '## '."""
    preamble, sections, cur_h, cur_b = [], [], None, []
    for ln in text.splitlines():
        if ln.startswith("## "):
            if cur_h is not None:
                sections.append((cur_h, cur_b))
            cur_h, cur_b = ln, []
        else:
            (cur_b if cur_h is not None else preamble).append(ln)
    if cur_h is not None:
        sections.append((cur_h, cur_b))
    return preamble, sections

def _section_body(sections, title_prefix):
    for h, body in sections:
        if h[3:].strip().lower().startswith(title_prefix):
            return body
    return []

def _first_content_line(body):
    for ln in body:
        s = ln.strip()
        if s and not s.startswith("<!--") and not s.startswith("- <") and "<待填>" not in s:
            return s
    return ""

def _current_milestone(sections):
    for ln in _section_body(sections, "milestones"):
        if "▶" in ln:
            return ln.strip()
    return ""

def _next_actions(sections):
    out = []
    for ln in _section_body(sections, "next action"):
        s = ln.strip()
        if re.match(r"^\d+\.", s):
            out.append(s)
    return out

def _milestone_items(sections):
    return [l.strip() for l in _section_body(sections, "milestones")
            if re.match(r"^\d+\.", l.strip())]

def _entry_advanced(block):
    """Extract the `advanced:` value from a JOURNAL entry block, or None."""
    for ln in block:
        m = re.search(r"advanced[^:：]*[:：]\s*(.+)", ln, re.I)
        if m:
            return m.group(1).strip()
    return None

def _lint(bd):
    """Validate bd's own invariants. Return list of (severity, ok, label, detail)."""
    _, sections = _split_sections(_read(os.path.join(bd, "COMPASS.md")))
    checks = []

    items = _milestone_items(sections)
    arrows = [l for l in items if "▶" in l]
    checks.append(("FAIL", len(items) > 0, "milestones-nonempty",
                   f"{len(items)} milestone item(s)"))
    checks.append(("FAIL", len(arrows) == 1, "one-current-milestone",
                   f"{len(arrows)} marked ▶ (need exactly 1)"))

    north = _first_content_line(_section_body(sections, "north star"))
    checks.append(("FAIL", bool(north) and "TODO" not in north,
                   "north-star-set", north or "<empty>"))

    actions = _next_actions(sections)
    checks.append(("FAIL", bool(actions), "next-action-set",
                   actions[0] if actions else "<none>"))
    has_verify = bool(actions) and all("verify" in a.lower() for a in actions)
    checks.append(("FAIL", has_verify, "next-action-verify",
                   "every Next Action needs a 'verify:' criterion"))

    align = _section_body(sections, "alignment")
    stamped = any("checked" in l for l in align)
    checks.append(("WARN", stamped, "alignment-stamped",
                   "Alignment has no 'checked <date>' stamp"))

    tail = _journal_tail(os.path.join(bd, "JOURNAL.md"), 3)
    advs = [a for a in (_entry_advanced(b) for b in tail) if a]
    drifting = len(advs) >= 2 and all(a.lower().startswith("none") for a in advs)
    checks.append(("WARN", not drifting, "no-drift",
                   f"latest {len(advs)} entries all 'advanced: none' — off target?"))
    return checks

# --- init ------------------------------------------------------------------

def cmd_init(args):
    bd = _bd_dir(args.project_dir)
    if os.path.isdir(bd):
        _die(f"bd/ already exists at {bd}")
    os.makedirs(bd)
    project = os.path.basename(os.path.abspath(args.project_dir))

    if args.quick:
        north = "<TODO: 一句话目标>"
        milestones = "1. ⬜ <定义里程碑 M1> — <可验证产出>"
        first_ms = "<M1>"
        next_action = "<TODO: 起手就能动的下一步>"
    else:
        north = args.north_star or "<TODO: 一句话目标>"
        ms = args.milestone or ["<定义里程碑 M1> — <可验证产出>"]
        lines = []
        for i, m in enumerate(ms, 1):
            mark = "▶" if i == 1 else "⬜"
            lines.append(f"{i}. {mark} {m}")
        milestones = "\n".join(lines)
        first_ms = ms[0].split("—")[0].strip()
        next_action = "<TODO: 起手就能动的下一步>"

    compass = COMPASS_TEMPLATE.format(
        project=project, north_star=north,
        constraints="<约束，可空>", milestones=milestones,
        first_milestone=first_ms, next_action=next_action,
        today=_today(), stamp=_stamp(),
    )
    _write(os.path.join(bd, "COMPASS.md"), compass)
    _write(os.path.join(bd, "JOURNAL.md"), JOURNAL_HEADER)
    _write(os.path.join(bd, "LESSONS.md"), LESSONS_HEADER)
    print(f"bd: initialized {bd}")


# --- resume ----------------------------------------------------------------

def _journal_tail(path, n):
    """Return the newest n entries (each a list of lines) from JOURNAL.md."""
    if not os.path.isfile(path):
        return []
    lines = _read(path).splitlines()
    starts = [i for i, ln in enumerate(lines) if ENTRY_RE.match(ln)]
    blocks = []
    for k, s in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(lines)
        blocks.append(lines[s:end])
    return blocks[:n]  # newest-first file, so first n are newest


def cmd_resume(args):
    bd = _require_bd(args.project_dir)
    compass_text = _read(os.path.join(bd, "COMPASS.md"))
    _, sections = _split_sections(compass_text)

    print("=" * 60)
    print(compass_text.rstrip())
    print("=" * 60)

    tail = _journal_tail(os.path.join(bd, "JOURNAL.md"), RESUME_TAIL_N)
    if tail:
        print(f"\n--- Recent journal (latest {len(tail)}) ---")
        for block in tail:
            print("\n".join(block).rstrip())
            print()

    milestone = _current_milestone(sections)
    actions = _next_actions(sections)
    na = actions[0] if actions else "<no Next Action set>"
    print("\n--- Alignment check ---")
    print(f"Current milestone: {milestone or '<none marked ▶>'}")
    print(f"Next Action[1]: {na}")
    print("Confirm Next Action[1] advances the current milestone, "
          "or correct it, before starting.")


# --- save ------------------------------------------------------------------

def _restamp_compass(bd, by):
    path = os.path.join(bd, "COMPASS.md")
    if not os.path.isfile(path):
        return
    preamble, sections = _split_sections(_read(path))
    stamp_line = f"{_stamp()} by {by}"
    found = False
    for idx, (h, body) in enumerate(sections):
        if h[3:].strip().lower().startswith("last updated"):
            sections[idx] = (h, ["", stamp_line, ""])
            found = True
    if not found:
        sections.append(("## Last updated", ["", stamp_line, ""]))
    out = "\n".join(preamble + [ln for h, b in sections for ln in [h, *b]])
    _write(path, out.rstrip("\n") + "\n")


def cmd_save(args):
    bd = _require_bd(args.project_dir)
    path = os.path.join(bd, "JOURNAL.md")
    body = sys.stdin.read().strip("\n")
    if not body:
        _die("empty journal body on stdin")
    if not os.path.isfile(path):
        _write(path, JOURNAL_HEADER)

    new_id = _next_id(path)
    entry = f"### [{new_id}] — {args.title}\n\n{body}\n"

    lines = _read(path).splitlines(keepends=True)
    insert_at = next((i for i, ln in enumerate(lines) if ENTRY_RE.match(ln)),
                     len(lines))
    head = "".join(lines[:insert_at]).rstrip("\n")
    tail = "".join(lines[insert_at:])
    _write(path, head + "\n\n" + entry + ("\n" + tail if tail else "\n"))

    _restamp_compass(bd, f"/bd save (entry {new_id})")

    _, sections = _split_sections(_read(os.path.join(bd, "COMPASS.md")))
    actions = _next_actions(sections)
    print(json.dumps({
        "id": new_id,
        "doc": "JOURNAL.md",
        "advanced": args.advanced,
        "alignment_reminder": {
            "current_milestone": _current_milestone(sections),
            "next_action_1": actions[0] if actions else None,
            "ask": "Did this advance the milestone? Is Next Action[1] still "
                   "the highest-leverage step? Rewrite COMPASS Frontier/Next/"
                   "Alignment accordingly.",
        },
    }, ensure_ascii=False))


# --- check -----------------------------------------------------------------

def cmd_check(args):
    bd = _require_bd(args.project_dir)
    if getattr(args, "lint", False):
        failed = 0
        print("bd lint — COMPASS / JOURNAL invariants")
        for sev, ok, label, detail in _lint(bd):
            if ok:
                print(f"  [ok]   {label}")
            else:
                print(f"  [{'FAIL' if sev == 'FAIL' else 'warn'}] {label}: {detail}")
                failed += sev == "FAIL"
        if failed:
            _die(f"{failed} invariant(s) failed", code=1)
        return
    _, sections = _split_sections(_read(os.path.join(bd, "COMPASS.md")))
    north = _first_content_line(_section_body(sections, "north star"))
    milestone = _current_milestone(sections)
    actions = _next_actions(sections)
    print(f"North Star: {north or '<unset>'}")
    print(f"Current milestone: {milestone or '<none marked ▶>'}")
    print(f"Next Action[1]: {actions[0] if actions else '<unset>'}")
    print("Is Next Action[1] the highest-leverage step that keeps you "
          "aligned to the milestone? If not, correct course now.")


# --- lesson ----------------------------------------------------------------

def cmd_lesson(args):
    bd = _require_bd(args.project_dir)
    path = os.path.join(bd, "LESSONS.md")
    body = sys.stdin.read().strip("\n")
    if not body:
        _die("empty lesson body on stdin")
    if not os.path.isfile(path):
        _write(path, LESSONS_HEADER)
    new_id = _next_id(path)
    block = f"\n### [{new_id}] — {args.title}\n\n{body}\n\n---\n"
    with open(path, "a", encoding="utf-8") as fh:  # append-only
        fh.write(block)
    print(json.dumps({"id": new_id, "doc": "LESSONS.md"}, ensure_ascii=False))


# --- branch ----------------------------------------------------------------

def cmd_branch(args):
    bd = _require_bd(args.project_dir)
    thread = os.path.join(bd, "threads", args.name)
    if os.path.isdir(thread):
        _die(f"thread already exists at {thread}")
    os.makedirs(thread)
    goal = args.goal or f"<TODO: 子线程 {args.name} 的目标>"
    compass = COMPASS_TEMPLATE.format(
        project=f"{os.path.basename(os.path.abspath(args.project_dir))}/{args.name}",
        north_star=goal, constraints="<约束，可空>",
        milestones="1. ▶ <子里程碑 1> — <可验证产出>",
        first_milestone="<子里程碑 1>", next_action="<TODO: 下一步>",
        today=_today(), stamp=_stamp(),
    )
    _write(os.path.join(thread, "COMPASS.md"), compass)
    _write(os.path.join(thread, "JOURNAL.md"), JOURNAL_HEADER)
    _write(os.path.join(thread, "LESSONS.md"), LESSONS_HEADER)
    print(f"bd: branched thread at {thread}")
    print("Paste this under the relevant parent COMPASS milestone:")
    print(f"   ▶ <M?> <name> — 展开为子线程 → threads/{args.name}/")


# --- archive ---------------------------------------------------------------

def cmd_archive(args):
    bd = _require_bd(args.project_dir)
    path = os.path.join(bd, "JOURNAL.md")
    if not os.path.isfile(path):
        _die("no JOURNAL.md to archive")
    lines = _read(path).splitlines(keepends=True)
    starts = [i for i, ln in enumerate(lines) if ENTRY_RE.match(ln)]
    if len(starts) <= args.keep:
        print(f"bd: {len(starts)} entries <= keep={args.keep}; nothing to archive")
        return
    cut = starts[args.keep]  # first index of the (keep+1)th entry
    head = "".join(lines[:cut])
    moved = "".join(lines[cut:])

    apath = os.path.join(bd, "JOURNAL.archive.md")
    if not os.path.isfile(apath):
        _write(apath, "<!-- JOURNAL.archive.md — paged-out entries, newest first. "
                      "Immutable. grep across this + JOURNAL.md. -->\n# Journal (archived)\n")
    # prepend moved block after the archive header's first blank line region
    a_lines = _read(apath).splitlines(keepends=True)
    a_insert = next((i for i, ln in enumerate(a_lines) if ENTRY_RE.match(ln)),
                    len(a_lines))
    a_head = "".join(a_lines[:a_insert]).rstrip("\n")
    a_tail = "".join(a_lines[a_insert:])
    _write(apath, a_head + "\n\n" + moved.rstrip("\n") + "\n" +
           ("\n" + a_tail if a_tail else "\n"))
    _write(path, head.rstrip("\n") + "\n")
    print(json.dumps({"kept": args.keep, "archived": len(starts) - args.keep,
                      "archive": apath}, ensure_ascii=False))


# --- rollup (milestone lifecycle) ------------------------------------------

def cmd_rollup(args):
    """Fold the oldest ✅ milestones into a '## Milestones (archived)' section,
    keeping the spine short. Deterministic text move; numbering left as-is for
    the agent to tidy on the next COMPASS rewrite."""
    bd = _require_bd(args.project_dir)
    path = os.path.join(bd, "COMPASS.md")
    preamble, sections = _split_sections(_read(path))

    mi = next((i for i, (h, _) in enumerate(sections)
               if h[3:].strip().lower().startswith("milestones")
               and "archived" not in h.lower()), None)
    if mi is None:
        _die("no '## Milestones' section in COMPASS.md")
    h, body = sections[mi]
    done = [i for i, l in enumerate(body)
            if re.match(r"^\d+\.", l.strip()) and "✅" in l]
    if len(done) <= args.keep_done:
        print(f"bd: {len(done)} done milestone(s) <= keep-done={args.keep_done}; "
              "nothing to roll up")
        return
    move = set(done[:len(done) - args.keep_done])  # oldest done, by list order
    moved = [body[i] for i in sorted(move)]
    sections[mi] = (h, [l for i, l in enumerate(body) if i not in move])

    ai = next((i for i, (hh, _) in enumerate(sections)
               if hh[3:].strip().lower().startswith("milestones (archived")), None)
    if ai is None:
        sections.insert(mi + 1, ("## Milestones (archived)", ["", *moved, ""]))
    else:
        hh, bb = sections[ai]
        sections[ai] = (hh, ["", *[l for l in bb if l.strip()], *moved, ""])

    out = "\n".join(preamble + [ln for hx, bx in sections for ln in [hx, *bx]])
    _write(path, out.rstrip("\n") + "\n")
    print(json.dumps({"rolled_up": len(moved), "kept_done": args.keep_done},
                     ensure_ascii=False))


# --- migrate ---------------------------------------------------------------

def _grab_section(text, title_prefix):
    """Return the body text under a '## <title>' heading (until next '## ')."""
    _, sections = _split_sections(text)
    for h, body in sections:
        if h[3:].strip().lower().startswith(title_prefix):
            return "\n".join(body).strip()
    return ""


def cmd_migrate(args):
    src = os.path.join(args.project_dir, args.src)
    bd = _bd_dir(args.project_dir)
    if os.path.isdir(bd):
        _die(f"bd/ already exists at {bd}; refuse to overwrite")
    if not os.path.isdir(src):
        _die(f"no v1 memory dir at {src}")
    os.makedirs(bd)

    def _read_if(name):
        p = os.path.join(src, name)
        return _read(p) if os.path.isfile(p) else ""

    goal = _first_content_line(_grab_section(_read_if("OVERVIEW.md"), "goal").splitlines()) \
        or "<TODO: 一句话目标>"
    next_steps = _grab_section(_read_if("STATE.md"), "next steps")
    first_next = ""
    for ln in next_steps.splitlines():
        if re.match(r"^\d+\.", ln.strip()):
            first_next = re.sub(r"^\d+\.\s*", "", ln.strip())
            break
    project = os.path.basename(os.path.abspath(args.project_dir))
    compass = COMPASS_TEMPLATE.format(
        project=project, north_star=goal, constraints="<从 v1 OVERVIEW.Constraints 迁入>",
        milestones="1. ⬜ <TODO: 由 agent 从 v1 STATE/ROADMAP 推导里程碑> — <可验证产出>",
        first_milestone="<M1>", next_action=first_next or "<TODO: 下一步>",
        today=_today(), stamp=_stamp(),
    )
    _write(os.path.join(bd, "COMPASS.md"), compass)

    # JOURNAL = SESSIONS entries, with DECISIONS folded in as tagged entries.
    sessions = _read_if("SESSIONS.md")
    decisions = _read_if("DECISIONS.md")
    journal = JOURNAL_HEADER
    s_body = "\n".join(l for l in sessions.splitlines() if not l.startswith("# "))
    journal += s_body.strip() + "\n"
    if decisions.strip():
        journal += "\n<!-- migrated from v1 DECISIONS.md -->\n"
        d_body = "\n".join(l for l in decisions.splitlines() if not l.startswith("# "))
        journal += d_body.strip() + "\n"
    _write(os.path.join(bd, "JOURNAL.md"), journal)

    lessons = _read_if("LESSONS.md") or LESSONS_HEADER
    _write(os.path.join(bd, "LESSONS.md"), lessons)

    print(json.dumps({"migrated_to": bd, "carried": [
        f for f in ("OVERVIEW.md", "STATE.md", "SESSIONS.md", "DECISIONS.md", "LESSONS.md")
        if os.path.isfile(os.path.join(src, f))]}, ensure_ascii=False))
    print("AGENT TODO after migrate:")
    print("  - Fill COMPASS Milestones (derive from v1 ROADMAP/STATE/SESSIONS).")
    print("  - Verify North Star + Next Action; add verify: criteria.")
    print("  - Mark the current milestone with ▶ and stamp Alignment.")


# --- CLI -------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(prog="bd", description=__doc__)
    p.add_argument("--project-dir", default=os.getcwd(),
                   help="Project directory containing bd/ (default: cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="scaffold bd/ (COMPASS/JOURNAL/LESSONS)")
    i.add_argument("--quick", action="store_true", help="placeholder seed, 5-sec start")
    i.add_argument("--north-star", default=None)
    i.add_argument("--milestone", action="append", default=None,
                   help="repeatable; '<name> — <verifiable output>'")
    i.set_defaults(func=cmd_init)

    r = sub.add_parser("resume", help="print spine + journal tail + alignment")
    r.set_defaults(func=cmd_resume)

    s = sub.add_parser("save", help="prepend a JOURNAL entry (stdin=body) + stamp")
    s.add_argument("--title", required=True)
    s.add_argument("--advanced", default=None, help="milestone advanced this session")
    s.set_defaults(func=cmd_save)

    c = sub.add_parser("check", help="print goal/milestone/next-action drift check")
    c.add_argument("--lint", action="store_true",
                   help="validate COMPASS invariants (exit 1 on FAIL)")
    c.set_defaults(func=cmd_check)

    l = sub.add_parser("lesson", help="append a LESSONS entry (stdin=body)")
    l.add_argument("--title", required=True)
    l.set_defaults(func=cmd_lesson)

    b = sub.add_parser("branch", help="promote a milestone to a recursive sub-thread")
    b.add_argument("name")
    b.add_argument("--goal", default=None)
    b.set_defaults(func=cmd_branch)

    ar = sub.add_parser("archive", help="page old JOURNAL entries to JOURNAL.archive.md")
    ar.add_argument("--keep", type=int, default=10, help="newest N entries kept inline")
    ar.set_defaults(func=cmd_archive)

    ru = sub.add_parser("rollup",
                        help="fold old ✅ milestones into '## Milestones (archived)'")
    ru.add_argument("--keep-done", type=int, default=2,
                    help="newest N done milestones kept inline (default 2)")
    ru.set_defaults(func=cmd_rollup)

    m = sub.add_parser("migrate", help="mechanical v1 MEMORY/ -> bd/ scaffold")
    m.add_argument("--src", default="MEMORY", help="v1 memory dir name (default MEMORY)")
    m.set_defaults(func=cmd_migrate)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
