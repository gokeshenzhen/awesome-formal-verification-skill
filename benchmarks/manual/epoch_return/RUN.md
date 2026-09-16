# 本轮运行步骤：中立案例预试跑

这是两次独立的开发预试跑，不是新旧 skill 的效果 A/B。
两次均使用 **GPT-5.5 / medium、相同 skill `@SKILL_COMMIT@`**，
用于观察是否自然出现候选失败，以及诊断是否帮助后续收敛。
不得给模型本说明、SCORING、校准记录、上轮报告或本对话中的解题信息。

## 已准备的目录

- 实验根：`@EXPERIMENT@`
- 第一次输出：`@EXPERIMENT@/blind/arm_a`
- 第二次输出：`@EXPERIMENT@/blind/arm_b`
- 每次私有 transcript：`@EXPERIMENT@/control/private/arm_<a或b>/user/.codex/sessions`
- 共同任务：`@EXPERIMENT@/common/TASK.md`

运行环境只挂载本次公开案例、一个冻结 skill、自己的 `/work`、必要工具。
TraceWeave 与 AI 在同一隔离边界内。宿主项目、作者校准、另一臂和历史记录不可见。
`.codex/skills/formal-verification` 与 `.agents/skills/formal-verification`
均指向 `/opt/formal-snapshot/adapters/claude-code`；该路径只映射本次选定副本。

## 开始前

封存和环境预检不调用模型、不运行案例证明。准备者先执行一次：

```bash
@EXPERIMENT@/launch.sh seal
@EXPERIMENT@/launch.sh check
@EXPERIMENT@/launch.sh preflight all
```

若已经有通过的预检，只需先 `check`。禁止通过改 pins、删启动回执或清空输出
复用旧运行。依赖变化、预检失败或中途退出都保留现场，在新目录重新准备。

## 两次手动运行

在真实 terminal 中启动第一次：

```bash
@EXPERIMENT@/launch.sh a
```

启动器已注入统一提示词，不需要额外提示技术：

> 请完整读取 /opt/experiment/common/TASK.md，按其中要求完成 /work 中分配的任务。

等它完成、写出 `FINAL_REPORT.md` 和最终复现 Tcl 后，正常退出 Codex 客户端，
让启动器写完退出回执。然后再启动第二次；不要复用上下文或补充第一次的结果：

```bash
@EXPERIMENT@/launch.sh b
```

完成后同样退出客户端。两次不得并发，防止争用 EDA 资源影响耗时。
`jg-run` 先执行未改 baseline；之后全部 Jasper 进程共用 180 秒墙钟预算，
包括 help、失败尝试和最终重放。客户端思考时间不算 Jasper 时间。

将两次 UUID 或实验根目录发回评测窗口即可。不需要在运行窗口打开 SCORING。
若两次都首版成功，照实记为 refinement 未触发，不重跑直到出现预期结果。

## 以后创建全新重复批次

在项目根执行，换一个从未使用过的目录名：

```bash
python3 benchmarks/manual/prepare_pilot.py \
  --dest test/epoch_return_pilot_gpt55_02 \
  --skill-revision @SKILL_COMMIT@
```

然后按新目录的 `README_RUN.md` 封存、预检、手动运行。
新的重复仍然是开发样本，不可事后挑选某次当作独立效果 A/B。
