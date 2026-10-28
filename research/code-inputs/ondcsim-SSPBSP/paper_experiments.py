from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List

from paper_evaluator import (
    FailureSeverityProfile,
    PaperEvaluationResult,
    SingleTaskPaperEvaluator,
    StateEvaluationResult,
)


def derive_time_structure_metrics(result: PaperEvaluationResult) -> Dict[str, float]:
    bottleneck_pair = max(result.pair_allocations, key=lambda allocation: allocation.comm_time)
    t_exec = result.t_local_max
    t_prop = bottleneck_pair.propagation_delay_s
    t_tx = max(0.0, bottleneck_pair.comm_time - t_prop)
    denom = result.t_iter if result.t_iter > 0 else 1e-9
    return {
        "T_exec": t_exec,
        "T_tx": t_tx,
        "T_prop": t_prop,
        "bottleneck_pair_propagation_delay_s": t_prop,
        "r_exec": t_exec / denom,
        "r_tx": t_tx / denom,
        "r_prop": t_prop / denom,
        "r_stall": result.t_stall / denom,
    }


def structure_distance_to_before(current: Dict[str, float], before: Dict[str, float]) -> float:
    return (
        abs(current["r_exec"] - before["r_exec"])
        + abs(current["r_tx"] - before["r_tx"])
        + abs(current["r_prop"] - before["r_prop"])
        + abs(current["r_stall"] - before["r_stall"])
    )


def build_evaluator(paper_config: Dict, referenced_files: Dict[str, Path]) -> SingleTaskPaperEvaluator:
    global_cfg = paper_config["global"]
    baseline_cfg = paper_config["baselines"]
    distance_cfg = global_cfg.get("recovery_distance_weights", {})
    rho_gpu_overrides = {
        int(dc_id): float(rho_value)
        for dc_id, rho_value in global_cfg.get("rho_gpu_overrides", {}).items()
    }
    rho_gpu_compensation_overrides = {
        int(dc_id): float(rho_value)
        for dc_id, rho_value in global_cfg.get("rho_gpu_compensation_overrides", {}).items()
    }
    return SingleTaskPaperEvaluator(
        topology_file=str(referenced_files["topology_file"]),
        datacenters_file=str(referenced_files["datacenters_file"]),
        service_file=str(referenced_files["service_file"]),
        training_topologies_file=str(referenced_files["training_topologies_file"]),
        wavelength_state_file=(
            str(referenced_files["wavelength_state_file"])
            if referenced_files.get("wavelength_state_file") is not None
            else None
        ),
        wavelength_state_profile=global_cfg.get("wavelength_state_profile"),
        bw_wave_gbps=global_cfg["bw_wave_gbps"],
        rho_gpu=global_cfg["rho_gpu"],
        rho_gpu_overrides=rho_gpu_overrides,
        rho_gpu_compensation=float(global_cfg.get("rho_gpu_compensation", global_cfg["rho_gpu"])),
        rho_gpu_compensation_overrides=rho_gpu_compensation_overrides,
        rho_wave=global_cfg["rho_wave"],
        alpha_mode=global_cfg["alpha_mode"],
        alpha_scale=global_cfg["alpha_scale"],
        recovery_distance_weight_dp=float(distance_cfg.get("dp", 1.0)),
        recovery_distance_weight_wave=float(distance_cfg.get("wave", 1.0)),
        optical_critical_beta=float(global_cfg.get("optical_critical_beta", 0.8)),
        optical_degradation_gamma=float(global_cfg.get("optical_degradation_gamma", 0.1)),
        fixed_tp=global_cfg["fixed_tp"],
        fixed_pp=global_cfg["fixed_pp"],
        n_wave_base_cap=baseline_cfg["n_wave_base_cap"],
        ssp_bound=int(global_cfg.get("ssp_bound", 1)),
        ssp_simulation_steps=int(global_cfg.get("ssp_simulation_steps", 100)),
        dp_reserve_ratio=float(global_cfg.get("dp_reserve_ratio", 0.2)),
        dp_softness_beta=float(global_cfg.get("dp_softness_beta", 0.7)),
        min_reserved_dp_groups=int(global_cfg.get("min_reserved_dp_groups", 1)),
    )


def ensure_output_dirs(output_root: Path) -> Dict[str, Path]:
    dirs = {
        "root": output_root,
        "json": output_root / "json",
        "csv": output_root / "csv",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def run_figures(
    paper_config: Dict,
    referenced_files: Dict[str, Path],
    selected_figure_names: Iterable[str],
) -> Dict[str, Dict[str, str]]:
    evaluator = build_evaluator(paper_config, referenced_files)
    output_root = Path(paper_config["global"]["output_dir"]).resolve()
    output_dirs = ensure_output_dirs(output_root)

    results: Dict[str, Dict[str, str]] = {}
    for figure_name in selected_figure_names:
        if figure_name == "figure1":
            payload = run_figure1_experiment(paper_config, evaluator)
        elif figure_name == "figure2":
            payload = run_figure2_experiment(paper_config, evaluator)
        elif figure_name == "figure3":
            payload = run_figure3_experiment(paper_config, evaluator)
        else:
            raise ValueError(f"Unsupported figure name: {figure_name}")

        json_path = output_dirs["json"] / f"{figure_name}.json"
        csv_path = output_dirs["csv"] / f"{figure_name}.csv"
        write_json(json_path, payload)
        write_csv(csv_path, payload["rows"])
        results[figure_name] = {
            "json": str(json_path),
            "csv": str(csv_path),
        }
    return results


def run_figure1_experiment(paper_config: Dict, evaluator: SingleTaskPaperEvaluator) -> Dict:
    figure_cfg = paper_config["figure1"]
    model_name = paper_config["global"]["model_name"]
    states = ["before_failure"] + list(paper_config["global"]["compare_states"])
    rows: List[Dict] = []

    for topology_name in figure_cfg["training_topologies"]:
        before_state_result = evaluator.evaluate_state(model_name, topology_name, "before_failure")
        before_structure = derive_time_structure_metrics(before_state_result.result)
        for state_name in states:
            state_result = before_state_result if state_name == "before_failure" else evaluator.evaluate_state(
                model_name,
                topology_name,
                state_name,
            )
            rows.append(flatten_state_result(state_result, before_structure_metrics=before_structure))

    return {
        "figure": "figure1",
        "model_name": model_name,
        "rows": rows,
    }


def run_figure2_experiment(paper_config: Dict, evaluator: SingleTaskPaperEvaluator) -> Dict:
    figure_cfg = paper_config["figure2"]
    model_name = paper_config["global"]["model_name"]
    topology_name = figure_cfg["training_topology"]
    states = ["no_opt", "pure_compute"]
    rows: List[Dict] = []

    severity_levels = figure_cfg.get("severity_levels", [])
    dp_base = evaluator.derive_dp_base(model_name, topology_name)
    n_wave_base = evaluator.derive_n_wave_base(topology_name)
    before_result = evaluator.evaluate(
        model_name=model_name,
        topology_name=topology_name,
        data_parallel=dp_base,
        n_wave=n_wave_base,
        use_failure_reroute=False,
    )
    before_structure = derive_time_structure_metrics(before_result)
    for level_cfg in severity_levels:
        severity = FailureSeverityProfile(
            name=level_cfg["name"],
            reroute_length_scale=float(level_cfg["reroute_length_scale"]),
            reroute_bandwidth_scale=float(level_cfg["reroute_bandwidth_scale"]),
        )
        for state_name in states:
            state_result = evaluator.evaluate_state(
                model_name,
                topology_name,
                state_name,
                severity_profile=severity,
            )
            rows.append(flatten_state_result(state_result, before_structure_metrics=before_structure))

    return {
        "figure": "figure2",
        "model_name": model_name,
        "x_metric": figure_cfg.get("x_metric"),
        "y_metric": figure_cfg.get("y_metric"),
        "aux_metric": figure_cfg.get("aux_metric"),
        "rows": rows,
    }


def run_figure3_experiment(paper_config: Dict, evaluator: SingleTaskPaperEvaluator) -> Dict:
    figure_cfg = paper_config["figure3"]
    model_name = paper_config["global"]["model_name"]
    topology_name = figure_cfg["training_topology"]
    dp_base = evaluator.derive_dp_base(model_name, topology_name)
    tp_base = evaluator.derive_tp_base(model_name)
    configured_tp_values = figure_cfg.get("tp_scan_values")
    if configured_tp_values:
        tp_values = [int(value) for value in configured_tp_values]
    else:
        tp_values = evaluator.derive_tp_scan_values(model_name, topology_name, dp_base)
    n_wave_base = evaluator.derive_n_wave_base(topology_name)
    rows: List[Dict] = []

    for tensor_parallel in tp_values:
        pure_compute = evaluator.evaluate(
            model_name=model_name,
            topology_name=topology_name,
            data_parallel=dp_base,
            n_wave=n_wave_base,
            use_failure_reroute=True,
            tensor_parallel_override=tensor_parallel,
            allow_gpu_compensation=True,
        )
        rows.append(
            flatten_result(
                pure_compute,
                state_name="pure_compute",
                topology_name=topology_name,
                dp_base=dp_base,
                tp_base=tp_base,
                n_wave_base=n_wave_base,
            )
        )

        budgets = evaluator.get_budget_snapshot(topology_name, use_failure_reroute=True)
        joint_candidates = [
            evaluator.evaluate(
                model_name=model_name,
                topology_name=topology_name,
                data_parallel=dp_base,
                n_wave=n_wave,
                use_failure_reroute=True,
                tensor_parallel_override=tensor_parallel,
                allow_gpu_compensation=True,
            )
            for n_wave in range(1, budgets.effective_max_waves + 1)
        ]
        joint = min(joint_candidates, key=lambda candidate: candidate.t_iter)
        rows.append(
            flatten_result(
                joint,
                state_name="joint",
                topology_name=topology_name,
                dp_base=dp_base,
                tp_base=tp_base,
                n_wave_base=n_wave_base,
            )
        )

    return {
        "figure": "figure3",
        "model_name": model_name,
        "rows": rows,
        "tp_values": tp_values,
    }


def flatten_state_result(
    state_result: StateEvaluationResult,
    before_structure_metrics: Dict[str, float] | None = None,
) -> Dict:
    return flatten_result(
        state_result.result,
        state_name=state_result.state_name,
        topology_name=state_result.result.topology_name,
        dp_base=state_result.dp_base,
        tp_base=state_result.tp_base,
        n_wave_base=state_result.n_wave_base,
        before_structure_metrics=before_structure_metrics,
        extra_fields={
            "recovery_target_t_iter": state_result.recovery_target_t_iter,
            "recovered_to_before": state_result.recovered_to_before,
        },
    )


def flatten_result(
    result: PaperEvaluationResult,
    state_name: str,
    topology_name: str,
    dp_base: int,
    tp_base: int,
    n_wave_base: int,
    before_structure_metrics: Dict[str, float] | None = None,
    extra_fields: Dict | None = None,
) -> Dict:
    local_dp_distribution = {metric.dc_id: metric.local_dp for metric in result.local_metrics}
    allocated_gpu_distribution = {metric.dc_id: metric.allocated_gpus for metric in result.local_metrics}
    total_allocated_training_gpus = sum(metric.allocated_gpus for metric in result.local_metrics)
    bottleneck_pair = max(result.pair_allocations, key=lambda allocation: allocation.comm_time)
    structure_metrics = derive_time_structure_metrics(result)
    row = {
        "figure_topology": topology_name,
        "state": state_name,
        "model_name": result.model_name,
        "use_failure_reroute": result.use_failure_reroute,
        "severity_name": result.severity_name,
        "reroute_length_scale": result.reroute_length_scale,
        "reroute_bandwidth_scale": result.reroute_bandwidth_scale,
        "dp_base": dp_base,
        "tp_base": tp_base,
        "n_wave_base": n_wave_base,
        "data_parallel": result.data_parallel,
        "optimized_data_parallel": "",
        "tensor_parallel": result.tensor_parallel,
        "optimized_tensor_parallel": result.tensor_parallel if state_name in {"pure_compute", "joint"} else "",
        "pipeline_parallel": result.pipeline_parallel,
        "n_wave": result.n_wave,
        "recovery_n_wave": result.n_wave,
        "alpha": result.alpha,
        "T_iter": result.t_iter,
        "T_inter": result.t_inter,
        "T_local_max": result.t_local_max,
        "T_comp_max": result.t_comp_max,
        "T_stall": result.t_stall,
        "T_exec": structure_metrics["T_exec"],
        "T_tx": structure_metrics["T_tx"],
        "T_prop": structure_metrics["T_prop"],
        "delta_balance": result.delta_balance,
        "imbalance_ratio": result.imbalance_ratio,
        "r_inter": result.r_inter,
        "r_comp": (result.t_comp_max / result.t_iter) if result.t_iter > 0 else 0.0,
        "r_exec": structure_metrics["r_exec"],
        "r_tx": structure_metrics["r_tx"],
        "r_prop": structure_metrics["r_prop"],
        "r_stall": structure_metrics["r_stall"],
        "structure_distance_to_before": (
            structure_distance_to_before(structure_metrics, before_structure_metrics)
            if before_structure_metrics is not None
            else None
        ),
        "recovery_gap_to_before": None,
        "bandwidth_eff_gbps": result.bandwidth_eff_gbps,
        "max_path_length_km": result.max_path_length_km,
        "max_path_propagation_delay_s": result.max_path_propagation_delay_s,
        "propagation_latency_growth_ratio": result.propagation_latency_growth_ratio,
        "bottleneck_pair": json.dumps(bottleneck_pair.dc_pair),
        "bottleneck_pair_comm_time": bottleneck_pair.comm_time,
        "bottleneck_pair_propagation_delay_s": structure_metrics["bottleneck_pair_propagation_delay_s"],
        "bottleneck_pair_bandwidth_gbps": bottleneck_pair.bandwidth_gbps,
        "bottleneck_pair_path_length_km": bottleneck_pair.path_length_km,
        "bottleneck_pair_allocated_n_wave": bottleneck_pair.allocated_n_wave,
        "bottleneck_pair_link_ids": json.dumps(bottleneck_pair.link_ids),
        "optical_extra_waves": result.optical_extra_waves,
        "optical_compensation_steps": result.optical_compensation_steps,
        "optical_last_marginal_gain": (
            result.optical_marginal_gain_trace[-1]
            if result.optical_marginal_gain_trace
            else 0.0
        ),
        "optical_marginal_gain_trace": json.dumps(result.optical_marginal_gain_trace),
        "optical_t_iter_trace": json.dumps(result.optical_t_iter_trace),
        "optical_t_stall_trace": json.dumps(result.optical_t_stall_trace),
        "avg_progress_gap": result.avg_progress_gap,
        "max_progress_gap": result.max_progress_gap,
        "ssp_bound": result.ssp_bound,
        "ssp_simulation_steps": result.ssp_simulation_steps,
        "total_effective_gpus": result.budgets.total_effective_gpus,
        "total_dp_capacity": result.budgets.total_dp_capacity,
        "total_allocated_training_gpus": total_allocated_training_gpus,
        "gpu_compensation_enabled": result.gpu_compensation_enabled,
        "effective_max_waves": result.budgets.effective_max_waves,
        "raw_max_waves": result.budgets.raw_max_waves,
        "local_dp_distribution": json.dumps(local_dp_distribution, ensure_ascii=False, sort_keys=True),
        "allocated_gpu_distribution": json.dumps(allocated_gpu_distribution, ensure_ascii=False, sort_keys=True),
    }
    if extra_fields:
        row.update(extra_fields)
    if "recovery_target_t_iter" in row and row["recovery_target_t_iter"] is not None:
        row["recovery_gap_to_before"] = result.t_iter - row["recovery_target_t_iter"]
    return row


def write_json(path: Path, payload: Dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        with path.open("w", encoding="utf-8", newline="") as file:
            file.write("")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
