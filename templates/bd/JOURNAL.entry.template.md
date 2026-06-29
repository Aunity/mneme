<!-- 单条 JOURNAL 模板。`bd save` 把新条目 **prepend** 到 JOURNAL.md（newest first）。
     条目 append-only / 不可变——绝不改旧条目；要更正就新追加一条引用旧 id。 -->

### [YYYY-MM-DD-NNN] — <session 标题，一行>

- **advanced**: ▶<Milestone>   <!-- 本次推进了哪个里程碑；若没有，写 "none — <为什么>"，这是漂移信号 -->
- **did**:
  - <2-5 条本次实质性工作>
- **[decision]**: <如有：选了什么 / 为什么 / 放弃了谁。inline 标签，不另开 DECISIONS 文件> <!-- 可省略 -->
- **[gotcha]**: <如有：顺手记的小坑；重坑请走 `bd lesson` 进 LESSONS> <!-- 可省略 -->
- **produced**:
  - `<文件路径>` — <作用>
- **next**: <本次把 COMPASS.Next Action 同步成了什么>
