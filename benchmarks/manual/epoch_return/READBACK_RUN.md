# 运行步骤：原始材料 vs 机械展开读值

这是一次诊断定位实验，不是新旧 skill 对比，也不运行新的 JasperGold 证明。

- 两臂相同 skill：@SKILL_COMMIT@，GPT-5.5 / medium。
- A：原始 RTL、未收敛候选与诊断文件。
- B：同一批文件，额外附上机械展开的 VCD 读值表。
- 固定一组，顺序 A → B；每臂一个全新会话，不并发、不追加解题提示。
- 原始现场和历史实验不改；本目录保持 Git 忽略。

## 准备者检查（不启动模型）

```bash
@EXPERIMENT@/launch.sh seal
@EXPERIMENT@/launch.sh check
@EXPERIMENT@/launch.sh preflight all
```

交付时已完成上述步骤。你只需 check，然后启动两臂；不要重新 seal。
依赖变化导致检查拒绝时，保留目录并反馈，不能改 pins 强行继续。

## 你需要执行的命令

先在真实 terminal 执行：

```bash
@EXPERIMENT@/launch.sh check
@EXPERIMENT@/launch.sh a
```

启动器自动提供统一任务。不要把本说明、评测规则、历史结果或我们的解题讨论
粘贴进去。等模型写完 FINAL_REPORT.md 和候选文件，再正常退出客户端。
启动器写完退出回执后，再执行：

```bash
@EXPERIMENT@/launch.sh b
```

同样等任务完成并退出。把两个会话 UUID 发回评测窗口即可。

本阶段不要求 P0 proven；新证明执行被禁用。禁止工具调用时的拒绝应如实保留，
不绕过，不因此追加其它阶段。候选是否成立留到后续独立验证。
若中途退出，保留现场并说明，不删除回执重跑该臂。

## 结果与隔离

- A 输出：@EXPERIMENT@/blind/arm_a
- B 输出：@EXPERIMENT@/blind/arm_b
- 统一内部工作目录：/work
- 两个 skill 入口均指向 /opt/formal-snapshot/adapters/claude-code；
  分别映射到 control/frozen/snapshot_a、snapshot_b，内容完全相同。
- 只有本臂的 MATERIALS.md 挂载到 /opt/experiment/input；B 的读值表
  不会出现在 A 的文件系统或 TraceWeave 中。
- 评估材料、原会话和另一臂不挂载。全局 skill 链接不改变。

评分看真实读值、解释与候选依据，不要求指定答案或格式。机械表只提供原值，
不代表模型已理解；查看 transcript 确认其完整进入上下文。此次结果不能作为
新旧 skill 的胜负，也不能与之前的完全证明成功率混算。
