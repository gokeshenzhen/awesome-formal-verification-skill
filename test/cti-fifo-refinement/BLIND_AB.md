**手工 skill / no-skill 对照：待执行协议**

这里的复跑脚本验证“缺失不变量 → 诊断 → 补强 → 收敛”。它们已经包含答案，
不能拿脚本执行结果充当独立模型发现答案的证据。仓库约定 skill A/B 由用户开启
两个独立会话执行；本文提供材料和验收条件，不启动自动双盲 harness。

给参与者的材料只能是 `neutral/` 内的五个文件：`sfifo.v`、`tb.sv`、
`setup.tcl`、`baseline.tcl`、`TASK.md`。复制到仓库以外的两个新目录，例如：

```bash
mkdir -p /tmp/fifo-arm-a /tmp/fifo-arm-b
cp neutral/sfifo.v neutral/tb.sv neutral/setup.tcl neutral/baseline.tcl neutral/TASK.md /tmp/fifo-arm-a/
cp neutral/sfifo.v neutral/tb.sv neutral/setup.tcl neutral/baseline.tcl neutral/TASK.md /tmp/fifo-arm-b/
```

目录应是新建的；若已有上次运行，改用新路径。不要复制本目录的 README、
helpers、诊断/收敛脚本或历史报告。参与者工作区不要位于本仓库之内，以免继承
仓库路由与答案。只复制文件不等于操作系统隔离；需同时限制会话的可读范围，
并检查实际工具记录是否越界。

两边使用同一模型版本、reasoning 设置、会话预算、Jasper/许可证环境和 TraceWeave。
共同保留 EDA 环境配置说明；唯一知识差异是 B 可读 `formal-verification` skill
及其路由到的知识文件，A 不可读。必须检查工具实际读取记录，不能只靠提示
“不用 skill”，同时仍把 skill 自动注入 A 的上下文。建议先选较弱模型，
但必须在看到结果前固定模型和预算。

分别开启全新会话，给两边完全相同的提示：

> 请完成当前工作目录 TASK.md 中的验证任务，遵守其中的预算、文件范围和交付要求。

禁止在提示中添加“CTI”“SST”“helper”“容量上界”等解题提示。
两边不要看对方的过程或结果。完整保留事件记录，另外记录模型版本、设置、
skill 内容哈希、工具版本、工作区源码哈希、预算、所有 Jasper 调用及耗时。

**什么结果才支持用户希望的表述**

- A 在预先固定的预算内未关闭原目标；不得将它写成“无 skill 永远无法证明”。
- B 自主定位未闭合义务，生成或获取诊断轨迹，实际读取信号值，解释缺失的关系，
  据此修改 helper；全过程能在事件记录里找到先后顺序。
- B 先证明新增关系及后续依赖，再证明未改动的原目标；所有支持义务的状态和
  有效性均为 `proven`，证明无界，读 cover 可达。额外假设、黑盒、cutpoint、
  `marked_proven` 或更弱目标不能冒充原设计完整证明。
- 收到两份报告后，在互不共享缓存的新 Jasper 项目中独立复跑各自 `final.tcl`，
  核对源码、环境、依赖和结果。若两边都证明，或 B 没有使用轨迹反馈，照实报告，
  不能称为“CTI skill 导致胜出”。

两份报告尚未产生前，本目录的证据结论仅为 **refinement 收敛案例**。
