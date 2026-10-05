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
