**CTI 反哺 Helper Refinement：快递接力教学例子**

```text
输入 → A：收件台 → B：暂存台 → C：出库台
```

每个台面保存包裹编号 `data_*`，验证参考 `ref_*` 保存对应的期望编号。
`valid[0]`、`valid[1]`、`valid[2]` 分别表示 A、B、C 有没有有效包裹。
`step=1` 时整个流水线前进一步，`step=0` 时一起暂停。

原目标 `P`：C 有包裹时，`data_c == ref_c`。
只给归纳检查这个条件，任意初态中的 B 仍可存在数据不一致，下一拍传到 C。
因此提出 `H0`：B 有包裹时，`data_b == ref_b`。
再检查 H0 的单步归纳，A 的不一致仍可能传到 B；于是将同一个 helper
加强成 `H1`：A、B 各自有包裹时，数据都与参考一致。

```tcl
assert -helper -name h_ab {
  ((!valid[0]) || (data_a == ref_a)) &&
  ((!valid[1]) || (data_b == ref_b))
}
```

复位建立 H1，暂停保持 H1；前进时同一输入建立 A 的关系，A 的旧关系保持
B 的新关系。证明 H1 后，显式选择它支持原目标 P。
H0 在可达状态中可以为真，但自身并不单步归纳闭合；refinement 补上的是
它依赖的上游关系。空拍时 data 可能保留旧值，因此不能省略 `valid` 条件。

这是人工设计的教学演示。普通 Jasper 也能直接证明这个小电路；
诊断在独立的新会话中显式请求，用于展开归纳加强过程，不作为性能加速基准。
工具导出的正式名称是 **SST trace**，必须核对 `tag SST`，
不能将它当作复位可达的设计反例或内部 IC3/PDR 引擎的 CTI 数据结构。

| 文件 | 用途 |
|---|---|
| [parcel_pipe.sv](parcel_pipe.sv) | 设计、数据参考和原始断言 |
| [setup.tcl](setup.tcl) | 公共模型设置、状态输出和 SST 导出 |
| [baseline.tcl](baseline.tcl) | 无 helper 的正常证明及出库/空拍 cover |
| [diagnose_target.tcl](diagnose_target.tcl) | 第一轮：原目标的 SST |
| [diagnose_helper.tcl](diagnose_helper.tcl) | 第二轮：初版 helper 的 SST |
| [prove_refined.tcl](prove_refined.tcl) | 先证明加强后的 helper，再支持原目标 |
| [induction_check.py](induction_check.py) | 穷举数学模型，区分可达性与单步归纳 |
| [collect_evidence.py](collect_evidence.py) | 从本次运行日志提取结果、出处和哈希 |

**从干净 clone 运行**

Python 路径只需要 Python 3 标准库，不需要 Jasper、TraceWeave 或任何预先生成的结果。
从仓库根目录执行：

```bash
cd test/cti-helper-refinement
python3 induction_check.py
```

脚本自动创建 `evidence/induction.json`。预期所有关系在复位可达状态中成立；
`P`、`H0_B`、`P_and_H0` 的 `one_step_inductive` 为 `false`，
`H1_AB`、`P_and_H1` 为 `true`。它枚举全部编码状态与输入，并完整遍历可达状态，
不使用随机测试。它不解析 RTL，不能代替 RTL 的 Jasper 证明。

要运行 RTL 证明，先确保已安装 JasperGold、`jg` 在 `PATH` 中，且许可证可用。
脚本按 JasperGold `2025.12p002` 的命令语义验证；其他版本先核对
`help prove`、`help sst`。继续在 `test/cti-helper-refinement/` 目录中执行：

```bash
jg -no_gui -proj runs/baseline -tcl baseline.tcl
jg -no_gui -proj runs/target_sst -tcl diagnose_target.tcl
jg -no_gui -proj runs/helper_sst -tcl diagnose_helper.tcl
jg -no_gui -proj runs/refined -tcl prove_refined.tcl
python3 collect_evidence.py
```

顶层 Tcl 按当前工作目录定位 `setup.tcl`，因此需在上述目录启动。
每条 Jasper 命令使用独立项目；脚本自动创建输出目录并退出。
在未运行 Jasper 时，不需要执行 `collect_evidence.py`。

| 运行 | 预期结果 | 运行后生成的文件 |
|---|---|---|
| `baseline` | 原目标 `proven`；出库、空拍数据不一致两个 cover 均 `covered` | `evidence/baseline.txt` |
| `target_sst` | 原目标 `undetermined`；附带 `tag SST` 的轨迹 | `evidence/target_sst.txt`、`target_sst.vcd` |
| `helper_sst` | H0 为 `undetermined`；附带 `tag SST` 的轨迹 | `evidence/helper_sst.txt`、`helper_sst.vcd` |
| `refined` | H1 与原目标均 `proven`，有效性为 `proven`，bound 为 `Infinite` | `evidence/refined.txt` |
| `collect_evidence.py` | 提取上述各运行的原始结果行及日志位置 | `evidence/proof-results.txt` |

完整日志在 `runs/<运行名>/sessionLogs/session_*/jg_session_*.log`。
`prove_refined.tcl` 在复用 helper 之前检查其状态和有效性，未证明则退出；
仅标记 `-helper` 并不等于证明或无条件假设。
SST 即使某个 bound 字段显示 `infinite`，也不能据此宣布完整证明。

**可选的波形分析**

用波形查看器检查导出的 VCD。若已配置 TraceWeave，依次调用
`get_formal_paths`、`search_signals`、`get_signals_around_time`，
读取当前状态和下一状态的 `valid`、`data_*`、`ref_*`、`step` 等信号。
从 VCD 的实际时间刻度选择采样时间；它不是芯片的性能参数。
具体反例编号可以随版本或求解选择变化，关注不相等关系和实际更新分支。

如自行保存了两份 TraceWeave 采样，可额外回放其状态投影：

```bash
python3 induction_check.py --replay-samples /path/to/local/samples
```

该目录须包含 `target_sst_samples.json` 与 `helper_sst_samples.json`。
每个文件的 `samples` 数组包含两个按时间排列的
`get_signals_around_time(return_mode="values_only")` JSON 结果对象。
至少保留 `parcel_pipe.rst_n`、`step`、`in_valid`、`in_data`、`valid`、
`data_a`、`data_b`、`ref_a`、`ref_b` 的完整路径；原目标的采样还包含 `data_c`、`ref_c`。
选择复位已释放且有相邻状态转移的样本。回放仅检查保存的信号投影，不能代替证明。
未指定该选项时不读取采样文件，报告明确标记 `sst_transition_replay: not requested`。

仓库仅包含源码和复跑说明。`runs/`、`evidence/` 都在本地生成并被 Git 忽略，
不需要下载任何历史结果。公众号讲稿与配图不属于这个可运行例子的依赖。

脚本没有输入假设、cutpoint 或黑盒。`ref_*` 是验证用的数据参考，
`valid` 与 DUT 共用；证明范围是有效数据的对应关系，
不包含独立的无丢包、无重排或反压协议验证。
