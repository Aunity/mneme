<!-- bd 脊柱模板。`bd save` 每次重写 "Current Frontier" 及其以下；North Star / Constraints /
     Milestones 很少动。每个 session 起手必读（或跑 `bd resume`）。小节顺序稳定，不要重排。 -->
# Compass — <project>

## North Star   (目标 · 少动)

<!-- 一两句：这个项目最终要达成什么；可验证的成功长什么样。整套 bd 的脊柱顶端。 -->
<目标一句话>

## Constraints   (硬约束 · 少动 · 可空)

<!-- 不可违反的边界（技术 / 资源 / 政策）。没有就留空。 -->
- <约束 1>

## Milestones   (路径 · 目标的有序分解 · 强制非空)

<!-- 每个里程碑是一个【可验证产出】，不是一个动作。状态：✅done / ▶now / ⬜next。
     done 行可附一句 rollup（这个里程碑是怎么达成的）。规模大时按 Phase 分组、老 done 滚入 archived。 -->
1. ✅ <M1 名称> — <可验证产出> — done <YYYY-MM-DD>：<一句 rollup>
2. ▶ <M2 名称> — <可验证产出>
3. ⬜ <M3 名称> — <可验证产出>

## Current Frontier   (前沿 · 每次 save 重写)

<!-- 在哪个里程碑；距达成还差什么。重档子任务在这里挂 thread 链接。 -->
- 在 ▶<M2>；距达成还差：<还剩什么>

## Next Action   (下一步 · 每次 save 重写 · 只列最高杠杆 1-3 个)

<!-- 第 1 条最具体（起手就能动）。每条必须带 verify：怎么算这步做完/做对。 -->
1. <最具体的下一步> — verify: <判据>
2. <次一步> — verify: <判据>

## Alignment   (对齐自检 · save / check 时盖章)

<!-- 校验 Next Action[1] 是否真的在推进当前 Milestone；偏了就写"已修正：…"。 -->
- Next Action[1] 是否服务于 ▶<M2>？ <yes / 已修正：…> — checked <YYYY-MM-DD>

## Open / Blocked   (可空)

<!-- 开放问题或卡点；每条带解封条件。 -->
- <问题 / blocker> — <解封条件>

## Last updated

<YYYY-MM-DD HH:MM> by /bd save (entry <id>) [emergency-save?]
