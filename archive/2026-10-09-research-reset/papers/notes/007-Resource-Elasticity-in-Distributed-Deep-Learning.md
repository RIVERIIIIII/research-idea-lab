---
schema_version: "1.0"
note_sequence: "007"
paper_id: "openalex-w3037519745"
title: "Resource Elasticity in Distributed Deep Learning"
source_url: "https://proceedings.mlsys.org/paper/2020/file/006f52e9102a8d3be2fe5614f42ba989-Paper.pdf"
pdf_url: null
input_coverage: "metadata_only"
evidence_level: "metadata_only"
created_at: "2026-10-04T10:00:00Z"
updated_at: "2026-10-04T10:00:00Z"
---

# 论文精读卡：Resource Elasticity in Distributed Deep Learning

## Input Coverage

- evidence_level：`metadata_only`
- 输入范围：仅使用 `selected.jsonl` 的标题、作者、年份、venue 和来源 URL；记录中没有摘要，PDF 尚未通过现有下载流程入缓存。
- 边界：不能从标题推断具体方法、实验或结论。本卡仅保留待核实入口，不作为肯定证据。

## Metadata

- paper_id：`openalex-w3037519745`
- authors：Andrew Or；Haoyu Zhang；Michael J. Freedman
- year：2020
- venue：Proceedings of Machine Learning and Systems
- DOI：未提供
- arXiv：未提供
- source URL：https://proceedings.mlsys.org/paper/2020/file/006f52e9102a8d3be2fe5614f42ba989-Paper.pdf

## Research Question

待全文核实。标题表明主题涉及分布式深度学习的资源弹性，但不能据此确定问题定义。[@openalex-w3037519745#E001]

## Motivation

当前输入不足，未核实。

## Method

当前输入不足，未核实。

## Experimental Setup

当前输入不足，未核实。

## Key Findings

当前输入不足，未核实。

## Limitations

### 作者明确承认

当前输入不足，未核实。

### 模型推断

不能仅凭“资源弹性”标题认定该工作能够通过移除不可用 DC/worker 解决本项目关注的光网络故障问题。其故障模型、训练正确性和网络假设必须读取全文后再判断。[@openalex-w3037519745#E002]

## Evidence Items

### E001

`[@openalex-w3037519745#E001]`

- type: unverified
- statement: 该论文可能研究分布式深度学习的资源弹性，但当前 metadata 无法核实具体问题、方法和结果。
- locator: {page: null, section: null, figure: null, table: null}
- supports: []
- confidence: low
- notes: 不能作为 gap 或 hypothesis 的肯定支持。

### E002

`[@openalex-w3037519745#E002]`

- type: model_inference
- statement: 需要核实论文是否支持 worker/DC 移除、其网络故障假设为何，以及弹性调整能否替代光层恢复；标题本身不足以回答。
- locator: {page: null, section: null, figure: null, table: null}
- supports: [E001]
- confidence: low
- notes: 这是负面测试问题，不是论文结论。

## Model Inference

见 E002。

## Research Inspiration

该条目承担“直接抛弃不可用 DC 是否足够”的反例检验入口。正式使用前必须取得全文证据。
