"""Cooperative A* pathfinding algorithm implementation."""
import itertools
from models import Zone, Graph, Drone  # noqa: F401
import heapq
from reservation_table import ReservationTable


class CooperativeAstar:
    """Cooperative A* pathfinding algorithm for multi-drone routing."""

    def __init__(
        self,
        graph: Graph,
        reservation_table: ReservationTable,
        heuristic: dict[str, float]
    ):
        """Initialize the Cooperative A* pathfinder with the graph.

        Args:
            graph (Graph): The graph representing the map.
            reservation_table (ReservationTable): The table for managing
                reservations.
            heuristic (dict[str, float]): The heuristic values for pathfinding.
        """
        self.graph = graph
        self.reservation_table = reservation_table
        self.heuristic = heuristic

    def find_path(self, drone: Drone) -> None:
        """Find and reserve a collision-free space-time path for a drone.

        Args:
            drone (Drone): The drone for which to find a path.
            heuristic (dict[str, float]): Heuristic values for zones.

        Returns:
            None
        """
        h = self.heuristic[self.graph.start_hub]
        if h == float('inf'):
            raise ValueError(
                f"No path found for drone {drone.id}: "
                "graph may be disconnected"
            )
        counter = itertools.count()
        spatio_timelines: list[tuple] = []
        heapq.heappush(
            spatio_timelines,
            (
                h,
                h,
                0,
                self.graph.start_hub,
                next(counter),
                [{"zone": self.graph.start_hub, "turn": 0}]
            )
        )

        zones = self.graph.zones
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
                    can_enter_link = self.reservation_table.can_use_link(
                        current_zone, neighbor, current_turn + 1
                    )
                    can_exit_link = self.reservation_table.can_use_link(
                        current_zone, neighbor, current_turn + 2
                    )
                    can_enter_dest = self.reservation_table.can_enter_zone(
                        neighbor, current_turn + 2
                    )
                    if can_enter_link and can_exit_link and can_enter_dest:
                        heapq.heappush(spatio_timelines, (
                            current_turn + 2 + self.heuristic[neighbor],
                            self.heuristic[neighbor],
                            current_turn + 2,
                            neighbor,
                            next(counter),
                            path_history + [
                                {"zone": neighbor, "turn": current_turn + 2}
                            ]
                        ))
                    continue

                can_use_link = self.reservation_table.can_use_link(
                    current_zone, neighbor, current_turn + 1
                )
                can_enter_zone = self.reservation_table.can_enter_zone(
                    neighbor, current_turn + 1
                )
                is_direct_zone = (
                    zones[neighbor].zone_type.value in ('priority', 'normal')
                )
                if can_use_link and can_enter_zone and is_direct_zone:
                    heapq.heappush(spatio_timelines, (
                        current_turn + 1 + self.heuristic[neighbor],
                        self.heuristic[neighbor],
                        current_turn + 1,
                        neighbor,
                        next(counter),
                        path_history + [
                            {"zone": neighbor, "turn": current_turn + 1}
                        ]
                    ))
        else:
            raise ValueError(
                f"No path found for drone {drone.id}: "
                "graph may be disconnected"
            )
        drone.path = path_history

        for i in range(1, len(drone.path)):
            prev_move = drone.path[i - 1]
            curr_move = drone.path[i]

            is_restricted = (
                zones[curr_move['zone']].zone_type.value == 'restricted'
            )
            move_cost = 2 if is_restricted else 1

            wait_end_turn = curr_move["turn"] - move_cost
            for t in range(prev_move["turn"] + 1, wait_end_turn + 1):
                self.reservation_table.reserve_zone(prev_move['zone'], t)

            if is_restricted:
                self.reservation_table.reserve_link(
                    prev_move['zone'], curr_move['zone'], curr_move["turn"] - 1
                )
            self.reservation_table.reserve_link(
                prev_move['zone'], curr_move['zone'], curr_move["turn"]
            )
            self.reservation_table.reserve_zone(
                curr_move['zone'], curr_move["turn"]
            )

    def assign_paths(self, drones: list[Drone]) -> list[Drone]:
        """Assign collision-free paths to all drones sequentially.

        Args:
            drones (list[Drone]): The list of drones to assign paths to.

        Returns:
            list[Drone]: The list of drones with assigned paths.
        """
        for drone in drones:
            self.find_path(drone)
        return drones
