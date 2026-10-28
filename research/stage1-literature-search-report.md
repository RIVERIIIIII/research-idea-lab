# 阶段一检索与筛选报告（2026-10-09）

## 范围与组织

上游为 CONFIRMED Research Brief 的阶段一：理解经典光网络生存性机制、成立条件、原有决策与适用边界。本轮为首批有界检索，不要求论文出现 LLM/AI，不开展新机制、gap 或 hypothesis 推导。

检索分三组：

1. 分类与保护/恢复：`optical network shared path protection restoration`。
2. 共因故障：`optical shared risk link group survivability`。
3. 服务降级：`bandwidth squeezed restoration elastic optical`。

三组使用现有 search_papers.py，arXiv/Semantic Scholar/OpenAlex 各 query 每源最多 4 篇，自动 select-count 为 0，由机制相关性人工式复筛。原始 28 条合并为 26 条；Semantic Scholar 两个 query 返回 429，故覆盖受限。首次沙箱运行 DNS 不可用，后续联网重跑成功；统计以成功重跑报告为准。

随后使用 OpenAlex 精确标题补查五组代表文献，各组最多 2 条，以及管道层保护一组最多 1 条。补查标题：

- `Survivability in optical networks`
- `Survivable WDM mesh networks`
- `A unified framework for shared protection schemes in optical mesh network`
- `Fast optical layer mesh protection using pre cross connected trails`
- `Robust QoT Assured Resource Allocation in Shared Backup Path Protection Based EONs`
- `Path Protection Routing Wavelength Assignment WDM Mesh Networks Duct Layer Constraints`

另以网页检索定位出版社与作者/大学公开 PDF。关键词包含 `bandwidth squeezed restoration`、`SRLG Zang`、`pre-cross-connected trails`、`Survivable WDM Mesh Networks pdf` 等；只用论文原文、作者公开版本或出版社摘要支持机制判断，未使用百科或商业聚合页作为事实依据。

## 筛选结果

当前 candidates 共 37 条，selected 7 条。该数量包含预印本/期刊同题记录，不等于 37 篇互不重复的独立研究。明确不相关结果排除，其余非入选记录 deferred；不以低引用或本轮未入选判断无关。

入选覆盖：经典分类与 APS、路径/链路保护与恢复、共享保护统一成本框架、PXT 预连接、管道/SRLG 保护、BSR 带宽压缩、故障状态 QoT。具体理由、元数据来源与稳定身份见 JSONL。

6 篇 PDF 使用现有 download_papers.py 成功下载并通过其完整 PDF 检查。笔记仅标 partial_text：有 PDF 不代表完整精读。BSR 2011 为 abstract_only，额外读取了出版社公开 Table I；未编造正文实验细节。

## 元数据校正与版本边界

- Zhou/Subramaniam 2000 作者顺序依据作者公开 PDF 校正，保留 paper_id。
- PXT 的旧 arXiv 编号补回 `cs/0209006`；期刊年份为 2004，阅读的是 arXiv v2，不将版本年份混为同一信息。
- QoT 同题 arXiv 与 IEEE Access 有不同 DOI，脚本标记冲突；本轮明确选择 arXiv v1 作为独立阅读版本，期刊记录 deferred，未合并身份或混用数值。版本等价关系仍待核验。
- 公开 PDF 链接的原文校正记录在 metadata_provenance，sources 保留实际 API 提供者。
- 历史保留笔记序号 001–015 不复用，本轮分配 016–022；下一可用为 023。注册表用于身份与序号，不定义 corpus 成员。

## 原始运行记录

- `research/search-records/stage1-search-run.json`
- `research/search-records/stage1-seed-search-run.json`
- `research/search-records/stage1-srlg-search-run.json`

运行报告保存脚本当时的自动筛选统计（selected=0）；最终人工式机制筛选后的状态以当前 JSONL 和本报告为准，不重写原始运行报告。

## 交付与剩余证据需求

7 份有明确输入边界的阅读卡与 `research/survey.md` 第一版机制表。不声称全面综述。

首要补件是 Sone 等的 BSR 2011 正文，DOI `10.1364/JOCN.3.000223`。若人有机构访问权限，可将合法取得的 PDF 放入 `papers_search_by_human/`，后续再按稳定 paper_id 缓存和核验；无需提供账号。

仍需补充 EON 资源约束的基础模型、跨域信息限制、多/区域故障、软故障和重新保护。它们是覆盖待补项，不是创新 gap。第二阶段任务特性检索尚未启动。

## 用户提供 BSR 全文后的补读更新（2026-10-09）

原始检索统计和初始证据状态保留以上历史记录；当前状态以此更新为准。用户已提供 DOI 对应的 11 页 PDF，首页核验后按既有 paper_id 缓存，原文件保留，哈希见 016 笔记。当前 7 篇均有 PDF 输入；6 份 partial_text，BSR 1 份 full_text。BSR 原 E001–E004 编号保留，新增 E005–E013 正文证据；初始未核验状态由新证据说明其后续解决情况。已补客户层协调、PBGR/BER 预留差别、频隙约束、示例评估与仿真器控制时间、作者明确未来工作；尚未复现结果或分析 AI 任务性能。BSR 原文补件请求已解决。


## 本轮补充进度

补充检索运行见 `stage1-supplement-search-run.json`、`stage1-supplement-seeds-run.json` 与 `stage1-supplement-exact-run.json`。主 candidates 52 条、selected 10 条；独立 seeds/exact 检索输出是待筛选线索，不自动属于 corpus。新增 EON 资源约束（作者草稿、partial_text）、双故障保护（abstract_only）、软故障频谱共享（用户 PDF、partial_text）。软故障沿用 004 与 E001–E011 的历史身份，当前重验依据新增为 E012–E014。跨域、区域与重新保护暂未形成正文机制卡；不得据此声称覆盖完成。


用户补充双故障论文 PDF 后，024 阅读卡升级为 partial_text；E003–E007 为 §III–IV.A 正文核验，保留原 E001–E002 摘要证据身份。当前 10 份卡：1 full_text、9 partial_text。未把数值实验或任意相关多故障保障视为已核验。
