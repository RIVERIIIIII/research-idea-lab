---
schema_version: "1.0"
note_sequence: "027"
paper_id: "doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102"
title: "Llumnix: Dynamic Scheduling for Large Language Model Serving"
source_url: "http://arxiv.org/abs/2406.03243"
pdf_url: "https://arxiv.org/pdf/2406.03243"
input_coverage: "partial_text"
evidence_level: "partial_text"
created_at: "2026-10-09T13:20:05.373542+00:00"
updated_at: "2026-10-09T13:20:05.373542+00:00"
---

# 论文阅读卡：Llumnix: Dynamic Scheduling for Large Language Model Serving

## Input Coverage

- evidence_level：partial_text
- 输入边界：公开作者版 arXiv:2406.03243v1，2024-06-05，PDF pp.1–2；仅核验引言/背景中的任务特性与控制描述，未逐项核验全部算法和实验。另已补读 PDF pp.5–6 §4.2，具体证据见 E004–E006。

## Metadata

- paper_id：`doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102`
- authors：Biao Sun; Ziming Huang; Hanyu Zhao; Wencong Xiao; Xinyi Zhang; Yong Li; Wei Ting Lin
- year / venue：2024 / arXiv (Cornell University)
- DOI：10.48550/arxiv.2406.03243
- 阅读版本：arXiv:2406.03243v1，2024-06-05；元数据年份与实际阅读版本分别保留。

## Research Question

哪些任务特性可被调度使用，依赖什么部署与控制条件？

## Motivation

为第二阶段任务特性表提供有边界证据，不预设光层机制。

## Method

Llumnix 在模型实例间重新调度运行中请求，迁移请求及 GPU 内存状态；迁移机制通过协调计算与状态传输减少停顿。 [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E002]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 任务规律 | 输入/输出长度与延迟要求具有异质性，最终生成 token 数事先未知；生成过程中 GPU 内存需求增长，执行时长与资源需求不能简单视为已知。 | [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E001] |
| 控制与边界 | Llumnix 在模型实例间重新调度运行中请求，迁移请求及 GPU 内存状态；迁移机制通过协调计算与状态传输减少停顿。 | [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E002] |
| 控制与边界 | 系统目标包含负载均衡、碎片整理、优先级和扩缩容；本文引言报告 16-GPU 集群评估，不构成跨地域故障恢复有效性的直接证据。 | [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E003] |
| 信息与控制成本 | 定量成本、预测误差、所需遥测接口尚未核验；不视为免费控制 | — |
| 光层决策 | 本文片段不提供光层保护/恢复机制 | — |

## Experimental Setup

未逐项核验 workload、baseline、拓扑与数值收益。

## Key Findings

迁移利用 KV cache 只追加、既有 token 状态不再改变的特性，将旧块复制与新 token 计算重叠；逐阶段复制新增块，最后暂停请求并复制末尾块。 [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E004]

作者所述低停顿依赖复制通常快于计算、增量块可很快追赶；总复制时长依赖序列长度，停顿主要为最终块复制时段。 [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E005]

每阶段源端请求目标端预分配显存块；显存不足则中止清理，请求结束/被抢占或对端失败也触发中止，最终释放源端块并通知目标端提交恢复。 [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E006]

输入/输出长度与延迟要求具有异质性，最终生成 token 数事先未知；生成过程中 GPU 内存需求增长，执行时长与资源需求不能简单视为已知。 [@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E001]

## Limitations

跨地域可迁移性须单独核验；部署范围和信息假设不自动视为作者缺陷。

## Evidence Items

### E001

[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E001]

- type: paper_claim
- statement: 输入/输出长度与延迟要求具有异质性，最终生成 token 数事先未知；生成过程中 GPU 内存需求增长，执行时长与资源需求不能简单视为已知。
- locator: {"page": 1, "section": "Introduction / Background", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码按当前作者版 PDF；其中跨地域适用性提醒是阅读范围限制，不是额外实验结论。

### E002

[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E002]

- type: paper_claim
- statement: Llumnix 在模型实例间重新调度运行中请求，迁移请求及 GPU 内存状态；迁移机制通过协调计算与状态传输减少停顿。
- locator: {"page": 2, "section": "Introduction / Background", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码按当前作者版 PDF；其中跨地域适用性提醒是阅读范围限制，不是额外实验结论。

### E003

[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E003]

- type: paper_claim
- statement: 系统目标包含负载均衡、碎片整理、优先级和扩缩容；本文引言报告 16-GPU 集群评估，不构成跨地域故障恢复有效性的直接证据。
- locator: {"page": 2, "section": "Introduction / Background", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码按当前作者版 PDF；其中跨地域适用性提醒是阅读范围限制，不是额外实验结论。

### E004

[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E004]

- type: paper_claim
- statement: 迁移利用 KV cache 只追加、既有 token 状态不再改变的特性，将旧块复制与新 token 计算重叠；逐阶段复制新增块，最后暂停请求并复制末尾块。
- locator: {"page": 5, "section": "4.2", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 按当前已注明版本的 PDF 页码；这是机制与条件核验，未独立复现实验。

### E005

[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E005]

- type: paper_claim
- statement: 作者所述低停顿依赖复制通常快于计算、增量块可很快追赶；总复制时长依赖序列长度，停顿主要为最终块复制时段。
- locator: {"page": 5, "section": "4.2; pp.5–6", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 按当前已注明版本的 PDF 页码；这是机制与条件核验，未独立复现实验。

### E006

[@doi-a1478aad65f6807e61c250d70ac98ee8e7d5553781dc37f12b9738a71833e102#E006]

- type: paper_claim
- statement: 每阶段源端请求目标端预分配显存块；显存不足则中止清理，请求结束/被抢占或对端失败也触发中止，最终释放源端块并通知目标端提交恢复。
- locator: {"page": 6, "section": "4.2; Fig.7", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 按当前已注明版本的 PDF 页码；这是机制与条件核验，未独立复现实验。

## Model Inference

本轮不将可观测规律等同任意可控能力，不生成光层机制。

## Research Inspiration

留待任务特性表证据补齐后交叉分析。

## Reading Priority

- 标签：值得精读
- 理由：补任务时序、服务指标及状态控制的条件和成本。
