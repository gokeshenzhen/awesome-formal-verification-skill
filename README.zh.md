# Awesome Formal Verification Skill

<p align="right">
  <a href="README.md">English</a> · <strong>简体中文</strong>
</p>

**让 AI 编程助手真正会用 JasperGold 做形式验证。**

一个装进 Claude Code / Codex 等 AI Agent 的形式验证 Skill：当证明卡住时，它告诉 AI *该用哪种技术*、*什么时候用*、*用哪条确切的 JasperGold 命令*，并按可审计的标准判断证明是否真的完成。

> 🎯 **当前支持**：JasperGold 形式属性验证（FPV）
> 🗺️ **规划中**：VC Formal、CDC/RDC、Superlint、Coverage

## 这解决什么问题？

**如果你不熟悉形式验证**：芯片设计（RTL）通常靠仿真验证——跑大量测试用例，看有没有出错。形式验证换了一种思路：用数学方法证明某条性质（断言）在*所有可能的输入和状态*下都成立。它能找到仿真很难碰到的深层 bug，但代价是计算量可能爆炸，证明经常“跑不完”。让证明收敛，靠的是大量工具经验。

**如果你是验证工程师**，痛点应该很熟悉：属性卡在 `undetermined`，状态空间爆炸，引擎选择全凭经验。通用 AI 助手懂方法论，会说“可以试试抽象或 helper lemma”，但它往往：

- 不知道确切的工具命令和参数，比如 `abstract -counter`、`assert -helper`、`prove -with_helpers`、`proof_structure -init`；
- 不知道*什么症状*该触发*哪种技术*，于是在原始证明上反复加时间、换引擎；
- 分不清“证明通过”和“在额外假设下通过”，容易把有条件的结果当成签核结论。

本 Skill 补的正是这三块：**工具专用命令 + 症状到技术的触发时机 + 证明验收纪律**。

## 效果

我们用“同一模型、同一任务、有无 Skill”做人工盲测。在较弱的模型（`gpt-5.4-mini`，Codex）上差别最明显：不带 Skill 的一侧两个案例都没能完成证明，带 Skill 的一侧都在秒级完成。

| 案例 | 不带 Skill | 带 Skill |
|---|---|---|
| 大位宽计数器（`cnt_abs`） | ❌ 16 分 46 秒后仍未签核：4 proven / 2 CEX，始终没找到计数器抽象 | ✅ 10.8 秒：7 proven / 6 covered，使用 `abstract -counter` |
| 双计数器等价（`helper_counters`） | ❌ 0 proven / 2 undetermined，始终没想到 helper lemma | ✅ 7 秒：先证明 helper `counter1==counter2`，再以 `-with_helpers` 证明目标 |

完整报告与每个数字的原始出处见 [`test/weak_model_ab/COMPARISON.md`](test/weak_model_ab/COMPARISON.md)。

**如实说明**：每侧只跑了 1 次（N=1）；`cnt_abs` 的解法在知识库中有同类示例。在前沿大模型上，多数案例两边打平，因为强模型能自己推出方法论。Skill 的价值集中在模型*推不出来*的部分——确切的工具命令和触发时机。所以模型越弱、工具细节越冷门，收益越大。

## 它能帮你做什么

| 你遇到的情况 | Skill 提供的帮助 |
|---|---|
| 要写 SVA 断言、假设、cover | 属性写法、常见模式与反模式，避免空洞证明（vacuity） |
| 证明卡在 `undetermined` / 状态爆炸 | 按症状选技术：计数器/存储抽象、cutpoint、case split、helper lemma、assume-guarantee、`proof_structure` |
| 加了 helper 仍不收敛 | 用 JasperGold SST 诊断轨迹定位缺失的关系，据此加强 helper，直至关闭原目标 |
| 不知道该用哪个引擎、跑多深 | 引擎选择与调优；需要找深层 bug 时使用 Deep Bug Hunting（`hunt`、swarm 模式） |
| 写 JasperGold Tcl 脚本 | 命令参考与脚本惯用法，如 `-silent`、设计/COI 查询、属性枚举 |
| 从零搭建一次 FPV | 端到端流程：analyze → elaborate → clock/reset → prove → report，以及结果验收标准 |

## 快速开始

```bash
git clone https://github.com/gokeshenzhen/awesome-formal-verification-skill.git
cd awesome-formal-verification-skill
bash scripts/install.sh
```

安装程序会自动检测本机的 AI Agent 并完成注册。重启 Agent 后，在你的 RTL 工程里直接提问即可，Skill 会自动触发。例如：

> 这个 FIFO 的数据正确性断言一直 undetermined，帮我分析原因并让它证明通过。

> 为这个 AXI 从设备写一组握手协议断言，并生成 JasperGold 运行脚本。

**前提**：本机已安装 JasperGold 且许可证可用（Skill 只提供知识，不附带 EDA 工具）。

<details>
<summary>安装细节（支持的 Agent、更新与卸载）</summary>

- **Claude Code** 和 **Codex**：安装程序用目录软链接把本仓库的 `adapters/claude-code/` 挂到全局 Skills 目录（`~/.claude/skills/`、`~/.agents/skills/`，旧版 Codex 为 `~/.codex/skills/`）。
- **Cursor** 和 **Gemini CLI**：这两个使用项目级规则文件。检测到后，安装程序会输出接入项目的具体方法。
- **更新**：入口是指向本仓库的软链接，`git pull` 即可生效，无需重装。
- **卸载**：`bash scripts/install.sh --uninstall`。移动仓库目录后需重新运行安装程序。

</details>

## 可选搭配：TraceWeave

[TraceWeave](https://github.com/gokeshenzhen/TraceWeave) 是一个 MCP 服务，让 AI Agent 能直接读取波形和调试产物。在本项目中，它是 Skill 在需要逐拍分析轨迹时推荐使用的**可选波形阅读工具**：

- **SST 引导的 helper 精化**：helper 仍不收敛时，Skill 让 AI 用 `get_formal_paths`（发现 JasperGold 产物）、`search_signals`（解析信号路径）、`get_signals_by_cycle` / `get_signals_around_time`（读取最后满足状态和失败状态）阅读 SST/CEX 轨迹，再从 RTL 推导缺失的关系。
- **可复现案例与盲测**：`test/cti-*` 案例和人工 A/B 基准用它做可审计的信号读取。

TraceWeave **不是必需依赖**：运行 Tcl 流程不需要它；如果波形是 VCD 格式，任何 VCD 查看器都能读取同样的信号。但如果波形是 **FSDB 或 FST** 格式（二进制格式，无法像 VCD 一样按文本读取），就需要用 TraceWeave 让 AI 读取。

## 适用范围与局限

- 目前只针对 **JasperGold FPV** 做了验证。VC Formal 等工具尚未覆盖。
- 知识主要提炼自官方文档与应用笔记，并经少量盲测验证。大多数模块还在等待真实项目反馈（见下方成熟度）。
- Skill 会要求 AI 如实披露结果的前提条件。抽象、黑盒、额外假设下的证明，以及 `hunt` / DBH 没有找到反例，都**不等于**原始 RTL 签核。

## 可复现案例

仓库附带可以直接复跑的 JasperGold 案例，适合了解 Skill 教的是什么：

- [`test/cti-fifo-refinement/`](test/cti-fifo-refinement/README.md)：FIFO 数据正确性证明。直接证明不收敛，初始 helper 也不收敛；SST 轨迹暴露缺失的容量关系，补上后关闭原目标。
- [`test/cti-helper-refinement/`](test/cti-helper-refinement/README.md)：三级流水线上的 helper 归纳加强入门示例，附不依赖 Jasper 的 Python 穷举检查。
- [`test/weak_model_ab/`](test/weak_model_ab/)：上面“效果”一节的盲测原始材料。

## 工作原理

知识与 Agent 解耦，分三层：

```
knowledge/        唯一事实来源：纯 Markdown，任何 Agent 都能读
  fpv/            五个 FPV 模块；较大的模块拆成“索引 + 子主题”，按需加载
  shared/         SVA、Tcl 等通用参考
adapters/         各 Agent 的薄路由层（Claude Code / Codex / Gemini CLI / Cursor），不含知识本身
tool-specific/    EDA 工具差异（JasperGold 已有；VC Formal 规划中）
benchmarks/       场景评测与人工 A/B 实验工具
```

Agent 只加载当前任务相关的模块，不会一次读入整个知识库。

## 模块成熟度

| 模块 | 状态 | 内容 |
|------|------|------|
| `fpv/complexity-management` | ⚠️ needs-validation | 抽象、cutpoint、case split、helper lemma 与 SST 引导的精化、assume-guarantee |
| `fpv/engine-tuning` | 🔬 from-docs | 引擎选择与调优、Deep Bug Hunting |
| `fpv/property-writing` | 🔬 from-docs | SVA 属性模式与最佳实践 |
| `fpv/tcl-commands` | 🔬 from-docs | JasperGold Tcl 命令与脚本惯用法 |
| `fpv/workflow` | 🔬 from-docs | 端到端流程、证明记录与验收标准 |

- ✅ `battle-tested`：已在真实生产项目中验证
- ⚠️ `needs-validation`：已有盲测证据，等待真实项目反馈
- 🔬 `from-docs`：提炼自官方文档，尚未经过实战验证

**欢迎反馈**：如果你在真实项目里用过，无论好坏，都请提 Issue。这是模块升级成熟度的唯一途径。

## 路线图

- [x] JasperGold FPV 五大模块
- [x] SST 引导的 helper 精化与证明验收标准
- [x] 场景评测与弱模型盲测
- [ ] VC Formal 工具层
- [ ] CDC/RDC 验证模块
- [ ] Superlint 自动化模块
- [ ] 覆盖率驱动验证模块

## 参与贡献

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)，内容包括：添加知识模块、报告实际使用中的不准确之处、支持新的 AI Agent 或 EDA 工具。

## 延伸阅读

- [微信公众号文章：Awesome Formal Verification Skill 项目介绍](https://mp.weixin.qq.com/s/utIrVrACSNOdHx_XbMbazQ)
- Skill 制作方法：[liandan](https://github.com/gokeshenzhen/liandan)，把高密度的形式验证资料提炼成可溯源、可迁移、可验证的 Agent Skill

## 许可证

[MIT](LICENSE)
