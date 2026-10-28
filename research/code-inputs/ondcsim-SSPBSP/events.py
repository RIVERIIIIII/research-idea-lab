from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Event:
    """Base class for all events."""
    event_id: int
    event_type: str
    arrival_time: float

@dataclass
class DistributedTrainingEvent(Event):
    """Event for distributed training across multiple datacenters."""
    dc_list: List[int]
    gpus_per_dc: int
    bandwidth_gbps: float

@dataclass
class FailureEvent(Event):
    """Event for node or link failure in the network."""
    failure_type: str  # 'node' or 'link'
    failed_node: Optional[int] = None
    failed_link: Optional[List[int]] = None  # [src, dst] if link failure
    duration: float = 0.0  # How long the failure lasts
