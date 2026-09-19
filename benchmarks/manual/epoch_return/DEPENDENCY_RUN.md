# 运行步骤：相同未完成证明现场，旧 skill / 新 skill

这是一组条件恢复测试，不是从零发现不变式。两臂都得到同一份未经修复的
原 A 候选脚本及对应原始 Jasper 日志，不提供修复脚本或成功结果。
不要把本说明、SCORING 或当前评测对话复制给模型；统一中立任务已由启动器注入。

- A：旧 skill `@OLD_COMMIT@`。
- B：新 skill `@NEW_COMMIT@`。
- 模型/努力：GPT-5.5 / medium；固定顺序 A → B，逐臂运行。
- 实验根：`@EXPERIMENT@`。
- 输出：`blind/arm_a`、`blind/arm_b`；会话数据由启动器保存在各自的隔离目录。
- 各臂先跑同一原始 baseline，再各有 180 秒新增 JG 整进程预算。

两臂的 `.codex/skills/formal-verification` 和 `.agents/skills/formal-verification`
都指向 `/opt/formal-snapshot/adapters/claude-code`。A 实际挂载本目录下的
`control/frozen/snapshot_a`，B 挂载 `snapshot_b`。宿主全局链接不会改变；
TraceWeave 同样处于隔离环境，无法读取另一个快照、另一臂或成功修复结果。

## 准备者封存及预检（无模型调用）

```bash
@EXPERIMENT@/launch.sh seal
@EXPERIMENT@/launch.sh check
@EXPERIMENT@/launch.sh preflight all
```

已经封存并预检通过时，不要再次 seal。启动前只需 check；如果内容漂移导致拒绝，
保留现场并报告，不修改 pins 绕过检查。预检只验证环境、toy proof/cover 和 MCP。

## 用户手动启动

先在真实 terminal 执行检查并启动 A：

```bash
@EXPERIMENT@/launch.sh check
@EXPERIMENT@/launch.sh a
```

任务会自动注入，不需要另贴提示词。等 A 完成报告与复现脚本后，用 `/exit`
正常退出客户端并等待 shell 返回，让启动器写完退出回执，再启动 B：

```bash
@EXPERIMENT@/launch.sh b
```

同样等 B 完成后正常退出。不要并发、不要 resume 旧会话、不要给解题提示，
不要把另一臂结果或本对话粘贴进去。中途退出也保留现场；不要清空目录、删除
launch 回执或重新使用同一臂。

两臂完成后，将两个 UUID 或本实验根目录发回评测窗口。若出现环境错误，提供
完整错误和路径；它单独记录为环境问题，不冒充证明失败或被悄悄替换掉。
