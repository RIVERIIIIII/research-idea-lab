# 机制机会分析与候选研究问题

## Gap Analysis Scope

- Research Brief 状态：CONFIRMED。
- 输入：research/survey.md、research/task-properties.md；本轮实际使用 004、018、020–029 中矩阵引用的证据项。
- 总 corpus 15 篇，1 full_text、14 partial_text；任务侧 5 篇均 partial_text。未默认读取 archive，也未使用历史问题禁区。
- 当前为小规模机制分析；所有交叉项与 GAP 均是条件性推断，不是作者结论、领域空白或创新候选。未知条件只降低判断强度，不作肯定依据。

## Mechanism Opportunity Matrix

| 交叉项 | 经典方案及证据 | 受限条件 | 任务特性证据 | 特性为何影响条件（推断） | 可能改变的决策位置 | 缺失证据/反证 | 处置 |
|---|---|---|---|---|---|---|---|
| X01 软故障频谱让渡 × 推理阶段 SLO | [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E013] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E014] | 经典模型按连接速率保障等级让渡；不同请求/阶段的边际延迟损失未由等级直接表达。等级本身可以合理。 | [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E001] [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E004] [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E005] | 当连接承载不同阶段且影响可估计时，同样降速可能对应不同 SLO 损失。 | 让渡对象及恢复频谱分配的任务代价描述 | 阶段到连接映射、容量到 TTFT/TPOT 的关系、在线估计代价；静态/动态权重可能已足够。 | 进入 GAP-001，问题级推断 |
| X02 故障态 QoT/RSA × 请求迁移 | [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E002] [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E001] [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E002] | 剩余路径并非只由容量决定；频谱连续、调制可达性及故障态 QoT 都会约束可用连接。 | [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E004] [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E005] [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E006] | 源端仍存活时，留在原位置等待网络恢复与迁移状态可能要求不同的可用光路和资源。 | 任务位置/状态动作与光路可行集合的关系 | 跨域复制追赶条件、目标显存、恢复路径与迁移路径竞争；纯 WAN 代价模型可能已能解释。 | 进入 GAP-002，问题级推断 |
| X03 备份共享 × 训练通信时序 | [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E002] [@doi-b5315866469261c081250bcdcf5fa7eef701933a1b79fb009fe7d265824076b9#E002] | 现有共享例子基于受保故障的调用兼容；时序能否扩展共享仍取决于故障后的请求重叠及切换能力。 | [@doi-4a2cb92e16659d031e79df0378662e3690b96277ac187b974382b5ba657518e0#E004] [@doi-4a2cb92e16659d031e79df0378662e3690b96277ac187b974382b5ba657518e0#E005] [@doi-4a2cb92e16659d031e79df0378662e3690b96277ac187b974382b5ba657518e0#E006] | 正常训练可协调通信，但故障后的时间窗口与光交换配置兼容尚不明确。 | 可能影响备份资源调用时间与配置 | 故障后时序、切换粒度/时延、严格保障；Brief 已列 TSBPP 为方法参考，尚未在当前 corpus 核验。 | 待补证，不生成 GAP |
| X04 SRLG/双故障保护 × 训练冗余 | [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001] [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E003] [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E005] | 光层保护按物理风险，Bamboo 按流水线邻居失效；失效对象与可用状态不同。 | [@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E001] [@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E003] [@doi-51b02a686de46dedf64a72d748c2733f09d519b29ea4035e1137e7eaea468f09#E003] | 网络分区不等同节点抢占，是否可用任务冗余替代部分光层冗余尚无状态可达性证据。 | 可能影响保障资源与任务副本放置 | 风险到任务失效映射、分区下正确性、计算冗余成本与失效相关性。 | 待补证，不生成 GAP |

## Candidate Gaps

### GAP-001 — 软故障恢复中连接速率保障与推理阶段损失的对应关系

- gap_id: GAP-001
- title: 软故障恢复中连接速率保障与推理阶段损失的对应关系
- gap_type: integration-driven
- description: 当软故障需要频谱让渡时，连接等级对任务损失的描述在什么条件下足够，什么条件下需要额外的阶段/状态信息？
- why_it_may_matter: 在相同故障、频谱预算与最低服务约定下，需判断恢复连接速率是否对应预期的推理 SLO，避免用牺牲其他业务保障换取表面收益。
- derived_from: [X01]
- supporting_papers: [doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922, doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3]
- evidence: [[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E013], [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E014], [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E001], [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E004], [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E005]]
- counter_evidence: [[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E013], [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E014], [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005], [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009]]
- uncertainty: 阶段与连接映射、带宽到 SLO 的因果关系及信息获取成本未核验；可能无需新机制即可用既有等级/权重表达。
- back_check_needed: true
- confidence: LOW

#### Observed Evidence

软故障文献已有 gold/bronze 等级、最低速率及权重，不能声称其完全不感知业务。[@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E013] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E014] DistServe 区分 TTFT/TPOT，并指出状态通信和带宽放置限制。[@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E001] [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E004]

#### Cross-paper Synthesis

synthesis/inference：连接保障等级与阶段 SLO 是不同层次的信息；在阶段被映射到光连接并受到其容量限制时，两者的对应关系值得核验。不能据此直接认定静态等级不足。

#### Candidate Gap Inference

若阶段/状态信息会改变相同约束下的让渡代价排序，才出现超出普通分级的研究问题；若已有权重可完整表达，或性能仅受 GPU 限制，则此项削弱或排除。

#### Mechanism Opportunity

- classical_problem_and_scheme: 固定路由等条件下的软故障频谱让渡与速率保障。
- limiting_assumption_and_boundary: 连接级最低速率是合理输入，但不是阶段性能映射本身。
- task_property_and_conditions: 推理两阶段 SLO 不同；带宽只有在相关状态传输路径上成为约束时才有意义。
- causal_link: 阶段状态可能改变让渡损失的描述，进而影响让渡对象，而非仅把 gold 改称高优先级推理。
- unresolved_question: 何时连接级等级/权重已足够，何时需要额外信息且能改变可行决策？
- missing_evidence: 工作负载映射、状态观测、SLO 对有效容量的敏感性和控制成本。

#### Counter Evidence

BSR 已有分级带宽和客户层协调，软故障共享已有权重调节；它们均须作为强替代解释。[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E014]

#### Uncertainty

光层必要性是待通过的门槛：若换成通用 WAN 后仅参数变化、决策逻辑不变，则不符合 Brief，不推进。当前不存在净收益证明。

#### Back-check Needed

后续需核查应用感知/延迟感知的软故障恢复、弹性频谱让渡、分阶段推理带宽控制及动态优先级替代方案；本轮未执行回查。

### GAP-002 — 光路可行性变化下推理请求留存与状态迁移的决策边界

- gap_id: GAP-002
- title: 光路可行性变化下推理请求留存与状态迁移的决策边界
- gap_type: integration-driven
- description: 光路故障或 QoT 变化后，源端仍存活时，哪些状态与光资源条件允许考虑迁移，哪些条件只能等待网络恢复或采取其他动作？
- why_it_may_matter: 迁移需要可用传输和显存，可能争用网络恢复资源；低停顿迁移不能代替故障后的可行性判断。
- derived_from: [X02]
- supporting_papers: [doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921, doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d, doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102]
- evidence: [[@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001], [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E002], [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E001], [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E002], [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E004], [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E005], [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E006]]
- counter_evidence: [[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E002], [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E006], [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E003]]
- uncertainty: 尚无跨域迁移成本及失效下状态可达性实证；可能退化为已有 WAN 迁移/放置问题。
- back_check_needed: true
- confidence: LOW

#### Observed Evidence

光路受连续频谱、调制可达性及故障态 QoT 约束。[@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E001] [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E002] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001] Llumnix 在线复制依赖源端持续计算、目标预分配显存和握手，复制需追赶增量；端点失败会中止。[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E004] [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E005] [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E006]

#### Cross-paper Synthesis

synthesis/inference：任务迁移能否执行与剩余传输可行集合有关；剩余“总带宽”不足以表示所有光连接条件，但是否改变最终任务动作尚需证据。

#### Candidate Gap Inference

值得核验的问题是光层可行性何时实质改变请求的可行动作，而不是把既有迁移部署到光网络后宣称新问题。

#### Mechanism Opportunity

- classical_problem_and_scheme: 指定故障集合下的光路恢复与故障态 QoT/RSA。
- limiting_assumption_and_boundary: 网络恢复和任务迁移各有成立条件，本轮没有证据宣称二者均被现有领域普遍忽略。
- task_property_and_conditions: 只考虑源端仍存活且状态可访问的追加式 KV 在线迁移；不覆盖源端状态丢失。
- causal_link: 剩余连续频谱、调制和 QoT 可能改变迁移传输的可行性与代价，从而改变任务动作选择。
- unresolved_question: 什么情况下光层约束使迁移与留存的决策发生实质变化，且简单重路由/普通 WAN 控制无法等价表达？
- missing_evidence: 复制与状态生成速率、WAN 往返/握手代价、显存余量、光路配置时延及资源竞争。

#### Counter Evidence

Llumnix 已提供迁移与重新调度，DistServe 已考虑带宽放置；“支持迁移”“考虑带宽”均不能单独作为贡献。[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E002] [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E003] 端点失效导致中止，也限制其作为失效后恢复的直接复用。[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E006]

#### Uncertainty

若所有光层细节都可无损压缩为固定链路容量/延迟且选择不变，应排除该方向。不得假定跨地域复制能追上状态增长，也不得假定迁移目标有空闲 GPU/显存。

#### Back-check Needed

后续需核查光网络服务迁移、VNF/状态迁移、网络感知 LLM 调度与 QoT 感知恢复；本轮未执行回查。

## Rejected / Weak Gap Candidates

- “传统机制不感知业务，给 LLM 增加优先级”：排除。已有分级带宽、客户协调及频谱让渡；没有额外决策差异就只是标签替换。[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E013]
- “利用训练空闲期共享备份即可创新”：待补证。Atlas 提供正常执行的协调，未证明故障后的调用兼容、光配置条件或严格保障；TSBPP 等 Brief 方法参考必须先回查。
- “训练有副本，所以可以减少 SRLG 保护”：待补证。节点冗余覆盖与光层共因风险不是同一故障对象，状态可达性和一致性未明确。[@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E001] [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001]
- “降低恢复带宽即可降低频谱开销”：排除。BSR 已有此能力，降低保障水平本身不能解释成同等保障下的收益。[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E013]

本轮未生成 hypothesis、back-check 或 candidate idea。GAP 只表示条件性问题值得核验，不表示此前无人解决；人工最终审查仍保留。

## 2026-10-10 映射核验更新

详见 `research/stage3-mapping-audit.md`。两 GAP 均由 MEDIUM 下调为 LOW，作为待补证问题保留，不进入 hypothesis。GAP-001 须改为具体 KV 传输事件与用户可见延迟，不能假定 decode 每个 token 都经过 WAN；GAP-002 尚未通过普通网络代价 oracle 的替代检查。新增反证 NetKV 已使用负载、缓存和网络成本选择 decode 实例。[@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E001] [@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E002] DistServe 交接流程的直接证据为 [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E007]。此前矩阵的“进入 GAP”只保留编号和历史推断位置，当前处置以本节为准。

## 直接已有工作补充

GORGO v1 只转发请求，不传 KV 内容，不能补证跨域迁移。[@doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1#E002] EdgeFlow 已研究地理分布式 KV 迁移与 activation 重计算的组合，成为 GAP-002 的直接部分解法。[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E001] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E002] 两问题仍 LOW，不生成 hypothesis；下一步补该文正文以检查故障模型和剩余差异。

## EdgeFlow 正文后的范围收缩

032 从 abstract_only 升为 partial_text，新增 E003–E008。其联合迁移目标/逐层直传—重计算策略为直接已有解法。[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E004] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E005] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E006] GAP-002 仅保留“任务迁移数据量与光层路由/频谱可行分配是否相互改变决策”的待核验关系；不是候选方案。过载/计划退出依赖源端可访问，不能直接称为硬断路后的状态恢复。[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E003] 两 GAP 维持 LOW；缺失实现条件 [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E008] 不作支持。

## 讨论标准修正：从待证关系进入假设

依据用户澄清：论文只需为基础事实与可用能力提供依据；新关系本身允许没有现成论文证明。缺少实测收益不作为排除线索的理由。进入 hypothesis 的门槛改为：边界具体、因果机制合理、前提可核验、与已有工作有明确比较、可被否定。光层不可替代性作为要检验的主张，而非必须已由文献证明的前置事实。

GAP-002 进入 HYP-001，置信度仍 LOW；条件性探索不表示先前未知条件已解决。将情形收窄为源端仍可达且状态可用的软故障/容量退化恢复，检验迁移数据量与光路频谱决策的反馈。当前不使用源端已失联、任意 token 均跨 WAN 或所有模型 activation 固定减半等假设。

GAP-001 继续保留：其具体数据流和延迟定义仍不够清楚，暂不独立生成假设。这是问题界定不足，不是已有论文未证明它。

为保持 HYP→GAP 证据链完整，GAP-002 supporting evidence 补充本轮已核验 EdgeFlow 的源端状态、重计算与目标/分界决策：[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E003] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E004] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E005] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E006]；软故障调制—频谱权衡依据 [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E012] [@doi-28ec1674c2592b53d660fec8e98d179b1d53d088ab9a3aa3ba317194ca8ec922#E013]。上述论文事实与新耦合关系严格区分。
