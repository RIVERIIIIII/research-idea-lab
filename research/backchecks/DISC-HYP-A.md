# DISC-HYP-A Targeted Literature Back-check

## Scope

- **hypothesis**：`DISC-HYP-A`
- **purpose**：检查是否已有工作同时覆盖光层软故障引起的调制/频谱/速率重配置，以及训练通信关键性驱动的受让流/牺牲流选择。
- **boundary**：定向回查，不是完整综述；未发现 DIRECT 工作不能证明其不存在。
- **data**：`research/backchecks/data/DISC-HYP-A-candidates.jsonl`

## Query Log

### 核心 queries

1. `soft failure recovery distributed deep learning elastic optical network`
2. `training-aware soft failure recovery optical network`
3. `failure-aware resource allocation geo-distributed machine learning optical network`
4. `QoT-aware distributed LLM training optical network`
5. `modulation adaptation distributed training optical WAN`
6. `spectrum sharing soft failure AI training optical network`

### Closest-work 精确补查

7. `Exploiting Spectrum Sharing for Soft Failure Recovery`
8. `P4-based Telemetry Processing for Fast Soft Failure Recovery in Packet-Optical Networks`
9. `Resource Allocation in Flexible-Bandwidth Fine-Grained Optical Transport Networks for Geo-Distributed Machine Learning`
10. `CD-CBA cross-domain communication-bound-aware resource allocation pipeline-parallel distributed LLM training`
11. `Memory-aware spectrum-efficient co-scheduling large model training heterogeneous optical WANs`

补查原因：组合查询容易把“用 ML 检测光故障”误排在前，需要用已识别的两条局部路线做精确交叉比较。

## Search Accounting

- 核心查询：96 条 raw，79 条去重结果。
- 精确补查：13 条 raw，向现有集合新增 12 条。
- **最终 metadata records：91 条。**
- 来源返回：arXiv 48 条、OpenAlex 61 条；Semantic Scholar 6 条 query 均为 HTTP 429。
- 发现一组同题双 DOI metadata（P4 soft-failure recovery）：`10.1364/OFC.2023.M1G.2` 与 `10.23919/OFC49934.2023.10117408`。全文比较不依赖二者自动合并，身份冲突继续保留供人工复核。

## Similar-work Classification

以下计数只针对进入人工比较的 8 篇关键工作，不代表全部 91 条记录。

- **DIRECT**：0
- **PARTIAL**：6
- **ADJACENT**：2

| ID | Work | Class | 核心判断 |
| --- | --- | --- | --- |
| BC-DHA-001 | Exploiting Spectrum Sharing for Soft Failure Recovery | PARTIAL | 覆盖软故障、调制切换、扩谱和低等级流降速；决策依据是静态 rate guarantee/class，不包含训练依赖。paper_id: `doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922` |
| BC-DHA-002 | P4-based Telemetry Processing for Fast Soft Failure Recovery in Packet-Optical Networks | PARTIAL | 使用 QoT/QoS telemetry 和剩余 bit rate 快速选择备选路径；不读取训练 job 结构。paper_id: `doi-fb702776ec0efd77688182ebd9f8a3c728cd9bdd50cb4ea82fb221a5eeacdcae` |
| BC-DHA-003 | Resource Allocation in fgOTN for Geo-Distributed Machine Learning | PARTIAL | 已建模 GDML 任务依赖、优先级和可调带宽，以任务完成率为目标；没有 soft-failure-induced QoT/modulation transition。paper_id: `doi-9a31f9cf00c5424841e64b70a521325632ad9fa457e6ca856337d1e6ce735962` |
| BC-DHA-004 | CD-CBA | PARTIAL | 已依据 pipeline communication-bound 状态进行多 DC 光网络频谱分配；摘要未包含软故障恢复。paper_id: `doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2` |
| BC-DHA-005 | Memory-aware and spectrum-efficient co-scheduling for large model training over heterogeneous optical WANs | PARTIAL | 联合训练负载、内存和 EON 频谱，但当前材料未包含软故障恢复。paper_id: `doi-c34b39cf00914f9d2fe73147d6b39112a32656d7a7f9c9cc5581ace6d63633bc` |
| BC-DHA-006 | Accelerating model synchronization for distributed machine learning in an optical WAN | PARTIAL | 联合 job、拓扑、波长和带宽以缩短同步时间；没有 soft failure/QoT 退化。paper_id: `doi-32972f71942352c2ec59d78d56fb2c86595b9ffe1fd06aa68c5a8c5a561ebfaf` |
| BC-DHA-007 | OSDL | ADJACENT | 根据 DDL 通信模式提供光切片、job placement 和 OCS/EPS scheduling；不处理目标故障模型。paper_id: `doi-2ad82b17c23c3155be9d5bccbe7a4bb6fbd8c372ccc1114748082ca85594ab37` |
| BC-DHA-008 | GeoPipe | ADJACENT | 证明训练迭代时间对跨 DC 带宽具有非线性响应，并提出进一步联动 optical control plane；实验没有软故障。paper_id: `doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7` |

## Closest-prior-work Comparison

### BC-DHA-001 — 最接近的光层恢复工作

- **failure model**：物理层软故障导致 QoT 恶化。
- **mechanism**：切换到更鲁棒调制，必要时让高等级光路从低等级光路获得频谱。
- **objective**：保障高优先级连接速率并降低网络成本。
- **covered portion**：`DISC-HYP-A` 的调制、扩谱、降速和受让/牺牲流框架已被覆盖。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E001] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E002]
- **remaining distinction**：全文确认该工作使用按 rate guarantee 定义的 gold/bronze 等级，不包含同步屏障、pipeline 关键边或 job-level 损失；同时报告 SS-RSA 最多恢复约 77% gold traffic，但明确以 bronze traffic 为代价。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E004] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E007]

### BC-DHA-003 / 004 / 005 — 最接近的训练感知光资源工作

- fgOTN 全文已经联合编码 task/subtask order、同步等待与可调连接带宽；CD-CBA 全文已经用 communication-bound task label 增减 FS 并联合选择路径。[@doi-9a31f9cf00c5424841e64b70a521325632ad9fa457e6ca856337d1e6ce735962#E003] [@doi-9a31f9cf00c5424841e64b70a521325632ad9fa457e6ca856337d1e6ce735962#E004] [@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E002] [@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E003]
- 这两篇全文使“training criticality 驱动光资源分配”本身成为已覆盖内容；只增加 soft-failure state 很可能只是普通约束。
- 两篇的模型与实验均未注入 soft-failure-induced QoT degradation、modulation transition 或不可避免的恢复容量缺口，因此仍保留一个更窄的待核查边界。[@doi-9a31f9cf00c5424841e64b70a521325632ad9fa457e6ca856337d1e6ce735962#E011] [@doi-9a31f9cf00c5424841e64b70a521325632ad9fa457e6ca856337d1e6ce735962#E012] [@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E011] [@doi-c0a1a370a2817c41b56baca60d53b263e1c7e65bd37473abb498764c84ff8ba2#E012]

### BC-DHA-002 — 强替代机制

- P4 全文确认：SDN 预装备选路由与 P4 规则，节点在 QoT threshold 被突破后，检查备选路径 QoT 并选择 residual bit rate 最大的路径；触发至首包转发约 2 μs。
- NS-3 测试比较了该方法、5 s telemetry-based SDN 和 hard-failure detection，论文报告 P4 方法丢包更少；作者明确限制当前 MLNT forwarding 为 1 hop。
- 因此候选必须限定在“没有同时满足 QoT 与带宽的备选路径”或“重路由后仍存在不可避免容量缺口”的情形；否则快速重路由直接绕开扩谱/降速冲突。

## Full-text Audit of Four Closest Works

| Work | Evidence level | Decisive effect on `DISC-HYP-A` |
| --- | --- | --- |
| Exploiting Spectrum Sharing for Soft Failure Recovery | full_text | 已覆盖 soft failure、modulation fallback、扩谱与牺牲低等级流；候选不能重复该机制。 |
| P4-based Telemetry Processing for Fast Soft Failure Recovery | full_text | 给出约 2 μs QoT/QoS-aware rerouting；把候选有效场景收窄为无足够备选路径/容量的情形。 |
| Resource Allocation in Flexible-Bandwidth fgOTN for GDML | full_text | 已覆盖同步依赖、task/subtask priority、跨任务资源竞争和动态光带宽。 |
| CD-CBA | full_text | 已覆盖 communication-bound task labeling、FS 增减、动态路径/频谱联合分配与训练级指标。 |

**综合结论**：原命题“training criticality 驱动 soft-failure recovery”过宽，因为其两半分别已有强 prior work。可保留的研究问题必须明确加入“soft failure 导致不可绕行的 QoT/调制容量缺口”，并把研究对象从一般增配频谱收紧为跨训练作业协调谁获得恢复频谱、谁被降速。该结论是 cross-paper synthesis，不是已有论文的原结论。

## Counter-evidence and Rejection Conditions

- 静态 rate guarantee/class 已能完成软故障频谱共享，训练语义可能不改变任何决策。
- 训练感知光资源分配已非常接近，新增 soft-failure state 可能只是一个普通约束。
- QoT/QoS-aware 快速重路由可能绕开扩谱和降速冲突。
- 如果训练损失能由普通 weighted bandwidth utility 准确表达，则不需要专门的 flow-to-job dependency。
- 如果后续全文发现 BC-DHA-001 或 BC-DHA-003/004/005 已联合建模相同 failure model、training semantics 和 optical decision variables，应将候选 REVISE 或 REJECT。

## Decision

- **human decision before full-text audit**：`KEEP`
- **decision after full-text audit**：`REVISE`
- **reason**：当前没有发现同时覆盖以下三项的 DIRECT 工作，但全文确认 training-aware optical allocation 已被明显覆盖：
  1. soft-failure-induced QoT/modulation transition；
  2. 无可行高质量备选路径时的不可避免频谱/容量缺口；
  3. 同步训练通信依赖驱动的 job-level 损失目标。
- **revised statement**：当 QoT-aware rerouting 无法提供足够残余带宽，且 soft-failure modulation fallback 造成不可避免的频谱缺口时，协调多个同步训练作业的恢复频谱受益流与降速牺牲流，是否能相对静态 rate class、GARA 类 task-priority allocation 和 CD-CBA 类 communication-bound allocation 降低 job-level barrier/bubble 损失。
- **strict boundary**：候选贡献不能是“把静态优先级换成训练权重”或“在 CD-CBA 上加入 failure flag”，而必须验证 QoT/调制可行域与 flow-to-job dependency 联合后产生既有训练感知分配无法表达的受益/牺牲决策。
- **confidence**：`MEDIUM`
- **interpretation**：REVISE 仍表示值得继续人工调查，不表示 novel、confirmed innovation 或 first work。

## Residual Uncertainty

- Semantic Scholar 全部限流。
- Memory-aware co-scheduling 等其余 closest work 尚未全部全文精读。
- P4 同题双 DOI 仍需人工处理 metadata identity；不影响本轮内容比较。
- 训练通信 trace 与光层 QoT/调制模型能否在同一验证环境中可靠耦合，尚未确认。
