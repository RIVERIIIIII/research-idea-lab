---
schema_version: "1.0"
note_sequence: "031"
paper_id: "doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1"
title: "GORGO: Online Tuning for Cross-Region Network-Aware LLM Serving"
source_url: "https://arxiv.org/html/2602.11688v1"
pdf_url: "https://arxiv.org/pdf/2602.11688"
input_coverage: "partial_text"
evidence_level: "partial_text"
---

# 论文阅读卡：GORGO: Online Tuning for Cross-Region Network-Aware LLM Serving

## Input Coverage

- evidence_level：partial_text
- 输入边界：阅读 arXiv:2602.11688v1 HTML §2.3、§3、§4.1、§5 Scope；元数据为当前改题版本，本文只支持 v1，不混用新版结果。未核验完整实验。

## Metadata

- paper_id：`doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1`
- authors：Alessio Ricci Toniolo; Rome Thorstenson; Abinaya Dinesh
- year / venue：2026 / arXiv (Cornell University)
- DOI：10.48550/arxiv.2602.11688
- 本次原始来源：https://arxiv.org/html/2602.11688v1

## Research Question

跨区域请求转发如何权衡缓存、网络延迟与负载？

## Motivation

明确真实通信对象及已有控制动作，避免把缓存感知路由当成状态迁移。

## Method

GORGO v1 在区域副本间转发新请求，选择依据缓存前缀、跨区域 RTT 与队列/准入状态；其控制对象是请求放置。 [@doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1#E001]

## Mechanism Decomposition

| 维度 | 内容与边界 | 证据 |
|---|---|---|
| 控制对象与已覆盖问题 | GORGO v1 在区域副本间转发新请求，选择依据缓存前缀、跨区域 RTT 与队列/准入状态；其控制对象是请求放置。 | [@doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1#E001] |
| 控制对象与已覆盖问题 | 前缀索引仅记录前缀到节点映射，不存放实际 KV 对；Scope 明确架构不需要传输 KV cache 内容。 | [@doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1#E002] |
| 控制对象与已覆盖问题 | v1 报告在 US West、Germany、Israel 三个区域的服务部署，使用 SGLang 和 Mistral-7B；它支持跨地域请求路由场景，不是跨地域 KV 迁移验证。 | [@doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1#E003] |

## Experimental Setup

仅定位到原文部署说明，未复核结果。

## Key Findings

见有定位的条目。

## Limitations

不把请求转发、阶段交接及运行中迁移混为同一机制；本次输入不支持广域光层故障下的可行性保证。

## Evidence Items

### E001

[@doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1#E001]

- type: paper_claim
- statement: GORGO v1 在区域副本间转发新请求，选择依据缓存前缀、跨区域 RTT 与队列/准入状态；其控制对象是请求放置。
- locator: {"page": null, "section": "3.2–3.4", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 阅读 arXiv:2602.11688v1 HTML §2.3、§3、§4.1、§5 Scope；元数据为当前改题版本，本文只支持 v1，不混用新版结果。未核验完整实验。

### E002

[@doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1#E002]

- type: paper_claim
- statement: 前缀索引仅记录前缀到节点映射，不存放实际 KV 对；Scope 明确架构不需要传输 KV cache 内容。
- locator: {"page": null, "section": "3.5 Prefix index; 5 Scope of applicability", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 阅读 arXiv:2602.11688v1 HTML §2.3、§3、§4.1、§5 Scope；元数据为当前改题版本，本文只支持 v1，不混用新版结果。未核验完整实验。

### E003

[@doi-e44731dc3b5862a8437c2152be2bb471a623376d36e71d60e1e3f94084066ce1#E003]

- type: paper_claim
- statement: v1 报告在 US West、Germany、Israel 三个区域的服务部署，使用 SGLang 和 Mistral-7B；它支持跨地域请求路由场景，不是跨地域 KV 迁移验证。
- locator: {"page": null, "section": "4.1 Setup", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 阅读 arXiv:2602.11688v1 HTML §2.3、§3、§4.1、§5 Scope；元数据为当前改题版本，本文只支持 v1，不混用新版结果。未核验完整实验。

## Model Inference

对本研究的比较意义仅为边界检查，不构成新颖性结论。

## Research Inspiration

需先明确本研究的故障模型与剩余差异，再决定是否继续。

## Reading Priority

- 标签：值得精读
- 理由：直接关系场景成立与已有机制覆盖。
