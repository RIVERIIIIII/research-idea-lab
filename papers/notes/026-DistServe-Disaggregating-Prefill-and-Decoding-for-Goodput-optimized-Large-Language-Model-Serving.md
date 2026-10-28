---
schema_version: "1.0"
note_sequence: "026"
paper_id: "doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3"
title: "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving"
source_url: "http://arxiv.org/abs/2401.09670"
pdf_url: "https://arxiv.org/pdf/2401.09670"
input_coverage: "partial_text"
evidence_level: "partial_text"
created_at: "2026-10-09T13:20:05.373542+00:00"
updated_at: "2026-10-09T13:20:05.373542+00:00"
---

# 论文阅读卡：DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving

## Input Coverage

- evidence_level：partial_text
- 输入边界：公开作者版 arXiv:2401.09670v3，2024-06-06，PDF pp.1–2；仅核验引言/背景中的任务特性与控制描述，未逐项核验全部算法和实验。另已补读 PDF pp.6–7 §3.3–4，具体证据见 E004–E006。

## Metadata

- paper_id：`doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3`
- authors：Yinmin Zhong; Shengyu Liu; Junda Chen; Hu, Jianbo; Yibo Zhu; Xuanzhe Liu; Xin Jin; Hao Zhang
- year / venue：2024 / arXiv (Cornell University)
- DOI：10.48550/arxiv.2401.09670
- 阅读版本：arXiv:2401.09670v3，2024-06-06；元数据年份与实际阅读版本分别保留。

## Research Question

哪些任务特性可被调度使用，依赖什么部署与控制条件？

## Motivation

为第二阶段任务特性表提供有边界证据，不预设光层机制。

## Method

prefill 与 decode 共置会相互干扰并耦合资源和并行策略；DistServe 将两阶段放在不同 GPU，分别配置资源与并行方式。 [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E002]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 任务规律 | 推理服务需分别考虑 TTFT 与 TPOT，应用的两类延迟要求可以不同；吞吐量不能替代满足 SLO 的请求处理能力。 | [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E001] |
| 控制与边界 | prefill 与 decode 共置会相互干扰并耦合资源和并行策略；DistServe 将两阶段放在不同 GPU，分别配置资源与并行方式。 | [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E002] |
| 控制与边界 | 两阶段分离引入中间状态通信，放置需考虑集群带宽；论文的现代 GPU 集群通信开销判断不自动适用于跨地域 WAN。 | [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E003] |
| 信息与控制成本 | 定量成本、预测误差、所需遥测接口尚未核验；不视为免费控制 | — |
| 光层决策 | 本文片段不提供光层保护/恢复机制 | — |

## Experimental Setup

未逐项核验 workload、baseline、拓扑与数值收益。

## Key Findings

OPT-66B 的 512-token 请求 KV cache 示例约 1.13 GB；10 请求/秒约需 11.3 GB/s，即约 90 Gbps 传输。低跨节点带宽时利用节点内 NVLINK，并将带宽条件纳入放置约束。 [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E004]

放置算法利用历史请求轨迹拟合到达及输入/输出长度分布，重采样驱动模拟器估计 SLO 达标率；作者明确短时间间隔不能精确预测，使用较长时间尺度的负载模式。 [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E005]

资源和并行配置搜索基于 GPU 数量/显存等可行约束及性能模拟；配置控制依赖模型、硬件与负载信息，不能把分布层面的预测等同单请求长度已知。 [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E006]

推理服务需分别考虑 TTFT 与 TPOT，应用的两类延迟要求可以不同；吞吐量不能替代满足 SLO 的请求处理能力。 [@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E001]

## Limitations

跨地域可迁移性须单独核验；部署范围和信息假设不自动视为作者缺陷。

## Evidence Items

### E001

[@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E001]

- type: paper_claim
- statement: 推理服务需分别考虑 TTFT 与 TPOT，应用的两类延迟要求可以不同；吞吐量不能替代满足 SLO 的请求处理能力。
- locator: {"page": 2, "section": "Introduction / Background", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码按当前作者版 PDF；其中跨地域适用性提醒是阅读范围限制，不是额外实验结论。

### E002

[@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E002]

- type: paper_claim
- statement: prefill 与 decode 共置会相互干扰并耦合资源和并行策略；DistServe 将两阶段放在不同 GPU，分别配置资源与并行方式。
- locator: {"page": 2, "section": "Introduction / Background", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码按当前作者版 PDF；其中跨地域适用性提醒是阅读范围限制，不是额外实验结论。

### E003

[@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E003]

- type: paper_claim
- statement: 两阶段分离引入中间状态通信，放置需考虑集群带宽；论文的现代 GPU 集群通信开销判断不自动适用于跨地域 WAN。
- locator: {"page": 2, "section": "Introduction / Background", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 页码按当前作者版 PDF；其中跨地域适用性提醒是阅读范围限制，不是额外实验结论。

### E004

[@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E004]

- type: paper_claim
- statement: OPT-66B 的 512-token 请求 KV cache 示例约 1.13 GB；10 请求/秒约需 11.3 GB/s，即约 90 Gbps 传输。低跨节点带宽时利用节点内 NVLINK，并将带宽条件纳入放置约束。
- locator: {"page": 6, "section": "3.3 Communication overhead", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 按当前已注明版本的 PDF 页码；这是机制与条件核验，未独立复现实验。

### E005

[@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E005]

- type: paper_claim
- statement: 放置算法利用历史请求轨迹拟合到达及输入/输出长度分布，重采样驱动模拟器估计 SLO 达标率；作者明确短时间间隔不能精确预测，使用较长时间尺度的负载模式。
- locator: {"page": 7, "section": "4.1", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 按当前已注明版本的 PDF 页码；这是机制与条件核验，未独立复现实验。

### E006

[@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E006]

- type: paper_claim
- statement: 资源和并行配置搜索基于 GPU 数量/显存等可行约束及性能模拟；配置控制依赖模型、硬件与负载信息，不能把分布层面的预测等同单请求长度已知。
- locator: {"page": 7, "section": "4.1–4.2", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 按当前已注明版本的 PDF 页码；这是机制与条件核验，未独立复现实验。

### E007

[@doi-9e89a0eecd7e32a9403c8e879ddb33febd74868da96839007c7c86a268fba4c3#E007]

- type: paper_claim
- statement: DistServe 的 prefill 实例产生首个输出 token 后，将主要为 KV cache 的中间状态发送到 decode 实例，后者负责后续 decoding steps；阶段分离本身不表示每个后续 token 都持续通过该交接光路通信。
- locator: {page: 3, section: "2 Opportunities", figure: null, table: null}
- supports: []
- confidence: high
- notes: 页码按 arXiv v3；最后的适用边界依照已读执行流程，不覆盖另行跨节点张量/流水线并行的部署。

## Model Inference

本轮不将可观测规律等同任意可控能力，不生成光层机制。

## Research Inspiration

留待任务特性表证据补齐后交叉分析。

## Reading Priority

- 标签：值得精读
- 理由：补任务时序、服务指标及状态控制的条件和成本。
