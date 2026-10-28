---
schema_version: "1.0"
note_sequence: "028"
paper_id: "doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3"
title: "Bamboo: Making Preemptible Instances Resilient for Affordable Training of Large DNNs"
source_url: "http://arxiv.org/abs/2204.12013"
pdf_url: "https://arxiv.org/pdf/2204.12013"
input_coverage: "partial_text"
evidence_level: "partial_text"
---

# 论文阅读卡：Bamboo: Making Preemptible Instances Resilient for Affordable Training of Large DNNs

## Input Coverage

- evidence_level：partial_text
- 阅读版本：公开 arXiv 作者版 2204.12013；本轮不混用其他版本结果
- 读取范围：PDF pp.2–3、6、9–10。未逐项核验全文算法、附录与数值收益。

## Metadata

- paper_id：`doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3`
- authors：Thorpe, John; Pengzhan Zhao; Jonathan Eyolfson; Yifan Qiao; Jia, Zhihao; Minjia Zhang; Ravi Netravali; Guoqing Harry Xu
- year / venue：2022 / arXiv (Cornell University)
- DOI：10.48550/arxiv.2204.12013

## Research Question

如何利用预置冗余减少节点失效后的训练中断？

## Motivation

补训练状态、恢复动作与正确性条件的代表证据；不预设光层优化。

## Method

每节点保存自身及后继节点的层并执行冗余计算；非相邻节点失效时前驱可接管，连续相邻节点失效超出单邻居冗余覆盖。 [@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E001]

## Mechanism Decomposition

| 维度 | 条件及动作 | 证据 |
|---|---|---|
| 状态、控制与边界 | 每节点保存自身及后继节点的层并执行冗余计算；非相邻节点失效时前驱可接管，连续相邻节点失效超出单邻居冗余覆盖。 | [@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E001] |
| 状态、控制与边界 | 前向冗余计算利用流水线空闲期预先执行；反向冗余计算在失效后按需执行并引入暂停；中间激活与优化器等状态占用内存，可换出 CPU 内存。 | [@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E002] |
| 状态、控制与边界 | 重配置用于重新平衡流水线并恢复后续容错能力，暂停长于冗余接管；系统周期性检查点在严重失效导致训练不能继续时用于重启。 | [@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E003] |
| 状态、控制与边界 | 重配置依赖集群状态和新节点可用性；在优化器步骤末尾检查是否有足够新节点或临近严重失效，必要时暂停训练申请资源。 | [@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E004] |
| 任务与光层关系 | 本轮不外推到跨域光层故障，不构造候选 | — |

## Experimental Setup

数值收益与完整实验配置本轮未复核。

## Key Findings

见机制表与证据项。

## Limitations

节点抢占及 GPU 弹性与光路故障不同；本文机制能否用于网络分区和跨地域环境尚未核验，不把恢复动作视为免费。

## Evidence Items

### E001

[@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E001]

- type: paper_claim
- statement: 每节点保存自身及后继节点的层并执行冗余计算；非相邻节点失效时前驱可接管，连续相邻节点失效超出单邻居冗余覆盖。
- locator: {"page": 2, "section": "Introduction", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: PDF 页码；机制描述不是独立实验验证。

### E002

[@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E002]

- type: paper_claim
- statement: 前向冗余计算利用流水线空闲期预先执行；反向冗余计算在失效后按需执行并引入暂停；中间激活与优化器等状态占用内存，可换出 CPU 内存。
- locator: {"page": 2, "section": "Introduction", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: PDF 页码；机制描述不是独立实验验证。

### E003

[@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E003]

- type: paper_claim
- statement: 重配置用于重新平衡流水线并恢复后续容错能力，暂停长于冗余接管；系统周期性检查点在严重失效导致训练不能继续时用于重启。
- locator: {"page": 10, "section": "6 Pipeline Reconfiguration", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: PDF 页码；机制描述不是独立实验验证。

### E004

[@doi-7fce45b00580a652cff98673b074c10cfea800f51e0249213329a67a4d4061e3#E004]

- type: paper_claim
- statement: 重配置依赖集群状态和新节点可用性；在优化器步骤末尾检查是否有足够新节点或临近严重失效，必要时暂停训练申请资源。
- locator: {"page": 10, "section": "6 Pipeline Reconfiguration", "figure": null, "table": null}
- supports: []
- confidence: high
- notes: PDF 页码；机制描述不是独立实验验证。

## Model Inference

不把节点失效等同光路故障；迁移/重配置和检查点恢复的可用状态须分别判断。

## Research Inspiration

作为任务侧能力及成本边界资料，不生成候选。

## Reading Priority

- 标签：值得精读
- 理由：补恢复条件与训练正确性。
