---
schema_version: "1.0"
note_sequence: "022"
paper_id: "doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693"
title: "Path-protection routing and wavelength assignment (RWA) in WDM mesh networks under duct-layer constraints"
source_url: "https://doi.org/10.1109/tnet.2003.810313"
pdf_url: "https://sites.pitt.edu/~dtipper/3955/Optical_SRLG.pdf"
input_coverage: "partial_text"
evidence_level: "partial_text"
created_at: "2026-10-09T12:32:21Z"
updated_at: "2026-10-09T12:32:21Z"
---

# 论文阅读卡：Path-protection routing and wavelength assignment (RWA) in WDM mesh networks under duct-layer constraints

## Input Coverage

- evidence_level：partial_text
- 输入边界：读取 PDF pp.248–250 的引言、管道层约束与模型引入；未逐项核验完整算法与实验。
- 本卡为阶段一机制阅读，不声称完成全文精读。

## Metadata

- paper_id：`doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693`
- authors：Hui Zang; Canhui Sam Ou; B. Mukherjee
- year / venue：2003 / IEEE/ACM Transactions on Networking
- DOI：10.1109/tnet.2003.810313
- arXiv：不适用
- source：[原始来源](https://doi.org/10.1109/tnet.2003.810313)

## Research Question

物理共因故障如何改变主备路由与备份共享？

## Motivation

物理共因故障如何改变主备路由与备份共享？ 对应的机制条件需要单独理解；不预设 AI 任务改进方案。

## Method

将管道层约束引入路径保护 RWA，而非只检查逻辑链路不相交。 [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 问题与原有决策 | 将管道层约束引入路径保护 RWA，而非只检查逻辑链路不相交。 | [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001] |
| 成立条件及边界 | 静态需求、无波长转换、单管道故障；一般 SRLG 启发式需可得图表示。 | [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E002] |
| 任务特性 | 不适用；本轮不研究大模型任务 | — |
| 实际改变的决策 | 见下方证据项；不补造新机制 | [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001] [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E002] |
| 收益与成本 | 阅读者边界判断：需掌握物理风险映射，且不相交要求减少可行路由和共享机会。；不作为额外实测结论 | [@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E004] |

## Experimental Setup

原文采用 ILP/启发式与数值例子；本卡未复核实验结果。

## Key Findings

本卡的可引用发现逐项列于 Evidence Items；未核验数值不转写为结论。

## Limitations

输入边界见上。条件失配是需检查的适用边界，不自动构成作者方法缺陷或研究 gap。

## Evidence Items

### E001

[@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E001]

- type: paper_claim
- statement: 单管道故障保障要求主备管道不相交；主路径共管道的两请求不能共享备份链路上的同一波长。
- locator:
  - page: 248
  - section: "Abstract; I.A"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E002

[@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E002]

- type: paper_claim
- statement: 管道是 SRLG 的一种；启发式推广需有可用或可推导的 SRLG 图表示。
- locator:
  - page: 249
  - section: "I.A Duct-Layer Constraints"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E003

[@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E003]

- type: paper_claim
- statement: 本文处理静态流量及无波长转换条件下的 RWA；联合 ILP 规模促使采用分解。
- locator:
  - page: 250
  - section: "I.A; I.C; II (pp.249–250)"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E004

[@doi-2a2f6d008bc2e03b8314ba5d2da83f6c84b44aef3d8605a2080f664d2cb81693#E004]

- type: model_inference
- statement: 阅读者适用性提示：需掌握物理风险映射，且不相交要求减少可行路由和共享机会。
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
