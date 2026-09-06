"""Cooperative A* pathfinding algorithm implementation."""
import itertools
from models import Zone, Graph, Drone  # noqa: F401
import heapq


class ReservationTable:
    """Spatiotemporal reservation table for zone and link capacities."""

    def __init__(self, graph: Graph):
        """Initialize empty reservations for the given graph."""
        self.graph = graph
        self.zone_reservations: dict[tuple[str, int], int] = dict()
        self.link_reservations: dict[tuple[str, str, int], int] = dict()

    def can_enter_zone(self, zone_name: str, turn: int) -> bool:
        """Check if a zone can accept a drone at the given turn."""
        zone_obj = self.graph.zones[zone_name]
        return (
            self.zone_reservations.get((zone_name, turn), 0)
            < zone_obj.max_drones
        )

    def can_use_link(
        self, current_zone: str, neighbor: str, turn: int
    ) -> bool:
        """Check if a link between zones is available at the given turn."""
        connection: tuple[str, str, int] = (
            (current_zone, neighbor, turn) if current_zone < neighbor
            else (neighbor, current_zone, turn)
        )
        return (
            self.link_reservations.get(connection, 0)
            < self.graph.zones[connection[0]].neighbors[connection[1]]
        )

    def reserve_zone(self, zone_name: str, turn: int) -> bool:
        """Reserve capacity in a zone for a specific turn."""
        if self.can_enter_zone(zone_name, turn) is False:
            return False
        if zone_name not in self.graph.zones:
            return False

        try:
            self.zone_reservations[(zone_name, turn)] += 1
        except KeyError:
            self.zone_reservations[(zone_name, turn)] = 1
        return True

    def reserve_link(self, current_zone: str, zone: str, turn: int) -> bool:
        """Reserve capacity on a link between zones for a specific turn."""
        link = (
            (current_zone, zone, turn) if current_zone < zone
            else (zone, current_zone, turn)
        )
        if self.can_use_link(current_zone, zone, turn) is False:
            return False

        try:
            self.link_reservations[link] += 1
        except KeyError:
            self.link_reservations[link] = 1
        return True


class CooperativeAstar:
    """Cooperative A* pathfinding algorithm for multi-drone routing."""

    def __init__(
        self,
        graph: Graph,
        reservation_table: ReservationTable,
        heuristic: dict[str, float]
    ):
        """Initialize the Cooperative A* pathfinder with the graph."""
        self.graph = graph
        self.reservation_table = reservation_table
        self.heuristic = heuristic

    def find_path(self, drone: Drone, heuristic: dict[str, float]) -> None:
        """Find and reserve a collision-free space-time path for a drone."""
        assert self.graph.start_hub is not None
        assert self.graph.end_hub is not None
        start_zone = self.graph.start_hub
        if self.heuristic[start_zone] == float('inf'):
            raise ValueError(
                f"No path found for drone {drone.id}: "
                "graph may be disconnected"
            )
        f_start = 0 + self.heuristic[start_zone]
        counter = itertools.count()

        zones = self.graph.zones
        spatio_timelines: list[tuple] = []
        heapq.heappush(
            spatio_timelines,
            (
                f_start,
                self.heuristic[start_zone],
                0,
                start_zone,
                next(counter),
                [{"zone": start_zone, "turn": 0}]
            )
        )
        visited = set()
        while spatio_timelines:
            f, h, current_turn, current_zone, _, path_history = heapq.heappop(
                spatio_timelines
            )
            if current_zone == self.graph.end_hub:
                break

            state = (current_zone, current_turn)
            if state in visited:
                continue
            visited.add(state)
            if self.reservation_table.can_enter_zone(
                current_zone, current_turn + 1
            ):
                heapq.heappush(
                    spatio_timelines,
                    (
                        f + 1,
                        h,
                        current_turn + 1,
                        current_zone,
                        next(counter),
                        path_history
                    )
                )

            for neighbor in zones[current_zone].neighbors:
                if zones[neighbor].zone_type.value == 'restricted':
                    if not (
                        self.reservation_table.can_use_link(
                            current_zone, neighbor, current_turn + 1
                        )
                        and self.reservation_table.can_use_link(
                            current_zone, neighbor, current_turn + 2
                        )
                        and self.reservation_table.can_enter_zone(
                            neighbor, current_turn + 2
                        )
                    ):
                        continue
                    else:
                        new_path_history = path_history + [
                            {"zone": neighbor, "turn": current_turn + 2}
                        ]
                        f_cost = (current_turn + 2) + self.heuristic[neighbor]
                        heapq.heappush(
                            spatio_timelines,
                            (
                                f_cost,
                                self.heuristic[neighbor],
                                current_turn + 2,
                                neighbor,
                                next(counter),
                                new_path_history
                            )
                        )
                        continue

                if not (
                    self.reservation_table.can_use_link(
                        current_zone, neighbor, current_turn + 1
                    )
                    and self.reservation_table.can_enter_zone(
                        neighbor, current_turn + 1
                    )
                ):
                    continue

                if (
                    zones[neighbor].zone_type.value == 'priority'
                    or zones[neighbor].zone_type.value == 'normal'
                    or zones[neighbor] == self.graph.end_hub
                ):
                    new_path_history = path_history + [
                        {"zone": neighbor, "turn": current_turn + 1}
                    ]
                    f_cost = (current_turn + 1) + self.heuristic[neighbor]
                    heapq.heappush(
                        spatio_timelines,
                        (
                            f_cost,
                            self.heuristic[neighbor],
                            current_turn + 1,
                            neighbor,
                            next(counter),
                            new_path_history
                        )
                    )
        else:
            raise ValueError(
                f"No path found for drone {drone.id}: "
                "graph may be disconnected"
            )
        drone.path = path_history

        for i in range(1, len(drone.path)):
            prev_move = drone.path[i - 1]
            curr_move = drone.path[i]

            prev_zone = prev_move["zone"]
            curr_zone = curr_move["zone"]

            is_restricted = zones[curr_zone].zone_type.value == 'restricted'
            move_cost = 2 if is_restricted else 1

            wait_end_turn = curr_move["turn"] - move_cost
            for t in range(prev_move["turn"] + 1, wait_end_turn + 1):
                self.reservation_table.reserve_zone(prev_zone, t)

            if is_restricted:
                self.reservation_table.reserve_link(
                    prev_zone, curr_zone, curr_move["turn"] - 1
                )
                self.reservation_table.reserve_link(
                    prev_zone, curr_zone, curr_move["turn"]
                )
            else:
                self.reservation_table.reserve_link(
                    prev_zone, curr_zone, curr_move["turn"]
                )

            self.reservation_table.reserve_zone(curr_zone, curr_move["turn"])

    def assign_paths(self, drones: list[Drone]) -> list[Drone]:
        """Assign collision-free paths to all drones sequentially."""
        for drone in drones:
            self.find_path(drone, self.heuristic)
        return drones
