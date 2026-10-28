---
schema_version: "1.0"
note_sequence: "015"
paper_id: "doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7"
title: "GeoPipe: a Geo-distributed LLM Training Framework with enhanced Pipeline Parallelism in a Lossless RDMA-enabled Datacenter Optical Transport Network"
source_url: "https://doi.org/10.1109/acp66871.2025.11350566"
pdf_url: "https://arxiv.org/pdf/2510.12064"
input_coverage: "full_text"
evidence_level: "full_text"
created_at: "2026-10-04T10:00:00Z"
updated_at: "2026-10-04T10:00:00Z"
---

# 论文精读卡：GeoPipe

## Input Coverage

- evidence_level：`full_text`
- 输入范围：已读取本地 PDF 全部 6 页，并核对系统、算法、实验和结论。
- 边界：论文实验关注健康网络中的跨 DC 通信开销与带宽变化，未报告故障注入实验。

## Metadata

- paper_id：`doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7`
- authors：Jun Dai；Xiaorun Wang；Kexiong Fang；Zheng Yang；Yuefeng Ji；Jiawei Zhang
- year：2025
- venue：ACP 2025（selected metadata 未提供 venue）
- DOI：`10.1109/acp66871.2025.11350566`
- arXiv：`2510.12064`
- source URL：https://doi.org/10.1109/acp66871.2025.11350566

## Research Question

如何在由 lossless RDMA-enabled DC-OTN 连接的多个数据中心中改造流水线并行，以隐藏受限跨 DC 带宽带来的通信开销并提高 LLM 训练效率。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E001]

## Motivation

LLM 参数增长使单 DC 资源可能不足，而把单 DC 训练直接扩展到多 DC 会受到跨域带宽和时延限制。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E001]

## Method

GeoPipe 将发送/接收解耦为非阻塞过程，使计算与跨 DC 通信重叠；其遗传式启发算法依据计算时间、HBM 上限、跨 DC 时延和带宽调整 micro-batch size、sequence length 和 forward-pass 数量 `ΔN`，在总 token 数相同的约束下最小化迭代时间。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002]

## Experimental Setup

- 8 个计算节点、每节点 8 个 Ascend 910B NPU（64 GB HBM），共 64 个 NPU 分布在 3 个区域。
- 区域间由具有 buffer 与 PFC 的 DC-OTN 连接；通过调整 spine 端口速率改变跨 DC 带宽。
- 模型为 Llama-2 13B/72B；TP=8 位于节点内，PP=8，只有 PP 流量跨 DC。
- baseline 为经典 1F1B pipeline parallelism。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E003]

## Key Findings

- 将 spine 端口从 400 Gbps 降为 200 Gbps 的拥塞测试中，作者报告 PFC 保持吞吐稳定且没有 retransmission。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E004]
- 相对 1F1B，GeoPipe 最高减少约 78.91% computation bubble，平均迭代时间改善约 9.1%。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E005]
- 论文观察到跨 DC 带宽存在训练性能优化点，并非带宽无限增加都会等比例改善训练。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E006]

## Limitations

### 作者明确承认

作者把训练 scheduler 与光网络 control plane 的更紧密集成、动态资源编排列为未来工作。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E007]

### 模型推断

实验采用 lossless、可控带宽的 DC-OTN，并未注入软故障、链路中断或区域故障；因此其结果可作为健康网络训练基线，但不能回答故障下的训练连续性或算网联合恢复问题。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]

## Evidence Items

### E001

`[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E001]`

- type: paper_claim
- statement: GeoPipe 面向 lossless RDMA-enabled DC-OTN 上的跨地域 LLM 训练，通过增强流水线并行降低跨 DC 通信影响。
- locator: {page: 1, section: "Abstract; Section I", figure: null, table: null}
- supports: []
- confidence: high
- notes: null

### E002

`[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E002]`

- type: paper_claim
- statement: 方法通过非阻塞通信实现计算—通信重叠，并用遗传式启发算法联合选择 micro-batch、序列长度和前向次数以最小化迭代时间。
- locator: {page: 2, section: "Section II", figure: "Figures 1–2", table: null}
- supports: []
- confidence: high
- notes: 方法描述延续至 PDF 第 3 页。

### E003

`[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E003]`

- type: experimental_evidence
- statement: 测试床含 3 区域、8 节点、64 个 Ascend 910B NPU，运行 Llama-2 13B/72B，采用 TP=8、PP=8，并以 1F1B 为 baseline。
- locator: {page: 4, section: "Section III", figure: "Figure 3", table: null}
- supports: [E001, E002]
- confidence: high
- notes: null

### E004

`[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E004]`

- type: experimental_evidence
- statement: 在端口速率由 400 Gbps 降到 200 Gbps 的测试中，作者报告 PFC 使吞吐稳定且未发生重传。
- locator: {page: 4, section: "Section III", figure: "Figure 4", table: null}
- supports: [E003]
- confidence: high
- notes: 这是拥塞/带宽变化实验，不是故障实验。

### E005

`[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E005]`

- type: experimental_evidence
- statement: 作者报告相对 1F1B 最高减少约 78.91% computation bubble，平均迭代时间改善约 9.1%。
- locator: {page: 5, section: "Section III", figure: "Figures 5–6", table: null}
- supports: [E002, E003]
- confidence: high
- notes: 仅适用于论文实验配置。

### E006

`[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E006]`

- type: paper_claim
- statement: 论文指出跨 DC 带宽存在训练性能优化点，带宽增加与训练收益并非简单线性关系。
- locator: {page: 5, section: "Section III", figure: "Figure 7", table: null}
- supports: [E003]
- confidence: high
- notes: null

### E007

`[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E007]`

- type: author_limitation
- statement: 作者将训练 scheduler 与光网络 control plane 的更紧密集成及动态资源编排列为未来工作。
- locator: {page: 6, section: "Section IV", figure: null, table: null}
- supports: []
- confidence: high
- notes: 未来工作不等同于已证实 research gap。

### E008

`[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]`

- type: model_inference
- statement: 该实验建立了健康网络下的算网协同训练基线，但未验证软故障、链路中断或区域故障下的行为。
- locator: {page: 4, section: "Section III", figure: "Figures 3–7", table: null}
- supports: [E003, E004, E005, E007]
- confidence: high
- notes: 基于实验覆盖范围的推断，不是作者原结论。

## Model Inference

见 E008。

## Research Inspiration

GeoPipe 表明训练调度确实可以读取跨 DC 光网络带宽约束；后续值得核实的问题是，这种联合接口在故障风险或恢复代价进入后是否已有充分研究。当前证据只支持继续调研，不支持 novelty 结论。[@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E007] [@doi-9b69963c66961509c7ce36bb9cf7676ceda50b1246e60ab2d14ee51010a89ad7#E008]
