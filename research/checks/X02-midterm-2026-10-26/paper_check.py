"""Finite arithmetic check of an explicitly synthetic X02 paper example.

Not a network/LLM simulator. No external packages or measured parameters.
Enumerates all configurations of the stated two-path menu, including forwarding.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent
MODES = {"robust": (F(1), 1200), "high": (F(2), 300)}
PATHS = {
    "UB": {"edges": ["U-Y", "Y-B"], "free": {1, 2, 3}, "km": 100},
    "AB": {"edges": ["A-Z", "Z-B"], "free": {5, 6, 7}, "km": 600},
}


def configs(path, ignore_reach=False):
    info = PATHS[path]
    out = []
    for mode, (rate_per_slot, reach) in MODES.items():
        if not ignore_reach and info["km"] > reach:
            continue
        for width in (1, 2):
            for start in sorted(info["free"]):
                # One guard slot is reserved after the payload block.
                occupied = set(range(start, start + width + 1))
                if occupied <= info["free"]:
                    out.append({"path": path, "mode": mode, "width": width,
                                "start": start, "slots": sorted(occupied),
                                "rate": width * rate_per_slot})
    return out


def evaluate(h=F(5, 2), service_limit=F(1), replay_per_chunk=F(1, 8),
             setup=F(1, 5), allow_replay=True, ignore_reach=False):
    rows = []
    ub = configs("UB", ignore_reach)
    ab = configs("AB", ignore_reach)
    for k in range(9):
        if k and not allow_replay:
            continue
        for u, a in product(ub, ab if k < 8 else [None]):
            # Prefix input records from U, suffix KV from A, in parallel.
            # Prefix replay starts after its record transfer (conservative).
            t_prefix = (F(1, 10) + F(k, 4) / u["rate"] + k * replay_per_chunk) if k else F(0)
            t_suffix = F(3, 5) + F(8-k) / a["rate"] if a else F(0)
            post_gap = F(2, 5) + F(1, 50) / u["rate"]
            # Decision .1, setup, source preparation .1, import .1,
            # switch .1, then full next-token execution/delivery.
            r = F(2, 5) + setup + max(t_prefix, t_suffix) + post_gap
            rows.append({"action": "handover", "prefix_chunks": k,
                         "u": u, "a": a, "R": r, "post_gap": post_gap,
                         "deadline_ok": r <= h, "service_ok": post_gap <= service_limit,
                         "admissible": r <= h and post_gap <= service_limit})
    for u, a in product(ub, ab):
        # U-B-A IP/OEO forwarding: A keeps its state. No KV copying.
        post_gap = F(8, 5) + F(1, 50)/u["rate"] + F(1, 50)/a["rate"]
        r = F(1, 5) + setup + post_gap
        rows.append({"action": "forward_to_A", "prefix_chunks": 0,
                     "u": u, "a": a, "R": r, "post_gap": post_gap,
                     "deadline_ok": r <= h, "service_ok": post_gap <= service_limit,
                     "admissible": r <= h and post_gap <= service_limit})
    return rows


def best(rows, predicate=lambda r: True):
    eligible = [r for r in rows if predicate(r)]
    return min(eligible, key=lambda r: r["R"]) if eligible else None


def plain(x):
    if isinstance(x, F):
        return float(x)
    if isinstance(x, dict):
        return {k: plain(v) for k, v in x.items()}
    if isinstance(x, list):
        return [plain(v) for v in x]
    return x


rows = evaluate()
winner = best(rows, lambda r: r["admissible"])
kv = best(rows, lambda r: r["action"] == "handover" and r["prefix_chunks"] == 0)
replay = best(rows, lambda r: r["action"] == "handover" and r["prefix_chunks"] == 8)
forward = best(rows, lambda r: r["action"] == "forward_to_A")
min_width = best(rows, lambda r: r["action"] == "handover"
                 and r["u"]["width"] == 1 and (r["a"] is None or r["a"]["width"] == 1))
max_capacity_then_state = best(rows, lambda r: r["action"] == "handover"
                 and r["u"]["rate"] == 4 and (r["a"] is None or r["a"]["rate"] == 2))
scenarios = {
    "base": rows,
    "relaxed_post_service_1_7": evaluate(service_limit=F(17, 10)),
    "no_replay_capability": evaluate(allow_replay=False),
    "expensive_replay": evaluate(replay_per_chunk=F(1)),
    "slow_configuration_2_0": evaluate(setup=F(2)),
    "incorrectly_ignore_reach": evaluate(ignore_reach=True),
}
summary = {
    "scope": "Synthetic arithmetic only; normalized units; not measured gains or novelty evidence.",
    "plan_count": len(rows),
    "admissible_count": sum(r["admissible"] for r in rows),
    "winner": winner,
    "comparators": {"KV_only": kv, "replay_only": replay, "forward": forward,
                    "minimum_width_then_state": min_width,
                    "maximum_capacity_then_state": max_capacity_then_state},
    "counterexamples": {name: {"admissible_count": sum(r["admissible"] for r in rr),
                                "best": best(rr, lambda r: r["admissible"])}
                        for name, rr in scenarios.items()},
}
(ROOT / "results.json").write_text(json.dumps(plain(summary), ensure_ascii=False, indent=2)+"\n")
with (ROOT / "plans.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["action", "prefix_chunks", "u_mode", "u_width", "u_start", "a_width", "a_start", "R", "post_gap", "admissible"])
    for r in rows:
        writer.writerow([r["action"], r["prefix_chunks"], r["u"]["mode"], r["u"]["width"], r["u"]["start"],
                         r["a"]["width"] if r["a"] else 0, r["a"]["start"] if r["a"] else 0,
                         float(r["R"]), float(r["post_gap"]), r["admissible"]])
print(json.dumps(plain(summary), ensure_ascii=False, indent=2))
