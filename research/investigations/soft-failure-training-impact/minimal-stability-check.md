# IDEA-002 最小稳定性核查

Status: `SYNTHETIC_STABILITY_PASS`

## Scope

本核查只回答一个问题：最小反例中的决策差异是否只依赖单个刻意数值点。

它不是光网络仿真、训练实验或现实发生概率估计，不能证明方法有效或候选具有 novelty。

## Model

使用 `minimal_stability_check.py` 穷举 81 个透明的合成组合：

- 可用恢复 FS blocks：`1 / 2 / 3`；
- Job A 两条同步流全部恢复后的收益：`36 / 40 / 44 ms`；
- 只恢复 Job A 一条流时的部分收益：`0 / 4 / 8 ms`；
- 恢复 Job B 单条 pipeline 关键流的收益：`27 / 30 / 33 ms`。

比较两类决策：

1. `per-flow greedy`：按单条流的即时收益排序，不向前观察流组互补关系；
2. `job-group-aware`：枚举可行恢复集合，按真实 job-level time reduction 选择。

“FS block 数量”表示 QoT-aware rerouting 后仍可用于 modulation fallback 的连续频谱块数量；模型没有模拟真实 topology、OSNR 或 fragmentation distribution。

## Results

- 总场景：81。
- 两种策略选择不同且 job-group-aware 更优：23。
- 改善范围：`1–17 ms`。
- 中等稀缺（2 blocks）：27 个场景中 23 个出现更优的组合选择。
- 严重稀缺（1 block）：0 个场景出现差异，因为无法完整恢复 Job A 的流组。
- 资源充足（3 blocks）：0 个场景出现差异，因为所有流都能恢复。
- 中等稀缺的另外 4 个场景没有差异：此时 `Job B 收益 + Job A 单流收益` 已不低于完整恢复 Job A 流组。

详细数据保存在 `minimal-stability-results.csv`。

## Interpretation

该差异不是单个数值点现象，而是在“资源刚好不足以恢复全部流、但足以在两个恢复组合之间选择”的中等稀缺区间稳定存在。

同时，核查也给出了清晰否定边界：

- 频谱过少，流组根本不可恢复时，不需要 group-aware coordination；
- 频谱充足，可恢复全部流时，不存在牺牲选择；
- 单流部分恢复收益足够高时，可加的 per-flow 决策可能已经足够。

因此，候选问题不是对所有 soft failure 都成立，而只在一个明确的 scarcity regime 内成立。这种边界可被建模和验证，优于无限制地声称训练感知恢复普遍有效。

## Remaining Risk

本次通过的是数学结构稳定性，不是现实场景稳定性。仍未验证：

1. 真实 EON 负载与 soft-failure severity 下，中等稀缺区间是否经常出现；
2. 真实训练 trace 是否普遍包含足够强的 flow-group complementarity；
3. GARA/CD-CBA 加入完整 job-level objective 后是否能直接得到相同结果；
4. spectrum continuity/contiguity 是否会增强而不是消除该组合差异。

## Decision

`SYNTHETIC_STABILITY_PASS`：最小问题结构在邻近参数中成立，不是单点构造。

`IDEA-002` 仍维持 `CONDITIONAL_PASS`，因为现实出现频率和相对 GARA/CD-CBA 的独立方法贡献尚未验证。
