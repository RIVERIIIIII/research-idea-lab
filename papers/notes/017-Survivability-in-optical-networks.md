---
schema_version: "1.0"
note_sequence: "017"
paper_id: "doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22"
title: "Survivability in optical networks"
source_url: "https://doi.org/10.1109/65.885666"
pdf_url: "https://bpb-us-w2.wpmucdn.com/web.seas.gwu.edu/dist/d/10/files/2019/06/Network-00-Surv.pdf"
input_coverage: "partial_text"
evidence_level: "partial_text"
created_at: "2026-10-09T12:32:21Z"
updated_at: "2026-10-09T12:32:21Z"
---

# 论文阅读卡：Survivability in optical networks

## Input Coverage

- evidence_level：partial_text
- 输入边界：读取作者公开 PDF pp.16–19 的分类、APS、动态恢复与多层协调章节；未逐项审读后半篇。
- 本卡为阶段一机制阅读，不声称完成全文精读。

## Metadata

- paper_id：`doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22`
- authors：Dongyun Zhou; Suresh Subramaniam
- year / venue：2000 / IEEE Network
- DOI：10.1109/65.885666
- arXiv：不适用
- source：[原始来源](https://doi.org/10.1109/65.885666)

## Research Question

保护资源如何配置，恢复由哪一层、何时启动？

## Motivation

保护资源如何配置，恢复由哪一层、何时启动？ 对应的机制条件需要单独理解；不预设 AI 任务改进方案。

## Method

区分预设计保护与动态恢复，以及 1+1、1:1、1:N APS。 [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E001]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 问题与原有决策 | 区分预设计保护与动态恢复，以及 1+1、1:1、1:N APS。 | [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E001] |
| 成立条件及边界 | 备用容量和可用路径是前提；动态恢复受故障后剩余资源限制。 | [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E002] |
| 任务特性 | 不适用；本轮不研究大模型任务 | — |
| 实际改变的决策 | 见下方证据项；不补造新机制 | [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E001] [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E002] |
| 收益与成本 | 阅读者边界判断：预留容量与故障后协调时延存在权衡。；不作为额外实测结论 | [@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E004] |

## Experimental Setup

综述性材料；本卡不抽取实验数值。

## Key Findings

本卡的可引用发现逐项列于 Evidence Items；未核验数值不转写为结论。

## Limitations

输入边界见上。条件失配是需检查的适用边界，不自动构成作者方法缺陷或研究 gap。

## Evidence Items

### E001

[@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E001]

- type: paper_claim
- statement: 1+1 同时发送两路信号并由接收端选择；1:1 故障后切换，备用可承载低优先级流量。
- locator:
  - page: 17
  - section: "Predesigned Protection / APS"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E002

[@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E002]

- type: paper_claim
- statement: 动态恢复故障后寻找资源，可能因备用不足而无法完整恢复。
- locator:
  - page: 18
  - section: "Dynamic Restoration"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E003

[@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E003]

- type: paper_claim
- statement: 多层恢复需协调；bottom-up 使用 holdoff timer 给下层恢复机会。
- locator:
  - page: 19
  - section: "Multilayer Protection in WDM Networks"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: 页码按期刊印刷页；PXT 与 QoT 预印本按 PDF 页序。

### E004

[@doi-77638408a2fdb08ff82b82f37dd43511d5a2f60546ab46a5506fd27d4fca3e22#E004]

- type: model_inference
- statement: 阅读者适用性提示：预留容量与故障后协调时延存在权衡。
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
