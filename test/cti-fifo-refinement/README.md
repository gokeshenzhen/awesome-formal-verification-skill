**CTI 反哺 Helper Refinement：让 FIFO 的数据证明收敛**

这是一个可复跑的收敛案例：直接证明数据正确性未在给定预算内完成；
初始数据 helper 也未闭合；SST 暴露缺失的容量关系；先证明这个关系，
再用它支持数据 helper，最终关闭未修改的原目标。

它验证 **refinement 的作用**。要进一步声称“无 skill 的模型失败、有 skill 的
模型自主读取 CTI 并成功”，还需要两个独立会话；当前没有这项新盲测结果。
[BLIND_AB.md](BLIND_AB.md) 提供隔离材料和验收条件。运行已经写好的脚本
不能充当模型自主发现 helper 的证据。

**设计与目标**

把 FIFO 看成只有 32 个货位的环形仓库。写指针标记下一个入库位置，
读指针标记待出库位置，`o_fill` 是账面库存。指针有 6 位：低 5 位选择
物理货位，额外一位区分绕圈；例如编号 20 和 52 指向同一个物理货位。

DUT 是 [ZipCPU sfifo 的固定版本](https://github.com/ZipCPU/zipcpu/blob/42606d2d6ef55df313772232977621b2d72f0159/rtl/ex/sfifo.v)，
配置见 [neutral/tb.sv](neutral/tb.sv)：32 位数据、32 项、寄存器读输出，
关闭满时写和空时读选项。只删除上游 `FORMAL` 条件块，保留其余源码与
public-domain 声明；来源和哈希见 [SOURCE.json](SOURCE.json)。复跑无需下载上游。

验证观察器任意选定一个固定的扩展地址 `watched_address`，记住该位置最近
一次被接受的写入数据。原目标 `testbench.P0`：当该位置是非空 FIFO 的队头时，
输出等于记录的数据。唯一输入假设是观察地址保持稳定；读写请求和数据任意。
这是数据对应关系的证明，不包含“每次请求最终都会被服务”的活性保证。

**refinement 补了什么**

初始 helper `H_mem_watch_live` 表达：

> 被观察位置仍在 FIFO 的有效区间里时，对应物理货位的数据等于观察器记录。

```tcl
assert -name H_mem_watch_live {
  ((watched_address - dut.rd_addr) < dut.o_fill)
  |-> dut.mem[watched_address[4:0]] == watched_data
}
```

已有控制关系包括 `fill == wr_addr - rd_addr`、`empty == (fill == 0)`、
`full == (fill == 32)`。减法按 6 位无符号数回绕。这些关系允许如下诊断状态：

| 信号/关系 | 当前状态 | 接受一次写入后 |
|---|---:|---:|
| `rd_addr` | 22 | 22 |
| `wr_addr` | 20 | 21 |
| `o_fill` | 62 | 63 |
| `watched_address` | 52 | 52 |
| `mem[20]` | 0 | 4096 |
| `watched_data` | 0 | 0 |

这组值用于手算，工具不保证每次选择相同值。当前复位已释放，写入被接受，
没有读出，输入数据为 4096。`(20 - 22) mod 64 = 62`，因此指针关系成立；
`52 - 22 = 30 < 62`，因此数据 helper 的前件也成立。
写指针 20 覆盖 `mem[20]`，但观察地址是 52，观察器不更新。下一拍数据不等，
helper 被打破。问题在于：**32 个货位的 FIFO，任意初态竟允许库存为 62。**

SST 提示要补上的关系是容量上界，而不是禁止这一个特殊编号：

```tcl
assert -name H_fill_range {dut.o_fill <= 6'd32}
```

先在原始复位、RTL 和输入环境上证明 `H_fill_range`；证明成功后，才把它加入
后续义务的支持集合。本例保持 `H_mem_watch_live` 的公式、引擎和预算相同，
只新增并证明容量关系。加强的是 **helper 集合**：`H_controls ∧ H_mem`
变为 `H_controls ∧ H_fill_range ∧ H_mem`。随后证明寄存器读路径的关系，
最终证明原始 `P0`。完整依赖顺序在 [prove_refined.tcl](prove_refined.tcl)。

工具正式导出的名称是 **SST trace**，脚本核对 `get_trace_info` 的 `tag SST`。
这里用它观察归纳加强缺口；它不是复位可达的设计反例，也不表示导出了
IC3/PDR 引擎内部的 CTI 数据结构。容量上界获证后，上述超容量状态的
不可达性才有独立证明支持。

**从干净 clone 复跑**

需要已安装并可用的 JasperGold（`jg` 在 PATH 中，许可证可用）；整理结果
需要 Python 3.9+，仅使用标准库。命令按 JasperGold `2025.12p002` 验证。
TraceWeave 是可选的波形阅读工具，不是运行 Tcl 的依赖。

从仓库根目录执行；各次 Jasper 运行使用独立项目：

```bash
cd test/cti-fifo-refinement/neutral
jg -no_gui -proj runs/baseline -tcl baseline.tcl
cd ..
jg -no_gui -proj runs/initial_helpers -tcl initial_helpers.tcl
jg -no_gui -proj runs/helper_sst -tcl diagnose_helper.tcl
jg -no_gui -proj runs/refined -tcl prove_refined.tcl
python3 collect_evidence.py
```

| 阶段 | 固定配置 | 预期观察 |
|---|---|---|
| baseline | 原目标，`H AM N`，120 秒证明预算 | `P0` 为 `undetermined` |
| initial_helpers | 先证明控制关系，再用 `H AM N` 证明数据 helper，20 秒 | 数据 helper 为 `undetermined`；停止在此，不复用未证关系 |
| helper_sst | 同样的控制关系；`-sst 2 -engine_mode B`，10 秒 | 数据 helper 仍为 `undetermined`，导出 `tag SST` 的轨迹 |
| refined | 新增且先证明容量上界；数据 helper 仍用 `H AM N`、20 秒 | 全部 helper 与 `P0` 均为 `proven`，有效性为 `proven`，证明无界；读 cover 为 `covered` |

时间限制是 proof 命令预算，不是整个 Jasper 进程的运行时间。不同版本、机器、
求解选择可能改变耗时、轨迹乃至基线结果；`undetermined` 只表示本次预算内
没有结论。若你的基线直接证明成功，记录该结果，不应修改报告把它写成未收敛。

`proof_utils.tcl` 在复用每个关系前检查状态、有效性和无界结果；新增容量关系
是 assertion，不是环境 assume。脚本不修改 DUT、不做黑盒/cutpoint、不用
`marked_proven`。读取 cover 单独求解。`initial` 块被 Jasper 忽略的警告可见于
日志；证明使用 `setup.tcl` 配置的显式复位。

结果均在本地生成：

- `neutral/evidence/baseline.txt` 与 `neutral/runs/baseline/`：基线报告和完整日志。
- `evidence/initial_helpers.txt`、`helper_sst.txt`、`refined.txt`：各阶段报告。
- `evidence/helper_sst.vcd`：当前运行的诊断波形；只包含目标相关信号。
- `runs/<阶段>/sessionLogs/session_*/jg_session_*.log`：原始日志。
- `evidence/results.json`：Python 脚本提取的状态、日志行号、哈希和检查结果。

`collect_evidence.py` 不执行证明，也不生成预置结果；它读取各项目最新的会话
日志。检查全部为 `true` 才表示当前复跑呈现了表格中的对比。如果缺少运行或
结果不同，它保留实际结果并返回非零。日志中的 property `time` 字段不能当作
全部 helper 加原目标的总耗时。

**阅读当前 SST**

有 TraceWeave 时依次使用 `get_formal_paths`、`get_waveform_summary`、
`search_signals`、`get_signals_around_time`。先从日志核对 trace 类型，再从波形
摘要确认时间刻度；读取相邻状态的 `o_fill`、`wr_addr`、`rd_addr`、
`watched_address`、`watched_data`、对应的 `mem` 槽，以及转移前的 `w_wr`、
`w_rd`、`i_data`、`i_reset`。没有 TraceWeave 时可用 VCD 查看器读取同样信号。
先解释旧关系如何允许该状态，再从 RTL 推导缺失关系，最后回到普通证明验证。

这些脚本复现已确定的修正步骤，并非自动从任意轨迹合成 helper 的程序。
仓库只提交源码、出处与复跑/盲测说明；运行结果、公众号讲稿和配图不提交。
