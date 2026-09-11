"""Data models for the simulation graph and entities."""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


class ZoneType(Enum):
    """Supported zone categories with their turn traversal costs."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def cost(self) -> int:
        """Movement cost in turns to enter this zone.

        Returns:
            int: The movement cost.
        """
        if self == ZoneType.RESTRICTED:
            return 2
        return 1


@dataclass
class Zone:
    """Represent a hub or zone in the flight network.

    Attributes:
        name: Name identifier of the zone.
        x: X-coordinate of the zone.
        y: Y-coordinate of the zone.
        zone_type: Zone category defining traversal rules and cost.
        max_drones: Maximum number of drones allowed simultaneously.
        color: Optional display color.
        neighbors: Dictionary mapping neighbor names to link capacity.
        is_end_start: Flag indicating if the zone is a start or end hub.
    """

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: float = 1
    color: Optional[str] = None
    neighbors: Dict[str, int] = field(default_factory=dict)
    is_end_start: bool = False

    def add_connection(
        self, neighbor_name: str, max_link_capacity: int = 1
    ) -> None:
        """Add a connection to a neighboring zone.

        Args:
            neighbor_name (str): Name of the neighboring zone.
            max_link_capacity (int): Maximum capacity of the link.

        Returns:
            None
        """
        self.neighbors[neighbor_name] = max_link_capacity


class Graph:
    """Represent the flight network of zones and drone configurations.

    Attributes:
        nb_drones: Total number of drones to route.
        zones: Mapping of zone names to Zone instances.
        start_hub: Name of the departure hub.
        end_hub: Name of the destination hub.
    """

    def __init__(
        self,
        nb_drones: int,
        start_hub: str,
        end_hub: str,
        zones: Dict[str, Zone]
    ):
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.zones = zones

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone (Zone): The Zone instance to add.

        Returns:
            None
        """
        self.zones[zone.name] = zone


@dataclass
class Drone:
    """Represent a drone and its planned flight path.

    Attributes:
        id: Unique identifier for the drone.
        path: List of movements or state history.
    """

    id: str
    path: List[Dict[str, Any]] = field(default_factory=list)
