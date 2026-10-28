import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = ROOT / "result" / "paper"
CSV_DIR = PAPER_DIR / "csv"
OUT_DIR = PAPER_DIR / "figure"
FIGURE1_CSV = CSV_DIR / "figure1.csv"
FIGURE3_CSV = CSV_DIR / "figure3.csv"
FIGURE_CSV = CSV_DIR / "figure.csv"
TOPOLOGY = "topo2"

STATE_ORDER = [
    "before_failure",
    "no_opt",
    "pure_optical",
    "pure_compute",
    "joint",
]

STATE_LABEL = {
    "before_failure": "Before Failure",
    "no_opt": "No Compensation",
    "pure_optical": "Optical Only",
    "pure_compute": "Compute Only",
    "joint": "Joint",
}

STATE_BREAKDOWN_METRICS = [
    ("Iteration time", "T_iter", "s", "Single-step iteration time T_iter"),
    ("Bottleneck DC exec time", "T_exec", "s", "Bottleneck DC local execution time T_exec"),
    ("Bottleneck pair comm time", "bottleneck_pair_comm_time", "s", "Bottleneck pair total communication time"),
    ("Sync wait time", "T_stall", "s", "BSP-style synchronization waiting time T_stall"),
]

FIGURE_CSV_FIELDS = [
    "plot_name",
    "x",
    "x_unit",
    "x_order",
    "state",
    "series",
    "value",
    "value_unit",
    "value_definition",
    "tensor_parallel",
    "n_wave",
    "total_allocated_training_gpus",
    "note",
]


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)
    if not rows:
        raise RuntimeError(f"Empty CSV: {path}")
    return rows


def load_figure1_rows() -> list[dict[str, str]]:
    rows = [row for row in load_csv_rows(FIGURE1_CSV) if row["figure_topology"] == TOPOLOGY]
    if not rows:
        raise RuntimeError(f"No rows found for topology '{TOPOLOGY}' in {FIGURE1_CSV}.")
    return rows


def load_figure3_rows() -> list[dict[str, str]]:
    rows = [row for row in load_csv_rows(FIGURE3_CSV) if row["figure_topology"] == TOPOLOGY]
    if not rows:
        raise RuntimeError(f"No rows found for topology '{TOPOLOGY}' in {FIGURE3_CSV}.")
    return rows


def row_by_state(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    mapping = {row["state"]: row for row in rows}
    missing = [state for state in STATE_ORDER if state not in mapping]
    if missing:
        raise RuntimeError(f"Missing states in figure1.csv for {TOPOLOGY}: {missing}")
    return mapping


def parse_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def parse_int(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.size": 11,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "legend.fontsize": 9,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "axes.unicode_minus": False,
        }
    )


def export_figure_csv(
    figure1_rows_by_state: dict[str, dict[str, str]],
    figure3_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    exported_rows: list[dict[str, object]] = []

    for x_order, state in enumerate(STATE_ORDER):
        row = figure1_rows_by_state[state]
        for series, field, unit, definition in STATE_BREAKDOWN_METRICS:
            exported_rows.append(
                {
                    "plot_name": "topo2_state_breakdown",
                    "x": STATE_LABEL[state],
                    "x_unit": "category",
                    "x_order": x_order,
                    "state": state,
                    "series": series,
                    "value": parse_float(row, field),
                    "value_unit": unit,
                    "value_definition": definition,
                    "tensor_parallel": parse_int(row, "tensor_parallel"),
                    "n_wave": parse_int(row, "n_wave"),
                    "total_allocated_training_gpus": parse_int(row, "total_allocated_training_gpus"),
                    "note": "",
                }
            )

    optical_row = figure1_rows_by_state["pure_optical"]
    optical_t_iter_trace = [float(value) for value in json.loads(optical_row["optical_t_iter_trace"])]
    optical_t_stall_trace = [float(value) for value in json.loads(optical_row["optical_t_stall_trace"])]
    for x_order, (t_iter_value, t_stall_value) in enumerate(zip(optical_t_iter_trace, optical_t_stall_trace)):
        exported_rows.append(
            {
                "plot_name": "topo2_optical_ablation",
                "x": x_order,
                "x_unit": "wavelength_count",
                "x_order": x_order,
                "state": "pure_optical",
                "series": "T_iter",
                "value": t_iter_value,
                "value_unit": "s",
                "value_definition": "Single-step iteration time T_iter",
                "tensor_parallel": parse_int(optical_row, "tensor_parallel"),
                "n_wave": "",
                "total_allocated_training_gpus": parse_int(optical_row, "total_allocated_training_gpus"),
                "note": "compensated_wavelengths",
            }
        )
        exported_rows.append(
            {
                "plot_name": "topo2_optical_ablation",
                "x": x_order,
                "x_unit": "wavelength_count",
                "x_order": x_order,
                "state": "pure_optical",
                "series": "Sync wait time",
                "value": t_stall_value,
                "value_unit": "s",
                "value_definition": "BSP-style synchronization waiting time T_stall",
                "tensor_parallel": parse_int(optical_row, "tensor_parallel"),
                "n_wave": "",
                "total_allocated_training_gpus": parse_int(optical_row, "total_allocated_training_gpus"),
                "note": "compensated_wavelengths",
            }
        )

    baseline_row = figure1_rows_by_state["no_opt"]
    pure_compute_rows = [row for row in figure3_rows if row["state"] == "pure_compute"]
    pure_compute_rows.sort(key=lambda row: parse_int(row, "total_allocated_training_gpus"))
    if not pure_compute_rows:
        raise RuntimeError("No pure_compute rows found for topo2 in figure3.csv.")

    compute_points = [baseline_row] + pure_compute_rows
    for x_order, row in enumerate(compute_points):
        exported_rows.append(
            {
                "plot_name": "topo2_compute_ablation",
                "x": parse_int(row, "total_allocated_training_gpus"),
                "x_unit": "gpu_count",
                "x_order": x_order,
                "state": row["state"],
                "series": "T_iter",
                "value": parse_float(row, "T_iter"),
                "value_unit": "s",
                "value_definition": "Single-step iteration time T_iter",
                "tensor_parallel": parse_int(row, "tensor_parallel"),
                "n_wave": parse_int(row, "n_wave"),
                "total_allocated_training_gpus": parse_int(row, "total_allocated_training_gpus"),
                "note": "allocated_gpus",
            }
        )
        exported_rows.append(
            {
                "plot_name": "topo2_compute_ablation",
                "x": parse_int(row, "total_allocated_training_gpus"),
                "x_unit": "gpu_count",
                "x_order": x_order,
                "state": row["state"],
                "series": "Compute time ratio",
                "value": parse_float(row, "r_comp"),
                "value_unit": "ratio",
                "value_definition": "Computation share T_comp / T_iter",
                "tensor_parallel": parse_int(row, "tensor_parallel"),
                "n_wave": parse_int(row, "n_wave"),
                "total_allocated_training_gpus": parse_int(row, "total_allocated_training_gpus"),
                "note": "allocated_gpus",
            }
        )

    with FIGURE_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIGURE_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(exported_rows)

    return exported_rows


def plot_state_breakdown(rows: dict[str, dict[str, str]]) -> None:
    states = [STATE_LABEL[state] for state in STATE_ORDER]
    metrics = {
        "Iteration time": [parse_float(rows[state], "T_iter") for state in STATE_ORDER],
        "Bottleneck DC exec time": [parse_float(rows[state], "T_exec") for state in STATE_ORDER],
        "Bottleneck pair comm time": [parse_float(rows[state], "bottleneck_pair_comm_time") for state in STATE_ORDER],
        "Sync wait time": [parse_float(rows[state], "T_stall") for state in STATE_ORDER],
    }
    colors = {
        "Iteration time": "#4C78A8",
        "Bottleneck DC exec time": "#F58518",
        "Bottleneck pair comm time": "#54A24B",
        "Sync wait time": "#E45756",
    }

    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    group_count = len(states)
    bar_count = len(metrics)
    total_group_width = 0.8
    bar_width = total_group_width / bar_count
    centers = list(range(group_count))
    metric_names = list(metrics.keys())
    offsets = [(-total_group_width / 2) + (i + 0.5) * bar_width for i in range(bar_count)]

    for idx, metric_name in enumerate(metric_names):
        xs = [c + offsets[idx] for c in centers]
        ax.bar(xs, metrics[metric_name], width=bar_width * 0.92, label=metric_name, color=colors[metric_name])

    ax.set_xticks(centers)
    ax.set_xticklabels(states, rotation=12)
    ax.set_ylabel("Time (s)")
    ax.set_title("Topo2 State-wise Time Breakdown")
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, loc="upper right")
    fig.tight_layout()

    fig.savefig(OUT_DIR / "topo2_state_breakdown_bar.png", bbox_inches="tight")
    fig.savefig(OUT_DIR / "topo2_state_breakdown_bar.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_optical_ablation(rows: dict[str, dict[str, str]]) -> None:
    optical_row = rows["pure_optical"]
    t_iter_trace = [float(value) for value in json.loads(optical_row["optical_t_iter_trace"])]
    t_stall_trace = [float(value) for value in json.loads(optical_row["optical_t_stall_trace"])]
    baseline_t_iter = t_iter_trace[0]
    baseline_t_stall = t_stall_trace[0]
    delta_t_iter_trace = [value - baseline_t_iter for value in t_iter_trace]
    delta_t_stall_trace = [value - baseline_t_stall for value in t_stall_trace]
    x_values = list(range(len(t_iter_trace)))
    best_idx = min(range(len(delta_t_iter_trace)), key=lambda idx: delta_t_iter_trace[idx])

    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=200)
    ax.plot(x_values, delta_t_iter_trace, marker="o", linewidth=2.0, color="#4C78A8", label="Delta T_iter")
    ax.plot(x_values, delta_t_stall_trace, marker="s", linewidth=2.0, color="#E45756", label="Delta sync wait time")
    ax.scatter([best_idx], [delta_t_iter_trace[best_idx]], color="#2E2E2E", zorder=5, s=40, label="Best optical point")
    ax.axhline(0.0, color="#808080", linewidth=0.9, linestyle="--", alpha=0.7)

    ax.set_xlabel("Compensated wavelengths")
    ax.set_ylabel("Change relative to step 0 (s)")
    ax.set_title("Topo2 Optical Compensation Ablation")
    ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.35)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()

    fig.savefig(OUT_DIR / "topo2_optical_ablation.png", bbox_inches="tight")
    fig.savefig(OUT_DIR / "topo2_optical_ablation.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_compute_ablation(figure1_rows_by_state: dict[str, dict[str, str]], figure3_rows: list[dict[str, str]]) -> None:
    baseline_row = figure1_rows_by_state["no_opt"]
    pure_compute_rows = [row for row in figure3_rows if row["state"] == "pure_compute"]
    pure_compute_rows.sort(key=lambda row: parse_int(row, "total_allocated_training_gpus"))
    if not pure_compute_rows:
        raise RuntimeError("No pure_compute rows found for topo2 in figure3.csv.")

    gpu_counts = [parse_int(baseline_row, "total_allocated_training_gpus")] + [
        parse_int(row, "total_allocated_training_gpus") for row in pure_compute_rows
    ]
    t_iter_values = [parse_float(baseline_row, "T_iter")] + [parse_float(row, "T_iter") for row in pure_compute_rows]
    compute_ratio_values = [parse_float(baseline_row, "r_comp")] + [parse_float(row, "r_comp") for row in pure_compute_rows]

    fig, ax1 = plt.subplots(figsize=(8.8, 4.8), dpi=200)
    ax1.plot(gpu_counts, t_iter_values, marker="o", linewidth=2.0, color="#4C78A8", label="T_iter")
    ax1.set_xlabel("Allocated GPUs")
    ax1.set_ylabel("T_iter (s)", color="#4C78A8")
    ax1.tick_params(axis="y", labelcolor="#4C78A8")
    ax1.grid(True, linestyle="--", linewidth=0.6, alpha=0.35)
    ax1.set_axisbelow(True)

    ax2 = ax1.twinx()
    ax2.plot(gpu_counts, compute_ratio_values, marker="s", linewidth=2.0, color="#F58518", label="Compute time ratio")
    ax2.set_ylabel("Compute time ratio (T_comp / T_iter)", color="#F58518")
    ax2.tick_params(axis="y", labelcolor="#F58518")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc="best")
    ax1.set_title("Topo2 Compute Compensation Ablation")
    fig.tight_layout()

    fig.savefig(OUT_DIR / "topo2_compute_ablation.png", bbox_inches="tight")
    fig.savefig(OUT_DIR / "topo2_compute_ablation.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    setup_style()
    figure1_rows_by_state = row_by_state(load_figure1_rows())
    figure3_rows = load_figure3_rows()
    export_figure_csv(figure1_rows_by_state, figure3_rows)
    plot_state_breakdown(figure1_rows_by_state)
    plot_optical_ablation(figure1_rows_by_state)
    plot_compute_ablation(figure1_rows_by_state, figure3_rows)


if __name__ == "__main__":
    main()
