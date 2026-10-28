import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from paper_experiments import build_evaluator, derive_time_structure_metrics
from paper_evaluator import FailureSeverityProfile
import yaml

CONFIG_PATH = ROOT / "data" / "paper_experiment.yaml"
CSV_DIR = ROOT / "result" / "paper" / "csv"
FIGURE_DIR = ROOT / "result" / "paper" / "figure"
SUMMARY_CSV = CSV_DIR / "topo2_joint_compensation_summary.csv"
SEARCH_CSV = CSV_DIR / "topo2_joint_compensation_search.csv"
RECOVERY_PNG = FIGURE_DIR / "topo2_joint_compensation_recovery.png"
RECOVERY_PDF = FIGURE_DIR / "topo2_joint_compensation_recovery.pdf"
TOPOLOGY = "topo2"
BASE_STATE = "no_opt"
MAX_TOTAL_ACTIONS = 16
RECOVERY_EPSILON = 1e-6


SUMMARY_FIELDS = [
    "section",
    "rank",
    "topology",
    "base_state",
    "model_name",
    "tensor_parallel",
    "pipeline_parallel",
    "data_parallel",
    "n_wave",
    "total_actions",
    "total_extra_dp_groups",
    "total_extra_waves",
    "chosen_action_type",
    "focus_target",
    "extra_dp_capacity_per_dc",
    "extra_waves_per_pair",
    "T_iter",
    "T_exec",
    "T_prop",
    "T_tx",
    "T_stall",
    "delta_T_iter_vs_no_opt",
    "delta_T_stall_vs_no_opt",
    "delta_T_iter_vs_before_failure",
    "delta_T_stall_vs_before_failure",
    "recovered_to_before",
    "recovery_gap_to_before",
    "bottleneck_pair",
    "note",
]


SEARCH_FIELDS = [
    "topology",
    "base_state",
    "model_name",
    "tensor_parallel",
    "pipeline_parallel",
    "data_parallel",
    "n_wave",
    "total_actions",
    "candidate_action_type",
    "focus_target",
    "total_extra_dp_groups",
    "total_extra_waves",
    "extra_dp_capacity_per_dc",
    "extra_waves_per_pair",
    "T_iter",
    "T_exec",
    "T_prop",
    "T_tx",
    "T_stall",
    "delta_T_iter_vs_no_opt",
    "delta_T_stall_vs_no_opt",
    "recovered_to_before",
    "recovery_gap_to_before",
    "search_phase",
]


def load_config() -> tuple[dict, dict[str, Path]]:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))["paper_experiment"]
    global_cfg = config["global"]
    refs = {
        "topology_file": ROOT / global_cfg["topology_file"],
        "datacenters_file": ROOT / global_cfg["datacenters_file"],
        "service_file": ROOT / global_cfg["service_file"],
        "training_topologies_file": ROOT / global_cfg["training_topologies_file"],
        "wavelength_state_file": ROOT / global_cfg["wavelength_state_file"],
    }
    return config, refs


def normalized_pair(pair: tuple[int, int]) -> tuple[int, int]:
    return tuple(sorted((int(pair[0]), int(pair[1]))))


def recovered_to_before(result, before_result) -> bool:
    return result.t_iter <= before_result.t_iter + RECOVERY_EPSILON


def candidate_key(result, before_result, dc_order: list[int], pair_order: list[tuple[int, int]]) -> tuple:
    recovered = recovered_to_before(result, before_result)
    return (
        0 if recovered else 1,
        result.t_stall if recovered else result.t_iter - before_result.t_iter,
        result.t_iter,
        tuple((result.extra_dp_capacity_per_dc or {}).get(dc_id, 0) for dc_id in dc_order),
        tuple(
            next(
                (
                    allocation.allocated_n_wave - 1
                    for allocation in result.pair_allocations
                    if normalized_pair(allocation.dc_pair) == pair
                ),
                0,
            )
            for pair in pair_order
        ),
    )


def summary_row(
    section: str,
    result,
    before_result,
    no_opt_result,
    extra_dp_capacity_per_dc: dict[int, int],
    extra_waves_per_pair: dict[tuple[int, int], int],
    rank: int | str = "",
    chosen_action_type: str = "",
    focus_target: str = "",
    note: str = "",
) -> dict[str, object]:
    structure = derive_time_structure_metrics(result)
    bottleneck_pair = max(result.pair_allocations, key=lambda allocation: allocation.comm_time).dc_pair
    recovered = recovered_to_before(result, before_result)
    return {
        "section": section,
        "rank": rank,
        "topology": result.topology_name,
        "base_state": BASE_STATE,
        "model_name": result.model_name,
        "tensor_parallel": result.tensor_parallel,
        "pipeline_parallel": result.pipeline_parallel,
        "data_parallel": result.data_parallel,
        "n_wave": result.n_wave,
        "total_actions": sum(extra_dp_capacity_per_dc.values()) + sum(extra_waves_per_pair.values()),
        "total_extra_dp_groups": sum(extra_dp_capacity_per_dc.values()),
        "total_extra_waves": sum(extra_waves_per_pair.values()),
        "chosen_action_type": chosen_action_type,
        "focus_target": focus_target,
        "extra_dp_capacity_per_dc": json.dumps(extra_dp_capacity_per_dc, ensure_ascii=False, sort_keys=True),
        "extra_waves_per_pair": json.dumps(
            {str(list(pair)): int(value) for pair, value in sorted(extra_waves_per_pair.items()) if int(value) > 0},
            ensure_ascii=False,
            sort_keys=True,
        ),
        "T_iter": result.t_iter,
        "T_exec": structure["T_exec"],
        "T_prop": structure["T_prop"],
        "T_tx": structure["T_tx"],
        "T_stall": result.t_stall,
        "delta_T_iter_vs_no_opt": result.t_iter - no_opt_result.t_iter,
        "delta_T_stall_vs_no_opt": result.t_stall - no_opt_result.t_stall,
        "delta_T_iter_vs_before_failure": result.t_iter - before_result.t_iter,
        "delta_T_stall_vs_before_failure": result.t_stall - before_result.t_stall,
        "recovered_to_before": recovered,
        "recovery_gap_to_before": max(0.0, result.t_iter - before_result.t_iter),
        "bottleneck_pair": json.dumps(list(bottleneck_pair)),
        "note": note,
    }


def search_row(
    result,
    before_result,
    no_opt_result,
    extra_dp_capacity_per_dc: dict[int, int],
    extra_waves_per_pair: dict[tuple[int, int], int],
    candidate_action_type: str,
    focus_target: str,
    search_phase: str,
) -> dict[str, object]:
    structure = derive_time_structure_metrics(result)
    recovered = recovered_to_before(result, before_result)
    return {
        "topology": result.topology_name,
        "base_state": BASE_STATE,
        "model_name": result.model_name,
        "tensor_parallel": result.tensor_parallel,
        "pipeline_parallel": result.pipeline_parallel,
        "data_parallel": result.data_parallel,
        "n_wave": result.n_wave,
        "total_actions": sum(extra_dp_capacity_per_dc.values()) + sum(extra_waves_per_pair.values()),
        "candidate_action_type": candidate_action_type,
        "focus_target": focus_target,
        "total_extra_dp_groups": sum(extra_dp_capacity_per_dc.values()),
        "total_extra_waves": sum(extra_waves_per_pair.values()),
        "extra_dp_capacity_per_dc": json.dumps(extra_dp_capacity_per_dc, ensure_ascii=False, sort_keys=True),
        "extra_waves_per_pair": json.dumps(
            {str(list(pair)): int(value) for pair, value in sorted(extra_waves_per_pair.items()) if int(value) > 0},
            ensure_ascii=False,
            sort_keys=True,
        ),
        "T_iter": result.t_iter,
        "T_exec": structure["T_exec"],
        "T_prop": structure["T_prop"],
        "T_tx": structure["T_tx"],
        "T_stall": result.t_stall,
        "delta_T_iter_vs_no_opt": result.t_iter - no_opt_result.t_iter,
        "delta_T_stall_vs_no_opt": result.t_stall - no_opt_result.t_stall,
        "recovered_to_before": recovered,
        "recovery_gap_to_before": max(0.0, result.t_iter - before_result.t_iter),
        "search_phase": search_phase,
    }


def plot_joint_recovery(summary_rows: list[dict[str, object]], before_t_iter: float) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    rows = [row for row in summary_rows if row["section"] == "best_allocation_by_action_budget"]
    rows.sort(key=lambda row: int(row["total_actions"]))
    xs = [int(row["total_actions"]) for row in rows]
    t_iters = [float(row["T_iter"]) for row in rows]
    t_stalls = [float(row["T_stall"]) for row in rows]

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.size": 11,
            "axes.labelsize": 11,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "axes.unicode_minus": False,
        }
    )

    fig, ax1 = plt.subplots(figsize=(8.5, 4.9), dpi=220)
    ax2 = ax1.twinx()
    line1 = ax1.plot(xs, t_iters, marker="o", color="#226A8A", linewidth=2.0, label="Joint T_iter")
    line2 = ax2.plot(xs, t_stalls, marker="s", color="#B65528", linewidth=2.0, label="Joint T_stall")
    ref = ax1.axhline(before_t_iter, color="#666666", linestyle="--", linewidth=1.2, label="T_iter before failure")

    ax1.set_xlabel("Total compensation actions")
    ax1.set_ylabel("Iteration time T_iter (s)", color="#226A8A")
    ax2.set_ylabel("Sync wait time T_stall (s)", color="#B65528")
    ax1.set_xticks(xs)
    ax1.grid(axis="y", alpha=0.25, linestyle="--")

    handles = line1 + line2 + [ref]
    labels = [handle.get_label() for handle in handles]
    ax1.legend(handles, labels, loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(RECOVERY_PNG, bbox_inches="tight")
    fig.savefig(RECOVERY_PDF, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    config, refs = load_config()
    evaluator = build_evaluator(config, refs)
    model_name = config["global"]["model_name"]
    severity = FailureSeverityProfile()

    tp_base = evaluator.derive_tp_base(model_name)
    dp_base = evaluator.derive_dp_base(model_name, TOPOLOGY)
    n_wave_base = evaluator.derive_n_wave_base(TOPOLOGY)

    before_network = evaluator.evaluate(
        model_name=model_name,
        topology_name=TOPOLOGY,
        data_parallel=dp_base,
        n_wave=n_wave_base,
        use_failure_reroute=False,
        tensor_parallel_override=tp_base,
    )
    before_result = evaluator.evaluate(
        model_name=model_name,
        topology_name=TOPOLOGY,
        data_parallel=dp_base,
        n_wave=n_wave_base,
        use_failure_reroute=False,
        tensor_parallel_override=tp_base,
        pair_allocations_override=before_network.pair_allocations,
        dp_allocation_strategy="optimal_t_iter",
    )

    no_opt_network = evaluator.evaluate(
        model_name=model_name,
        topology_name=TOPOLOGY,
        data_parallel=dp_base,
        n_wave=n_wave_base,
        use_failure_reroute=True,
        tensor_parallel_override=tp_base,
    )
    no_opt_result = evaluator.evaluate(
        model_name=model_name,
        topology_name=TOPOLOGY,
        data_parallel=dp_base,
        n_wave=n_wave_base,
        use_failure_reroute=True,
        tensor_parallel_override=tp_base,
        pair_allocations_override=no_opt_network.pair_allocations,
        dp_allocation_strategy="optimal_t_iter",
    )

    dc_order = [metric.dc_id for metric in no_opt_result.local_metrics]
    pair_order = [normalized_pair(allocation.dc_pair) for allocation in no_opt_result.pair_allocations]
    dp_limits = evaluator.extra_dp_capacity_limits(
        topology_name=TOPOLOGY,
        tensor_parallel=no_opt_result.tensor_parallel,
        pipeline_parallel=no_opt_result.pipeline_parallel,
        use_failure_reroute=True,
        allow_gpu_compensation=False,
    )

    current_extra_dp = {dc_id: 0 for dc_id in dc_order}
    current_extra_waves = {pair: 0 for pair in pair_order}
    current_pair_allocations = list(no_opt_result.pair_allocations)
    current_result = no_opt_result

    summary_rows: list[dict[str, object]] = []
    search_rows: list[dict[str, object]] = []

    summary_rows.append(
        summary_row(
            section="baseline",
            result=no_opt_result,
            before_result=before_result,
            no_opt_result=no_opt_result,
            extra_dp_capacity_per_dc=current_extra_dp,
            extra_waves_per_pair=current_extra_waves,
            rank=0,
            note="faulted no_opt baseline",
        )
    )
    summary_rows.append(
        summary_row(
            section="best_allocation_by_action_budget",
            result=no_opt_result,
            before_result=before_result,
            no_opt_result=no_opt_result,
            extra_dp_capacity_per_dc=current_extra_dp,
            extra_waves_per_pair=current_extra_waves,
            rank=0,
            note="joint greedy trajectory baseline",
        )
    )

    for total_actions in range(1, MAX_TOTAL_ACTIONS + 1):
        best_result = None
        best_key = None
        best_action_type = ""
        best_focus_target = ""
        best_pair_allocations = None
        best_extra_dp = None
        best_extra_waves = None

        for dc_id in dc_order:
            if current_extra_dp[dc_id] >= dp_limits[dc_id]:
                continue
            trial_extra_dp = dict(current_extra_dp)
            trial_extra_dp[dc_id] += 1
            candidate = evaluator.evaluate(
                model_name=model_name,
                topology_name=TOPOLOGY,
                data_parallel=current_result.data_parallel,
                n_wave=max(allocation.allocated_n_wave for allocation in current_pair_allocations),
                use_failure_reroute=True,
                tensor_parallel_override=current_result.tensor_parallel,
                extra_dp_capacity_per_dc=trial_extra_dp,
                pair_allocations_override=current_pair_allocations,
                dp_allocation_strategy="optimal_t_iter",
            )
            search_rows.append(
                search_row(
                    result=candidate,
                    before_result=before_result,
                    no_opt_result=no_opt_result,
                    extra_dp_capacity_per_dc=trial_extra_dp,
                    extra_waves_per_pair=current_extra_waves,
                    candidate_action_type="compute",
                    focus_target=str(dc_id),
                    search_phase=f"joint_step_{total_actions}",
                )
            )
            key = candidate_key(candidate, before_result, dc_order, pair_order)
            if best_key is None or key < best_key:
                best_key = key
                best_result = candidate
                best_action_type = "compute"
                best_focus_target = str(dc_id)
                best_pair_allocations = list(current_pair_allocations)
                best_extra_dp = trial_extra_dp
                best_extra_waves = dict(current_extra_waves)

        for pair in pair_order:
            updated_allocations = evaluator.allocate_extra_waves_to_pairs(
                model_name=model_name,
                topology_name=TOPOLOGY,
                base_pair_allocations=current_pair_allocations,
                extra_waves_per_pair={pair: 1},
                use_failure_reroute=True,
                severity_profile=severity,
            )
            if updated_allocations is None:
                continue
            trial_extra_waves = dict(current_extra_waves)
            trial_extra_waves[pair] += 1
            candidate = evaluator.evaluate(
                model_name=model_name,
                topology_name=TOPOLOGY,
                data_parallel=current_result.data_parallel,
                n_wave=max(allocation.allocated_n_wave for allocation in updated_allocations),
                use_failure_reroute=True,
                tensor_parallel_override=current_result.tensor_parallel,
                extra_dp_capacity_per_dc=current_extra_dp,
                pair_allocations_override=updated_allocations,
                dp_allocation_strategy="optimal_t_iter",
            )
            search_rows.append(
                search_row(
                    result=candidate,
                    before_result=before_result,
                    no_opt_result=no_opt_result,
                    extra_dp_capacity_per_dc=current_extra_dp,
                    extra_waves_per_pair=trial_extra_waves,
                    candidate_action_type="bandwidth",
                    focus_target=json.dumps(list(pair)),
                    search_phase=f"joint_step_{total_actions}",
                )
            )
            key = candidate_key(candidate, before_result, dc_order, pair_order)
            if best_key is None or key < best_key:
                best_key = key
                best_result = candidate
                best_action_type = "bandwidth"
                best_focus_target = json.dumps(list(pair))
                best_pair_allocations = updated_allocations
                best_extra_dp = dict(current_extra_dp)
                best_extra_waves = trial_extra_waves

        if best_result is None or best_pair_allocations is None or best_extra_dp is None or best_extra_waves is None:
            break

        current_result = best_result
        current_pair_allocations = best_pair_allocations
        current_extra_dp = best_extra_dp
        current_extra_waves = best_extra_waves

        summary_rows.append(
            summary_row(
                section="best_allocation_by_action_budget",
                result=current_result,
                before_result=before_result,
                no_opt_result=no_opt_result,
                extra_dp_capacity_per_dc=current_extra_dp,
                extra_waves_per_pair=current_extra_waves,
                rank=total_actions,
                chosen_action_type=best_action_type,
                focus_target=best_focus_target,
                note="joint greedy trajectory",
            )
        )

    with SUMMARY_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary_rows)

    with SEARCH_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SEARCH_FIELDS)
        writer.writeheader()
        writer.writerows(search_rows)

    plot_joint_recovery(summary_rows, before_result.t_iter)

    print(f"Wrote summary CSV to {SUMMARY_CSV}")
    print(f"Wrote exhaustive search CSV to {SEARCH_CSV}")
    print(f"Wrote recovery plot to {RECOVERY_PNG}")
    print(f"Wrote recovery plot to {RECOVERY_PDF}")


if __name__ == "__main__":
    main()
