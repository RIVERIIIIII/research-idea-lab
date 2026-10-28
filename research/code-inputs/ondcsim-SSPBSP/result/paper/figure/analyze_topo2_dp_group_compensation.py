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
import yaml

CONFIG_PATH = ROOT / "data" / "paper_experiment.yaml"
OUT_DIR = ROOT / "result" / "paper" / "csv"
SUMMARY_CSV = OUT_DIR / "topo2_dp_group_compensation_summary.csv"
SEARCH_CSV = OUT_DIR / "topo2_dp_group_compensation_search.csv"
FIGURE_DIR = ROOT / "result" / "paper" / "figure"
RECOVERY_PNG = FIGURE_DIR / "topo2_dp_group_compensation_recovery.png"
RECOVERY_PDF = FIGURE_DIR / "topo2_dp_group_compensation_recovery.pdf"
TOPOLOGY = "topo2"
BASE_STATE = "no_opt"
MAX_EXTRA_DP_GROUPS = 16


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
    "unit_gpus_per_extra_dp_group",
    "total_extra_dp_groups",
    "focus_dc",
    "extra_dp_capacity_per_dc",
    "extra_dp_capacity_vector",
    "T_iter",
    "T_exec",
    "T_prop",
    "T_tx",
    "T_stall",
    "delta_T_iter_vs_no_opt",
    "delta_T_stall_vs_no_opt",
    "delta_T_iter_vs_before_failure",
    "delta_T_stall_vs_before_failure",
    "limits_per_dc",
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
    "unit_gpus_per_extra_dp_group",
    "total_extra_dp_groups",
    "extra_dp_capacity_per_dc",
    "extra_dp_capacity_vector",
    "T_iter",
    "T_exec",
    "T_prop",
    "T_tx",
    "T_stall",
    "delta_T_iter_vs_no_opt",
    "delta_T_stall_vs_no_opt",
    "candidate_focus_dc",
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


def metrics_row(
    section: str,
    result,
    before_result,
    no_opt_result,
    unit_gpus: int,
    limits_per_dc: dict[int, int],
    rank: int | str = "",
    focus_dc: int | str = "",
    note: str = "",
) -> dict[str, object]:
    structure = derive_time_structure_metrics(result)
    extra_dp = dict(result.extra_dp_capacity_per_dc or {})
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
        "unit_gpus_per_extra_dp_group": unit_gpus,
        "total_extra_dp_groups": result.total_extra_dp_groups,
        "focus_dc": focus_dc,
        "extra_dp_capacity_per_dc": json.dumps(extra_dp, ensure_ascii=False, sort_keys=True),
        "extra_dp_capacity_vector": json.dumps(
            [extra_dp.get(metric.dc_id, 0) for metric in result.local_metrics],
            ensure_ascii=False,
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
        "limits_per_dc": json.dumps(limits_per_dc, ensure_ascii=False, sort_keys=True),
        "note": note,
    }


def search_row(result, no_opt_result, unit_gpus: int) -> dict[str, object]:
    structure = derive_time_structure_metrics(result)
    extra_dp = dict(result.extra_dp_capacity_per_dc or {})
    return {
        "topology": result.topology_name,
        "base_state": BASE_STATE,
        "model_name": result.model_name,
        "tensor_parallel": result.tensor_parallel,
        "pipeline_parallel": result.pipeline_parallel,
        "data_parallel": result.data_parallel,
        "n_wave": result.n_wave,
        "unit_gpus_per_extra_dp_group": unit_gpus,
        "total_extra_dp_groups": result.total_extra_dp_groups,
        "extra_dp_capacity_per_dc": json.dumps(extra_dp, ensure_ascii=False, sort_keys=True),
        "extra_dp_capacity_vector": json.dumps(
            [extra_dp.get(metric.dc_id, 0) for metric in result.local_metrics],
            ensure_ascii=False,
        ),
        "T_iter": result.t_iter,
        "T_exec": structure["T_exec"],
        "T_prop": structure["T_prop"],
        "T_tx": structure["T_tx"],
        "T_stall": result.t_stall,
        "delta_T_iter_vs_no_opt": result.t_iter - no_opt_result.t_iter,
        "delta_T_stall_vs_no_opt": result.t_stall - no_opt_result.t_stall,
    }


def plot_recovery_curve(summary_rows: list[dict[str, object]]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    k_rows = [
        row for row in summary_rows
        if row["section"] == "best_allocation_by_k"
    ]
    k_rows.sort(key=lambda row: int(row["total_extra_dp_groups"]))
    ks = [int(row["total_extra_dp_groups"]) for row in k_rows]
    t_iters = [float(row["T_iter"]) for row in k_rows]
    t_stalls_ms = [float(row["T_stall"]) * 1000.0 for row in k_rows]

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.size": 18,
            "axes.labelsize": 21,
            "legend.fontsize": 19,
            "xtick.labelsize": 18,
            "ytick.labelsize": 18,
            "axes.unicode_minus": False,
        }
    )

    fig, ax1 = plt.subplots(figsize=(8.4, 4.8), dpi=220)
    ax2 = ax1.twinx()

    line1 = ax1.plot(ks, t_iters, marker="o", color="#24577A", linewidth=2.0, label="Iteration time")
    line2 = ax2.plot(ks, t_stalls_ms, marker="s", color="#C4632E", linewidth=2.0, label="Sync waiting time")

    ax1.set_xlabel("Number of extra DP groups")
    ax1.set_ylabel("Iteration time (s)", color="#24577A")
    ax2.set_ylabel("Sync waiting time (ms)", color="#C4632E")
    ax1.set_xticks(ks)
    ax1.grid(axis="y", alpha=0.25, linestyle="--")

    handles = line1 + line2
    labels = [handle.get_label() for handle in handles]
    ax1.legend(handles, labels, loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(RECOVERY_PNG, bbox_inches="tight")
    fig.savefig(RECOVERY_PDF, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    config, refs = load_config()
    evaluator = build_evaluator(config, refs)
    model_name = config["global"]["model_name"]

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

    tensor_parallel = no_opt_result.tensor_parallel
    pipeline_parallel = no_opt_result.pipeline_parallel
    unit_gpus = tensor_parallel * pipeline_parallel

    limits_per_dc = evaluator.extra_dp_capacity_limits(
        topology_name=TOPOLOGY,
        tensor_parallel=tensor_parallel,
        pipeline_parallel=pipeline_parallel,
        use_failure_reroute=True,
        allow_gpu_compensation=False,
    )

    summary_rows: list[dict[str, object]] = []
    search_rows: list[dict[str, object]] = []
    dc_order = [metric.dc_id for metric in no_opt_result.local_metrics]

    summary_rows.append(
        metrics_row(
            section="baseline",
            result=no_opt_result,
            before_result=before_result,
            no_opt_result=no_opt_result,
            unit_gpus=unit_gpus,
            limits_per_dc=limits_per_dc,
            rank=1,
            note="faulted no_opt baseline",
        )
    )
    search_rows.append(
        {
            **search_row(no_opt_result, no_opt_result, unit_gpus),
            "candidate_focus_dc": "",
            "search_phase": "baseline",
        }
    )

    single_group_results = []
    for dc_id, limit in sorted(limits_per_dc.items()):
        if limit < 1:
            continue
        candidate = evaluator.evaluate(
            model_name=model_name,
            topology_name=TOPOLOGY,
            data_parallel=no_opt_result.data_parallel,
            n_wave=no_opt_result.n_wave,
            use_failure_reroute=True,
            severity_profile=None,
            tensor_parallel_override=tensor_parallel,
            extra_dp_capacity_per_dc={dc_id: 1},
            pair_allocations_override=no_opt_result.pair_allocations,
            dp_allocation_strategy="optimal_t_iter",
        )
        single_group_results.append((dc_id, candidate))

    single_group_results.sort(
        key=lambda item: (
            item[1].t_iter,
            item[1].t_stall,
            tuple(item[1].extra_dp_capacity_per_dc.get(metric.dc_id, 0) for metric in item[1].local_metrics),
        )
    )
    for rank, (dc_id, candidate) in enumerate(single_group_results, start=1):
        summary_rows.append(
            metrics_row(
                section="single_group_marginal",
                result=candidate,
                before_result=before_result,
                no_opt_result=no_opt_result,
                unit_gpus=unit_gpus,
                limits_per_dc=limits_per_dc,
                rank=rank,
                focus_dc=dc_id,
                note="+1 extra DP group on a single DC",
            )
        )

    current_allocation = {dc_id: 0 for dc_id in dc_order}
    summary_rows.append(
        metrics_row(
            section="best_allocation_by_k",
            result=no_opt_result,
            before_result=before_result,
            no_opt_result=no_opt_result,
            unit_gpus=unit_gpus,
            limits_per_dc=limits_per_dc,
            rank=0,
            note="greedy best allocation for the given total extra DP groups",
        )
    )

    for total_extra in range(1, MAX_EXTRA_DP_GROUPS + 1):
        best_result = None
        best_key = None
        best_focus_dc = None
        for dc_id in dc_order:
            if current_allocation[dc_id] >= limits_per_dc[dc_id]:
                continue
            allocation = dict(current_allocation)
            allocation[dc_id] += 1
            candidate = evaluator.evaluate(
                model_name=model_name,
                topology_name=TOPOLOGY,
                data_parallel=no_opt_result.data_parallel,
                n_wave=no_opt_result.n_wave,
                use_failure_reroute=True,
                severity_profile=None,
                tensor_parallel_override=tensor_parallel,
                extra_dp_capacity_per_dc=allocation,
                pair_allocations_override=no_opt_result.pair_allocations,
                dp_allocation_strategy="optimal_t_iter",
            )
            search_rows.append(
                {
                    **search_row(candidate, no_opt_result, unit_gpus),
                    "candidate_focus_dc": dc_id,
                    "search_phase": f"greedy_k_{total_extra}",
                }
            )
            candidate_key = (
                candidate.t_iter,
                candidate.t_stall,
                tuple(candidate.extra_dp_capacity_per_dc.get(dc, 0) for dc in dc_order),
            )
            if best_key is None or candidate_key < best_key:
                best_key = candidate_key
                best_result = candidate
                best_focus_dc = dc_id

        if best_result is None:
            raise RuntimeError(f"No feasible candidate found for total_extra_dp_groups={total_extra}.")
        current_allocation = dict(best_result.extra_dp_capacity_per_dc or {})
        summary_rows.append(
            metrics_row(
                section="best_allocation_by_k",
                result=best_result,
                before_result=before_result,
                no_opt_result=no_opt_result,
                unit_gpus=unit_gpus,
                limits_per_dc=limits_per_dc,
                rank=total_extra,
                focus_dc=(best_focus_dc if best_focus_dc is not None else ""),
                note="greedy best allocation for the given total extra DP groups",
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

    plot_recovery_curve(summary_rows)

    print(f"Wrote summary CSV to {SUMMARY_CSV}")
    print(f"Wrote exhaustive search CSV to {SEARCH_CSV}")
    print(f"Wrote recovery plot to {RECOVERY_PNG}")
    print(f"Wrote recovery plot to {RECOVERY_PDF}")


if __name__ == "__main__":
    main()
