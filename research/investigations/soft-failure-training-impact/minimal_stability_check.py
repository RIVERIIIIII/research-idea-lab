#!/usr/bin/env python3
"""Synthetic sanity check for IDEA-002's minimal counterexample.

This is not a network simulator and does not produce empirical evidence. It
only enumerates whether a non-additive job-level objective can change recovery
selection across a small neighborhood of transparent parameters.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from itertools import product
from pathlib import Path


@dataclass(frozen=True)
class Scenario:
    recovery_blocks: int
    job_a_group_gain_ms: int
    job_a_single_gain_ms: int
    job_b_gain_ms: int


def actual_gain(selected: frozenset[str], scenario: Scenario) -> int:
    """Return job-level time reduction for a selected flow set."""
    if {"A1", "A2"}.issubset(selected):
        job_a_gain = scenario.job_a_group_gain_ms
    elif selected.intersection({"A1", "A2"}):
        job_a_gain = scenario.job_a_single_gain_ms
    else:
        job_a_gain = 0

    job_b_gain = scenario.job_b_gain_ms if "B1" in selected else 0
    return job_a_gain + job_b_gain


def per_flow_greedy(scenario: Scenario) -> frozenset[str]:
    """Select flows by immediate single-flow gain, without group look-ahead."""
    scores = {
        "A1": scenario.job_a_single_gain_ms,
        "A2": scenario.job_a_single_gain_ms,
        "B1": scenario.job_b_gain_ms,
    }
    ordered = sorted(scores, key=lambda flow: (-scores[flow], flow))
    return frozenset(ordered[: scenario.recovery_blocks])


def job_group_optimal(scenario: Scenario) -> frozenset[str]:
    """Enumerate feasible recovery sets and maximize actual job-level gain."""
    flows = ("A1", "A2", "B1")
    best_set: frozenset[str] = frozenset()
    best_gain = -1
    for mask in range(1 << len(flows)):
        selected = frozenset(
            flow for index, flow in enumerate(flows) if mask & (1 << index)
        )
        if len(selected) > scenario.recovery_blocks:
            continue
        gain = actual_gain(selected, scenario)
        if gain > best_gain or (gain == best_gain and tuple(sorted(selected)) < tuple(sorted(best_set))):
            best_gain = gain
            best_set = selected
    return best_set


def main() -> None:
    output = Path(__file__).with_name("minimal-stability-results.csv")
    rows: list[dict[str, object]] = []

    for blocks, group_gain, single_gain, b_gain in product(
        (1, 2, 3),
        (36, 40, 44),
        (0, 4, 8),
        (27, 30, 33),
    ):
        scenario = Scenario(blocks, group_gain, single_gain, b_gain)
        greedy = per_flow_greedy(scenario)
        grouped = job_group_optimal(scenario)
        greedy_gain = actual_gain(greedy, scenario)
        grouped_gain = actual_gain(grouped, scenario)
        rows.append(
            {
                "recovery_blocks": blocks,
                "job_a_group_gain_ms": group_gain,
                "job_a_single_gain_ms": single_gain,
                "job_b_gain_ms": b_gain,
                "greedy_selection": "+".join(sorted(greedy)),
                "group_selection": "+".join(sorted(grouped)),
                "greedy_gain_ms": greedy_gain,
                "group_gain_ms": grouped_gain,
                "selection_differs": greedy != grouped,
                "group_advantage_ms": grouped_gain - greedy_gain,
            }
        )

    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    differs = [row for row in rows if row["selection_differs"]]
    improves = [row for row in rows if row["group_advantage_ms"] > 0]
    medium = [row for row in rows if row["recovery_blocks"] == 2]
    medium_improves = [row for row in medium if row["group_advantage_ms"] > 0]

    print(f"scenarios={len(rows)}")
    print(f"selection_differs={len(differs)}")
    print(f"group_improves={len(improves)}")
    print(f"medium_scarcity_scenarios={len(medium)}")
    print(f"medium_scarcity_improves={len(medium_improves)}")
    if improves:
        advantages = [int(row["group_advantage_ms"]) for row in improves]
        print(f"advantage_min_ms={min(advantages)}")
        print(f"advantage_max_ms={max(advantages)}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
