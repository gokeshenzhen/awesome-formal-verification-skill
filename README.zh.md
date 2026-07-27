# Awesome Formal Verification Skill

<p align="right">
  <a href="README.md">English</a> · <strong>简体中文</strong>
</p>

一个开源、与 AI Agent 无关的形式验证知识库，旨在通过任意 AI 编码助手增强你的 EDA 工作流。

> 🎯 **当前重点**：JasperGold 形式属性验证（FPV）
> 🗺️ **路线图**：CDC/RDC、Superlint、Coverage、VC Formal 支持

## 这是什么？

本项目将深度形式验证专业知识整理成 AI 编码 Agent 可以使用的结构化“技能”。无需反复向 AI 助手解释 FPV 概念、证明引擎调优技巧或 TCL 脚本模式，只需让它加载本 Skill，即可直接应用这些知识。

**核心设计原则：**
- **Agent 无关**：核心知识采用纯 Markdown。通过轻量适配层支持 Claude Code、Codex、Gemini CLI、Cursor 等 Agent。
- **工具感知**：JasperGold 和 VC Formal 各有特性。通用验证知识与特定工具细节分开维护。
- **社区驱动**：每个模块都有成熟度标识，由真实工程师在实践中验证，而不只是从文档中提取。

## Skill 制作方法

本项目的 Skill 制作方法来自作者维护的 [liandan](https://github.com/gokeshenzhen/liandan)：把高密度形式验证资料整理成可溯源、可迁移、可验证的 Agent Skill。

## 项目介绍

- [微信公众号文章：Awesome Formal Verification Skill 项目介绍](https://mp.weixin.qq.com/s/utIrVrACSNOdHx_XbMbazQ)

## 快速开始

克隆仓库，然后运行一次安装程序：

```bash
git clone https://github.com/gokeshenzhen/awesome-formal-verification-skill.git
cd awesome-formal-verification-skill
bash scripts/install.sh
```

安装程序会自动检测本机上的 AI Agent，并为每个 Agent 注册本 Skill：

- **Claude Code** 和 **Codex**：两者都使用全局 Skills 目录。安装程序通过目录软链接，将其指向本仓库的标准 Skill 目录（`adapters/claude-code/`）：当前 Codex 使用 `~/.agents/skills/`，Claude Code 使用 `~/.claude/skills/`，旧版 Codex 安装使用 `~/.codex/skills/`。重启 Agent 后，本 Skill 会在任何 FPV 任务中自动触发（formal / property / assertion / prove / CEX / JasperGold / VC Formal / FPV）。
- **Cursor** 和 **Gemini CLI**：两者使用项目级规则或上下文文件，而不是全局 Skills 目录。检测到这些 Agent 后，安装程序会输出将本 Skill 接入项目的具体方法。

每个 Agent 的 Skill 入口都是指向当前检出目录的软链接，因此更新仓库（`git pull`）会立即更新所有 Agent，无需重新安装。`SKILL.md` 本身仍是仓库内正常跟踪的文件，避免文件级 `SKILL.md` 软链接造成扫描问题。移动仓库后请重新运行安装程序；使用 `bash scripts/install.sh --uninstall` 可移除这些链接。

> `adapters/` 下的各 Agent 包装文件是安装程序所连接的来源清单，通常无需直接修改。

## 项目结构

```
awesome-formal-verification-skill/
├── knowledge/                  # 核心知识（Agent 无关）
│   ├── fpv/                    # 形式属性验证
│   │   ├── property-writing.md
│   │   ├── engine-tuning.md             # 索引（引擎 + DBH 路由）
│   │   ├── engine-tuning/               # DBH 子主题叶子
│   │   ├── complexity-management.md     # 索引（渐进式披露）
│   │   ├── complexity-management/       # 子主题叶子
│   │   ├── tcl-commands.md
│   │   └── workflow.md
│   ├── shared/                 # 跨应用共享知识
│   │   ├── sva-reference.md
│   │   └── tcl-common.md
│   ├── cdc/                    # 🔜 CDC 验证
│   └── lint/                   # 🔜 Superlint
│
├── adapters/                   # Agent 专用包装层
│   ├── claude-code/SKILL.md
│   ├── codex/AGENTS.md
│   ├── gemini-cli/GEMINI.md
│   └── cursor/.cursorrules
│
├── tool-specific/              # EDA 工具差异
│   ├── jaspergold/
│   └── vc-formal/              # 🔜
│
└── benchmarks/                 # 验证测试用例
    └── fpv/
```

## 模块成熟度

| 模块 | 状态 | 说明 |
|------|------|------|
| `fpv/property-writing` | 🔬 from-docs | SVA 属性模式与最佳实践 |
| `fpv/engine-tuning` | 🔬 from-docs | 证明引擎选择、调优与 Deep Bug Hunting |
| `fpv/complexity-management` | 🔬 from-docs | 复杂度降低技术 |
| `fpv/tcl-commands` | 🔬 from-docs | FPV TCL 命令参考 |
| `fpv/workflow` | 🔬 from-docs | 端到端 FPV 工作流 |

**成熟度级别：**
- ✅ `battle-tested`：已在真实生产项目中验证
- ⚠️ `needs-validation`：已经整理和审阅，等待实际项目反馈
- 🔬 `from-docs`：从官方文档中提取，尚未经过现场验证

## 参与贡献

贡献指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)，包括：
- 添加新的知识模块
- 报告实际使用中发现的不准确内容
- 支持新的 AI Agent
- 支持新的 EDA 工具

## 路线图

- [x] 项目骨架与适配器框架
- [x] FPV 属性编写模块
- [x] FPV 引擎调优模块
- [x] FPV 复杂度管理模块
- [x] FPV TCL 命令模块
- [x] FPV 端到端工作流模块
- [x] FPV 基准测试用例
- [ ] CDC/RDC 验证模块
- [ ] Superlint 自动化模块
- [ ] VC Formal 工具专用层
- [ ] 覆盖率驱动验证模块

## 许可证

[MIT](LICENSE)

## 致谢

本项目凝聚了芯片验证社区的经验，由 AI 提供能力支持，并由工程师进行验证。
