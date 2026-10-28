---
schema_version: "1.0"
note_sequence: "016"
paper_id: "doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66"
title: "Bandwidth Squeezed Restoration in Spectrum-Sliced Elastic Optical Path Networks (SLICE)"
source_url: "https://doi.org/10.1364/JOCN.3.000223"
pdf_url: null
input_coverage: "full_text"
evidence_level: "full_text"
created_at: "2026-10-09T12:32:21Z"
updated_at: "2026-10-09T12:49:19Z"
---

# 论文精读卡：Bandwidth Squeezed Restoration in Spectrum-Sliced Elastic Optical Path Networks (SLICE)

## Input Coverage

- evidence_level：full_text。读取用户提供的 11 页 PDF，正文 pp.223–231，参考文献与作者信息 pp.231–233；图表重点核对 Table I–III、Fig.4、Fig.10–11。
- 原始文件：`papers_search_by_human/Bandwidth_Squeezed_Restoration_in_Spectrum-Sliced_Elastic_Optical_Path_Networks_SLICE.pdf`；缓存：`papers/.cache/pdfs/doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66.pdf`。
- SHA-256：`f7109fa355a46db05fccb390fae0279114e163e6edf1eaa3288129fbfa644872`。DOI 与首页核对一致。未重新下载或修改原始 PDF；未复现实验。

## Metadata

- paper_id：`doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66`；note_sequence：016，均不变。
- 作者：Y. Sone, A. Watanabe, W. Imajuku, Y. Tsukishima, B. Kozicki, H. Takara, M. Jinno。
- 2011，Journal of Optical Communications and Networking，3(3)，223–233。
- DOI：10.1364/JOCN.3.000223；arXiv：不适用。

## Research Question

故障后无法恢复原光路全带宽时，如何利用弹性光路和客户服务规范，恢复承诺流量并提高受限频谱下的可恢复连接数？ [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E001] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E006]

## Motivation

固定波长粒度可能为仅部分需要保证的流量预留整波长容量。BSR 将恢复带宽与原工作带宽解耦，同时保持客户服务等级的约束；并非任意丢弃业务。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E001] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009]

## Method

1. 区分预先承诺的恢复带宽（FBGR/PBGR）与故障后按资源决定的 BER；路由可预定或故障后确定，不应仅凭 BSR 名称归为某一种预留方式。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E006]
2. 用 BV transponder/BV-OXC 改变子载波/stream 数；RSA 检查连续与端到端一致的频隙，不能只比较总空闲容量。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E001] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E007]
3. 在客户层/光层安置 marker、mapper、policer，并用 UNI/GMPLS 协调恢复状态。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E010]

## Mechanism Decomposition

| 维度 | 内容与适用条件 | 证据 |
|---|---|---|
| 经典问题与保障对象 | 光路容量恢复与客户承诺服务 | [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E001] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E002] |
| 原有决策 | 全带宽恢复；BSR 增加部分保证和按资源恢复 | [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E006] |
| 成立条件 | 带宽可调硬件、SLS、频谱连续/一致性；示例主备节点不相交 | [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E001] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E007] |
| 场景信息与控制 | 已知 committed/excess rate、报文颜色；可改变 stream、映射与 policing | [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E010] |
| 实际改变的变量 | 恢复带宽、承载 stream 数与客户边缘转发策略 | [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E006] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009] |
| 收益来源 | 降低恢复容量预留，或让部分空闲资源仍能承载恢复连接 | [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E008] |
| 成本与消失条件 | 需付出分类/控制与状态同步成本；若不能降低承诺带宽或无可行连续频谱，不能假定获益 | [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E013] |

本论文已有一般业务的服务信息和层间控制，尚不能等同于具体大模型任务特性或任务恢复证据。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E004]

## Experimental Setup

- 网络设计评估：4×5 格点，570 个双向需求，顺序随机到达，建立后不拆除或改路，400 Gbps 工作带宽。对 31 个单链路故障平均。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E008]
- baseline：FBGR；对照 PBGR 100/200/300 Gbps、随机混合与 BER。总资源评估不设每纤容量上限；恢复率评估设 4.5 Tbps。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E008]
- OFDM/频谱示例：25 GHz 槽宽、每子载波服务速率 100 Gbps；Table II 的分配频隙分别为 3/4/5/6，不与业务速率线性同比缩减。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E007]
- 控制验证：BV-OXC 仿真器、预计算恢复路由、带背景 LSP；不当作真实广域硬件测试。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E011]

## Key Findings

- PBGR 必须保证指定恢复容量；不足算恢复失败。BER 不预留并按可用资源恢复，不能把它当作同一容量承诺下的替代。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E006]
- 示例中 100/200/300 Gbps PBGR 节省频隙 28%/19%/9%；它们对应不同恢复带宽，不能当作相同服务保障下的纯算法优势。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E008] [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E013]
- 约 1.05 s 的控制切换含 1 s holding，余量不能外推为真实设备或任务恢复时延。 [@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E011]

## Limitations

作者明确未来工作见 E012。其预评估是单链路故障集；文中对灾难恢复的动机与预期不等于已经验证区域灾害。AI 任务净收益未研究；见 E004、E013 的阅读者判断。

## Evidence Items

### E001

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E001]

- type: paper_claim
- statement: BSR 利用可变带宽光路，依据客户服务规范压缩恢复带宽。
- locator:
  - page: 224
  - section: "II.A"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: null

### E002

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E002]

- type: paper_claim
- statement: Table I 区分全带宽保证 FBGR、部分带宽保证 PBGR、尽力恢复 BER。
- locator:
  - page: 225
  - section: "II.B"
  - figure: null
  - table: "I"
- supports: []
- confidence: high
- notes: null

### E003

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E003]

- type: unverified
- statement: 首次摘要阅读时未核验正文算法、控制时延与数值收益；该历史待核验项现由 E005–E012 补证，不再表示全文不可得。
- locator:
  - page: null
  - section: null
  - figure: null
  - table: null
- supports: []
- confidence: low
- notes: "保留原 evidence ID；引用具体正文结论时使用新增证据，不用本历史状态作正面支持。"

### E004

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E004]

- type: model_inference
- statement: 降级对具体 AI 任务的净代价仍未核验；本文客户分级带宽机制不直接证明训练/推理性能保障。
- locator:
  - page: null
  - section: null
  - figure: null
  - table: null
- supports: ["E001", "E002", "E009"]
- confidence: medium
- notes: "原条目涉及重配置成本的待查部分现由 E009–E011 补充，AI 代价仍未解决。"

### E005

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E005]

- type: paper_claim
- statement: FBGR/PBGR 先确定恢复带宽，需预留至少指定容量；切换时低于指定带宽则恢复失败。FBGR 为 PBGR 的全带宽特例。
- locator:
  - page: 225
  - section: "II.B"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: null

### E006

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E006]

- type: paper_claim
- statement: BER 不预留备份带宽，按备份路由可用资源分配，直到指定上限；本例以 100 Gbps 为粒度、400 Gbps 为上限。
- locator:
  - page: 225
  - section: "II.B; II.C (pp.225–226)"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: null

### E007

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E007]

- type: paper_claim
- statement: RSA 要求端到端使用相同连续频隙；采用 first-fit 连续频谱分配，示例主备路由节点不相交。
- locator:
  - page: 226
  - section: "II.C"
  - figure: null
  - table: "II"
- supports: []
- confidence: high
- notes: null

### E008

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E008]

- type: experimental_evidence
- statement: 4×5 格点、570 个双向需求、工作带宽 400 Gbps、静态建立后不变，平均恢复率覆盖 31 个单链路故障。PBGR 100/200/300 Gbps 的所需频隙比 FBGR 下降 28%/19%/9%；资源总量评估不限制光纤容量，恢复率评估限制为每纤 4.5 Tbps。
- locator:
  - page: 225
  - section: "II.C (pp.225–227)"
  - figure: 4
  - table: null
- supports: []
- confidence: high
- notes: "比例为文中报告，不是独立复现；未将 Fig.4 的恢复率增幅改写为百分点。"

### E009

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E009]

- type: paper_claim
- statement: 架构 A 为光层识别颜色映射，B 为光层 policing 加不识别颜色映射，C 由 UNI 通知客户边缘更新 policing。C 不要求光层逐包识别颜色，但需同步客户与光层状态。
- locator:
  - page: 227
  - section: "III (pp.227–229)"
  - figure: null
  - table: "III"
- supports: []
- confidence: high
- notes: null

### E010

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E010]

- type: paper_claim
- statement: GMPLS 实现采用光路/stream 两级 LSP；私有 RSVP-TE 扩展 CNS、ENS 及 BER 标志与 Label_Set 资源信息。BER 带宽由出口据收集信息决定。
- locator:
  - page: 230
  - section: "IV"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: null

### E011

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E011]

- type: experimental_evidence
- statement: BER 在 BV-OXC 仿真器网络中验证；恢复路由已预算并配置于入口，背景 LSP 占三条 stream。失败 LSP 按资源用一条 stream 恢复，切换约 1.05 s，包含 1 s holding period。
- locator:
  - page: 230
  - section: "IV"
  - figure: 10–11
  - table: null
- supports: []
- confidence: high
- notes: "Figures 10–11；不是实体收发器调谐或广域端到端任务恢复实测。"

### E012

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E012]

- type: author_limitation
- statement: 作者尚未解决子载波故障触发标准及两端一致的失败信息、先进 stream preemption、多层 grooming/bypass 与更有效 RSA；初步评估采用 primitive algorithm。
- locator:
  - page: 230
  - section: "V. Future Work"
  - figure: null
  - table: null
- supports: []
- confidence: high
- notes: null

### E013

[@doi-f2da11e9c262e630efad483c72a2ed48fac9df666ba67c868e9a0db98d6efa66#E013]

- type: model_inference
- statement: PBGR 降低保证带宽，BER 改变容量保证方式；应把保证等级变化与频谱收益同时比较。新增任务机制必须与已有分级带宽、客户层协调和恢复控制比较，不能以“传统均全带宽且不感知业务”为前提。
- locator:
  - page: null
  - section: null
  - figure: null
  - table: null
- supports: ["E005", "E006", "E009"]
- confidence: medium
- notes: null

## Model Inference

E004 标记尚缺 AI 任务代价证据；E013 提醒按服务保证与资源预算作公平比较。不将带宽恢复等同于任务性能恢复。

## Research Inspiration

本阶段仅补经典机制。以后讨论任务赋能时，须说明超出一般 committed/excess rate 与 UNI 协调的实际决策变化，不据本卡生成 gap 或候选。

## Reading Priority

- 标签：值得精读（本轮已完成全文机制阅读）。
- 理由：直接提供部分保证/尽力恢复、客户层协调及控制实现的经典基线。
