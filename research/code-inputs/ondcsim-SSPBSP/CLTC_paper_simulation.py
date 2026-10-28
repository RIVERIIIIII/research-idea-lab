#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import yaml

from paper_experiments import run_figures


REQUIRED_STRATEGIES = (
    "before_failure",
    "no_opt",
    "pure_optical",
    "pure_compute",
    "joint",
)
FIGURE_NAMES = ("figure1", "figure2", "figure3")


def load_yaml_file(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping at the root: {path}")
    return data


def resolve_path(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()

    candidates = (
        (base_dir / path).resolve(),
        (Path.cwd() / path).resolve(),
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def require_mapping(parent: Dict, key: str) -> Dict:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Expected '{key}' to be a mapping.")
    return value


def validate_config(config: Dict, config_dir: Path) -> Tuple[Dict, Dict]:
    paper_config = require_mapping(config, "paper_experiment")
    global_cfg = require_mapping(paper_config, "global")
    strategies = require_mapping(paper_config, "strategies")

    for strategy_name in REQUIRED_STRATEGIES:
        if strategy_name not in strategies:
            raise ValueError(f"Missing required strategy config: {strategy_name}")

    referenced_files = {
        "topology_file": resolve_path(config_dir, global_cfg["topology_file"]),
        "datacenters_file": resolve_path(config_dir, global_cfg["datacenters_file"]),
        "service_file": resolve_path(config_dir, global_cfg["service_file"]),
        "training_topologies_file": resolve_path(config_dir, global_cfg["training_topologies_file"]),
    }
    wavelength_state_file = global_cfg.get("wavelength_state_file")
    if wavelength_state_file:
        referenced_files["wavelength_state_file"] = resolve_path(config_dir, wavelength_state_file)
    for label, path in referenced_files.items():
        if not path.exists():
            raise FileNotFoundError(f"Configured {label} does not exist: {path}")

    return paper_config, referenced_files


def load_training_topologies(path: Path) -> Dict:
    training_cfg = load_yaml_file(path)
    topologies = training_cfg.get("topologies")
    if not isinstance(topologies, dict) or not topologies:
        raise ValueError("training_topologies.yaml must define a non-empty 'topologies' mapping.")
    return topologies


def selected_figures(figure_arg: str) -> Iterable[str]:
    if figure_arg == "all":
        return FIGURE_NAMES
    return (figure_arg,)


def validate_figure_references(paper_config: Dict, available_topologies: Dict, figures: Iterable[str]) -> None:
    for figure_name in figures:
        figure_cfg = require_mapping(paper_config, figure_name)
        if figure_name == "figure1":
            topo_names = figure_cfg.get("training_topologies", [])
            if not isinstance(topo_names, list) or not topo_names:
                raise ValueError("figure1.training_topologies must be a non-empty list.")
        else:
            topo_names = [figure_cfg.get("training_topology")]
            if topo_names[0] is None:
                raise ValueError(f"{figure_name}.training_topology is required.")

        for topo_name in topo_names:
            if topo_name not in available_topologies:
                raise ValueError(f"{figure_name} references unknown training topology: {topo_name}")


def summarize_figure(paper_config: Dict, figure_name: str, available_topologies: Dict) -> str:
    figure_cfg = paper_config[figure_name]
    if figure_name == "figure1":
        topo_names: List[str] = figure_cfg["training_topologies"]
    else:
        topo_names = [figure_cfg["training_topology"]]

    topo_sizes = [len(available_topologies[name]["dc_nodes"]) for name in topo_names]
    return (
        f"{figure_name}: topologies={topo_names}, "
        f"dc_counts={topo_sizes}, "
        f"x_metric={figure_cfg.get('x_metric')}, "
        f"y_metric={figure_cfg.get('y_metric')}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CLTC paper simulation entrypoint for single-task fault-recovery experiments."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="data/paper_experiment.yaml",
        help="Path to the paper experiment configuration file.",
    )
    parser.add_argument(
        "--figure",
        choices=("all",) + FIGURE_NAMES,
        default="all",
        help="Run or validate one figure section, or all figure sections.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and print the resolved experiment summary without running simulations.",
    )
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = load_yaml_file(config_path)
    paper_config, referenced_files = validate_config(config, config_path.parent)
    available_topologies = load_training_topologies(referenced_files["training_topologies_file"])
    figures = tuple(selected_figures(args.figure))
    validate_figure_references(paper_config, available_topologies, figures)

    global_cfg = paper_config["global"]
    print("CLTC paper experiment configuration loaded successfully.")
    print(f"Config: {config_path}")
    print(f"Model: {global_cfg['model_name']}")
    print(f"Budget factors: rho_gpu={global_cfg['rho_gpu']}, rho_wave={global_cfg['rho_wave']}")
    rho_gpu_overrides = global_cfg.get("rho_gpu_overrides", {})
    if rho_gpu_overrides:
        print(f"Per-DC rho_gpu overrides: {rho_gpu_overrides}")
    if global_cfg.get("wavelength_state_profile"):
        print(
            "Wavelength state profile: "
            f"{global_cfg['wavelength_state_profile']} "
            f"({referenced_files['wavelength_state_file']})"
        )
    print(f"Collective alpha: mode={global_cfg['alpha_mode']}, scale={global_cfg['alpha_scale']}")
    distance_cfg = global_cfg.get("recovery_distance_weights", {})
    print(
        "Recovery distance weights: "
        f"dp={distance_cfg.get('dp', 1.0)}, wave={distance_cfg.get('wave', 1.0)}"
    )
    print(
        "Optical compensation thresholds: "
        f"beta={global_cfg.get('optical_critical_beta', 0.8)}, "
        f"gamma={global_cfg.get('optical_degradation_gamma', 0.1)}"
    )
    print(f"Fixed TP/PP: tp={global_cfg['fixed_tp']}, pp={global_cfg['fixed_pp']}")
    print(
        "SSP simulation: "
        f"bound={global_cfg.get('ssp_bound', 1)}, steps={global_cfg.get('ssp_simulation_steps', 100)}"
    )
    print("Strategies:", ", ".join(name for name in REQUIRED_STRATEGIES if paper_config["strategies"][name]["enabled"]))
    print(f"Selected figures: {', '.join(figures)}")
    for figure_name in figures:
        print("  " + summarize_figure(paper_config, figure_name, available_topologies))

    if args.dry_run:
        print("Dry run complete. No simulations were executed.")
        return 0

    generated_files = run_figures(paper_config, referenced_files, figures)
    print("Paper experiments completed.")
    for figure_name in figures:
        figure_files = generated_files[figure_name]
        print(f"  {figure_name}:")
        print(f"    json: {figure_files['json']}")
        print(f"    csv: {figure_files['csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
