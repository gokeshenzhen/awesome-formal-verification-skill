# 运行步骤：相同失败现场的新旧 skill 恢复测试

本轮是条件恢复测试，不是从零开始的中立 A/B。两臂都得到同一份首版候选、
原始证明日志及 SST 波形；不提供成功脚本或波形解读。不要将本说明或 SCORING
复制给运行中的模型。统一任务已经由启动器注入。

- A：旧 skill `@OLD_COMMIT@`。
- B：新 skill `@NEW_COMMIT@`。
- 模型/努力：GPT-5.5 / medium；两臂工具及预算相同。
- 实验根：`@EXPERIMENT@`；输出：`blind/arm_a`、`blind/arm_b`。
- 冻结现场：`control/frozen/checkpoint`，在两臂内只读映射到 `/opt/experiment/checkpoint`。

两臂的 `.codex/skills/formal-verification` 和 `.agents/skills/formal-verification`
都指向 `/opt/formal-snapshot/adapters/claude-code`，分别映射自己的
`control/frozen/snapshot_a` 或 `snapshot_b`。宿主全局链接不会改变。
TraceWeave 和模型处于同一隔离环境，不能读取另一臂、作者校准或评测材料。

## 封存与预检（准备者执行，无模型调用）

```bash
@EXPERIMENT@/launch.sh seal
@EXPERIMENT@/launch.sh check
@EXPERIMENT@/launch.sh preflight all
```

如果已经完成封存并预检通过，不要重复 seal，启动前只需 check。
预检只运行 toy proof/cover 和 MCP 读值，不求解本案例。

## 在两个全新会话中顺序运行

先在真实 terminal 执行：

```bash
@EXPERIMENT@/launch.sh a
```

等 A 写完 FINAL_REPORT.md 和最终复现脚本，正常退出客户端，使启动器写完退出
回执，再执行：

```bash
@EXPERIMENT@/launch.sh b
```

不要补充解题提示、粘贴前一臂结果或复用上下文。运行后同样正常退出客户端。
两臂都先跑一次原 baseline，然后各有 180 秒新增 JG 整进程预算；历史现场不计入
新增预算。不要求重新跑历史失败候选。模型思考时间不算 Jasper 时间。

最终把两个 UUID 或本实验根目录发回评测窗口。先评审这一对，再决定是否进入
已经另行准备的中立端到端比较。中途退出保留现场，不删回执、不清空、不续用该臂。

## 有明确需要时创建新批次

在仓库根运行，使用从未存在过的新目录名，并显式指定历史现场来源：

```bash
python3 benchmarks/manual/prepare_recovery.py \
  --dest test/epoch_return_recovery_ab_gpt55_02 \
  --old-revision @OLD_COMMIT@ --new-revision @NEW_COMMIT@ \
  --checkpoint-arm /absolute/path/to/original/blind/arm_b
```

任何新批次都单独记录动机与结果；不能重跑后只报告成功的一次。
