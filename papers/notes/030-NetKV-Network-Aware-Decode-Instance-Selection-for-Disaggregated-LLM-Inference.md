---
schema_version: "1.0"
note_sequence: "030"
paper_id: "doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29"
title: "NetKV: Network-Aware Decode Instance Selection for Disaggregated LLM Inference"
source_url: "https://arxiv.org/abs/2606.03910"
pdf_url: "https://arxiv.org/pdf/2606.03910"
input_coverage: "partial_text"
evidence_level: "partial_text"
---

# 论文阅读卡：NetKV: Network-Aware Decode Instance Selection for Disaggregated LLM Inference

## Input Coverage

- evidence_level：partial_text
- 版本：arXiv:2606.03910v1（2026-06-02），PDF pp.1–4；仿真结果、证明和 related work 的排他性声明未独立核验。预印本，不视为经复现的性能证据。

## Metadata

- paper_id：`doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29`
- authors：Mubarak Adetunji Ojewale
- year / venue：2026 / arXiv (Cornell University)
- DOI：10.48550/arxiv.2606.03910

## Research Question

网络传输成本怎样进入 decode 实例选择？

## Motivation

作为普通网络感知调度的直接替代与反证，核查阶段信息加网络代价是否已有表达。

## Method

NetKV 将 decode 实例选择建模为在线请求调度，考虑计算负载、前缀缓存命中与网络传输成本，使用网络 cost oracle 提供信号。 [@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E001]

## Mechanism Decomposition

| 维度 | 内容 | 证据 |
|---|---|---|
| 网络感知决策及边界 | NetKV 将 decode 实例选择建模为在线请求调度，考虑计算负载、前缀缓存命中与网络传输成本，使用网络 cost oracle 提供信号。 | [@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E001] |
| 网络感知决策及边界 | 其传输模型按有效 KV 数据量、有效带宽与分层延迟计算；有效带宽考虑背景拥塞及在途 KV 流竞争，不联合分配波长、连续频槽或调制。 | [@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E002] |
| 网络感知决策及边界 | 网络 cost oracle 将拓扑距离抽象为 locality tier，并配合带宽与拥塞估计；论文明确跨高层网络的拥塞聚合及 ECMP 存在近似。 | [@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E003] |

## Experimental Setup

摘要报告数据中心仿真；本轮未核验具体配置或收益。

## Key Findings

计算负载、缓存与网络传输成本的联合选择已是一个现有问题表述，不能仅靠增加这几项声称新机制。[@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E001]

## Limitations

本轮仅核验论文自身模型；未核验其对其他系统的排他性判断。通用网络抽象是否能充分表示光层故障，是当前研究需单独回答的问题。

## Evidence Items

### E001

[@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E001]

- type: paper_claim
- statement: NetKV 将 decode 实例选择建模为在线请求调度，考虑计算负载、前缀缓存命中与网络传输成本，使用网络 cost oracle 提供信号。
- locator: {"page": 1, "section": "I; pp.1–2", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 当前预印本的模型描述，非独立验证；关于未联合光变量仅指已读模型。

### E002

[@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E002]

- type: paper_claim
- statement: 其传输模型按有效 KV 数据量、有效带宽与分层延迟计算；有效带宽考虑背景拥塞及在途 KV 流竞争，不联合分配波长、连续频槽或调制。
- locator: {"page": 3, "section": "III; equations (3)–(4)", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 当前预印本的模型描述，非独立验证；关于未联合光变量仅指已读模型。

### E003

[@doi-40a6e6a6631c624764ffeb27e308e16447a0fd4ecc7c15565443605c866f7e29#E003]

- type: paper_claim
- statement: 网络 cost oracle 将拓扑距离抽象为 locality tier，并配合带宽与拥塞估计；论文明确跨高层网络的拥塞聚合及 ECMP 存在近似。
- locator: {"page": 4, "section": "III.D–E; pp.3–4", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: 当前预印本的模型描述，非独立验证；关于未联合光变量仅指已读模型。

## Model Inference

不能把增加网络成本项作为当前方向的独有贡献；光层必要性仍待核验。

## Research Inspiration

作为后续对照方案，不生成候选。

## Reading Priority

- 标签：值得速读
- 理由：直接限制一般网络感知推理调度的贡献边界。
