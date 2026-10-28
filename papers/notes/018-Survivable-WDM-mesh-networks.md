---
schema_version: "1.0"
note_sequence: "018"
paper_id: "doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4"
title: "Survivable WDM mesh networks"
source_url: "https://doi.org/10.1109/jlt.2002.806338"
pdf_url: "https://users.encs.concordia.ca/~assi/courses/encs6811/surv3.pdf"
input_coverage: "partial_text"
evidence_level: "partial_text"
created_at: "2026-10-09T12:32:21Z"
updated_at: "2026-10-09T12:32:21Z"
---

# 论文阅读卡：Survivable WDM mesh networks

## Input Coverage

- evidence_level：partial_text
- 输入边界：读取 PDF pp.870–875、878–880 的模型与协议及摘要；未完整复核全部实验表格。
- 本卡为阶段一机制阅读，不声称完成全文精读。

## Metadata

- paper_id：`doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4`
- authors：Sundar Ramamurthy; Laxman H. Sahasrabuddhe; Biswanath Mukherjee
- year / venue：2003 / Journal of Lightwave Technology
- DOI：10.1109/jlt.2002.806338
- arXiv：不适用
- source：[原始来源](https://doi.org/10.1109/jlt.2002.806338)

## Research Question

保护粒度、容量共享和配置时延如何影响资源与恢复？

## Motivation

保护粒度、容量共享和配置时延如何影响资源与恢复？ 对应的机制条件需要单独理解；不预设 AI 任务改进方案。

## Method

比较专用路径、共享路径、共享链路保护，及分布式动态恢复。 [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E001]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 问题与原有决策 | 比较专用路径、共享路径、共享链路保护，及分布式动态恢复。 | [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E001] |
| 成立条件及边界 | 模型给定需求与候选路由，无波长转换、波长连续；协议假定控制网可靠。 | [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E002] |
| 任务特性 | 不适用；本轮不研究大模型任务 | — |
| 实际改变的决策 | 见下方证据项；不补造新机制 | [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E001] [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E002] |
| 收益与成本 | 阅读者边界判断：共享节省容量，但故障后配置与信令仍有代价；不能固定断言某类保护总是最快。；不作为额外实测结论 | [@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E005] |

## Experimental Setup

模型与分布式协议仿真；本卡不复述未逐表核验的收益数值。

## Key Findings

本卡的可引用发现逐项列于 Evidence Items；未核验数值不转写为结论。

## Limitations

输入边界见上。条件失配是需检查的适用边界，不自动构成作者方法缺陷或研究 gap。

## Evidence Items

### E001

[@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E001]

- type: paper_claim
- statement: 专用路径保护在本论文指 1:1；共享备份按不会同时发生的故障情形复用。
- locator:
  - page: 871
  - section: "I. Introduction"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E002

[@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E002]

- type: paper_claim
- statement: 模型保护单链路故障；共享同一备份波长要求对应主路径光纤不相交。
- locator:
  - page: 874
  - section: "II.B / ILP2"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E003

[@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E003]

- type: paper_claim
- statement: 共享保护配置时延会改变方案速度排序；动态恢复协议假定可靠控制网。
- locator:
  - page: 878
  - section: "III.B; IV.A (pp.878–879)"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E004

[@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E004]

- type: model_inference
- statement: 本模型的完全恢复指连接容量恢复，不能直接推出 AI 任务性能恢复。
- locator:
  - page: 873
  - section: "II. Problem Formulation"
  - figure: null
  - table: null
- supports: ["E001", "E002"]
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E005

[@doi-a22d0d255b08b024f83f312ccb3a0e008badf042bdd2ebf2e9cf360ee2a7f9f4#E005]

- type: model_inference
- statement: 阅读者适用性提示：共享节省容量，但故障后配置与信令仍有代价；不能固定断言某类保护总是最快。
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
