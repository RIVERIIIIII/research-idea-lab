---
schema_version: "1.0"
note_sequence: "021"
paper_id: "doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921"
title: "Robust QoT Assured Resource Allocation in Shared Backup Path Protection Based EONs"
source_url: "https://arxiv.org/abs/2201.05270"
pdf_url: "https://arxiv.org/pdf/2201.05270"
input_coverage: "partial_text"
evidence_level: "partial_text"
created_at: "2026-10-09T12:32:21Z"
updated_at: "2026-10-09T12:32:21Z"
---

# 论文阅读卡：Robust QoT Assured Resource Allocation in Shared Backup Path Protection Based EONs

## Input Coverage

- evidence_level：partial_text
- 输入边界：只读取 arXiv v1 的 §§1、3、8 及 §7.1 片段；未核验完整 MILP/全部实验，也未阅读 IEEE Access 期刊版本。
- 本卡为阶段一机制阅读，不声称完成全文精读。

## Metadata

- paper_id：`doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921`
- authors：Venkatesh Chebolu; Sadananda Behera; Goutam Das
- year / venue：2022 / arXiv (Cornell University)
- DOI：10.48550/arxiv.2201.05270
- arXiv：2201.05270
- source：[原始来源](https://arxiv.org/abs/2201.05270)

## Research Question

主备切换改变活跃光路集合时，如何保障故障状态的 QoT？

## Motivation

主备切换改变活跃光路集合时，如何保障故障状态的 QoT？ 对应的机制条件需要单独理解；不预设 AI 任务改进方案。

## Method

对单链路/SRLG 故障情形考虑最坏干扰，进行鲁棒 RSA。 [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 问题与原有决策 | 对单链路/SRLG 故障情形考虑最坏干扰，进行鲁棒 RSA。 | [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001] |
| 成立条件及边界 | 结论受故障集合、节点结构及物理损伤模型约束；主要处理带内串扰、ASE 和拍频噪声。 | [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E002] |
| 任务特性 | 不适用；本轮不研究大模型任务 | — |
| 实际改变的决策 | 见下方证据项；不补造新机制 | [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001] [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E002] |
| 收益与成本 | 阅读者边界判断：更严格 QoT 保障可能牺牲共享程度、频谱和阻塞性能。；不作为额外实测结论 | [@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E004] |

## Experimental Setup

§7.1 包含 6 节点 MILP/启发式比较和 14 节点启发式分析；本卡不复述百分比。

## Key Findings

本卡的可引用发现逐项列于 Evidence Items；未核验数值不转写为结论。

## Limitations

输入边界见上。条件失配是需检查的适用边界，不自动构成作者方法缺陷或研究 gap。

## Evidence Items

### E001

[@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E001]

- type: paper_claim
- statement: 故障激活不同备份，改变活跃光路集合及干扰；正常状态 QoT 不足以替代故障状态校验。
- locator:
  - page: 3
  - section: "1. Introduction"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E002

[@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E002]

- type: paper_claim
- statement: 论文用最坏故障状态干扰开展鲁棒 RSA，主要建模带内串扰、ASE 和拍频噪声。
- locator:
  - page: 6
  - section: "1; 3 (PDF pp.3,6)"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E003

[@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E003]

- type: paper_claim
- statement: 结论指出其 QoT 保障伴随 BBP、shareability 和频谱用量方面的折中。
- locator:
  - page: 41
  - section: "8. Conclusion (PDF pp.41–42)"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E004

[@doi-73123ce06b0b578da0559aaaad9ae243e94d2b792c9f67340a10ff6c1b7bb921#E004]

- type: model_inference
- statement: 阅读者适用性提示：更严格 QoT 保障可能牺牲共享程度、频谱和阻塞性能。
- locator:
  - page: null
  - section: null
  - figure: null
  - table: null
- supports: [E001, E002]
- confidence: medium
- notes: 条件性解释，不是额外实验结论；待全文核验项不作肯定证据。

## Model Inference

表中成本与适用性提示为阅读者解释，不外推绝对性能排序，不作为新候选的证据。

## Research Inspiration

本阶段仅提取经典机制；任务交叉分析留待后续阶段。

## Reading Priority

- 标签：值得精读
- 理由：补足对应机制的模型条件；当前为有边界的机制阅读。
