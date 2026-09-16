# 运行步骤：从零开始的新旧 skill A/B

这是固定系列中的第 **@PAIR_INDEX@ / @PAIR_COUNT@** 对。系列前缀：`@SERIES@`。
先完成并评审条件恢复测试，再启动本系列。不要给模型本说明、SCORING、此前
失败现场、答案、报告或对话中的解题信息。启动器已注入统一中立任务。

- A：旧 skill `@OLD_COMMIT@`；B：新 skill `@NEW_COMMIT@`。
- GPT-5.5 / medium；两臂任务、工具、预算相同。
- 两臂都只从固定 RTL 和 baseline 开始，**没有预置 helper 或 SST 波形**。
- 实验根：`@EXPERIMENT@`；输出：`blind/arm_a`、`blind/arm_b`。
- 本对的固定启动顺序：**@FIRST_ARM@ → @SECOND_ARM@**，启动器检查该顺序。

本轮比较新增的读值/修订指导，不是有 skill 对比无 skill，也不是有 SST 对比
无 SST。案例是开发案例，不将这次结果包装成独立的泛化验证。

## 准备者封存及预检（无模型调用）

```bash
@EXPERIMENT@/launch.sh seal
@EXPERIMENT@/launch.sh check
@EXPERIMENT@/launch.sh preflight all
```

已完成时不再 seal，启动前只执行 check。依赖变化应保留本目录并准备新系列，
不能修改 pins 绕过拒绝。若恢复试验后又修改了 skill，不要运行这个旧快照系列。

## 手动运行

在真实 terminal 先执行：

```bash
@EXPERIMENT@/launch.sh @FIRST_ARM@
```

等待模型写完 FINAL_REPORT.md 和复现脚本，正常退出客户端，让启动器写完退出
回执，再开全新会话：

```bash
@EXPERIMENT@/launch.sh @SECOND_ARM@
```

不要并发、不要粘贴另一臂结果、不要额外指定证明方法。完成后退出客户端。
每臂先跑原 baseline，之后所有 JG 调用合计预算 180 秒。初次 helper 直接证明
成功也正常记录，不要求为了测试而制造失败或调用 SST。

两臂的 `.codex` 与 `.agents` skill 入口都指向
`/opt/formal-snapshot/adapters/claude-code`，分别映射本目录的
`control/frozen/snapshot_a` / `snapshot_b`。TraceWeave 同样在隔离环境内。
宿主全局 skill、其他实验、评测材料与另一臂均不挂载。

按预定顺序完成整个系列，把每对的 UUID 或根目录发回评测窗口。保留所有结果，
不只挑选成功样本。若一臂中途退出，保留现场并说明，不删除回执重新启动。

## 另建系列（仅在已说明原因时）

```bash
python3 benchmarks/manual/prepare_e2e.py \
  --dest-prefix test/epoch_return_e2e_ab_gpt55_repeat --pairs @PAIR_COUNT@ \
  --old-revision @OLD_COMMIT@ --new-revision @NEW_COMMIT@
```

该命令只生成新的固定批次，不会启动模型；每个新目录按其 README_RUN.md 操作。
