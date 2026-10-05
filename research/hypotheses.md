# Candidate Hypotheses

## Scope & Status

- **inputs**：已确认的 `research/research-brief.md`、pipeline-validation `research/gaps.md`、`research/survey.md` 及对应 paper evidence。
- **GAP coverage**：读取 `GAP-001` 与 `GAP-002`；二者都能形成原则上可证伪的待回查判断，因此各生成一个 hypothesis。
- **validation boundary**：以下内容仅验证 `GAP → grounded + falsifiable hypothesis → back-check queries`。它们不是事实、正式创新点、novelty 结论或 confirmed contribution。
- **status rule**：所有 hypothesis 均为 `NEEDS_BACK_CHECK`；本阶段不执行查询。

## HYP-001 — 预测驱动的训练状态感知软故障协同控制可能降低任务级恢复代价

- **hypothesis_id**：`HYP-001`
- **title**：预测驱动的训练状态感知软故障协同控制可能降低任务级恢复代价
- **statement**：在光层渐进式软故障能够被提前预测、且预测窗口足以完成至少一种控制调整的条件下，联合使用预测的 QoT/BER 演化与训练运行状态来选择光层频谱/调制调整和训练侧配置，相比固定 QoT 阈值维修或仅按静态业务等级进行频谱共享，将降低故障期间的训练任务完成时间增量，同时维持既定光路 QoT 保障。
- **derived_from**：[`GAP-001`]
- **research_problem**：软故障预测给出了动作时间窗口，但当前证据没有说明训练所处阶段、剩余工作量或训练配置是否应改变光层维护/重配置决策；反过来，健康网络中的训练配置优化也没有说明如何响应持续 QoT 退化。
- **rationale**：软故障预测工作证明了未来约 4 天退化轨迹可被建模，并报告其维修时机优于固定阈值；频谱共享工作给出了光层可执行动作；GeoPipe 则表明训练配置确实能够读取跨 DC 光网络约束。三类证据共同支持“联合关系值得调查”，但没有证明联合控制一定有效。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E004] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E006] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002]
- **supporting_evidence**：
  - 软故障预测输入 50 个 BER 观测并预测未来 70 步、约 4 天，为提前动作提供时间窗口。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E004]
  - 在论文单光路设置下，预测维修比固定阈值更接近硬故障且 QoT margin 更低。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E006]
  - 光层已有调制与频谱共享动作，可作为被联合选择的网络侧机制。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
  - GeoPipe 已联合考虑计算、HBM、跨 DC 时延和带宽来调整训练配置，并指出带宽与训练收益不是简单线性关系。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E006]
  - GeoPipe 作者把 scheduler 与 optical control plane 的更紧密集成列为未来工作。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E007]
- **counter_evidence**：
  - 静态业务等级驱动的频谱共享与在线 RSA 可能已经足以保障关键连接，使训练状态带来的增益很小。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
  - GeoPipe 的训练侧配置可主动适应带宽约束，可能无需增加故障感知的联合控制。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E006]
  - 资源弹性可能通过移除不可用 worker/DC 提供更简单替代，但当前只有 metadata，尚不能确认。[@openalex-w3037519745#E002]
- **assumptions**：
  - 软故障预测精度和提前量足以支撑控制动作；非平稳数据不会使预测在关键时刻失效。[@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E005] [@doi-ffdb39e27e6ff730db4c1d1bcd3a37df8c5c735ce4247d36f37fbb406e7413c4#E007]
  - 光层 QoT/频谱变化能够造成可观察的训练完成时间损失，而不是完全被传输层或训练框架吸收。
  - 训练状态会改变不同恢复动作的相对代价，并且训练框架允许有限的运行时配置调整。
  - 光层频谱/调制与训练侧配置在控制时间尺度上均可调整。
- **falsifiability**：如果在满足上述条件的故障场景中，联合使用训练状态与 QoT 预测相对网络侧固定阈值/静态优先级基线不能稳定降低任务完成时间增量，或任何收益都以违反相同 QoT 保障为代价，则该 hypothesis 被否定；如果网络侧恢复或训练侧独立适应始终达到相同结果，也会否定联合决策的必要性。
- **uncertainty**：当前没有论文直接测量软故障演化对 LLM 训练完成时间和连续性的影响；频谱共享只有摘要证据；训练状态的具体有效变量尚未由当前 corpus 确认。
- **back_check_queries**：
  - `"optical soft failure" "distributed training" proactive reconfiguration`
  - `QoT degradation aware geo-distributed machine learning scheduling`
  - `training-stage-aware optical network control soft failure`
  - `predictive maintenance elastic optical network AI workload continuity`
  - `resource elasticity worker removal versus network recovery distributed training failure`
- **confidence**：`MEDIUM`
- **evidence_status**：`inferred`
- **status**：`NEEDS_BACK_CHECK`

## HYP-002 — PSRLG 风险感知的算力放置与光保护联合选择可能降低区域故障下的训练中断

- **hypothesis_id**：`HYP-002`
- **title**：PSRLG 风险感知的算力放置与光保护联合选择可能降低区域故障下的训练中断
- **statement**：在区域相关故障概率不可忽略、且训练实例与光路可能暴露于共同地理风险的条件下，依据 PSRLG 概率联合选择训练实例/并行拓扑放置与光层保护资源，相比先独立确定算力放置、再选择光路或保护路径，将在相同算力与光谱资源预算下减少预期训练中断时间或任务完成时间损失。
- **derived_from**：[`GAP-002`]
- **research_problem**：PSRLG 能表达联合失效和路径存活概率，跨 DC 训练也明确依赖区域间光网络，但当前已读证据没有确认相关风险是否会实质改变训练拓扑与光保护的共同选择。
- **rationale**：相关故障概率不能只用失效链路数量代替；同时，训练并行拓扑会决定跨 DC 通信关系。因此，当计算实例与光路共享风险时，顺序式独立决策可能隐藏共同失效点。不过当前没有任务级区域故障实验，这一关系仍高度不确定。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E005] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E003]
- **supporting_evidence**：
  - PSRLG 模型可查询任意资源集合的联合失效概率及路径存活概率。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002] [@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E006]
  - 不同故障基数的概率区间重叠，说明简单按故障数量建模可能遗漏风险差异。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E005]
  - GeoPipe 的训练测试床跨 3 个区域，训练配置明确依赖跨 DC 光网络参数。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E003]
  - GeoPipe 未注入区域或链路故障，当前证据不能验证风险条件下的行为。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]
- **counter_evidence**：
  - PSRLG 工作已经提出将概率模型用于 VM placement 类 SLA 问题，联合算力放置可能是已有模型的直接应用，而非新的研究关系。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E006]
  - 健康网络下的训练配置已经能够感知跨 DC 带宽；加入风险变量可能只增加一个输入参数，并不改变决策结构。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002]
  - 当前 selected corpus 中仍有区域故障韧性、灾害保护和光数据中心论文尚未精读，可能直接覆盖该判断。
- **assumptions**：
  - PSRLG 概率在目标地区和时间尺度上足够校准；现有模型的地域近似不会主导误差。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E007]
  - 算力站点与光路的地理暴露关系可以映射到同一风险模型。
  - 区域相关风险高到足以改变放置/保护选择，而不是被普通冗余完全吸收。
  - 存在多个资源预算可比的可行方案，联合选择不会仅因增加资源而获益。
- **falsifiability**：如果在相关风险被正确建模且资源预算相同的条件下，顺序式独立决策在预期训练中断或完成时间损失上始终与联合决策相当或更优；或者 PSRLG 概率变化不会改变任何最优放置/保护选择，则该 hypothesis 被否定。
- **uncertainty**：缺少区域故障下的训练任务级证据；PSRLG 到训练损失的映射尚未建立；未精读的 selected papers 很可能提供直接覆盖或更强 counter-evidence。
- **back_check_queries**：
  - `PSRLG-aware geo-distributed training placement optical protection`
  - `regional failure resilient compute network co-allocation distributed machine learning`
  - `disaster-aware virtual infrastructure mapping optical datacenter AI training`
  - `shared risk link group compute placement optical network protection`
  - `correlated failure aware pipeline parallel training multi-datacenter network`
- **confidence**：`LOW`
- **evidence_status**：`inferred`
- **status**：`NEEDS_BACK_CHECK`
