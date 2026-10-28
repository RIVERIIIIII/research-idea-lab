# Candidate Hypothesis 模板

```markdown
# Candidate Hypotheses

## Scope & Status
- inputs:
- validation boundary:

## HYP-001 — 标题
- hypothesis_id: HYP-001
- title:
- statement:
- derived_from: [GAP-001]
- research_problem:
- rationale:
- supporting_evidence:
  - [@paper_id#E001]
- counter_evidence:
  - statement + [@paper_id#E002]
- assumptions:
  - ...
- mechanism_chain:
  - classical_problem:
  - classical_scheme_and_decision:
  - limiting_condition_and_boundary:
  - task_property_evidence_and_control_conditions:
  - decision_change_and_causal_link:
  - expected_benefit_and_source:
- quality_checks:
  - property_authenticity:
  - mechanism_effectiveness:
  - net_benefit_and_costs:
  - prior_art_risk:
- comparison_conditions: 资源预算、故障模型、保障水平及适用的经典/简单替代基线。
- counterfactual: 移除特性或禁止新增控制后，决策与收益应如何变化？
- benefit_disappearance_conditions:
- falsifiability:
- uncertainty:
- back_check_queries:
  - "query 1"
  - "query 2"
  - "query 3"
- confidence: HIGH | MEDIUM | LOW
- evidence_status: inferred
- status: NEEDS_BACK_CHECK
```

## 写作检查

- `statement` 必须包含条件、关系/机制、比较对象和指标类别。
- `falsifiability` 必须描述会否定假设的观察，而不是重复 statement。
- query 应覆盖核心机制、同义表达、邻近技术路线和替代方案。
- 不为凑数生成 hypothesis；证据不足的 GAP 保留在 gaps 文件等待补强。

## 毕业论文讨论补充（不新增状态枚举）

按 Research Brief 与 docs/mechanism-discovery.md，另列讨论说明：

- 光网络贡献核心（硬性）：任务信息/约束/控制能力 → 具体保护、恢复、共享、风险或光资源配置决策变化 → 因果机制与反事实；仅任务侧优化或把光网络作为背景不符合要求。
- 相对第一点：关键条件变化、第一点不能直接解决的原因、不同决策机制。
- 相对最近邻工作：已覆盖机制、具体剩余差异与待回查项。
- 共用模型及必要扩展：仅为排序偏好，不作排除门槛。
- 中期交付：初步模型、基线、指标、可否定验证思路；未完成验证明确标记。

允许合理增量、独立支撑一章即可，不要求独立投稿或此时完成实验；基础事实须有据，新机制允许为具体可证伪推断。最终验证与人工审查要求保持。
