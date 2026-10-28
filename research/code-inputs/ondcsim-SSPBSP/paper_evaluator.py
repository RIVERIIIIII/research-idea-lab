from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Iterable, Iterator, List, Tuple

import networkx as nx
import yaml

from common_utils import CrossDomainCalculator, LocalPerformanceCalculator, SPEED_OF_LIGHT_FIBER
from topology_OTN import TopologyManager, haversine_distance


@dataclass(frozen=True)
class ModelSpec:
    model_name: str
    model_config: Dict
    training_config: Dict


@dataclass(frozen=True)
class TrainingTopologyScenario:
    name: str
    dc_nodes: List[int]
    link_ids: List[int]
    reroutes: List[Dict]

    def effective_segments(self, use_failure_reroute: bool) -> List[List[int]]:
        reroute_map = {}
        if use_failure_reroute:
            for reroute in self.reroutes:
                reroute_map[reroute["failed_link_id"]] = list(reroute["replacement_link_ids"])
        return [reroute_map.get(link_id, [link_id]) for link_id in self.link_ids]

    def communication_paths(self, use_failure_reroute: bool) -> List[List[int]]:
        return self.effective_segments(use_failure_reroute)

    def effective_backbone_link_ids(self, use_failure_reroute: bool) -> List[int]:
        backbone_links: List[int] = []
        reroute_map = {
            int(reroute["failed_link_id"]): [int(link_id) for link_id in reroute["replacement_link_ids"]]
            for reroute in self.reroutes
        }
        for link_id in self.link_ids:
            current_link_id = int(link_id)
            if use_failure_reroute and current_link_id in reroute_map:
                for replacement_link_id in reroute_map[current_link_id]:
                    if replacement_link_id not in backbone_links:
                        backbone_links.append(replacement_link_id)
                continue
            if current_link_id not in backbone_links:
                backbone_links.append(current_link_id)
        return backbone_links

    def rerouted_replacement_links(self, use_failure_reroute: bool) -> set[int]:
        if not use_failure_reroute:
            return set()
        rerouted_links: set[int] = set()
        for reroute in self.reroutes:
            rerouted_links.update(int(link_id) for link_id in reroute["replacement_link_ids"])
        return rerouted_links

    def is_cycle(self) -> bool:
        return len(self.link_ids) >= len(self.dc_nodes)


@dataclass(frozen=True)
class FailureSeverityProfile:
    name: str = "base"
    reroute_length_scale: float = 1.0
    reroute_bandwidth_scale: float = 1.0


@dataclass(frozen=True)
class BudgetSnapshot:
    effective_gpu_per_dc: Dict[int, int]
    dp_capacity_per_dc: Dict[int, int]
    total_effective_gpus: int
    total_dp_capacity: int
    effective_max_waves: int
    raw_max_waves: int


@dataclass(frozen=True)
class LocalDcMetrics:
    dc_id: int
    local_dp: int
    allocated_gpus: int
    local_comp_time: float
    local_comm_time: float
    local_bubble_time: float
    local_total_time: float


@dataclass(frozen=True)
class DpAllocationState:
    total_groups: int
    max_local: float
    max_step: float
    min_step: float
    allocation: Tuple[int, ...]


@dataclass(frozen=True)
class PairAllocation:
    dc_pair: Tuple[int, int]
    link_ids: Tuple[int, ...]
    wavelength_ids: Tuple[int, ...]
    allocated_n_wave: int
    bandwidth_gbps: float
    path_length_km: float
    propagation_delay_s: float
    comm_time: float


@dataclass(frozen=True)
class PaperEvaluationResult:
    model_name: str
    topology_name: str
    use_failure_reroute: bool
    severity_name: str
    reroute_length_scale: float
    reroute_bandwidth_scale: float
    data_parallel: int
    tensor_parallel: int
    pipeline_parallel: int
    n_wave: int
    alpha: float
    t_iter: float
    t_inter: float
    t_local_max: float
    t_comp_max: float
    t_stall: float
    delta_balance: float
    imbalance_ratio: float
    r_inter: float
    bandwidth_eff_gbps: float
    max_path_length_km: float
    max_path_propagation_delay_s: float
    propagation_latency_growth_ratio: float
    avg_progress_gap: float
    max_progress_gap: int
    ssp_bound: int
    ssp_simulation_steps: int
    budgets: BudgetSnapshot
    local_metrics: List[LocalDcMetrics]
    pair_allocations: List[PairAllocation]
    gpu_compensation_enabled: bool = False
    extra_dp_capacity_per_dc: Dict[int, int] | None = None
    total_extra_dp_groups: int = 0
    optical_extra_waves: int = 0
    optical_compensation_steps: int = 0
    optical_marginal_gain_trace: Tuple[float, ...] = ()
    optical_t_iter_trace: Tuple[float, ...] = ()
    optical_t_stall_trace: Tuple[float, ...] = ()


@dataclass(frozen=True)
class StateEvaluationResult:
    state_name: str
    dp_base: int
    tp_base: int
    n_wave_base: int
    recovery_target_t_iter: float
    recovered_to_before: bool
    result: PaperEvaluationResult


class SingleTaskPaperEvaluator:
    def __init__(
        self,
        topology_file: str,
        datacenters_file: str,
        service_file: str,
        training_topologies_file: str,
        wavelength_state_file: str | None = None,
        wavelength_state_profile: str | None = None,
        bw_wave_gbps: float = 100.0,
        rho_gpu: float = 1.0,
        rho_gpu_overrides: Dict[int, float] | None = None,
        rho_gpu_compensation: float | None = None,
        rho_gpu_compensation_overrides: Dict[int, float] | None = None,
        rho_wave: float = 1.0,
        alpha_mode: str = "groups_per_dc",
        alpha_scale: float = 1.0,
        recovery_distance_weight_dp: float = 1.0,
        recovery_distance_weight_wave: float = 1.0,
        optical_critical_beta: float = 0.8,
        optical_degradation_gamma: float = 0.1,
        fixed_tp: int | None = None,
        fixed_pp: int | None = None,
        n_wave_base_cap: int = 8,
        ssp_bound: int = 1,
        ssp_simulation_steps: int = 100,
        dp_reserve_ratio: float = 0.2,
        dp_softness_beta: float = 0.7,
        min_reserved_dp_groups: int = 1,
    ) -> None:
        self.topology_file = Path(topology_file)
        self.datacenters_file = Path(datacenters_file)
        self.service_file = Path(service_file)
        self.training_topologies_file = Path(training_topologies_file)
        self.wavelength_state_file = Path(wavelength_state_file) if wavelength_state_file else None
        self.wavelength_state_profile = wavelength_state_profile
        self.bw_wave_gbps = bw_wave_gbps
        self.rho_gpu = rho_gpu
        self.rho_gpu_overrides = dict(rho_gpu_overrides or {})
        self.rho_gpu_compensation = rho_gpu if rho_gpu_compensation is None else rho_gpu_compensation
        self.rho_gpu_compensation_overrides = dict(rho_gpu_compensation_overrides or {})
        self.rho_wave = rho_wave
        self.alpha_mode = alpha_mode
        self.alpha_scale = alpha_scale
        self.recovery_distance_weight_dp = recovery_distance_weight_dp
        self.recovery_distance_weight_wave = recovery_distance_weight_wave
        self.optical_critical_beta = optical_critical_beta
        self.optical_degradation_gamma = optical_degradation_gamma
        self.fixed_tp = fixed_tp
        self.fixed_pp = fixed_pp
        self.n_wave_base_cap = n_wave_base_cap
        self.ssp_bound = ssp_bound
        self.ssp_simulation_steps = ssp_simulation_steps
        self.dp_reserve_ratio = dp_reserve_ratio
        self.dp_softness_beta = dp_softness_beta
        self.min_reserved_dp_groups = min_reserved_dp_groups

        topology_manager = TopologyManager(str(self.topology_file), str(self.datacenters_file))
        self.graph = topology_manager.get_graph()
        self.local_calculator = LocalPerformanceCalculator()
        self.cross_domain_calculator = CrossDomainCalculator()
        self._local_profile_cache: Dict[Tuple[str, str, int, int, int, int], float] = {}

        self.model_specs = self._load_model_specs(self.service_file)
        self.training_topologies = self._load_training_topologies(self.training_topologies_file)
        self.link_metadata = self._load_link_metadata(self.topology_file)
        self.wavelength_state_profiles = self._load_wavelength_state_profiles(self.wavelength_state_file)
        if self.wavelength_state_profile:
            self._apply_wavelength_state_profile(self.wavelength_state_profile)

    def derive_dp_base(self, model_name: str, topology_name: str) -> int:
        model_spec = self.get_model_spec(model_name)
        scenario = self.get_training_topology(topology_name)
        budgets = self.get_budget_snapshot(topology_name, use_failure_reroute=False)
        tensor_parallel = int(model_spec.model_config["parallelism"]["tensor_parallel"])
        pipeline_parallel = int(model_spec.model_config["parallelism"]["pipeline_parallel"])
        unit_gpus = tensor_parallel * pipeline_parallel
        total_dp_capacity = sum(effective_gpu // unit_gpus for effective_gpu in budgets.effective_gpu_per_dc.values())
        preferred_dp = int(model_spec.model_config["parallelism"]["data_parallel"])
        return max(len(scenario.dc_nodes), min(preferred_dp, total_dp_capacity))

    def derive_tp_base(self, model_name: str) -> int:
        model_spec = self.get_model_spec(model_name)
        return int(model_spec.model_config["parallelism"]["tensor_parallel"])

    def derive_n_wave_base(self, topology_name: str) -> int:
        budgets = self.get_budget_snapshot(topology_name, use_failure_reroute=False)
        return max(1, min(self.n_wave_base_cap, budgets.effective_max_waves))

    def derive_tp_scan_values(self, model_name: str, topology_name: str, data_parallel: int) -> List[int]:
        model_spec = self.get_model_spec(model_name)
        scenario = self.get_training_topology(topology_name)
        pipeline_parallel = int(model_spec.model_config["parallelism"]["pipeline_parallel"])
        base_tp = int(model_spec.model_config["parallelism"]["tensor_parallel"])
        hidden_dim = int(model_spec.model_config["hidden_dim"])
        budgets = self.get_budget_snapshot(
            topology_name,
            use_failure_reroute=True,
            allow_gpu_compensation=True,
        )

        values: List[int] = []
        candidate_tp = max(1, base_tp)
        while candidate_tp <= hidden_dim:
            if hidden_dim % candidate_tp == 0:
                unit_gpus = candidate_tp * pipeline_parallel
                dp_capacity_per_dc = {
                    dc_id: effective_gpu // unit_gpus
                    for dc_id, effective_gpu in budgets.effective_gpu_per_dc.items()
                }
                total_dp_capacity = sum(dp_capacity_per_dc.values())
                if total_dp_capacity >= data_parallel and all(
                    dp_capacity_per_dc.get(dc_id, 0) >= 1 for dc_id in scenario.dc_nodes
                ):
                    values.append(candidate_tp)
            candidate_tp *= 2
        if base_tp not in values:
            values.append(base_tp)
        return sorted(set(values))

    def derive_dp_scan_values(self, model_name: str, topology_name: str) -> List[int]:
        scenario = self.get_training_topology(topology_name)
        model_spec = self.get_model_spec(model_name)
        budgets = self.get_budget_snapshot(topology_name, use_failure_reroute=True)
        tensor_parallel = int(model_spec.model_config["parallelism"]["tensor_parallel"])
        pipeline_parallel = int(model_spec.model_config["parallelism"]["pipeline_parallel"])
        unit_gpus = tensor_parallel * pipeline_parallel
        total_dp_capacity = sum(effective_gpu // unit_gpus for effective_gpu in budgets.effective_gpu_per_dc.values())
        min_dp = len(scenario.dc_nodes)
        natural_base = self.derive_dp_base(model_name, topology_name)

        values = set()
        current = 1
        while current < min_dp:
            current *= 2
        while current <= natural_base:
            values.add(current)
            current *= 2
        values.add(min_dp)
        values.add(natural_base)
        return sorted(value for value in values if min_dp <= value <= total_dp_capacity)

    def evaluate_state(
        self,
        model_name: str,
        topology_name: str,
        state_name: str,
        severity_profile: FailureSeverityProfile | None = None,
    ) -> StateEvaluationResult:
        dp_base = self.derive_dp_base(model_name, topology_name)
        tp_base = self.derive_tp_base(model_name)
        n_wave_base = self.derive_n_wave_base(topology_name)
        before_failure_result = self.evaluate(
            model_name=model_name,
            topology_name=topology_name,
            data_parallel=dp_base,
            n_wave=n_wave_base,
            use_failure_reroute=False,
            tensor_parallel_override=tp_base,
        )
        recovery_target_t_iter = before_failure_result.t_iter

        if state_name == "before_failure":
            result = before_failure_result
        elif state_name == "no_opt":
            result = self.evaluate(
                model_name=model_name,
                topology_name=topology_name,
                data_parallel=dp_base,
                n_wave=n_wave_base,
                use_failure_reroute=True,
                severity_profile=severity_profile,
                tensor_parallel_override=tp_base,
            )
        elif state_name == "pure_optical":
            no_opt_result = self.evaluate(
                model_name=model_name,
                topology_name=topology_name,
                data_parallel=dp_base,
                n_wave=n_wave_base,
                use_failure_reroute=True,
                severity_profile=severity_profile,
                tensor_parallel_override=tp_base,
            )
            result = self._incremental_optical_compensation(
                model_name=model_name,
                topology_name=topology_name,
                before_failure_result=before_failure_result,
                initial_result=no_opt_result,
                target_t_iter=recovery_target_t_iter,
                severity_profile=severity_profile,
            )
        elif state_name == "pure_compute":
            result = self._optimize_tensor_parallel(
                model_name=model_name,
                topology_name=topology_name,
                data_parallel=dp_base,
                n_wave=n_wave_base,
                use_failure_reroute=True,
                target_t_iter=recovery_target_t_iter,
                tp_base=tp_base,
                n_wave_base=n_wave_base,
                severity_profile=severity_profile,
            )
        elif state_name == "joint":
            result = self._optimize_joint_tp_n_wave(
                model_name=model_name,
                topology_name=topology_name,
                data_parallel=dp_base,
                use_failure_reroute=True,
                target_t_iter=recovery_target_t_iter,
                tp_base=tp_base,
                n_wave_base=n_wave_base,
                before_failure_result=before_failure_result,
                severity_profile=severity_profile,
            )
        else:
            raise ValueError(f"Unsupported paper evaluation state: {state_name}")

        return StateEvaluationResult(
            state_name=state_name,
            dp_base=dp_base,
            tp_base=tp_base,
            n_wave_base=n_wave_base,
            recovery_target_t_iter=recovery_target_t_iter,
            recovered_to_before=(result.t_iter <= recovery_target_t_iter),
            result=result,
        )

    def _load_model_specs(self, service_file: Path) -> Dict[str, ModelSpec]:
        with service_file.open("r", encoding="utf-8") as file:
            service_cfg = yaml.safe_load(file)["service"]

        model_specs: Dict[str, ModelSpec] = {}
        models = service_cfg["random_event_config"]["distributed_training"]["model_configs"]
        for model_cfg in models:
            model_name = model_cfg["model_name"]
            training_cfg = dict(model_cfg.get("training_config", {}))
            parallelism = dict(model_cfg.get("parallelism", {}))
            if self.fixed_tp is not None:
                parallelism["tensor_parallel"] = self.fixed_tp
            if self.fixed_pp is not None:
                parallelism["pipeline_parallel"] = self.fixed_pp

            normalized_model_cfg = dict(model_cfg)
            normalized_model_cfg["parallelism"] = parallelism
            model_specs[model_name] = ModelSpec(
                model_name=model_name,
                model_config=normalized_model_cfg,
                training_config=training_cfg,
            )
        return model_specs

    def _load_training_topologies(self, training_topologies_file: Path) -> Dict[str, TrainingTopologyScenario]:
        with training_topologies_file.open("r", encoding="utf-8") as file:
            topologies_cfg = yaml.safe_load(file)["topologies"]

        scenarios: Dict[str, TrainingTopologyScenario] = {}
        for name, cfg in topologies_cfg.items():
            backbone_link_ids = cfg.get("backbone_link_ids")
            if backbone_link_ids is None:
                backbone_link_ids = cfg["link_ids"]
            scenarios[name] = TrainingTopologyScenario(
                name=name,
                dc_nodes=list(cfg["dc_nodes"]),
                link_ids=list(backbone_link_ids),
                reroutes=list(cfg.get("reroutes", [])),
            )
        return scenarios

    def _load_link_metadata(self, topology_file: Path) -> Dict[int, Dict]:
        with topology_file.open("r", encoding="utf-8") as file:
            raw_topology = yaml.safe_load(file)

        node_metadata = {
            int(item["id"]): item
            for item in raw_topology.get("nodes", [])
        }
        link_sections = ("links", "dc_to_otn_links", "user_to_otn_links")
        metadata: Dict[int, Dict] = {}
        for section_name in link_sections:
            for item in raw_topology.get(section_name, []):
                entry = dict(item)
                length_km = float(entry.get("length_km", 0.0))
                if length_km == 0.0:
                    src_node = node_metadata.get(int(entry["src"]))
                    dst_node = node_metadata.get(int(entry["dst"]))
                    if src_node is not None and dst_node is not None:
                        src_lat = float(src_node.get("lat", 0.0))
                        src_lon = float(src_node.get("lon", 0.0))
                        dst_lat = float(dst_node.get("lat", 0.0))
                        dst_lon = float(dst_node.get("lon", 0.0))
                        entry["length_km"] = haversine_distance(src_lat, src_lon, dst_lat, dst_lon)
                metadata[int(entry["id"])] = entry
        return metadata

    def _load_wavelength_state_profiles(self, wavelength_state_file: Path | None) -> Dict[str, Dict[int, Dict]]:
        if wavelength_state_file is None:
            return {}

        with wavelength_state_file.open("r", encoding="utf-8") as file:
            raw_profiles = yaml.safe_load(file) or {}

        profiles_cfg = raw_profiles.get("wavelength_state_profiles", {})
        if not isinstance(profiles_cfg, dict):
            raise ValueError("wavelength_state_profiles.yaml must define a 'wavelength_state_profiles' mapping.")

        normalized_profiles: Dict[str, Dict[int, Dict]] = {}
        for profile_name, profile_cfg in profiles_cfg.items():
            if not isinstance(profile_cfg, dict):
                raise ValueError(f"Wavelength state profile '{profile_name}' must be a mapping.")
            links_cfg = profile_cfg.get("links", {})
            if not isinstance(links_cfg, dict):
                raise ValueError(f"Wavelength state profile '{profile_name}' must define a 'links' mapping.")

            normalized_profiles[profile_name] = {}
            for raw_link_id, state_cfg in links_cfg.items():
                link_id = int(raw_link_id)
                if link_id not in self.link_metadata:
                    raise KeyError(f"Wavelength state profile '{profile_name}' references unknown link ID {link_id}.")
                normalized_profiles[profile_name][link_id] = self._normalize_wavelength_state(link_id, state_cfg)

        return normalized_profiles

    def _normalize_wavelength_state(self, link_id: int, state_cfg: Dict) -> Dict:
        if not isinstance(state_cfg, dict):
            raise ValueError(f"Wavelength state for link {link_id} must be a mapping.")

        link_entry = self.link_metadata[link_id]
        total_wavelengths = int(link_entry.get("total_wavelengths", 0))
        default_available = self._default_link_available_wavelength_ids(link_entry)
        occupied = self._parse_wavelength_id_spec(
            state_cfg.get("occupied_wavelength_ids", []),
            total_wavelengths,
            f"link {link_id} occupied_wavelength_ids",
        )
        failed = self._parse_wavelength_id_spec(
            state_cfg.get("failed_wavelength_ids", []),
            total_wavelengths,
            f"link {link_id} failed_wavelength_ids",
        )

        occupied_by_tenant = state_cfg.get("occupied_by_tenant", {})
        if occupied_by_tenant:
            if not isinstance(occupied_by_tenant, dict):
                raise ValueError(f"link {link_id} occupied_by_tenant must be a mapping.")
            for tenant_name, tenant_spec in occupied_by_tenant.items():
                if isinstance(tenant_spec, dict):
                    tenant_values = tenant_spec.get("wavelength_ids", [])
                else:
                    tenant_values = tenant_spec
                occupied.update(
                    self._parse_wavelength_id_spec(
                        tenant_values,
                        total_wavelengths,
                        f"link {link_id} occupied_by_tenant.{tenant_name}",
                    )
                )

        explicit_available = state_cfg.get("available_wavelength_ids")
        if explicit_available is not None:
            available = self._parse_wavelength_id_spec(
                explicit_available,
                total_wavelengths,
                f"link {link_id} available_wavelength_ids",
            )
        else:
            available = set(default_available)

        available -= occupied
        available -= failed

        return {
            "available_wavelength_ids": tuple(sorted(available)),
            "occupied_wavelength_ids": tuple(sorted(occupied)),
            "failed_wavelength_ids": tuple(sorted(failed)),
            "notes": state_cfg.get("notes", ""),
        }

    def _parse_wavelength_id_spec(
        self,
        raw_values: object,
        total_wavelengths: int,
        label: str,
    ) -> set[int]:
        if raw_values is None:
            return set()
        if not isinstance(raw_values, list):
            raise ValueError(f"{label} must be a list of integers or inclusive ranges like '5-8'.")

        parsed: set[int] = set()
        for item in raw_values:
            if isinstance(item, int):
                values = [item]
            elif isinstance(item, str) and "-" in item:
                start_raw, end_raw = item.split("-", 1)
                start = int(start_raw)
                end = int(end_raw)
                if end < start:
                    raise ValueError(f"{label} contains an invalid range '{item}'.")
                values = list(range(start, end + 1))
            elif isinstance(item, str):
                values = [int(item)]
            else:
                raise ValueError(f"{label} contains unsupported wavelength identifier {item!r}.")

            for wavelength_id in values:
                if wavelength_id < 1 or wavelength_id > total_wavelengths:
                    raise ValueError(
                        f"{label} contains wavelength ID {wavelength_id}, outside the valid range 1..{total_wavelengths}."
                    )
                parsed.add(wavelength_id)

        return parsed

    def _default_link_available_wavelength_ids(self, link_entry: Dict) -> set[int]:
        total_wavelengths = int(link_entry.get("total_wavelengths", 0))
        wavelength_channels = link_entry.get("wavelength_channels", [])
        if isinstance(wavelength_channels, list):
            channel_ids = {
                int(channel["wavelength_id"])
                for channel in wavelength_channels
                if isinstance(channel, dict) and "wavelength_id" in channel
            }
            if len(channel_ids) >= min(total_wavelengths, 2):
                return {
                    int(channel["wavelength_id"])
                    for channel in wavelength_channels
                    if isinstance(channel, dict) and int(channel.get("status", 0)) == 0
                }
        return set(range(1, total_wavelengths + 1))

    def _apply_wavelength_state_profile(self, profile_name: str) -> None:
        if profile_name not in self.wavelength_state_profiles:
            available_profiles = ", ".join(sorted(self.wavelength_state_profiles)) or "<none>"
            raise KeyError(
                f"Unknown wavelength state profile '{profile_name}'. Available profiles: {available_profiles}"
            )

        for link_id, state in self.wavelength_state_profiles[profile_name].items():
            link_entry = self.link_metadata[link_id]
            link_entry["available_wavelength_ids"] = state["available_wavelength_ids"]
            link_entry["occupied_wavelength_ids"] = state["occupied_wavelength_ids"]
            link_entry["failed_wavelength_ids"] = state["failed_wavelength_ids"]
            link_entry["wavelength_state_notes"] = state["notes"]
            link_entry["wavelength_state_profile"] = profile_name

    def _link_available_wavelength_ids(self, link_id: int) -> set[int]:
        link_entry = self.link_metadata[int(link_id)]
        explicit_available = link_entry.get("available_wavelength_ids")
        if explicit_available is not None:
            return {int(wavelength_id) for wavelength_id in explicit_available}
        return self._default_link_available_wavelength_ids(link_entry)

    def _path_common_available_wavelength_ids(self, path_link_ids: List[int] | Tuple[int, ...]) -> set[int]:
        common_available: set[int] | None = None
        for link_id in path_link_ids:
            link_available = self._link_available_wavelength_ids(int(link_id))
            common_available = link_available if common_available is None else common_available & link_available
            if not common_available:
                return set()
        return common_available or set()

    def get_model_spec(self, model_name: str) -> ModelSpec:
        if model_name not in self.model_specs:
            raise KeyError(f"Unknown model name: {model_name}")
        return self.model_specs[model_name]

    def get_training_topology(self, topology_name: str) -> TrainingTopologyScenario:
        if topology_name not in self.training_topologies:
            raise KeyError(f"Unknown training topology: {topology_name}")
        return self.training_topologies[topology_name]

    def _effective_gpu_per_dc(
        self,
        scenario: TrainingTopologyScenario,
        allow_gpu_compensation: bool = False,
    ) -> Dict[int, int]:
        effective_gpu_per_dc: Dict[int, int] = {}
        for dc_id in scenario.dc_nodes:
            raw_available = int(self.graph.nodes[dc_id].get("available_gpu", 0))
            if allow_gpu_compensation:
                rho_gpu = self.rho_gpu_compensation_overrides.get(dc_id, self.rho_gpu_compensation)
                effective_gpu = math.floor(raw_available * rho_gpu)
            else:
                rho_gpu = self.rho_gpu_overrides.get(dc_id, self.rho_gpu)
                effective_gpu = math.floor(raw_available * rho_gpu)
            effective_gpu_per_dc[dc_id] = effective_gpu
        return effective_gpu_per_dc

    def get_budget_snapshot(
        self,
        topology_name: str,
        use_failure_reroute: bool = False,
        allow_gpu_compensation: bool = False,
    ) -> BudgetSnapshot:
        scenario = self.get_training_topology(topology_name)

        effective_gpu_per_dc = self._effective_gpu_per_dc(
            scenario,
            allow_gpu_compensation=allow_gpu_compensation,
        )
        dp_capacity_per_dc: Dict[int, int] = {}
        total_effective_gpus = sum(effective_gpu_per_dc.values())

        # Capacity in DP groups depends on TP/PP, so it is populated in evaluate().
        raw_max_waves, effective_max_waves = self._calculate_wave_budget(scenario, use_failure_reroute)
        return BudgetSnapshot(
            effective_gpu_per_dc=effective_gpu_per_dc,
            dp_capacity_per_dc=dp_capacity_per_dc,
            total_effective_gpus=total_effective_gpus,
            total_dp_capacity=0,
            effective_max_waves=effective_max_waves,
            raw_max_waves=raw_max_waves,
        )

    def raw_dp_capacity_per_dc(
        self,
        topology_name: str,
        tensor_parallel: int,
        pipeline_parallel: int | None = None,
    ) -> Dict[int, int]:
        scenario = self.get_training_topology(topology_name)
        pipeline_parallel = (
            int(pipeline_parallel)
            if pipeline_parallel is not None
            else int(self.get_model_spec(next(iter(self.model_specs))).model_config["parallelism"]["pipeline_parallel"])
        )
        unit_gpus = int(tensor_parallel) * pipeline_parallel
        return {
            dc_id: int(self.graph.nodes[dc_id].get("available_gpu", 0)) // unit_gpus
            for dc_id in scenario.dc_nodes
        }

    def extra_dp_capacity_limits(
        self,
        topology_name: str,
        tensor_parallel: int,
        pipeline_parallel: int | None = None,
        use_failure_reroute: bool = False,
        allow_gpu_compensation: bool = False,
    ) -> Dict[int, int]:
        scenario = self.get_training_topology(topology_name)
        pipeline_parallel = (
            int(pipeline_parallel)
            if pipeline_parallel is not None
            else int(self.get_model_spec(next(iter(self.model_specs))).model_config["parallelism"]["pipeline_parallel"])
        )
        unit_gpus = int(tensor_parallel) * pipeline_parallel
        raw_capacity_per_dc = self.raw_dp_capacity_per_dc(
            topology_name=topology_name,
            tensor_parallel=tensor_parallel,
            pipeline_parallel=pipeline_parallel,
        )
        budget_snapshot = self.get_budget_snapshot(
            topology_name,
            use_failure_reroute=use_failure_reroute,
            allow_gpu_compensation=allow_gpu_compensation,
        )
        base_capacity_per_dc = {
            dc_id: budget_snapshot.effective_gpu_per_dc[dc_id] // unit_gpus
            for dc_id in scenario.dc_nodes
        }
        return {
            dc_id: max(0, raw_capacity_per_dc[dc_id] - base_capacity_per_dc[dc_id])
            for dc_id in scenario.dc_nodes
        }

    def iter_extra_dp_capacity_allocations(
        self,
        topology_name: str,
        total_extra_dp_groups: int,
        tensor_parallel: int,
        pipeline_parallel: int | None = None,
        use_failure_reroute: bool = False,
        allow_gpu_compensation: bool = False,
    ) -> Iterator[Dict[int, int]]:
        scenario = self.get_training_topology(topology_name)
        dc_nodes = list(scenario.dc_nodes)
        limits = self.extra_dp_capacity_limits(
            topology_name=topology_name,
            tensor_parallel=tensor_parallel,
            pipeline_parallel=pipeline_parallel,
            use_failure_reroute=use_failure_reroute,
            allow_gpu_compensation=allow_gpu_compensation,
        )
        if total_extra_dp_groups < 0:
            raise ValueError("total_extra_dp_groups must be non-negative.")
        if sum(limits.values()) < total_extra_dp_groups:
            raise ValueError(
                f"Requested total_extra_dp_groups={total_extra_dp_groups} exceeds the physical extra capacity "
                f"{sum(limits.values())} for topology '{topology_name}'."
            )

        def _walk(index: int, remaining: int, current: Dict[int, int]) -> Iterator[Dict[int, int]]:
            if index == len(dc_nodes):
                if remaining == 0:
                    yield {dc_id: current.get(dc_id, 0) for dc_id in dc_nodes}
                return

            dc_id = dc_nodes[index]
            remaining_limit = sum(limits[node_id] for node_id in dc_nodes[index + 1:])
            upper = min(limits[dc_id], remaining)
            lower = max(0, remaining - remaining_limit)
            for extra in range(lower, upper + 1):
                current[dc_id] = extra
                yield from _walk(index + 1, remaining - extra, current)
            current.pop(dc_id, None)

        yield from _walk(0, total_extra_dp_groups, {})

    def _resolved_budget_snapshot(
        self,
        topology_name: str,
        scenario: TrainingTopologyScenario,
        unit_gpus: int,
        use_failure_reroute: bool,
        allow_gpu_compensation: bool = False,
        extra_dp_capacity_per_dc: Dict[int, int] | None = None,
    ) -> Tuple[BudgetSnapshot, Dict[int, int]]:
        budget_snapshot = self.get_budget_snapshot(
            topology_name,
            use_failure_reroute,
            allow_gpu_compensation=allow_gpu_compensation,
        )
        base_dp_capacity_per_dc = {
            dc_id: budget_snapshot.effective_gpu_per_dc[dc_id] // unit_gpus
            for dc_id in scenario.dc_nodes
        }
        raw_dp_capacity_per_dc = {
            dc_id: int(self.graph.nodes[dc_id].get("available_gpu", 0)) // unit_gpus
            for dc_id in scenario.dc_nodes
        }
        normalized_extra_dp_capacity: Dict[int, int] = {}
        effective_gpu_per_dc = dict(budget_snapshot.effective_gpu_per_dc)
        dp_capacity_per_dc: Dict[int, int] = {}

        for dc_id in scenario.dc_nodes:
            requested_extra = 0 if extra_dp_capacity_per_dc is None else int(extra_dp_capacity_per_dc.get(dc_id, 0))
            requested_extra = max(0, requested_extra)
            max_extra = max(0, raw_dp_capacity_per_dc[dc_id] - base_dp_capacity_per_dc[dc_id])
            applied_extra = min(requested_extra, max_extra)
            normalized_extra_dp_capacity[dc_id] = applied_extra
            effective_gpu_per_dc[dc_id] += applied_extra * unit_gpus
            dp_capacity_per_dc[dc_id] = base_dp_capacity_per_dc[dc_id] + applied_extra

        total_effective_gpus = sum(effective_gpu_per_dc.values())
        total_dp_capacity = sum(dp_capacity_per_dc.values())
        return (
            BudgetSnapshot(
                effective_gpu_per_dc=effective_gpu_per_dc,
                dp_capacity_per_dc=dp_capacity_per_dc,
                total_effective_gpus=total_effective_gpus,
                total_dp_capacity=total_dp_capacity,
                effective_max_waves=budget_snapshot.effective_max_waves,
                raw_max_waves=budget_snapshot.raw_max_waves,
            ),
            normalized_extra_dp_capacity,
        )

    def evaluate(
        self,
        model_name: str,
        topology_name: str,
        data_parallel: int,
        n_wave: int,
        use_failure_reroute: bool,
        severity_profile: FailureSeverityProfile | None = None,
        tensor_parallel_override: int | None = None,
        allow_gpu_compensation: bool = False,
        extra_dp_capacity_per_dc: Dict[int, int] | None = None,
        pair_allocations_override: List[PairAllocation] | None = None,
        dp_allocation_strategy: str = "heuristic",
    ) -> PaperEvaluationResult:
        model_spec = self.get_model_spec(model_name)
        scenario = self.get_training_topology(topology_name)
        severity = severity_profile or FailureSeverityProfile()

        tensor_parallel = (
            int(tensor_parallel_override)
            if tensor_parallel_override is not None
            else int(model_spec.model_config["parallelism"]["tensor_parallel"])
        )
        pipeline_parallel = int(model_spec.model_config["parallelism"]["pipeline_parallel"])
        unit_gpus = tensor_parallel * pipeline_parallel

        budgets, normalized_extra_dp_capacity = self._resolved_budget_snapshot(
            topology_name=topology_name,
            scenario=scenario,
            unit_gpus=unit_gpus,
            use_failure_reroute=use_failure_reroute,
            allow_gpu_compensation=allow_gpu_compensation,
            extra_dp_capacity_per_dc=extra_dp_capacity_per_dc,
        )
        dp_capacity_per_dc = budgets.dp_capacity_per_dc
        total_dp_capacity = budgets.total_dp_capacity

        if data_parallel < len(scenario.dc_nodes):
            raise ValueError(
                f"data_parallel={data_parallel} is smaller than the number of fixed training DCs={len(scenario.dc_nodes)}."
            )
        if total_dp_capacity < data_parallel:
            raise ValueError(
                f"data_parallel={data_parallel} exceeds the effective DP capacity {total_dp_capacity} "
                f"for topology '{topology_name}'."
            )
        if budgets.effective_max_waves < n_wave:
            raise ValueError(
                f"n_wave={n_wave} exceeds the effective wave budget {budgets.effective_max_waves} "
                f"for topology '{topology_name}'."
            )

        pair_allocations = self._allocate_pair_routes(
            model_spec=model_spec,
            scenario=scenario,
            n_wave=n_wave,
            use_failure_reroute=use_failure_reroute,
            severity_profile=severity,
        ) if pair_allocations_override is None else list(pair_allocations_override)
        local_metrics, local_time_by_dc, t_local_max, t_comp_max = self._evaluate_local_stage(
            model_spec=model_spec,
            scenario=scenario,
            data_parallel=data_parallel,
            dp_capacity_per_dc=dp_capacity_per_dc,
            unit_gpus=unit_gpus,
            tensor_parallel=tensor_parallel,
            pair_allocations=pair_allocations,
            dp_allocation_strategy=dp_allocation_strategy,
        )
        return self._build_result_from_pair_allocations(
            model_name=model_name,
            topology_name=topology_name,
            severity=severity,
            data_parallel=data_parallel,
            n_wave=n_wave,
            scenario=scenario,
            use_failure_reroute=use_failure_reroute,
            budgets=budgets,
            local_metrics=local_metrics,
            local_time_by_dc=local_time_by_dc,
            t_local_max=t_local_max,
            t_comp_max=t_comp_max,
            pair_allocations=pair_allocations,
            tensor_parallel=tensor_parallel,
            pipeline_parallel=pipeline_parallel,
            gpu_compensation_enabled=allow_gpu_compensation,
            extra_dp_capacity_per_dc=normalized_extra_dp_capacity,
        )

    def _build_event(
        self,
        model_spec: ModelSpec,
        data_parallel: int,
        tensor_parallel: int | None = None,
    ) -> SimpleNamespace:
        model_config = dict(model_spec.model_config)
        parallelism = dict(model_config.get("parallelism", {}))
        parallelism["data_parallel"] = data_parallel
        if tensor_parallel is not None:
            parallelism["tensor_parallel"] = int(tensor_parallel)
        model_config["parallelism"] = parallelism
        return SimpleNamespace(
            model_config=model_config,
            training_config=dict(model_spec.training_config),
        )

    def _evaluate_local_stage(
        self,
        model_spec: ModelSpec,
        scenario: TrainingTopologyScenario,
        data_parallel: int,
        dp_capacity_per_dc: Dict[int, int],
        unit_gpus: int,
        tensor_parallel: int,
        pair_allocations: List[PairAllocation] | None = None,
        dp_allocation_strategy: str = "heuristic",
    ) -> Tuple[List[LocalDcMetrics], Dict[int, float], float, float]:
        if dp_allocation_strategy == "heuristic":
            local_dp_per_dc = self._allocate_dp_groups(scenario.dc_nodes, dp_capacity_per_dc, data_parallel)
        elif dp_allocation_strategy == "optimal_t_iter":
            if pair_allocations is None:
                raise ValueError("pair_allocations are required for optimal_t_iter DP allocation.")
            local_dp_per_dc = self._allocate_dp_groups_optimal_t_iter(
                model_spec=model_spec,
                scenario=scenario,
                data_parallel=data_parallel,
                dp_capacity_per_dc=dp_capacity_per_dc,
                tensor_parallel=tensor_parallel,
                pair_allocations=pair_allocations,
            )
        else:
            raise ValueError(f"Unsupported dp_allocation_strategy: {dp_allocation_strategy}")
        event = self._build_event(model_spec, data_parallel, tensor_parallel=tensor_parallel)

        local_metrics: List[LocalDcMetrics] = []
        local_time_by_dc: Dict[int, float] = {}
        t_local_max = 0.0
        t_comp_max = 0.0
        for dc_id in scenario.dc_nodes:
            local_dp = local_dp_per_dc[dc_id]
            local_result = self.local_calculator.calculate_local_execution_time(
                event=event,
                dc_id=dc_id,
                data_parallel=data_parallel,
                local_dp=local_dp,
                gpu_model=str(self.graph.nodes[dc_id].get("gpu_type", "NVIDIA_A100")),
            )
            local_total = (
                local_result["local_comp_time"]
                + local_result["local_comm_time"]
                + local_result["local_bubble_time"]
            )
            local_metrics.append(
                LocalDcMetrics(
                    dc_id=dc_id,
                    local_dp=local_dp,
                    allocated_gpus=local_dp * unit_gpus,
                    local_comp_time=local_result["local_comp_time"],
                    local_comm_time=local_result["local_comm_time"],
                    local_bubble_time=local_result["local_bubble_time"],
                    local_total_time=local_total,
                )
            )
            local_time_by_dc[dc_id] = local_total
            t_local_max = max(t_local_max, local_total)
            t_comp_max = max(t_comp_max, local_result["local_comp_time"])
        return local_metrics, local_time_by_dc, t_local_max, t_comp_max

    def _dc_comm_penalties(self, scenario: TrainingTopologyScenario, pair_allocations: List[PairAllocation]) -> Dict[int, float]:
        penalties = {dc_id: 0.0 for dc_id in scenario.dc_nodes}
        for allocation in pair_allocations:
            src, dst = allocation.dc_pair
            penalties[src] = max(penalties[src], allocation.comm_time)
            penalties[dst] = max(penalties[dst], allocation.comm_time)
        return penalties

    def _local_time_profiles(
        self,
        model_spec: ModelSpec,
        scenario: TrainingTopologyScenario,
        data_parallel: int,
        dp_capacity_per_dc: Dict[int, int],
        tensor_parallel: int,
    ) -> Dict[int, List[Tuple[int, float]]]:
        event = self._build_event(model_spec, data_parallel, tensor_parallel=tensor_parallel)
        profiles: Dict[int, List[Tuple[int, float]]] = {}
        max_groups_for_any_dc = data_parallel - len(scenario.dc_nodes) + 1
        for dc_id in scenario.dc_nodes:
            max_local_dp = min(dp_capacity_per_dc[dc_id], max_groups_for_any_dc)
            profile: List[Tuple[int, float]] = []
            for local_dp in range(1, max_local_dp + 1):
                cache_key = (
                    model_spec.model_name,
                    scenario.name,
                    data_parallel,
                    tensor_parallel,
                    dc_id,
                    local_dp,
                )
                local_total = self._local_profile_cache.get(cache_key)
                if local_total is None:
                    local_result = self.local_calculator.calculate_local_execution_time(
                        event=event,
                        dc_id=dc_id,
                        data_parallel=data_parallel,
                        local_dp=local_dp,
                        gpu_model=str(self.graph.nodes[dc_id].get("gpu_type", "NVIDIA_A100")),
                    )
                    local_total = (
                        local_result["local_comp_time"]
                        + local_result["local_comm_time"]
                        + local_result["local_bubble_time"]
                    )
                    self._local_profile_cache[cache_key] = local_total
                profile.append((local_dp, local_total))
            profiles[dc_id] = profile
        return profiles

    @staticmethod
    def _prune_dp_allocation_states(states: List[DpAllocationState]) -> List[DpAllocationState]:
        pruned: List[DpAllocationState] = []
        for candidate in sorted(
            states,
            key=lambda state: (
                state.max_local,
                state.max_step,
                -state.min_step,
                state.allocation,
            ),
        ):
            dominated = False
            for existing in pruned:
                if (
                    existing.max_local <= candidate.max_local
                    and existing.max_step <= candidate.max_step
                    and existing.min_step >= candidate.min_step
                ):
                    dominated = True
                    break
            if dominated:
                continue

            pruned = [
                existing
                for existing in pruned
                if not (
                    candidate.max_local <= existing.max_local
                    and candidate.max_step <= existing.max_step
                    and candidate.min_step >= existing.min_step
                )
            ]
            pruned.append(candidate)
        return pruned

    def _allocate_dp_groups_optimal_t_iter(
        self,
        model_spec: ModelSpec,
        scenario: TrainingTopologyScenario,
        data_parallel: int,
        dp_capacity_per_dc: Dict[int, int],
        tensor_parallel: int,
        pair_allocations: List[PairAllocation],
    ) -> Dict[int, int]:
        dc_nodes = list(scenario.dc_nodes)
        for dc_id in dc_nodes:
            if dp_capacity_per_dc.get(dc_id, 0) < 1:
                raise ValueError(f"DC {dc_id} cannot host even one DP group under the current GPU budget.")

        comm_penalties = self._dc_comm_penalties(scenario, pair_allocations)
        local_profiles = self._local_time_profiles(
            model_spec=model_spec,
            scenario=scenario,
            data_parallel=data_parallel,
            dp_capacity_per_dc=dp_capacity_per_dc,
            tensor_parallel=tensor_parallel,
        )
        suffix_capacity: List[int] = [0] * (len(dc_nodes) + 1)
        suffix_minimum_groups: List[int] = [0] * (len(dc_nodes) + 1)
        for index in range(len(dc_nodes) - 1, -1, -1):
            dc_id = dc_nodes[index]
            suffix_capacity[index] = suffix_capacity[index + 1] + len(local_profiles[dc_id])
            suffix_minimum_groups[index] = suffix_minimum_groups[index + 1] + 1

        frontier: Dict[int, List[DpAllocationState]] = {0: [DpAllocationState(0, 0.0, 0.0, 0.0, tuple())]}
        for index, dc_id in enumerate(dc_nodes):
            next_frontier: Dict[int, List[DpAllocationState]] = {}
            remaining_capacity = suffix_capacity[index + 1]
            remaining_minimum = suffix_minimum_groups[index + 1]
            for assigned_so_far, states in frontier.items():
                for state in states:
                    for local_dp, local_total in local_profiles[dc_id]:
                        new_total = assigned_so_far + local_dp
                        remaining_needed = data_parallel - new_total
                        if remaining_needed < remaining_minimum or remaining_needed > remaining_capacity:
                            continue

                        step_time = local_total + comm_penalties[dc_id]
                        if not state.allocation:
                            new_state = DpAllocationState(
                                total_groups=new_total,
                                max_local=local_total,
                                max_step=step_time,
                                min_step=step_time,
                                allocation=(local_dp,),
                            )
                        else:
                            new_state = DpAllocationState(
                                total_groups=new_total,
                                max_local=max(state.max_local, local_total),
                                max_step=max(state.max_step, step_time),
                                min_step=min(state.min_step, step_time),
                                allocation=state.allocation + (local_dp,),
                            )
                        next_frontier.setdefault(new_total, []).append(new_state)

            frontier = {
                total_groups: self._prune_dp_allocation_states(states)
                for total_groups, states in next_frontier.items()
            }

        candidates = frontier.get(data_parallel, [])
        if not candidates:
            raise ValueError("No feasible DP allocation found under the given capacities.")

        best = min(
            candidates,
            key=lambda state: (
                state.max_local + state.max_step - state.min_step,
                state.max_step - state.min_step,
                state.max_local,
                state.allocation,
            ),
        )
        return {
            dc_id: local_dp
            for dc_id, local_dp in zip(dc_nodes, best.allocation)
        }

    def _build_result_from_pair_allocations(
        self,
        model_name: str,
        topology_name: str,
        severity: FailureSeverityProfile,
        data_parallel: int,
        n_wave: int,
        scenario: TrainingTopologyScenario,
        use_failure_reroute: bool,
        budgets: BudgetSnapshot,
        local_metrics: List[LocalDcMetrics],
        local_time_by_dc: Dict[int, float],
        t_local_max: float,
        t_comp_max: float,
        pair_allocations: List[PairAllocation],
        tensor_parallel: int,
        pipeline_parallel: int,
        gpu_compensation_enabled: bool,
        extra_dp_capacity_per_dc: Dict[int, int] | None = None,
        optical_extra_waves: int = 0,
        optical_compensation_steps: int = 0,
        optical_marginal_gain_trace: Tuple[float, ...] = (),
        optical_t_iter_trace: Tuple[float, ...] = (),
        optical_t_stall_trace: Tuple[float, ...] = (),
    ) -> PaperEvaluationResult:
        t_inter = max(allocation.comm_time for allocation in pair_allocations)
        max_path_length_km = max(allocation.path_length_km for allocation in pair_allocations)
        max_path_propagation_delay_s = max(allocation.propagation_delay_s for allocation in pair_allocations)
        bandwidth_eff_gbps = sum(allocation.bandwidth_gbps for allocation in pair_allocations) / max(1, len(pair_allocations))

        base_step_time_by_dc = {dc_id: local_time_by_dc[dc_id] for dc_id in scenario.dc_nodes}
        for allocation in pair_allocations:
            src, dst = allocation.dc_pair
            base_step_time_by_dc[src] = max(base_step_time_by_dc[src], local_time_by_dc[src] + allocation.comm_time)
            base_step_time_by_dc[dst] = max(base_step_time_by_dc[dst], local_time_by_dc[dst] + allocation.comm_time)

        _, avg_progress_gap, max_progress_gap, t_stall = self._simulate_ssp(base_step_time_by_dc)
        t_iter = t_local_max + t_inter + t_stall

        before_lengths_km = self._reference_pair_path_lengths_km(scenario)
        before_max_delay = max(before_lengths_km) * 1000.0 / SPEED_OF_LIGHT_FIBER
        after_max_delay = max_path_length_km * 1000.0 / SPEED_OF_LIGHT_FIBER
        if before_max_delay > 0:
            propagation_latency_growth_ratio = (after_max_delay - before_max_delay) / before_max_delay
        else:
            propagation_latency_growth_ratio = 0.0

        return PaperEvaluationResult(
            model_name=model_name,
            topology_name=topology_name,
            use_failure_reroute=use_failure_reroute,
            severity_name=severity.name,
            reroute_length_scale=severity.reroute_length_scale,
            reroute_bandwidth_scale=severity.reroute_bandwidth_scale,
            data_parallel=data_parallel,
            tensor_parallel=tensor_parallel,
            pipeline_parallel=pipeline_parallel,
            n_wave=n_wave,
            alpha=1.0,
            t_iter=t_iter,
            t_inter=t_inter,
            t_local_max=t_local_max,
            t_comp_max=t_comp_max,
            t_stall=t_stall,
            delta_balance=abs(t_local_max - t_inter),
            imbalance_ratio=(
                max(t_local_max, t_inter) / min(t_local_max, t_inter)
                if min(t_local_max, t_inter) > 0
                else float("inf")
            ),
            r_inter=(t_inter / t_iter) if t_iter > 0 else 0.0,
            bandwidth_eff_gbps=bandwidth_eff_gbps,
            max_path_length_km=max_path_length_km,
            max_path_propagation_delay_s=max_path_propagation_delay_s,
            propagation_latency_growth_ratio=propagation_latency_growth_ratio,
            avg_progress_gap=avg_progress_gap,
            max_progress_gap=max_progress_gap,
            ssp_bound=self.ssp_bound,
            ssp_simulation_steps=self.ssp_simulation_steps,
            budgets=budgets,
            local_metrics=local_metrics,
            pair_allocations=pair_allocations,
            gpu_compensation_enabled=gpu_compensation_enabled,
            extra_dp_capacity_per_dc=(dict(extra_dp_capacity_per_dc) if extra_dp_capacity_per_dc else {}),
            total_extra_dp_groups=sum(extra_dp_capacity_per_dc.values()) if extra_dp_capacity_per_dc else 0,
            optical_extra_waves=optical_extra_waves,
            optical_compensation_steps=optical_compensation_steps,
            optical_marginal_gain_trace=optical_marginal_gain_trace,
            optical_t_iter_trace=optical_t_iter_trace,
            optical_t_stall_trace=optical_t_stall_trace,
        )

    def _calculate_wave_budget(self, scenario: TrainingTopologyScenario, use_failure_reroute: bool) -> Tuple[int, int]:
        path_wave_caps: List[int] = []
        for path_link_ids in scenario.communication_paths(use_failure_reroute):
            wave_cap = len(self._path_common_available_wavelength_ids(path_link_ids))
            path_wave_caps.append(wave_cap)

        raw_max_waves = min(path_wave_caps) if path_wave_caps else 0
        effective_max_waves = math.floor(raw_max_waves * self.rho_wave)
        if raw_max_waves > 0:
            effective_max_waves = max(1, effective_max_waves)
        return raw_max_waves, effective_max_waves

    def _path_lengths_km(
        self,
        scenario: TrainingTopologyScenario,
        use_failure_reroute: bool,
        severity_profile: FailureSeverityProfile | None,
    ) -> List[float]:
        path_lengths: List[float] = []
        severity = severity_profile or FailureSeverityProfile()
        for path_link_ids in scenario.communication_paths(use_failure_reroute):
            length_km = sum(float(self.link_metadata[link_id]["length_km"]) for link_id in path_link_ids)
            if use_failure_reroute:
                length_km *= severity.reroute_length_scale
            path_lengths.append(length_km)
        return path_lengths

    def _normalized_adjustment_distance(
        self,
        result: PaperEvaluationResult,
        tp_base: int,
        n_wave_base: int,
    ) -> float:
        tp_gap = self.recovery_distance_weight_dp * abs(result.tensor_parallel - tp_base) / max(1, tp_base)
        n_wave_gap = self.recovery_distance_weight_wave * abs(result.n_wave - n_wave_base) / max(1, n_wave_base)
        return tp_gap + n_wave_gap

    def _operating_point_distance(
        self,
        candidate: PaperEvaluationResult,
        reference: PaperEvaluationResult,
    ) -> float:
        """Measure how close a candidate is to the pre-failure compute/communication regime."""
        local_ref = max(reference.t_local_max, 1e-9)
        inter_ref = max(reference.t_inter, 1e-9)
        local_gap = (candidate.t_local_max - reference.t_local_max) / local_ref
        inter_gap = (candidate.t_inter - reference.t_inter) / inter_ref
        return math.hypot(local_gap, inter_gap)

    def _select_recovery_preferred_candidate(
        self,
        candidates: List[PaperEvaluationResult],
        target_t_iter: float,
        tp_base: int,
        n_wave_base: int,
    ) -> PaperEvaluationResult:
        if not candidates:
            raise ValueError("No feasible candidates were generated during paper-state optimization.")

        recovered = [candidate for candidate in candidates if candidate.t_iter <= target_t_iter]
        if recovered:
            return min(
                recovered,
                key=lambda candidate: (
                    self._normalized_adjustment_distance(candidate, tp_base, n_wave_base),
                    abs(target_t_iter - candidate.t_iter),
                    candidate.t_iter,
                    abs(candidate.n_wave - n_wave_base),
                    abs(candidate.tensor_parallel - tp_base),
                ),
            )

        return min(
            candidates,
            key=lambda candidate: (
                candidate.t_iter,
                self._normalized_adjustment_distance(candidate, tp_base, n_wave_base),
                abs(candidate.t_iter - target_t_iter),
                abs(candidate.n_wave - n_wave_base),
                abs(candidate.tensor_parallel - tp_base),
            ),
        )

    def _select_training_optimal_candidate(
        self,
        candidates: List[PaperEvaluationResult],
        tp_base: int,
        n_wave_base: int,
        before_failure_result: PaperEvaluationResult | None = None,
    ) -> PaperEvaluationResult:
        if not candidates:
            raise ValueError("No feasible candidates were generated during training-optimal selection.")

        return min(
            candidates,
            key=lambda candidate: (
                candidate.t_iter,
                self._operating_point_distance(candidate, before_failure_result)
                if before_failure_result is not None
                else 0.0,
                self._normalized_adjustment_distance(candidate, tp_base, n_wave_base),
                candidate.n_wave,
                candidate.tensor_parallel,
            ),
        )

    def _select_joint_operating_point_candidate(
        self,
        candidates: List[PaperEvaluationResult],
        before_failure_result: PaperEvaluationResult,
    ) -> PaperEvaluationResult:
        """
        Select the recovered candidate that best restores the pre-failure operating point.

        The primary recovery goal is to bring T_iter back to the pre-failure level.
        Among candidates that satisfy this hard constraint, prefer the one whose
        (T_local_max, T_inter) decomposition is closest to the pre-failure regime.
        """
        if not candidates:
            raise ValueError("No feasible candidates were generated during joint optimization.")

        target_t_iter = before_failure_result.t_iter
        recovered = [candidate for candidate in candidates if candidate.t_iter <= target_t_iter]
        if recovered:
            return min(
                recovered,
                key=lambda candidate: (
                    self._operating_point_distance(candidate, before_failure_result),
                    abs(candidate.t_iter - target_t_iter),
                    abs(candidate.r_inter - before_failure_result.r_inter),
                    candidate.t_iter,
                ),
            )

        return min(
            candidates,
            key=lambda candidate: (
                candidate.t_iter,
                self._operating_point_distance(candidate, before_failure_result),
                abs(candidate.r_inter - before_failure_result.r_inter),
                abs(candidate.t_iter - target_t_iter),
            ),
        )

    def _allocate_dp_groups_greedy_legacy(
        self,
        dc_nodes: List[int],
        dp_capacity_per_dc: Dict[int, int],
        data_parallel: int,
    ) -> Dict[int, int]:
        for dc_id in dc_nodes:
            if dp_capacity_per_dc.get(dc_id, 0) < 1:
                raise ValueError(f"DC {dc_id} cannot host even one DP group under the current GPU budget.")

        allocation = {dc_id: 1 for dc_id in dc_nodes}
        remaining = data_parallel - len(dc_nodes)
        while remaining > 0:
            candidate = max(
                dc_nodes,
                key=lambda dc_id: (dp_capacity_per_dc[dc_id] - allocation[dc_id], -allocation[dc_id], -dc_id),
            )
            residual = dp_capacity_per_dc[candidate] - allocation[candidate]
            if residual <= 0:
                raise ValueError("Not enough residual DP capacity to complete the allocation.")
            allocation[candidate] += 1
            remaining -= 1
        return allocation

    def _bounded_weighted_allocation(
        self,
        dc_nodes: List[int],
        capacities: Dict[int, int],
        weights: Dict[int, float],
        total: int,
    ) -> Dict[int, int]:
        if total < len(dc_nodes):
            raise ValueError("Total allocation must be at least the number of selected DCs.")

        allocation = {dc_id: 1 for dc_id in dc_nodes}
        remaining = total - len(dc_nodes)
        residual_capacity = {dc_id: capacities[dc_id] - 1 for dc_id in dc_nodes}

        while remaining > 0:
            eligible = [dc_id for dc_id in dc_nodes if residual_capacity[dc_id] > 0]
            if not eligible:
                raise ValueError("Not enough residual DP capacity to complete the allocation.")

            total_weight = sum(max(weights.get(dc_id, 0.0), 0.0) for dc_id in eligible)
            if total_weight <= 0.0:
                normalized_weights = {dc_id: 1.0 for dc_id in eligible}
                total_weight = float(len(eligible))
            else:
                normalized_weights = {
                    dc_id: max(weights.get(dc_id, 0.0), 0.0)
                    for dc_id in eligible
                }

            quota = {
                dc_id: remaining * normalized_weights[dc_id] / total_weight
                for dc_id in eligible
            }
            increments = {
                dc_id: min(residual_capacity[dc_id], int(math.floor(quota[dc_id])))
                for dc_id in eligible
            }
            assigned = sum(increments.values())

            if assigned == 0:
                ordered = sorted(
                    eligible,
                    key=lambda dc_id: (
                        quota[dc_id] - math.floor(quota[dc_id]),
                        normalized_weights[dc_id],
                        residual_capacity[dc_id],
                        -dc_id,
                    ),
                    reverse=True,
                )
                chosen = ordered[0]
                increments[chosen] = 1
                assigned = 1
            else:
                leftover = remaining - assigned
                if leftover > 0:
                    ordered = sorted(
                        eligible,
                        key=lambda dc_id: (
                            quota[dc_id] - math.floor(quota[dc_id]),
                            normalized_weights[dc_id],
                            residual_capacity[dc_id],
                            -dc_id,
                        ),
                        reverse=True,
                    )
                    for dc_id in ordered:
                        if leftover <= 0:
                            break
                        if increments[dc_id] >= residual_capacity[dc_id]:
                            continue
                        increments[dc_id] += 1
                        assigned += 1
                        leftover -= 1

            for dc_id, extra in increments.items():
                if extra <= 0:
                    continue
                allocation[dc_id] += extra
                residual_capacity[dc_id] -= extra

            remaining -= assigned

        return allocation

    def _allocate_dp_groups(
        self,
        dc_nodes: List[int],
        dp_capacity_per_dc: Dict[int, int],
        data_parallel: int,
    ) -> Dict[int, int]:
        for dc_id in dc_nodes:
            if dp_capacity_per_dc.get(dc_id, 0) < 1:
                raise ValueError(f"DC {dc_id} cannot host even one DP group under the current GPU budget.")

        soft_capacities: Dict[int, int] = {}
        reserve_capacities: Dict[int, int] = {}
        soft_weights: Dict[int, float] = {}

        for dc_id in dc_nodes:
            capacity = dp_capacity_per_dc[dc_id]
            max_reserve = max(0, capacity - 1)
            reserve = min(
                max_reserve,
                max(self.min_reserved_dp_groups, int(math.ceil(capacity * self.dp_reserve_ratio))),
            )
            soft_capacity = max(1, capacity - reserve)
            reserve_capacities[dc_id] = capacity - soft_capacity
            soft_capacities[dc_id] = soft_capacity
            soft_weights[dc_id] = float(soft_capacity) ** self.dp_softness_beta

        soft_total_capacity = sum(soft_capacities.values())
        if data_parallel <= soft_total_capacity:
            return self._bounded_weighted_allocation(
                dc_nodes,
                soft_capacities,
                soft_weights,
                data_parallel,
            )

        allocation = self._bounded_weighted_allocation(
            dc_nodes,
            soft_capacities,
            soft_weights,
            soft_total_capacity,
        )
        spillover = data_parallel - soft_total_capacity
        full_capacities = {
            dc_id: allocation[dc_id] + reserve_capacities[dc_id]
            for dc_id in dc_nodes
        }
        reserve_weights = {
            dc_id: float(max(1, reserve_capacities[dc_id])) ** self.dp_softness_beta
            for dc_id in dc_nodes
        }
        return self._bounded_weighted_allocation(
            dc_nodes,
            full_capacities,
            reserve_weights,
            soft_total_capacity + spillover,
        )

    def _collective_alpha(self, data_parallel: int, num_dcs: int) -> float:
        if self.alpha_mode == "constant":
            alpha = 1.0
        elif self.alpha_mode == "linear_dp":
            alpha = float(data_parallel)
        elif self.alpha_mode == "dp_minus_one":
            alpha = float(max(1, data_parallel - 1))
        elif self.alpha_mode == "groups_per_dc":
            alpha = float(max(1, math.ceil(data_parallel / num_dcs)))
        elif self.alpha_mode == "log2_dp":
            alpha = float(max(1, math.ceil(math.log2(max(1, data_parallel)))))
        else:
            raise ValueError(f"Unsupported alpha_mode: {self.alpha_mode}")
        return self.alpha_scale * alpha

    def _pair_path_candidates(
        self,
        scenario: TrainingTopologyScenario,
        use_failure_reroute: bool,
        severity_profile: FailureSeverityProfile,
    ) -> Dict[Tuple[int, int], List[Tuple[int, ...]]]:
        rerouted_links = scenario.rerouted_replacement_links(use_failure_reroute)
        backbone_link_ids = scenario.effective_backbone_link_ids(use_failure_reroute)
        subgraph = nx.Graph()
        for link_id in backbone_link_ids:
            link_meta = self.link_metadata[int(link_id)]
            src = int(link_meta["src"])
            dst = int(link_meta["dst"])
            weight = float(link_meta["length_km"])
            if use_failure_reroute and int(link_id) in rerouted_links:
                weight *= severity_profile.reroute_length_scale
            subgraph.add_edge(src, dst, link_id=int(link_id), weight=weight)

        dc_nodes = list(scenario.dc_nodes)
        pair_candidates: Dict[Tuple[int, int], List[Tuple[int, ...]]] = {}

        for left in range(len(dc_nodes)):
            for right in range(left + 1, len(dc_nodes)):
                src = dc_nodes[left]
                dst = dc_nodes[right]
                try:
                    node_path = nx.shortest_path(subgraph, src, dst, weight="weight")
                except (nx.NetworkXNoPath, nx.NodeNotFound) as exc:
                    raise ValueError(
                        f"No feasible training-backbone path exists between DC {src} and DC {dst} "
                        f"for topology '{scenario.name}' with use_failure_reroute={use_failure_reroute}."
                    ) from exc

                link_path: List[int] = []
                for path_src, path_dst in zip(node_path, node_path[1:]):
                    link_path.append(int(subgraph[path_src][path_dst]["link_id"]))
                pair_candidates[(src, dst)] = [tuple(link_path)]
        return pair_candidates

    @staticmethod
    def _flatten_segments(segments: List[List[int]]) -> List[int]:
        flattened: List[int] = []
        for segment in segments:
            flattened.extend(int(link_id) for link_id in segment)
        return flattened

    def _link_path_length_km(
        self,
        link_ids: Tuple[int, ...] | List[int],
        rerouted_links: set[int],
        severity_profile: FailureSeverityProfile,
        use_failure_reroute: bool,
    ) -> float:
        total = 0.0
        for link_id in link_ids:
            length = float(self.link_metadata[int(link_id)]["length_km"])
            if use_failure_reroute and int(link_id) in rerouted_links:
                length *= severity_profile.reroute_length_scale
            total += length
        return total

    def _reference_pair_path_lengths_km(self, scenario: TrainingTopologyScenario) -> List[float]:
        pair_candidates = self._pair_path_candidates(
            scenario=scenario,
            use_failure_reroute=False,
            severity_profile=FailureSeverityProfile(),
        )
        return [
            self._link_path_length_km(candidates[0], set(), FailureSeverityProfile(), False)
            for candidates in pair_candidates.values()
        ]

    def _select_wavelengths_for_link_path(
        self,
        link_ids: Tuple[int, ...],
        requested_waves: int,
        link_allocated_wavelengths: Dict[int, set[int]],
    ) -> Tuple[int, ...] | None:
        available_wavelengths: set[int] | None = None
        for link_id in link_ids:
            link_available = self._link_available_wavelength_ids(int(link_id))
            link_available -= link_allocated_wavelengths.get(int(link_id), set())
            available_wavelengths = link_available if available_wavelengths is None else available_wavelengths & link_available
            if not available_wavelengths:
                return None

        if available_wavelengths is None or len(available_wavelengths) < requested_waves:
            return None
        return tuple(sorted(available_wavelengths)[:requested_waves])

    def _common_idle_wavelengths_for_link_path(
        self,
        link_ids: Tuple[int, ...],
        link_allocated_wavelengths: Dict[int, set[int]],
    ) -> Tuple[int, ...]:
        available_wavelengths: set[int] | None = None
        for link_id in link_ids:
            link_available = self._link_available_wavelength_ids(int(link_id))
            link_available -= link_allocated_wavelengths.get(int(link_id), set())
            available_wavelengths = link_available if available_wavelengths is None else available_wavelengths & link_available
            if not available_wavelengths:
                return ()
        return tuple(sorted(available_wavelengths or ()))

    def _allocate_pair_routes(
        self,
        model_spec: ModelSpec,
        scenario: TrainingTopologyScenario,
        n_wave: int,
        use_failure_reroute: bool,
        severity_profile: FailureSeverityProfile,
    ) -> List[PairAllocation]:
        if n_wave <= 0:
            raise ValueError("Per-pair target wavelength count must be positive.")

        pair_candidates = self._pair_path_candidates(scenario, use_failure_reroute, severity_profile)
        rerouted_links = scenario.rerouted_replacement_links(use_failure_reroute)
        bandwidth_scale = severity_profile.reroute_bandwidth_scale if use_failure_reroute else 1.0
        link_allocated_wavelengths: Dict[int, set[int]] = {}

        pair_order = sorted(
            pair_candidates.items(),
            key=lambda item: (
                self._link_path_length_km(item[1][0], rerouted_links, severity_profile, use_failure_reroute),
                item[0],
            ),
        )

        pair_state: Dict[Tuple[int, int], Dict[str, object]] = {}
        for dc_pair, candidate_paths in pair_order:
            chosen_path: Tuple[int, ...] | None = None
            chosen_wavelength = None
            for link_ids in candidate_paths:
                wavelength_ids = self._select_wavelengths_for_link_path(
                    link_ids=link_ids,
                    requested_waves=1,
                    link_allocated_wavelengths=link_allocated_wavelengths,
                )
                if wavelength_ids is None:
                    continue
                for link_id in link_ids:
                    link_allocated_wavelengths.setdefault(int(link_id), set()).update(wavelength_ids)
                chosen_path = link_ids
                chosen_wavelength = wavelength_ids[0]
                break

            if chosen_path is None or chosen_wavelength is None:
                raise ValueError(
                    f"Pair {dc_pair} cannot obtain even one feasible wavelength under n_wave={n_wave}."
                )

            pair_state[dc_pair] = {
                "link_ids": chosen_path,
                "wavelength_ids": [int(chosen_wavelength)],
            }

        for _ in range(2, n_wave + 1):
            for dc_pair, _candidate_paths in pair_order:
                link_ids = tuple(pair_state[dc_pair]["link_ids"])  # type: ignore[arg-type]
                wavelength_ids = self._select_wavelengths_for_link_path(
                    link_ids=link_ids,
                    requested_waves=1,
                    link_allocated_wavelengths=link_allocated_wavelengths,
                )
                if wavelength_ids is None:
                    continue
                for link_id in link_ids:
                    link_allocated_wavelengths.setdefault(int(link_id), set()).update(wavelength_ids)
                pair_state[dc_pair]["wavelength_ids"].append(int(wavelength_ids[0]))  # type: ignore[index]

        allocations: List[PairAllocation] = []
        for dc_pair, _candidate_paths in pair_order:
            link_ids = tuple(pair_state[dc_pair]["link_ids"])  # type: ignore[arg-type]
            wavelength_ids = tuple(pair_state[dc_pair]["wavelength_ids"])  # type: ignore[arg-type]
            allocated_n_wave = len(wavelength_ids)
            bandwidth_gbps = allocated_n_wave * self.bw_wave_gbps * bandwidth_scale
            path_length_km = self._link_path_length_km(
                link_ids,
                rerouted_links,
                severity_profile,
                use_failure_reroute,
            )
            propagation_delay_s = path_length_km * 1000.0 / SPEED_OF_LIGHT_FIBER
            comm_time = self.cross_domain_calculator.calculate_cross_domain_comm_time(
                model_params=float(model_spec.model_config["model_params"]),
                data_type=model_spec.training_config.get("precision", "fp16"),
                num_dcs=len(scenario.dc_nodes),
                aggregate_bw=bandwidth_gbps,
                path_length=path_length_km * 1000.0,
            )
            allocations.append(
                PairAllocation(
                    dc_pair=dc_pair,
                    link_ids=link_ids,
                    wavelength_ids=wavelength_ids,
                    allocated_n_wave=allocated_n_wave,
                    bandwidth_gbps=bandwidth_gbps,
                    path_length_km=path_length_km,
                    propagation_delay_s=propagation_delay_s,
                    comm_time=comm_time,
                )
            )

        return allocations

    def _rebuild_pair_allocations_from_state(
        self,
        model_spec: ModelSpec,
        scenario: TrainingTopologyScenario,
        pair_state: Dict[Tuple[int, int], Dict[str, object]],
        use_failure_reroute: bool,
        severity_profile: FailureSeverityProfile,
    ) -> List[PairAllocation]:
        rerouted_links = scenario.rerouted_replacement_links(use_failure_reroute)
        bandwidth_scale = severity_profile.reroute_bandwidth_scale if use_failure_reroute else 1.0
        allocations: List[PairAllocation] = []

        for dc_pair in sorted(pair_state):
            state = pair_state[dc_pair]
            link_ids = tuple(int(link_id) for link_id in state["link_ids"])  # type: ignore[index]
            wavelength_ids = tuple(sorted(int(wavelength_id) for wavelength_id in state["wavelength_ids"]))  # type: ignore[index]
            allocated_n_wave = len(wavelength_ids)
            bandwidth_gbps = allocated_n_wave * self.bw_wave_gbps * bandwidth_scale
            path_length_km = self._link_path_length_km(
                link_ids,
                rerouted_links,
                severity_profile,
                use_failure_reroute,
            )
            propagation_delay_s = path_length_km * 1000.0 / SPEED_OF_LIGHT_FIBER
            comm_time = self.cross_domain_calculator.calculate_cross_domain_comm_time(
                model_params=float(model_spec.model_config["model_params"]),
                data_type=model_spec.training_config.get("precision", "fp16"),
                num_dcs=len(scenario.dc_nodes),
                aggregate_bw=bandwidth_gbps,
                path_length=path_length_km * 1000.0,
            )
            allocations.append(
                PairAllocation(
                    dc_pair=dc_pair,
                    link_ids=link_ids,
                    wavelength_ids=wavelength_ids,
                    allocated_n_wave=allocated_n_wave,
                    bandwidth_gbps=bandwidth_gbps,
                    path_length_km=path_length_km,
                    propagation_delay_s=propagation_delay_s,
                    comm_time=comm_time,
                )
            )

        return allocations

    @staticmethod
    def _pair_state_from_allocations(
        pair_allocations: List[PairAllocation],
    ) -> Tuple[Dict[Tuple[int, int], Dict[str, object]], Dict[int, set[int]]]:
        pair_state: Dict[Tuple[int, int], Dict[str, object]] = {}
        link_allocated_wavelengths: Dict[int, set[int]] = {}
        for allocation in pair_allocations:
            wavelength_ids = [int(wavelength_id) for wavelength_id in allocation.wavelength_ids]
            pair_state[allocation.dc_pair] = {
                "link_ids": tuple(int(link_id) for link_id in allocation.link_ids),
                "wavelength_ids": list(wavelength_ids),
            }
            for link_id in allocation.link_ids:
                link_allocated_wavelengths.setdefault(int(link_id), set()).update(wavelength_ids)
        return pair_state, link_allocated_wavelengths

    def allocate_extra_waves_to_pairs(
        self,
        model_name: str,
        topology_name: str,
        base_pair_allocations: List[PairAllocation],
        extra_waves_per_pair: Dict[Tuple[int, int], int],
        use_failure_reroute: bool,
        severity_profile: FailureSeverityProfile | None = None,
    ) -> List[PairAllocation] | None:
        severity = severity_profile or FailureSeverityProfile()
        model_spec = self.get_model_spec(model_name)
        scenario = self.get_training_topology(topology_name)
        pair_state, link_allocated_wavelengths = self._pair_state_from_allocations(base_pair_allocations)

        normalized_requests = {
            tuple(sorted((int(pair[0]), int(pair[1])))): max(0, int(extra_waves))
            for pair, extra_waves in extra_waves_per_pair.items()
            if int(extra_waves) > 0
        }
        if not normalized_requests:
            return list(base_pair_allocations)

        for dc_pair in sorted(normalized_requests):
            if dc_pair not in pair_state:
                raise KeyError(f"Unknown dc_pair {dc_pair} for topology '{topology_name}'.")
            link_ids = tuple(pair_state[dc_pair]["link_ids"])  # type: ignore[arg-type]
            for _ in range(normalized_requests[dc_pair]):
                common_idle = self._common_idle_wavelengths_for_link_path(link_ids, link_allocated_wavelengths)
                if not common_idle:
                    return None
                selected_wave = int(common_idle[0])
                pair_state[dc_pair]["wavelength_ids"].append(selected_wave)  # type: ignore[index]
                for link_id in link_ids:
                    link_allocated_wavelengths.setdefault(int(link_id), set()).add(selected_wave)

        return self._rebuild_pair_allocations_from_state(
            model_spec=model_spec,
            scenario=scenario,
            pair_state=pair_state,
            use_failure_reroute=use_failure_reroute,
            severity_profile=severity,
        )

    def _incremental_optical_compensation(
        self,
        model_name: str,
        topology_name: str,
        before_failure_result: PaperEvaluationResult,
        initial_result: PaperEvaluationResult,
        target_t_iter: float,
        severity_profile: FailureSeverityProfile | None = None,
        stop_when_recovered: bool = True,
    ) -> PaperEvaluationResult:
        severity = severity_profile or FailureSeverityProfile()
        model_spec = self.get_model_spec(model_name)
        scenario = self.get_training_topology(topology_name)
        local_time_by_dc = {
            metric.dc_id: metric.local_total_time
            for metric in initial_result.local_metrics
        }

        pair_state: Dict[Tuple[int, int], Dict[str, object]] = {}
        link_allocated_wavelengths: Dict[int, set[int]] = {}
        for allocation in initial_result.pair_allocations:
            wavelength_ids = [int(wavelength_id) for wavelength_id in allocation.wavelength_ids]
            pair_state[allocation.dc_pair] = {
                "link_ids": tuple(int(link_id) for link_id in allocation.link_ids),
                "wavelength_ids": list(wavelength_ids),
            }
            for link_id in allocation.link_ids:
                link_allocated_wavelengths.setdefault(int(link_id), set()).update(wavelength_ids)

        before_comm_time = {
            allocation.dc_pair: allocation.comm_time
            for allocation in before_failure_result.pair_allocations
        }
        current_result = initial_result
        candidate_results: List[PaperEvaluationResult] = [initial_result]
        marginal_gain_trace: List[float] = []
        t_iter_trace: List[float] = [initial_result.t_iter]
        t_stall_trace: List[float] = [initial_result.t_stall]
        compensation_steps = 0

        while (current_result.t_iter > target_t_iter) if stop_when_recovered else True:
            current_comm_time = {
                allocation.dc_pair: allocation.comm_time
                for allocation in current_result.pair_allocations
            }
            comm_max_after = max(current_comm_time.values(), default=0.0)
            critical_candidates: List[Tuple[float, float, int, Tuple[int, int], Tuple[int, ...]]] = []

            for dc_pair, comm_after in current_comm_time.items():
                comm_before = max(before_comm_time.get(dc_pair, 0.0), 1e-9)
                degradation_ratio = (comm_after - comm_before) / comm_before
                if degradation_ratio < self.optical_degradation_gamma:
                    continue
                if comm_after < self.optical_critical_beta * comm_max_after:
                    continue

                link_ids = tuple(pair_state[dc_pair]["link_ids"])  # type: ignore[arg-type]
                common_idle = self._common_idle_wavelengths_for_link_path(link_ids, link_allocated_wavelengths)
                critical_candidates.append(
                    (
                        degradation_ratio,
                        comm_after,
                        len(common_idle),
                        dc_pair,
                        common_idle,
                    )
                )

            if not critical_candidates:
                break

            critical_candidates.sort(
                key=lambda item: (
                    -item[0],
                    -item[1],
                    item[2],
                    item[3],
                )
            )

            selected_pair: Tuple[int, int] | None = None
            selected_wave: int | None = None
            for _degradation_ratio, _comm_after, _idle_count, dc_pair, common_idle in critical_candidates:
                if not common_idle:
                    continue
                selected_pair = dc_pair
                selected_wave = int(common_idle[0])
                break

            if selected_pair is None or selected_wave is None:
                break

            pair_state[selected_pair]["wavelength_ids"].append(selected_wave)  # type: ignore[index]
            link_ids = tuple(pair_state[selected_pair]["link_ids"])  # type: ignore[arg-type]
            for link_id in link_ids:
                link_allocated_wavelengths.setdefault(int(link_id), set()).add(selected_wave)

            previous_t_iter = current_result.t_iter
            pair_allocations = self._rebuild_pair_allocations_from_state(
                model_spec=model_spec,
                scenario=scenario,
                pair_state=pair_state,
                use_failure_reroute=True,
                severity_profile=severity,
            )
            current_result = self._build_result_from_pair_allocations(
                model_name=model_name,
                topology_name=topology_name,
                severity=severity,
                data_parallel=initial_result.data_parallel,
                tensor_parallel=initial_result.tensor_parallel,
                pipeline_parallel=initial_result.pipeline_parallel,
                n_wave=max(allocation.allocated_n_wave for allocation in pair_allocations),
                scenario=scenario,
                use_failure_reroute=True,
                budgets=initial_result.budgets,
                local_metrics=initial_result.local_metrics,
                local_time_by_dc=local_time_by_dc,
                t_local_max=initial_result.t_local_max,
                t_comp_max=initial_result.t_comp_max,
                pair_allocations=pair_allocations,
                gpu_compensation_enabled=initial_result.gpu_compensation_enabled,
                extra_dp_capacity_per_dc=initial_result.extra_dp_capacity_per_dc,
                optical_extra_waves=compensation_steps + 1,
                optical_compensation_steps=compensation_steps + 1,
                optical_marginal_gain_trace=tuple(marginal_gain_trace),
                optical_t_iter_trace=tuple(t_iter_trace),
                optical_t_stall_trace=tuple(t_stall_trace),
            )
            marginal_gain_trace.append(previous_t_iter - current_result.t_iter)
            compensation_steps += 1
            t_iter_trace.append(current_result.t_iter)
            t_stall_trace.append(current_result.t_stall)
            current_result = self._build_result_from_pair_allocations(
                model_name=model_name,
                topology_name=topology_name,
                severity=severity,
                data_parallel=initial_result.data_parallel,
                tensor_parallel=initial_result.tensor_parallel,
                pipeline_parallel=initial_result.pipeline_parallel,
                n_wave=max(allocation.allocated_n_wave for allocation in pair_allocations),
                scenario=scenario,
                use_failure_reroute=True,
                budgets=initial_result.budgets,
                local_metrics=initial_result.local_metrics,
                local_time_by_dc=local_time_by_dc,
                t_local_max=initial_result.t_local_max,
                t_comp_max=initial_result.t_comp_max,
                pair_allocations=pair_allocations,
                gpu_compensation_enabled=initial_result.gpu_compensation_enabled,
                extra_dp_capacity_per_dc=initial_result.extra_dp_capacity_per_dc,
                optical_extra_waves=compensation_steps,
                optical_compensation_steps=compensation_steps,
                optical_marginal_gain_trace=tuple(marginal_gain_trace),
                optical_t_iter_trace=tuple(t_iter_trace),
                optical_t_stall_trace=tuple(t_stall_trace),
            )
            candidate_results.append(current_result)

        if stop_when_recovered:
            selected = self._select_recovery_preferred_candidate(
                candidate_results,
                target_t_iter,
                before_failure_result.tensor_parallel,
                before_failure_result.n_wave,
            )
        else:
            selected = self._select_training_optimal_candidate(
                candidate_results,
                before_failure_result.tensor_parallel,
                before_failure_result.n_wave,
                before_failure_result=before_failure_result,
            )
        return self._build_result_from_pair_allocations(
            model_name=selected.model_name,
            topology_name=selected.topology_name,
            severity=FailureSeverityProfile(
                name=selected.severity_name,
                reroute_length_scale=selected.reroute_length_scale,
                reroute_bandwidth_scale=selected.reroute_bandwidth_scale,
            ),
            data_parallel=selected.data_parallel,
            tensor_parallel=selected.tensor_parallel,
            pipeline_parallel=selected.pipeline_parallel,
            n_wave=selected.n_wave,
            scenario=scenario,
            use_failure_reroute=selected.use_failure_reroute,
            budgets=selected.budgets,
            local_metrics=selected.local_metrics,
            local_time_by_dc=local_time_by_dc,
            t_local_max=selected.t_local_max,
            t_comp_max=selected.t_comp_max,
            pair_allocations=selected.pair_allocations,
            gpu_compensation_enabled=selected.gpu_compensation_enabled,
            extra_dp_capacity_per_dc=selected.extra_dp_capacity_per_dc,
            optical_extra_waves=selected.optical_extra_waves,
            optical_compensation_steps=selected.optical_compensation_steps,
            optical_marginal_gain_trace=tuple(marginal_gain_trace),
            optical_t_iter_trace=tuple(t_iter_trace),
            optical_t_stall_trace=tuple(t_stall_trace),
        )

    def _simulate_ssp(
        self,
        base_step_time_by_dc: Dict[int, float],
    ) -> Tuple[float, float, int, float]:
        progress = {dc_id: 0 for dc_id in base_step_time_by_dc}
        finish_time_by_dc = {
            dc_id: step_time
            for dc_id, step_time in base_step_time_by_dc.items()
        }
        stalled_since = {dc_id: None for dc_id in base_step_time_by_dc}
        current_time = 0.0
        weighted_gap_sum = 0.0
        max_gap = 0
        total_system_stall_time = 0.0

        while min(progress.values()) < self.ssp_simulation_steps:
            next_finish_time = min(
                finish_time
                for finish_time in finish_time_by_dc.values()
                if finish_time is not None
            )
            current_gap = max(progress.values()) - min(progress.values())
            interval = next_finish_time - current_time
            weighted_gap_sum += current_gap * interval
            if any(stalled_time is not None for stalled_time in stalled_since.values()):
                total_system_stall_time += interval
            max_gap = max(max_gap, current_gap)
            current_time = next_finish_time

            completed_dcs = [
                dc_id
                for dc_id, finish_time in finish_time_by_dc.items()
                if finish_time is not None and math.isclose(finish_time, current_time, rel_tol=0.0, abs_tol=1e-12)
            ]
            for dc_id in completed_dcs:
                finish_time_by_dc[dc_id] = None
                progress[dc_id] += 1

            self._resume_unblocked_dcs(progress, finish_time_by_dc, stalled_since, current_time, base_step_time_by_dc)
            max_gap = max(max_gap, max(progress.values()) - min(progress.values()))

            for dc_id in completed_dcs:
                if progress[dc_id] >= self.ssp_simulation_steps:
                    continue
                if self._can_start_next_step(progress, dc_id):
                    finish_time_by_dc[dc_id] = current_time + base_step_time_by_dc[dc_id]
                else:
                    stalled_since[dc_id] = current_time

            self._resume_unblocked_dcs(progress, finish_time_by_dc, stalled_since, current_time, base_step_time_by_dc)
            max_gap = max(max_gap, max(progress.values()) - min(progress.values()))

            if all(finish_time is None for finish_time in finish_time_by_dc.values()) and min(progress.values()) < self.ssp_simulation_steps:
                raise ValueError("SSP simulation deadlocked before reaching the requested number of steps.")

        average_gap = weighted_gap_sum / current_time if current_time > 0 else 0.0
        average_system_stall = total_system_stall_time / self.ssp_simulation_steps
        average_iter_time = current_time / self.ssp_simulation_steps
        return average_iter_time, average_gap, max_gap, average_system_stall

    def _resume_unblocked_dcs(
        self,
        progress: Dict[int, int],
        finish_time_by_dc: Dict[int, float | None],
        stalled_since: Dict[int, float | None],
        current_time: float,
        base_step_time_by_dc: Dict[int, float],
    ) -> None:
        for dc_id, stalled_time in stalled_since.items():
            if stalled_time is None:
                continue
            if progress[dc_id] >= self.ssp_simulation_steps:
                stalled_since[dc_id] = None
                continue
            if self._can_start_next_step(progress, dc_id):
                finish_time_by_dc[dc_id] = current_time + base_step_time_by_dc[dc_id]
                stalled_since[dc_id] = None

    def _can_start_next_step(self, progress: Dict[int, int], dc_id: int) -> bool:
        slowest_progress = min(progress.values())
        return progress[dc_id] <= slowest_progress + self.ssp_bound

    def _optimize_n_wave(
        self,
        model_name: str,
        topology_name: str,
        data_parallel: int,
        tensor_parallel: int,
        use_failure_reroute: bool,
        target_t_iter: float,
        tp_base: int,
        n_wave_base: int,
        severity_profile: FailureSeverityProfile | None = None,
    ) -> PaperEvaluationResult:
        budgets = self.get_budget_snapshot(topology_name, use_failure_reroute)
        candidates: List[PaperEvaluationResult] = []
        for n_wave in range(1, budgets.effective_max_waves + 1):
            candidates.append(
                self.evaluate(
                    model_name=model_name,
                    topology_name=topology_name,
                    data_parallel=data_parallel,
                    n_wave=n_wave,
                    use_failure_reroute=use_failure_reroute,
                    severity_profile=severity_profile,
                    tensor_parallel_override=tensor_parallel,
                )
            )
        return self._select_recovery_preferred_candidate(candidates, target_t_iter, tp_base, n_wave_base)

    def _optimize_tensor_parallel(
        self,
        model_name: str,
        topology_name: str,
        data_parallel: int,
        n_wave: int,
        use_failure_reroute: bool,
        target_t_iter: float,
        tp_base: int,
        n_wave_base: int,
        severity_profile: FailureSeverityProfile | None = None,
    ) -> PaperEvaluationResult:
        before_failure_result = self.evaluate(
            model_name=model_name,
            topology_name=topology_name,
            data_parallel=data_parallel,
            n_wave=n_wave_base,
            use_failure_reroute=False,
            tensor_parallel_override=tp_base,
        )
        candidates: List[PaperEvaluationResult] = []
        tp_values = self.derive_tp_scan_values(model_name, topology_name, data_parallel)
        for tensor_parallel in tp_values:
            candidates.append(
                self.evaluate(
                    model_name=model_name,
                    topology_name=topology_name,
                    data_parallel=data_parallel,
                    n_wave=n_wave,
                    use_failure_reroute=use_failure_reroute,
                    severity_profile=severity_profile,
                    tensor_parallel_override=tensor_parallel,
                    allow_gpu_compensation=True,
                )
            )
        return self._select_training_optimal_candidate(
            candidates,
            tp_base,
            n_wave_base,
            before_failure_result=before_failure_result,
        )

    def _optimize_joint_tp_n_wave(
        self,
        model_name: str,
        topology_name: str,
        data_parallel: int,
        use_failure_reroute: bool,
        target_t_iter: float,
        tp_base: int,
        n_wave_base: int,
        before_failure_result: PaperEvaluationResult,
        severity_profile: FailureSeverityProfile | None = None,
    ) -> PaperEvaluationResult:
        tp_values = self.derive_tp_scan_values(model_name, topology_name, data_parallel)
        candidates: List[PaperEvaluationResult] = []
        for tensor_parallel in tp_values:
            initial_result = self.evaluate(
                model_name=model_name,
                topology_name=topology_name,
                data_parallel=data_parallel,
                n_wave=n_wave_base,
                use_failure_reroute=use_failure_reroute,
                severity_profile=severity_profile,
                tensor_parallel_override=tensor_parallel,
                allow_gpu_compensation=True,
            )
            candidates.append(
                self._incremental_optical_compensation(
                    model_name=model_name,
                    topology_name=topology_name,
                    before_failure_result=before_failure_result,
                    initial_result=initial_result,
                    target_t_iter=target_t_iter,
                    severity_profile=severity_profile,
                    stop_when_recovered=False,
                )
            )
        return self._select_training_optimal_candidate(
            candidates,
            tp_base,
            n_wave_base,
            before_failure_result=before_failure_result,
        )
