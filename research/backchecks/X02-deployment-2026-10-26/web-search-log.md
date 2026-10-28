# 网页补充检索与访问记录

日期：2026-10-26。项目 skill 的逐查询原始记录见 search-run-network.json 和 exact-run.json；此文件补充网页检索入口及阅读范围，不声称保存了搜索引擎全部结果或覆盖全部相关文献。

## 检索分支

- 真实跨地域分段推理及断连后的状态恢复 → Petals，arXiv:2312.08361v1。
- 部署中的 P/D 解耦、故障处理与流式请求 → P/D-Serve，arXiv:2408.08147v1。
- 跨数据中心 KV 交付、链路与评估方式 → PrfaaS，arXiv:2604.15039v2；PDD，arXiv:2609.13161v1。
- 光云服务迁移、原端点恢复资源限制与备份启用 → 2016 PR-SRD、2021 SCORE。
- 最后一轮精确网页查询：`"An empirical analysis of intra- and inter-datacenter network failures"` → 微软出版记录和两页原文。

各版本原文 URL、关键节号、证据层级、限制见 report.md 的 E01–E07。仅将原始论文/作者稿作为技术事实来源。

## 辅助查得但未用于核心全文论证

- NFV recovery strategies for critical services after massive failures in optical networks，DOI:10.1016/j.osn.2024.100790：仅摘要，不据此判断具体算法覆盖。
- Enabling Software-Defined Tiered LLM Inference Continuum on Passive Optical Network，DOI:10.1109/ACCESS.2026.3651558：仅摘要，描述仿真，不能作为生产光故障案例。
- Cisco AI Inference White Paper — Architecture for Wide Area Networks：产业架构说明，不当作故障测量数据。

## 访问与版本说明

- 六篇 reading-selected.jsonl 定向下载：5成功、1失败。2016 DiVA 作者稿首次和后续重试均超时；网页工具成功打开10页PDF并读取§III、Eq.(3)、HRP算法。
- 2013故障研究镜像：本地下载 HTTP403；网页工具成功读取2页全文。微软出版页核对标题、作者和2013年会议记录。
- 2016作者稿保留出版日期模板，引用正式 DOI，不把模板日期当出版日；SCORE作者稿带仓储封面，PDF定位已计入封面。
- PDD HTML显示日期与arXiv编号月份冲突，保留冲突，不依据该项论证时间先后。
- 初次项目检索DNS失败和获准联网后的成功运行分别保存在 search-run.json 与 search-run-network.json。

结论边界：这是为两个具体问题开展的定向回查，没有建立“所有生产推理光网故障”的完备案例库，也没有把未找到案例解释为不存在。
