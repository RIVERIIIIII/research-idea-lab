---
schema_version: "1.0"
note_sequence: "024"
paper_id: "doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142"
title: "Routing and Spectrum Assignment for Dual Failure Path Protected Elastic Optical Networks"
source_url: "https://doi.org/10.1109/access.2016.2599511"
pdf_url: null
input_coverage: "partial_text"
evidence_level: "partial_text"
created_at: "2026-10-09T13:08:33.891629+00:00"
updated_at: "2026-10-09T13:08:33.891629+00:00"
---

# 论文阅读卡：Routing and Spectrum Assignment for Dual Failure Path Protected Elastic Optical Networks

## Input Coverage

- evidence_level：partial_text
- 输入边界：已核验用户提供 PDF 的题名、作者与 DOI；重点读取 §III–IV.A（PDF pp.3–7，期刊 pp.5145–5149），并目视核验 p.5147 的共享公式否定横线。未逐项核验后续 ILP、启发式及实验数值。

## Metadata

- paper_id：`doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142`
- authors：Hong Guo; Gangxiang Shen; Sanjay Kumar Bose
- year / venue：2016 / IEEE Access
- DOI：10.1109/access.2016.2599511
- arXiv：未提供
- source URL：https://doi.org/10.1109/access.2016.2599511

## Research Question

双故障保护如何影响备份资源共享与 RSA？

## Motivation

理解经典机制依赖的条件，为后续任务特性研究提供比较基础。

## Method

论文研究双故障保护 EON 的 RSA，并区分 dedicated/mixed 1:1:1、1+1:1 和 1+1+1 的资源共享能力。 [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E001]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 经典问题与原有决策 | 论文研究双故障保护 EON 的 RSA，并区分 dedicated/mixed 1:1:1、1+1:1 和 1+1+1 的资源共享能力。 | [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E001] |
| 条件与边界 | 三条光路链路不相交；共享按式(1)–(4)检查双故障下的争用兼容。 | [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E002] |
| 场景特性 | 本轮不提取训练/推理特性 | — |
| 收益与成本 | 扩大可共享备份类别以增加资源复用空间；性能数值与任务收益未复核 | — |

## Experimental Setup

本轮未复核实验设置、baseline 或数值；不填推测。

## Key Findings

每个业务配置一条工作光路与两条预定义保护光路，三者链路不相交，以保障模型中的双链路故障；这不自动覆盖节点故障或任意规模 SRLG。 [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E003]

1+1:1 的第一保护资源专用、第二保护可共享；dedicated 1:1:1 允许第一保护之间及第二保护之间共享，但不允许跨类别共享；mixed 1:1:1 进一步允许第一与第二保护之间共享。此处 dedicated 不表示所有备份均独占。 [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E004]

共享判据依赖两业务其余两条路径的交叠关系。以两个第二保护路径共享为例，须同时排除“两个工作路径相交且两个第一保护路径相交”及“各工作路径与另一业务第一保护路径交叉相交”两类组合；第一保护及跨类别共享依同理检查式(2)–(4)。 [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E005]

## Limitations

输入与版本边界见 Input Coverage；模型条件不自动构成研究缺口。

## Evidence Items

### E001

[@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E001]

- type: paper_claim
- statement: 论文研究双故障保护 EON 的 RSA，并区分 dedicated/mixed 1:1:1、1+1:1 和 1+1+1 的资源共享能力。
- locator: {"page": null, "section": "Abstract", "figure": null, "table": null}
- supports: []
- confidence: medium
- notes: 仅 OpenAlex 返回的摘要；未取得正文，不推导具体共享判据、实验参数或数值。

### E002

[@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E002]

- type: paper_claim
- statement: 摘要报告使用 ILP 和 spectrum window plane 启发式，目标包括最大使用频槽数；具体共享规则与可行条件尚未核验。
- locator: {"page": null, "section": "Abstract", "figure": null, "table": null}
- supports: []
- confidence: medium
- notes: 仅 OpenAlex 返回的摘要；未取得正文，不推导具体共享判据、实验参数或数值。

### E003

[@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E003]

- type: paper_claim
- statement: 每个业务配置一条工作光路与两条预定义保护光路，三者链路不相交，以保障模型中的双链路故障。
- locator: {"page": 5146, "section": "III", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码为期刊印刷页；共享公式中的否定横线经 PDF 图像核验，未沿用纯文本丢失横线后的表达。

### E004

[@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E004]

- type: paper_claim
- statement: 1+1:1 的第一保护资源专用、第二保护可共享；dedicated 1:1:1 允许第一保护之间及第二保护之间共享，但不允许跨类别共享；mixed 1:1:1 进一步允许第一与第二保护之间共享。此处 dedicated 不表示所有备份均独占。
- locator: {"page": 5147, "section": "III.A–C; pp.5144,5146–5147", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码为期刊印刷页；共享公式中的否定横线经 PDF 图像核验，未沿用纯文本丢失横线后的表达。

### E005

[@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E005]

- type: paper_claim
- statement: 共享判据依赖两业务其余两条路径的交叠关系。以两个第二保护路径共享为例，须同时排除“两个工作路径相交且两个第一保护路径相交”及“各工作路径与另一业务第一保护路径交叉相交”两类组合；第一保护及跨类别共享依同理检查式(2)–(4)。
- locator: {"page": 5147, "section": "III.A–C; equations (1)–(4), pp.5146–5147", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码为期刊印刷页；共享公式中的否定横线经 PDF 图像核验，未沿用纯文本丢失横线后的表达。

### E006

[@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E006]

- type: paper_claim
- statement: 模型给定静态需求、双向光纤链路及 BPSK/QPSK/8-QAM；假设收发器完全可调，每条光路频槽连续，在无频谱转换节点时沿路频谱一致。主备可分配不同频槽与不同调制。
- locator: {"page": 5148, "section": "IV.A", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码为期刊印刷页；共享公式中的否定横线经 PDF 图像核验，未沿用纯文本丢失横线后的表达。

### E007

[@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E007]

- type: paper_claim
- statement: 按路径长度选择调制及频槽数以承载相同需求速率；优化网络最大使用频槽数，联合决定三条光路、频谱及共享关系。
- locator: {"page": 5149, "section": "IV.A.3–4", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码为期刊印刷页；共享公式中的否定横线经 PDF 图像核验，未沿用纯文本丢失横线后的表达。

## Model Inference

适用性提示：三条链路不相交不自动覆盖节点故障或任意规模 SRLG；距离可达模型也不等同完整故障态 QoT 验证。此为模型边界解释，依据 [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E003] [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E006] [@doi-2b0e890a041c91c2eab4f73380d6bb48b71480134536a1e8e8a038c4e969c142#E007]，不构成研究 gap。

## Research Inspiration

仅纳入经典机制表，不生成候选或创新性结论。

## Reading Priority

- 标签：值得精读
- 理由：补足本阶段机制条件；未核验部分留待正文阅读。
