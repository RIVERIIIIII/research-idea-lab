---
schema_version: "1.0"
note_sequence: "032"
paper_id: "doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226"
title: "Efficient KV Cache Migration for Geo-Distributed LLM Inference in Collaborative Edge Computing"
source_url: "https://ieeexplore.ieee.org/document/11619197/"
pdf_url: null
input_coverage: "partial_text"
evidence_level: "partial_text"
---

# 论文阅读卡：Efficient KV Cache Migration for Geo-Distributed LLM Inference in Collaborative Edge Computing

## Input Coverage

- evidence_level：partial_text
- 输入边界：用户提供 IEEE ICDCS 2026 正式版，题名/作者/DOI 与记录一致；重点核验 PDF pp.1–5、7–8、10（印刷 pp.272–276、278–279、281）的背景、迁移模型及部分设置。未逐行复核 LP 证明、完整性能图或实现，保持 partial_text。

## Metadata

- paper_id：`doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226`
- authors：Mingjin Zhang; Jiannong Cao; Tao Wu; Xiangchun Chen; Ne Wang
- year / venue：2026 / IEEE International Conference on Distributed Computing Systems (ICDCS)
- DOI：10.1109/2575-8411.2026.00033
- 本次原始来源：https://ieeexplore.ieee.org/document/11619197/

## Research Question

地理分布式推理的 KV 状态如何在传输与重计算之间选择？

## Motivation

明确真实通信对象及已有控制动作，避免把缓存感知路由当成状态迁移。

## Method

出版社摘要描述地理分布的异构边缘服务器联合承载模型分片及 KV 状态，在断连或过载风险背景下研究状态迁移以维持服务。 [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E001]

## Mechanism Decomposition

| 维度 | 内容与边界 | 证据 |
|---|---|---|
| 控制对象与已覆盖问题 | 出版社摘要描述地理分布的异构边缘服务器联合承载模型分片及 KV 状态，在断连或过载风险背景下研究状态迁移以维持服务。 | [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E001] |
| 控制对象与已覆盖问题 | EdgeFlow 提出直接 KV 传输与基于 activation 的重计算相结合，利用计算/通信并行降低迁移时间，并研究多节点迁移优化。 | [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E002] |

## Experimental Setup

已核验 §V 的部分设置（E007）；本轮不引用摘要中的最大性能收益，不把设定迁移节点比例视为真实故障实验。

## Key Findings

引言与模型的具体迁移触发为节点过载或计划退出；模型仍从迁移源节点向目标发送 KV 或 activations，未给出源端状态不可访问后的获取协议。 [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E003]

activation-based 重建通过目标端对每层输入 activation 应用 Wk/Wv 投影恢复 KV，因此需要对应 activations 与投影参数可用；不是直接从历史 token 进行完整 prefill。 [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E004]

混合策略决定 act-layers 与 KV-layers 的比例/分界，先传 activations 并让后续传输与目标重计算重叠；在论文的均一层成本假设下将层选择简化为数量/分界点。 [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E005]

多节点模型给定源/目标集合、端点对带宽 Bk,n、目标计算能力及显存预算，联合选择每源的目标节点和分界 Pk，最小化最慢迁移完成时间。已读 P1 不联合选择物理光路、频谱、调制或 QoT。 [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E006]

## Limitations

原文式(1)–(4)按文中激活与 KV 维度写出数据量关系；“activation 为 KV 数据量一半”仅在该模型下使用，实际模型的 KV 头数、精度、分片和张量维度须单独核验，不能普遍外推。[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E004] [@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E008]

不把请求转发、阶段交接及运行中迁移混为同一机制；本次输入不支持广域光层故障下的可行性保证。

## Evidence Items

### E001

[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E001]

- type: paper_claim
- statement: 出版社摘要描述地理分布的异构边缘服务器联合承载模型分片及 KV 状态，在断连或过载风险背景下研究状态迁移以维持服务。
- locator: {"page": null, "section": "Publisher Abstract", "figure": null, "table": null}
- supports: []
- confidence: medium
- notes: 仅出版社 IEEE 摘要；未取得正文，不推导源端失效后的状态获取、具体光层模型或算法细节，不采纳摘要性能数字为独立核验结果。

### E002

[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E002]

- type: paper_claim
- statement: EdgeFlow 提出直接 KV 传输与基于 activation 的重计算相结合，利用计算/通信并行降低迁移时间，并研究多节点迁移优化。
- locator: {"page": null, "section": "Publisher Abstract", "figure": null, "table": null}
- supports: []
- confidence: medium
- notes: 仅出版社 IEEE 摘要；未取得正文，不推导源端失效后的状态获取、具体光层模型或算法细节，不采纳摘要性能数字为独立核验结果。

### E003

[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E003]

- type: paper_claim
- statement: 引言与模型的具体迁移触发为节点过载或计划退出；模型仍从迁移源节点向目标发送 KV 或 activations，未给出源端状态不可访问后的获取协议。
- locator: {"page": 272, "section": "I; III.B pp.275–276", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 正文事实仅指已读模型；未显式建模不等于现实不存在，也不能作为全领域空白证据。

### E004

[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E004]

- type: paper_claim
- statement: activation-based 重建通过目标端对每层输入 activation 应用 Wk/Wv 投影恢复 KV，因此需要对应 activations 与投影参数可用；不是直接从历史 token 进行完整 prefill。
- locator: {"page": 274, "section": "II.B; equations (2)–(4)", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 正文事实仅指已读模型；未显式建模不等于现实不存在，也不能作为全领域空白证据。

### E005

[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E005]

- type: paper_claim
- statement: 混合策略决定 act-layers 与 KV-layers 的比例/分界，先传 activations 并让后续传输与目标重计算重叠；在论文的均一层成本假设下将层选择简化为数量/分界点。
- locator: {"page": 275, "section": "III.A; Theorems 1–2", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 正文事实仅指已读模型；未显式建模不等于现实不存在，也不能作为全领域空白证据。

### E006

[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E006]

- type: paper_claim
- statement: 多节点模型给定源/目标集合、端点对带宽 Bk,n、目标计算能力及显存预算，联合选择每源的目标节点和分界 Pk，最小化最慢迁移完成时间。已读 P1 不联合选择物理光路、频谱、调制或 QoT。
- locator: {"page": 276, "section": "III.B; equations (6)–(14)", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 正文事实仅指已读模型；未显式建模不等于现实不存在，也不能作为全领域空白证据。

### E007

[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E007]

- type: paper_claim
- statement: 实现收集节点可用性、节点间带宽、GPU 类型/利用率/显存及模型配置；实验采用 PolyLink 平台、llama-box 与异构 GPU，设置带宽和待迁移节点比例，不等于测量真实光纤故障恢复。
- locator: {"page": 278, "section": "III workflow p.274; V.A–B pp.278–279", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 正文事实仅指已读模型；未显式建模不等于现实不存在，也不能作为全领域空白证据。

### E008

[@doi-343e35e7b4b90a450f7a36bcfd0bcd4ee9f5c63bab90dee0ebd378cf14047226#E008]

- type: unverified
- statement: 尚未核验：各历史 token、各迁移层的 activation 如何保存/获取及其持续内存成本，迁移期间是否暂停生成及如何保证状态一致，模型参数部署时间、真实 KV 维度与式(1)–(4)的适配、共享路径竞争/握手/光路配置代价。
- locator: {"page": null, "section": "II.B–III; implementation details pending", "figure": null, "table": null}
- supports: []
- confidence: low
- notes: 正文事实仅指已读模型；未显式建模不等于现实不存在，也不能作为全领域空白证据。

## Model Inference

对本研究的比较意义仅为边界检查，不构成新颖性结论。

## Research Inspiration

需先明确本研究的故障模型与剩余差异，再决定是否继续。

## Reading Priority

- 标签：值得精读
- 理由：直接关系场景成立与已有机制覆盖。
