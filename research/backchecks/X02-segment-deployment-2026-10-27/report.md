# X02跨地域分段推理场景回查

日期：2026-10-27。针对用户质疑的定向回查；不改正式corpus、既有paper_id、HYP或候选状态。已读取Brief、数据契约、机制规范、note-registry和literature-search技能。

## 判断

需要回查，不能以场景图替代证据。跨地域分段推理存在直接学术及原型依据，但当前已读材料不足以将其称为成熟运营商光网生产部署。X02可保留为显式研究设定，尚需确认其目标资源池和通信映射，不能由“单卡显存不足”直接推出“必须跨地域”。

## 关键原文

1. Distributed Inference and Fine-tuning of Large Language Models Over The Internet，Petals，arXiv:2312.08361v1。https://arxiv.org/html/2312.08361v1
   - §1、§2.1：通过分散设备持有模型层并交换激活执行推理，动机是资源汇聚与降低使用大模型的硬件门槛。
   - §4.2 Real-world setup：14台异构服务器位于欧洲和北美，公网连接100–1000Mbit/s。这是跨地域真实系统实验，不是仅有概念设想。
   - §4.2 Analysis：该评估下单请求生成更受延迟影响，不能默认增加频谱带宽即可显著提高生成速度。
   - 不支持：运营商可控光层的实际部署、特定光故障记录、严格商业SLO。
2. Optimizing resource allocation for geographically-distributed inference by large language models，Sun/He/Ji/Parag，Performance Evaluation 170 (2025) 102527，DOI:10.1016/j.peva.2025.102527。
   作者稿：https://ece.iisc.ac.in/~parimal/papers/2025/peva.pdf
   - §1、Fig.1：明确研究跨地域流水分段推理，模型块放置与请求路由；基于Petals，独立开展资源优化研究，但系统基础非独立新部署。
   - §1：client-centric模式由客户端缓存并转发各段输入输出，是hub-spoke通信。计算顺序不等于站点直接链式通信。
   - §4.1：3或8块A100上的虚拟GPU环境，Linux namespace/tc模拟时延和带宽，另有数据驱动仿真。不是另一个真实跨地域试验网。
   - 不支持：真实光故障、光路/频谱配置、模型分段必须跨数据中心。

## 对现有图和方案的影响

model-segments.html中的甲→乙→丙只可作为计算依赖的抽象示意，不能直接充当Petals真实网络路径。应先选择客户端中转或直接段间通信，再画故障承载。当前不自动改研究点或淘汰候选。

建议下一阶段先完成部署场景资格检查：说明哪些站点无法独立容纳目标模型、为何利用跨地域资源、可接受时延及基线本地部署；再将每轮通信、状态恢复流和光承载逐条对应。若只能依靠人为禁止本地部署支撑场景，应修订X02场景，而不是继续堆算法。

## 检索记录与限制

网页查询："geo-distributed" "LLM inference" "pipeline"；Petals distributed inference intercontinental real world network latency 2023。仅采用论文原文，不以聚合站摘要作依据。
项目skill补充命令：search_openalex.py --query 'geographically distributed inference large language models pipeline' --max-results 5 --output 本目录/openalex.jsonl。首次沙箱DNS失败，随后网络重试；命令元数据不代表原文已精读。未开展系统综述或以缺失结果证明不存在。

## 补查：至少三篇直接相关论文

2026-10-27，按用户要求补查。不将Petals两篇版本拆算成独立系统证据。

3. InferSlice: A Reference Architecture for SLO-driven LLM Inference over a Telco Wide-Area Network，Parra-Ullauri等，arXiv:2610.32638v1，2026-10-23预印本。https://arxiv.org/abs/2610.32638 ，全文 https://arxiv.org/pdf/2610.32638 。
   - §2.1.1明确PP按层分组；§4.5及Table5（PDF第16页）报告两段PP的实际跨站部署，伦敦UCL—南安普敦、UCL—贝尔法斯特、贝尔法斯特—都柏林，实测RTT分别9/18/33ms。
   - §1说明JOINER真实共享广域网测试；这是独立于Petals的电信广域试验网原型，非仅模拟网络。
   - Table7、§5–6：随距离增大可持续请求率显著下降，不能以低负载可运行推出负载下满足SLO。作者将PP适用范围收敛到近/中距离跨站。预印本尚不能当作已同行评审。
   - 附录A说明JANET光传送及NDFF连接能力；不意味着推理实验做了光层配置或光纤故障恢复测试。

本轮结论更新：有三篇直接研究同一模型跨地域分段推理的论文（Petals 2023、Sun等2025、InferSlice2026），其中前后两篇有实际跨地域实验，Sun等是基于Petals的模拟网络实验。不能表述为三套独立真实跨地域部署。新证据增强场景存在性和电信WAN关联，但不证明X02状态恢复协议、光层恢复机制或所有距离下商业SLO。之前“已核验材料没有电信广域原型”的覆盖范围现由InferSlice补充，原结论仍保留检索时间与边界，不静默覆盖。

补充查询：LLM inference geo distributed pipeline parallelism model partition WAN paper；"distributed inference" "geographically" "pipeline" large language models；"LLM" "cross-region" "pipeline parallelism" inference。PARALLAX作者技术稿也讨论地理分散设备PP，但已读实验段未明确地点/距离，未计入三篇核心证据。未更改正式corpus或候选状态。
