# Next-Candidate Branch Screening

## Scope

- Purpose: small exploratory screening for the next independently publishable research problem.
- Research Brief status: `CONFIRMED`.
- This is not formal corpus construction and does not change `papers/candidates.jsonl` or `papers/selected.jsonl`.
- Search date: 2026-10-06.
- Sources attempted: arXiv, OpenAlex, Semantic Scholar.
- Semantic Scholar returned HTTP 429 during the attempted queries; conclusions below therefore remain provisional.

## Search Accounting

| Branch | Queries | Raw results | After deduplication | arXiv | OpenAlex | Semantic Scholar |
|---|---:|---:|---:|---:|---:|---:|
| Optical reconfiguration + collective communication | 2 | 20 | 18 | 10 | 10 | 0 |
| Optical protection + training checkpoint | 2 | 20 | 20 | 10 | 10 | 0 |
| Optical survivability + distributed LLM inference/MoE | 2 | 15 | 15 | 10 | 5 | 0 |
| Correlated optical degradation + collective adaptation | 3 | 34 | 30 | 18 | 16 | 0 |
| Training-symptom-assisted optical diagnosis | 3 | 36 | 29 | 18 | 18 | 0 |

Result counts include query noise. They measure API retrieval, not relevant-paper counts.

## Branch 1 — Failure-triggered optical reconfiguration for collective communication

**Decision: REJECT in its generic form.**

### Why it initially looked valid

Optical reconfiguration delay and transient capacity changes can directly stall synchronized training. Collective topology, scheduling, and optical circuit configuration appear to form a genuine compute-network coupling.

### Why it does not currently clear the paper threshold

- The exploratory set already contains direct work on reconfiguration/communication overlap, photonic collective communication, runtime-reconfigurable optical fabrics, training-phase-aware OCS reconfiguration, and collective-algorithm optimization for reconfigurable optical networks.
- `RECCL`, `PCCL`, `MixNet`, and *Enabling Reconfiguration-Communication Overlap for Collective Communication in Optical Networks* cover much of the healthy-state mechanism space.
- `STON` explicitly targets non-disruptive logical-topology transition, so "avoid reconfiguration interruption" is not by itself an uncovered problem.
- `PRISM` already uses training semantics and failure context to control network recovery in AI training fabrics. Merely replacing the fabric with an optical network would be an insufficient contribution.
- A failure-triggered version also risks collapsing into the already-published post-failure cross-layer recovery contribution.

### Possible revival condition

Only reconsider if an optical-specific failure transition creates a distinct state-consistency or temporary-feasibility problem that is not handled by topology-transition, collective-remapping, or workload-aware recovery work. That mechanism must remain different from ordinary WAN rerouting and from the published recovery paper.

## Branch 2 — Joint optical protection and training checkpoint/restart

**Decision: REJECT.**

### Core causal problem

An optical-path failure normally causes communication delay, timeout, or rerouting; it does not necessarily destroy model/optimizer state. Checkpoint/restart primarily protects computation state. Without a demonstrated condition under which an optical failure forces rollback or loses distributed state, jointly optimizing the two is an artificial combination rather than a necessary coupling.

### Counter-evidence and overlap

- Existing distributed-training work already addresses fault-tolerant in-memory checkpointing.
- `PRISM` includes checkpoint-elapsed time in workload-aware network recovery and migration decisions, reducing the distinctness of a generic "checkpoint-aware network recovery" proposal.
- For inference, `LUMEN`, `Concordia`, and `GhostServe` already address failure recovery using request/KV state. Adding optical protection without a new optical mechanism would again be a domain substitution.

### Revival condition

Require evidence that a defined optical failure mode causes partial, inconsistent, or prohibitively expensive AI state reconstruction, and that optical protection resources and checkpoint placement have a bidirectional decision dependency. That evidence is currently absent.

## Branch 3 — Optical survivability for distributed LLM inference or MoE

**Decision: REJECT in its current form.**

### Why it initially looked valid

Disaggregated prefill/decode, KV transfer, expert placement, and request SLOs are network-sensitive and could expose different consequences from synchronized training.

### Why it does not currently clear the paper threshold

- The current search mostly returned generic service placement, MEC continuity, LLM serving, and MoE scheduling work rather than an optical-layer survivability problem.
- `LUMEN`, `Concordia`, `GhostServe`, and related serving systems already address failure recovery, checkpointing, reconstruction, and capacity restoration at the LLM system layer.
- Optical protection plus replica/expert placement can easily reduce to standard survivable service placement with an LLM label.
- No retrieved evidence yet shows an optical-specific variable whose behavior changes the inference recovery mechanism rather than merely supplying bandwidth.

### Revival condition

Require a failure effect unique to optical transport—for example, correlated lightpath/QoT degradation that changes prefill/decode or expert-routing feasibility—and show why ordinary rerouting, replication, or load balancing cannot solve it.

## Interim Conclusion for Branches 1–3

No new candidate idea is promoted from these three branches. This is a successful rejection outcome rather than a pipeline failure:

- Branch 1 has substantial direct prior-art pressure and overlaps the published recovery narrative.
- Branch 2 lacks a necessary causal coupling between optical failure and checkpoint state.
- Branch 3 currently looks like workload relabeling rather than an optical research problem.

The existing `IDEA-002` remains the only newly screened potential candidate in this round. Its status and conditional boundaries are unchanged.

## Branch 4 — Correlated multi-lightpath degradation and collective adaptation

**Decision: REJECT in its current form.**

Tested formulation:

> When an SRLG or spatially correlated soft failure leaves several optical paths connected but asymmetrically degraded, can joint optical restoration and training collective-topology/algorithm remapping reduce synchronization stall compared with fixed-collective optical recovery?

This branch initially met the structural criteria because:

- the failure object is optical-specific: correlated path/QoT/capacity degradation;
- the task consequence is explicit: collective synchronization stall;
- the compute-side decision is structural rather than a priority label: ring/tree/hierarchical collective selection or remapping;
- it might form a different narrative from single-path post-failure resource reallocation.

The back-check exposed two direct mechanism overlaps:

- `RECCL` dynamically changes collective communication relationships for a reconfigured optical topology.
- `OptCC` redesigns AllReduce for network-failure-induced asymmetric bandwidth and directly targets the degraded worker remaining on the collective critical path.

Together with `PRISM`'s workload-aware network fault recovery, these works cover the main causal chain of failure/degradation, asymmetric network state, and collective/training adaptation. An SRLG or correlated-QoT label alone does not yet create a different research mechanism. Combining optical correlated-failure models with an existing adaptive collective therefore currently looks integration-driven and incremental.

### Revival condition

Only reconsider if correlated optical impairment creates a constraint absent from both RECCL and OptCC—for example, coupled QoT feasibility across several lightpaths that makes collective transitions mutually dependent—and if that constraint changes the optimal collective or recovery policy in a way that ordinary asymmetric-bandwidth models cannot represent.

## Updated Screening Conclusion

All four newly tested branches are rejected in their current form. No additional candidate idea is created. This keeps the decision standard aligned with the requirement that one candidate must support a complete and distinct paper narrative.

The next search should not continue varying the same `optical recovery + training-aware scheduling/collective` template. A genuinely new branch needs a different optical failure consequence or a different cross-layer decision dependency.

## Branch 5 — Training-symptom-assisted optical soft-failure diagnosis

**Initial decision: KEEP FOR HUMAN DISCUSSION. Updated 2026-10-07: REJECT AS CURRENT FORM after minimal distinguishability check.**

### Candidate hypothesis (`DISC-HYP-B`)

> When optical telemetry is partial or its distribution changes after lightpath reconfiguration, jointly using optical telemetry and the mapped synchronization symptoms of distributed training may improve the localization and task-impact ranking of optical soft failures over optical-telemetry-only diagnosis, because a training collective exposes correlated end-to-end effects across the lightpaths that carry its dependent flows.

This is a hypothesis to review, not a fact or novelty claim.

### Why this is structurally different

- It changes the cross-layer direction: task behavior becomes feedback for optical fault management rather than merely an objective for post-failure resource allocation.
- The optical object is explicit: lightpaths, QoT/BER/OSNR telemetry, physical-device soft failures, and path-to-flow mapping.
- The AI consequence is explicit: synchronization delay, communication straggler propagation, or iteration-time anomaly.
- It is not solved by discarding an unavailable DC, because the premise is an ambiguous soft failure rather than an obviously disconnected site.
- It does not require a second recovery scheduler; the research object is diagnosis and impact attribution before choosing a recovery action.

### Prior-art pressure and required narrowing

Optical-only diagnosis is already strong:

- dynamic network-aware GNN localization reports robustness under topology reconfiguration;
- partial-telemetry ML localization already interpolates missing optical measurements;
- P4-based packet-optical telemetry enables microsecond-scale detection and local mitigation;
- optical monitoring literature already addresses failure evolution, localization, and telemetry scalability.

Therefore the candidate must not claim that application telemetry is generically faster or more accurate. Its defensible target is narrower: cases in which optical observations alone are ambiguous, while mapped training symptoms add information about end-to-end causality or task impact.

### Complete-paper test

- **Problem:** distinguish and locate task-impacting optical soft failures under partial or shifting optical telemetry, while separating them from compute stragglers and benign optical variation.
- **Model/input:** lightpath-to-training-flow mapping, optical telemetry, and a small set of training communication/synchronization signals.
- **Mechanism:** cross-layer correlation or causal inference that outputs fault location and task-impact ranking.
- **Baselines:** optical-only localization, task-only straggler diagnosis, and a generic time-correlation method.
- **Metrics:** localization top-k/F1, false alarms, detection delay, task-impact ranking quality, and downstream recovery-trigger precision.
- **Feasible validation:** injected soft failures plus compute/network straggler controls in simulation, emulation, or a small packet-optical testbed.

### Falsification conditions

Reject the hypothesis if any of the following holds:

- optical-only telemetry already localizes the relevant failures with equivalent accuracy and delay under the same partial/dynamic conditions;
- training symptoms occur too late or are too noisy to add diagnostic information;
- task signals cannot distinguish an optical impairment from compute, software, or congestion stragglers;
- the lightpath-to-training-flow mapping required by the method is unavailable or too expensive to maintain;
- direct prior work already performs the same optical-plus-training causal diagnosis.

### Immediate back-check still required

- distributed-training root-cause diagnosis using network and collective telemetry;
- service-impact-aware optical soft-failure management;
- cross-layer fault localization joining application SLO/telemetry with optical measurements;
- whether P4 packet-optical telemetry already consumes application/collective semantics beyond QoS and residual bit rate.

## Final Screening Conclusion

- Branches 1–4: rejected in their current form.
- Branch 5 / `DISC-HYP-B`: initially retained for discussion, then rejected in its current form after testing against ordinary per-flow network observability and compute-straggler confounding; see `research/explorations/next-candidate/diagnosis-early-check.md`.
- No new `IDEA-*` record is created. The current diagnostic formulation does not pass the independent-problem threshold.
- `IDEA-002` remains unchanged.

## External Prior-work Leads for the Next Check

- *Enabling Reconfiguration-Communication Overlap for Collective Communication in Optical Networks*, DOI `10.1145/3808672`.
- *RECCL: optimizing collective algorithms for reconfigurable optical networks*, DOI `10.1364/JOCN.555632`.
- *Training-Phase-Aware Optical Circuit Switching Reconfiguration for Large Language Model*, OFC 2026.
- *STON: Enabling Non-disruptive Logical Topology Reconfiguration in Optical Circuit Switched Network for LLM Training*, IEEE JCC 2026.
- *PRISM: Workload-Aware Autonomous Network Fault Recovery for Hyperscale AI Training Fabrics*, IEEE CLOUD 2026.
- *LUMEN: Coordinated Failure Recovery for Distributed LLM Serving*, arXiv `2606.17787`.
- *Dynamic network-aware soft failure localization using machine learning in optical networks*, JOCN 2025.
- *Machine-learning-based soft-failure localization with partial software-defined networking telemetry*, DOI `10.1364/JOCN.424654`.

These leads are prior-art checks, not proof that the recommended branch is uncovered.
