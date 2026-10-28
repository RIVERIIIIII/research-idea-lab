---
schema_version: "1.0"
note_sequence: "023"
paper_id: "doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d"
title: "A Survey on OFDM-Based Elastic Core Optical Networking"
source_url: "https://doi.org/10.1109/surv.2012.010912.00123"
pdf_url: "https://biblio.ugent.be/publication/4196669/file/4196727.pdf"
input_coverage: "partial_text"
evidence_level: "partial_text"
created_at: "2026-10-09T13:08:33.891629+00:00"
updated_at: "2026-10-09T13:08:33.891629+00:00"
---

# 论文阅读卡：A Survey on OFDM-Based Elastic Core Optical Networking

## Input Coverage

- evidence_level：partial_text
- 输入边界：作者公开的 2011 年 11 月带审稿批注草稿，PDF pp.30–33（印刷 pp.27–30）；不是出版社最终版本，不沿用数值结果。

## Metadata

- paper_id：`doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d`
- authors：Guoying Zhang; Marc De Leenheer; Annalisa Morea; Biswanath Mukherjee
- year / venue：2012 / IEEE Communications Surveys & Tutorials
- DOI：10.1109/surv.2012.010912.00123
- arXiv：未提供
- source URL：https://doi.org/10.1109/surv.2012.010912.00123

## Research Question

弹性光网中路由、频谱与调制受哪些共同约束？

## Motivation

理解经典机制依赖的条件，为后续任务特性研究提供比较基础。

## Method

RSA 需要沿路频谱一致、每连接频槽连续、不同连接不重叠，并计入相邻光信道保护带；空闲频谱碎片可能难以利用。 [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E001]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 经典问题与原有决策 | RSA 需要沿路频谱一致、每连接频槽连续、不同连接不重叠，并计入相邻光信道保护带；空闲频谱碎片可能难以利用。 | [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E001] |
| 条件与边界 | 距离自适应 RSA 联合选择调制与频宽；长路径可使用更低阶调制和更宽频谱，光程及跨越节点、滤波等限制可达性。 | [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E002] |
| 条件与边界 | 静态 RSA 使用预先给定的需求矩阵离线分配；该草稿介绍的简化可达性示例忽略非线性，不宜代替完整 QoT 模型。 | [@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E003] |
| 场景特性 | 本轮不提取训练/推理特性 | — |
| 收益与成本 | 仅记录来源支持的资源权衡，未复核数值与任务收益 | — |

## Experimental Setup

本轮未复核实验设置、baseline 或数值；不填推测。

## Key Findings

见上述有定位的机制条目。

## Limitations

输入与版本边界见 Input Coverage；模型条件不自动构成研究缺口。

## Evidence Items

### E001

[@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E001]

- type: paper_claim
- statement: RSA 需要沿路频谱一致、每连接频槽连续、不同连接不重叠，并计入相邻光信道保护带；空闲频谱碎片可能难以利用。
- locator: {"page": 30, "section": "4.3.2.2", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 作者公开的 2011 年 11 月带审稿批注草稿，PDF pp.30–33（印刷 pp.27–30）；不是出版社最终版本，不沿用数值结果。

### E002

[@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E002]

- type: paper_claim
- statement: 距离自适应 RSA 联合选择调制与频宽；长路径可使用更低阶调制和更宽频谱，光程及跨越节点、滤波等限制可达性。
- locator: {"page": 32, "section": "4.3.2.2.4; PDF pp.32–33", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 作者公开的 2011 年 11 月带审稿批注草稿，PDF pp.30–33（印刷 pp.27–30）；不是出版社最终版本，不沿用数值结果。

### E003

[@doi-b4c7f54ab60d4863993ed1f59a288c4a2dea2c8ab42d0a310a8aadd2938e0d3d#E003]

- type: paper_claim
- statement: 静态 RSA 使用预先给定的需求矩阵离线分配；该草稿介绍的简化可达性示例忽略非线性，不宜代替完整 QoT 模型。
- locator: {"page": 33, "section": "4.3.2.2.1; 4.3.2.2.4", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 作者公开的 2011 年 11 月带审稿批注草稿，PDF pp.30–33（印刷 pp.27–30）；不是出版社最终版本，不沿用数值结果。

## Model Inference

本轮不引入任务侧推断。

## Research Inspiration

仅纳入经典机制表，不生成候选或创新性结论。

## Reading Priority

- 标签：值得精读
- 理由：补足本阶段机制条件；未核验部分留待正文阅读。
