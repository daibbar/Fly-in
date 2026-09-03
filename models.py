from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field

class ZoneType(Enum):
    """Supported zone categories with their turn traversal costs."""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def cost(self) -> int:
        """Movement cost in turns to enter this zone."""
        if self == ZoneType.RESTRICTED:
            return 2
        return 1

@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: int = 1
    color: Optional[str] = None
    # Use default_factory for mutable objects in dataclasses
    neighbors: Dict[str, int] = field(default_factory=dict) ## ??

    def add_connection(self, neighbor_name: str, max_link_capacity: int = 1) -> None:
        self.neighbors[neighbor_name] = max_link_capacity


@dataclass
class Graph:
    nb_drones: int
    zones: Dict[str, Zone] = field(default_factory=dict)
    start_hub: Optional[str] = None
    end_hub: Optional[str] = None

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone

    def get_valid_neighbors(self, zone_name: str) -> List[str]:
        zone = self.zones[zone_name]
        # Return neighbor names where the destination is not blocked
        return [
            neigh for neigh in zone.neighbors
            if self.zones[neigh].zone_type != ZoneType.BLOCKED
        ]

@dataclass
class Drone:
    id: str
    path: List[Dict[str, any]] = field(default_factory=list)
