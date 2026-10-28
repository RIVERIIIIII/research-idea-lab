---
schema_version: "1.0"
note_sequence: "012"
paper_id: "doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250"
title: "Probabilistic Shared Risk Link Groups Modeling Correlated Resource Failures Caused by Disasters"
source_url: "https://doi.org/10.1109/jsac.2021.3064652"
pdf_url: "https://repository.tudelft.nl/file/File_0743bacf-6346-4236-aab7-290d69073094"
input_coverage: "full_text"
evidence_level: "full_text"
created_at: "2026-10-04T10:00:00Z"
updated_at: "2026-10-04T10:00:00Z"
---

# 论文精读卡：Probabilistic Shared Risk Link Groups Modeling Correlated Resource Failures Caused by Disasters

## Input Coverage

- evidence_level：`full_text`
- 输入范围：已读取仓储版本 PDF 全部 17 页；文章正文从 PDF 第 2 页开始。
- 边界：本文提供灾害相关故障概率模型，不直接研究大模型训练 workload。

## Metadata

- paper_id：`doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250`
- authors：Balázs Vass；János Tapolcai；Zalán Heszberger；József Bíró；David A. Hay；Fernando A. Kuipers；Jorik Oostenbrink；Alessandro Valentini；Lajos Rónyai
- year：2021
- venue：IEEE Journal on Selected Areas in Communications, 39(9), 2672–2687
- DOI：`10.1109/jsac.2021.3064652`
- arXiv：未提供
- source URL：https://doi.org/10.1109/jsac.2021.3064652

## Research Question

如何对灾害导致的地理相关链路/节点故障建立概率模型，并高效计算资源集合同时失效、节点断连或路径存活的概率。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E001]

## Motivation

自然灾害和大范围攻击使仅考虑独立单组件故障不足以评估骨干网服务可用性；传统确定性 SRLG 也难以表达不同相关故障场景的概率差异。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E001]

## Method

论文提出随机区域故障模型，定义 PSRLG 的 failure probability 与 cumulative failure probability，并设计离线预计算及准线性规模的数据结构，以查询任意网络资源集合的联合失效概率；模型先处理链路，后扩展到节点。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002]

## Experimental Setup

- 使用 7 个真实/常用光骨干拓扑：OpticEU、Italian、US、NobelEU、EU、North-American、NFSNET，规模从 22/45 到 79/108 节点/链路。
- 使用意大利、欧洲和美国地震危险数据，考察烈度阈值 VI/VII；另包含随机形状灾害实验。
- 评估 CFP/FP 数据结构规模、不同基数故障概率及拓扑相关查询。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E003]

## Key Findings

- Table I 显示不同拓扑和阈值下需要保存的 CFP/FP 数量差异明显，例如 Italian/VI 为 12106 个 CFP、308 个 FP，NFSNET 对应 14199/969。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E004]
- 平均单、双、三链路故障概率区间分别约为 `4.2×10^-4–2.1×10^-3`、`1.2×10^-5–3.9×10^-4` 和 `1.9×10^-6–9.3×10^-5`。不同基数的概率有重叠，因此仅按失效链路数量筛场景可能不可靠。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E005]

## Limitations

### 作者明确承认

欧洲实验把由意大利地震目录拟合的关系式用于欧洲范围，作者明确称其为 first approximation；模型还依赖故障概率随震中距离变化等假设。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E007]

### 模型推断

PSRLG 能为区域故障提供风险输入，但没有把训练拓扑、阶段或任务恢复代价纳入风险决策。因此它适合作为故障模型，而不是算网联合优化方案本身。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E008]

## Evidence Items

### E001

`[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E001]`

- type: paper_claim
- statement: 地理灾害会造成相关资源故障，仅考虑独立单组件故障不足以评估骨干服务可用性。
- locator: {page: 2, section: "Abstract; Section I", figure: null, table: null}
- supports: []
- confidence: high
- notes: PDF 第 1 页为仓储封面。

### E002

`[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E002]`

- type: paper_claim
- statement: 论文建立随机区域故障模型与 PSRLG 术语/数据结构，可离线预计算并查询任意资源集合的联合失效概率。
- locator: {page: 2, section: "Abstract; Section I", figure: null, table: null}
- supports: []
- confidence: high
- notes: null

### E003

`[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E003]`

- type: experimental_evidence
- statement: 评估覆盖 7 个光骨干拓扑，并将预处理地震危险数据与真实拓扑匹配，同时包含随机形状灾害。
- locator: {page: 11, section: "Section VI", figure: "Figures 7–11", table: "Table I"}
- supports: [E002]
- confidence: high
- notes: 评估延续至 PDF 第 15 页。

### E004

`[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E004]`

- type: experimental_evidence
- statement: Table I 报告 Italian/VI 为 12106 个 CFP、308 个 FP，NFSNET 为 14199/969，表明预计算规模随拓扑和灾害阈值变化。
- locator: {page: 13, section: "Section VI", figure: null, table: "Table I"}
- supports: [E002]
- confidence: high
- notes: null

### E005

`[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E005]`

- type: experimental_evidence
- statement: 单、双、三链路故障概率区间存在重叠，支持作者关于不能只用故障基数代表风险的判断。
- locator: {page: 14, section: "Section VI", figure: "Figures 9–10", table: null}
- supports: [E001]
- confidence: high
- notes: null

### E006

`[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E006]`

- type: paper_claim
- statement: 作者提出该模型可用于路径存活、节点断连和资源集合联合失效概率查询，并提到可服务于满足 SLA 的 VM placement。
- locator: {page: 15, section: "Sections VI–VII", figure: null, table: null}
- supports: [E002]
- confidence: high
- notes: null

### E007

`[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E007]`

- type: author_limitation
- statement: 用意大利地震目录得到的关系式扩展到欧洲范围只是 first approximation，并依赖灾害强度与距离关系等模型假设。
- locator: {page: 12, section: "Section VI-A", figure: null, table: null}
- supports: []
- confidence: high
- notes: null

### E008

`[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E008]`

- type: model_inference
- statement: PSRLG 可提供区域故障风险，但把该风险转化为面向大模型训练的算力—光网络联合动作仍需额外模型。
- locator: {page: 15, section: "Section VII", figure: null, table: null}
- supports: [E002, E006]
- confidence: medium
- notes: 不是作者的 novelty 声明。

## Model Inference

见 E008。

## Research Inspiration

该工作为“区域相关故障是否值得区别于单点故障”提供概率建模依据；下一步应检查现有算网联合工作是否已经使用此类风险，而不能仅凭当前 corpus 宣称空白。[@doi-1915b7050a926a547d48ce40f328a1037a59347ca6c1f0e41e9e5e2cc708c250#E008]
