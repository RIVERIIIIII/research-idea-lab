---
schema_version: "1.0"
note_sequence: "019"
paper_id: "doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64"
title: "A unified framework for shared protection schemes in optical mesh network"
source_url: "https://www.scielo.br/j/pope/a/dLmBhxsGdLGFNDpCwyXn7wH/?lang=en"
pdf_url: "https://www.scielo.br/j/pope/a/dLmBhxsGdLGFNDpCwyXn7wH/?lang=en&format=pdf"
input_coverage: "partial_text"
evidence_level: "partial_text"
created_at: "2026-10-09T12:32:21Z"
updated_at: "2026-10-09T12:32:21Z"
---

# 论文阅读卡：A unified framework for shared protection schemes in optical mesh network

## Input Coverage

- evidence_level：partial_text
- 输入边界：读取 PDF pp.534–535 及出版社正文 §§2.1.2、3；未复核全部列生成公式。
- 本卡为阶段一机制阅读，不声称完成全文精读。

## Metadata

- paper_id：`doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64`
- authors：Caroline Rocha; Brigitte Jaumard
- year / venue：2009 / Pesquisa Operacional
- DOI：10.1590/s0101-74382009000300004
- arXiv：不适用
- source：[原始来源](https://www.scielo.br/j/pope/a/dLmBhxsGdLGFNDpCwyXn7wH/?lang=en)

## Research Question

预连接结构对共享保护的容量成本有什么约束？

## Motivation

预连接结构对共享保护的容量成本有什么约束？ 对应的机制条件需要单独理解；不预设 AI 任务改进方案。

## Method

统一比较共享链路、共享路径、p-cycle 与 FIPP，采用列生成与整数规划。 [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E001]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 问题与原有决策 | 统一比较共享链路、共享路径、p-cycle 与 FIPP，采用列生成与整数规划。 | [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E001] |
| 成立条件及边界 | 工作路由预先给定，单链路故障；恢复流量允许按整数信道拆分。 | [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E002] |
| 任务特性 | 不适用；本轮不研究大模型任务 | — |
| 实际改变的决策 | 见下方证据项；不补造新机制 | [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E001] [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E002] |
| 收益与成本 | 阅读者边界判断：循环结构约束可能增加备用成本；不能把论文中的可拆分容量模型直接等同不可拆分单光路。；不作为额外实测结论 | [@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E004] |

## Experimental Setup

§3 比较四个网络实例的保护成本；未将二手速度描述作为本论文时延实测。

## Key Findings

本卡的可引用发现逐项列于 Evidence Items；未核验数值不转写为结论。

## Limitations

输入边界见上。条件失配是需检查的适用边界，不自动构成作者方法缺陷或研究 gap。

## Evidence Items

### E001

[@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E001]

- type: paper_claim
- statement: 模型固定工作路由，并允许恢复时按整数信道拆分需求。
- locator:
  - page: 535
  - section: "2. Mathematical Models"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E002

[@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E002]

- type: paper_claim
- statement: p-cycle 预连接，故障后仅故障端点切换，并保护环上与跨接链路。
- locator:
  - page: null
  - section: "2.1.2 p-Cycle Model"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E003

[@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E003]

- type: experimental_evidence
- statement: §3 的计算比较中 p-cycle/FIPP 比相应基本共享方案需要更多备用成本，差异依赖拓扑。
- locator:
  - page: null
  - section: "3. Computational Results"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E004

[@doi-85146ea788146e7a6b6f23c953aac77952b3b69f4a144d109da5ff2cdf9aed64#E004]

- type: model_inference
- statement: 阅读者适用性提示：循环结构约束可能增加备用成本；不能把论文中的可拆分容量模型直接等同不可拆分单光路。
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
