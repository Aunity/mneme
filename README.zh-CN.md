# bd (北斗) — 目标牵引的项目记忆

[English](README.md) | **中文**

> 一套**目标牵引**的 AI 协作记忆工作流：把项目记忆从"为归档而记录"翻转为"为推进目标而记录"。
> 每个项目一根脊柱（COMPASS）+ 两个 append-only 日志（JOURNAL / LESSONS），一条常驻 rule，一个纯标准库 CLI。

## 解决的 4 个痛点

1. **跨 session 失忆** —— `bd resume` 把脊柱 + 最近日志 + 对齐提示一次打印。
2. **deep-dive 污染主 session** —— `bd branch` 把子任务分到 `bd/threads/<name>/` 的递归脊柱。
3. **context 满前的 session 焦虑** —— 记忆住在磁盘、不占 context；逼近极限可做 `[emergency-save]`。
4. **记录两难** —— 3 个核心文档；决策以 inline `[decision]` 标签内联，不再分拣归档。

## 核心模型：1 根脊柱 + 2 个日志

| 文档 | 性质 | 生命周期 |
|---|---|---|
| `bd/COMPASS.md` | 脊柱：North Star / Constraints / **Milestones** / Frontier / **Next Action（带 verify）** / **Alignment** | "Frontier 以下"每次 save 重写；目标少动 |
| `bd/JOURNAL.md` | append-only，newest-first，一次 save 一条 | 不可变；决策内联 `[decision]` |
| `bd/LESSONS.md` | append-only，永不丢的坑 | 不可变 |

强制项：Milestones 非空；每条 Next Action 带 `verify:`；每次 save 盖一次 Alignment（含 `advanced:` 字段，连续 `none` = 漂移告警）。

## CLI（`tools/bd.py`，纯 Python 3 标准库，零依赖）

| 命令 | 作用 |
|---|---|
| `bd init [--quick]` | 起一个项目（问 3 个问题 / 或 5 秒占位） |
| `bd resume` | 打印脊柱 + 最近 N 条 journal + 对齐提示 |
| `bd save --title … --advanced …` | 从 stdin 收 JOURNAL 正文 → 盖 id、prepend、刷新 stamp + 对齐提示 |
| `bd check [--lint]` | 漂移自检；`--lint` 校验 COMPASS 不变量（FAIL 退出非零） |
| `bd lesson --title …` | append 一条 LESSONS |
| `bd branch <name>` | 把一个 Milestone 升级为 `bd/threads/<name>/` 递归子线程 |
| `bd rollup [--keep-done N]` | 把旧 ✅ 里程碑折进 `## Milestones (archived)`，保持脊柱短 |
| `bd archive [--keep N]` | 把老 JOURNAL 条目翻入 `JOURNAL.archive.md` |

机械 / 语义分工：CLI 只做 id / 落位 / 重写脚手架 / 打印对齐；语义（条目正文、里程碑该不该关、对齐结论）由 agent 提供。

## 安装

没有安装脚本，把三样东西复制进你的 agent 配置目录即可（Cursor 是 `.cursor/`；其他框架见 [在 Cursor 之外使用 bd](#在-cursor-之外使用-bd)）：

| 源 | 目标 |
|---|---|
| `rules/bd.mdc` | `<config>/rules/bd.mdc` —— 唯一一条常驻 rule（~1 页） |
| `skills/bd-{init,resume,save,log,branch}/` | `<config>/skills/` |
| `tools/bd.py` | `<config>/tools/bd.py`（或直接 in-place 运行） |

然后起一个项目：

```bash
python tools/bd.py --project-dir /path/to/project init
```

## 触发词速查

| 触发词 | 行为 |
|---|---|
| `/bd init` | 3 问起手，创建 `bd/` 骨架 |
| `/bd resume` | 读脊柱 + 最近日志 + 对齐提示（只读，不自动开工） |
| `/bd save` | prepend 一条 JOURNAL + 重写 COMPASS Frontier/Next/Alignment |
| `/bd lesson` | append 一条 LESSONS |
| `/bd branch` | 升级一个 Milestone 为递归子线程 |

## 在 Cursor 之外使用 bd

bd 由可移植的**引擎**与一层薄薄的**集成层**组成：

- **引擎** —— `tools/bd.py`（纯标准库）+ 纯 markdown 的 `bd/` 文件。零 Cursor 依赖，在任何 agent、甚至裸终端里都一样跑。
- **集成层** —— 只是"agent 如何自动加载常驻 rule、如何发现 skills"。只有这一层会随框架变。

移植时，把 `rules/bd.mdc` 的正文塞进宿主框架的常驻指令文件，再把 skills 放到该框架查找的位置：

| 框架 | 常驻 rule → | Skills / commands |
|---|---|---|
| Cursor | `.cursor/rules/bd.mdc` | `.cursor/skills/` |
| Claude Code | `CLAUDE.md` | `.claude/skills/` + `.claude/commands/` |
| Codex | `AGENTS.md` | 无 skill 机制 —— 把流程内联进去，或靠 CLI 自述 |
| Gemini CLI | `GEMINI.md` | `activate_skill` |

CLI 本身到哪都不变（`python tools/bd.py …`）；`/bd …` 这类斜杠触发词退化成普通 prompt 即可。

**一点注意**：没有 skill 机制的框架（如 Codex / `AGENTS.md`）无法按需懒加载 `bd-*` 流程 —— 要么把简短流程内联进常驻文件，要么靠 CLI 自述（`bd resume` 会打印脊柱 + 日志 + 对齐；`bd save` 会打印对齐提示）。

## 许可证

[MIT](LICENSE)
