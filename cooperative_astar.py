import heapq
from models import Zone, Graph, Drone

# graph = {
#     'A': {'B': 4, 'C': 5, 'F': 8},
#     'B': {'A': 4, 'C': 11, 'D': 9, 'E': 7},
#     'C': {'A': 5, 'B': 11, 'E': 3, 'F': 6},
#     'D': {'B': 9, 'E': 2, 'F': 10},
#     'E': {'B': 7, 'C': 3, 'D': 2, 'F': 4},
#     'F': {'A': 8, 'C': 6, 'D': 10, 'E': 4}
# }

# alors le but est de trouve le minimum cout de A vers tous les noeuds du graph
# alors on doit commnecer par une dict des distance de A vers tous les autres points
class CooperativeAstar:
    def __init__(self, graph: Graph):
        self.graph = graph

    class ReservationTable:
        def __init__(self, graph: Graph):
            self.graph = graph
            self.zone_reservations : dict[tuple[str, int], int] = dict()
            self.link_reservations : dict[tuple[str, str, int], int] = dict()


        def can_enter_zone(self, neighbor: Zone, turn: int):
            if neighbor.name == self.graph.current_zone \
                or neighbor.name == self.graph.end_hub:
                return True
            return self.zone_reservations.get((neighbor.name, turn), 0) < \
                neighbor.max_drones

        def can_use_link(self, current_zone: str, neighbor: str, turn: int):
            connection: tuple[str, str, int] = (current_zone, neighbor, turn) if current_zone < neighbor \
                else (neighbor, current_zone, turn)
            return self.link_reservations.get(connection, 0) < \
                self.graph.zones[connection[0]].neighbors[connection[1]]


        def reserve_zone(self, zone_name: str, turn: int):
            if (self.can_enter_zone(zone_name, turn) is False):
                return False
            if zone_name not in self.graph.zones:
                return False

            if zone_name == self.graph.current_zone or \
                zone_name == self.graph.end_hub:
                return True

            try:
                self.zone_reservations[(zone_name, turn)] += 1
            except KeyError:
                self.zone_reservations[(zone_name, turn)] = 1
            return True

        def reserve_link(self, current_zone: str, zone: str, turn: int):
            link = (current_zone, zone, turn) if current_zone < zone else \
                    (zone, current_zone, turn)
            if (self.can_use_link(current_zone, zone, turn) is False):
                return False

            try:
                self.link_reservations[link] += 1
            except KeyError:
                self.link_reservations[link] = 1
            return True

    @staticmethod
    def dijkstra(graph: Graph, start_name: str):
        # 1. Initialize distances
        distance = {zone_name: float('inf') for zone_name in graph.zones}
        distance[start_name] = 0
        
        # 2. Setup the priority queue
        heap = [(0, start_name)]
        
        while heap:
            current_distance, zone_name = heapq.heappop(heap)

            if current_distance > distance[zone_name]:
                continue
                
            current_zone = graph.zones[zone_name]
            # 3. Look at neighbors
            for neighbor_name in current_zone.neighbors:
                neighbor_zone = graph.zones[neighbor_name]
                
                # Immediately reject blocked zones
                if neighbor_zone.zone_type == "blocked":
                    continue
                    
                # Cost depends on the DESTINATION zone
                cost = 2 if neighbor_zone.zone_type == "restricted" else 1
                new_distance = current_distance + cost
                
                # Update and push if we found a shorter path
                if new_distance < distance[neighbor_name]:
                    distance[neighbor_name] = new_distance
                    heapq.heappush(heap, (new_distance, neighbor_name))
                    
        return distance

    @staticmethod
    def astar_node_cost(heuristic: dict[str, int], main_algo: dict[str, int]):
        def fn(zone_name: str):
            return heuristic[zone_name] + main_algo[zone_name]
        return fn

        

    def _find_path(self, drone: Drone, reservation_table: ReservationTable):
        heuristic: dict[str, int] = self.dijkstra(self.graph, self.graph.end_hub)
        start_dijkstra : dict[str, int] = self.dijkstra(self.graph, self.graph.start_hub)
        fn = self.astar_node_cost(heuristic, start_dijkstra)


        zones = self.graph.zones
        spatio_timelines = []
        start_zone = self.graph.start_hub
        heapq.heappush(spatio_timelines, (fn(start_zone), heuristic[start_zone], 0, start_zone, 
                    [{"zone": start_zone, "turn": 0}]))
        # now we will try to discover all the available spatio-timelines and push the available ones to the heap
        while True:
            f, h, current_turn, current_zone, path_history = heapq.heappop(spatio_timelines)
            if current_zone == self.graph.end_hub:
                break
            if reservation_table.can_enter_zone(current_zone, current_turn + 1):
                heapq.heappush(spatio_timelines, (f + 1, h, current_turn + 1, current_zone, path_history))

            for neighbor in zones[current_zone].neighbors:
                # check if the goal zone is restricted, if yes the taken actions will be different
                if zones[neighbor].zone_type == 'restricted':
                    if not (reservation_table.can_use_link(current_zone, neighbor, current_turn + 1) \
                        and reservation_table.can_use_link(current_zone, neighbor, current_turn + 2) \
                        and reservation_table.can_enter_zone(neighbor, current_turn + 2)):
                            continue
                    else:
                        new_path_history = path_history + [{"zone": neighbor, "turn": current_turn + 2}]    
                        heapq.heappush(spatio_timelines, (fn(neighbor), heuristic[neighbor], 
                                        current_turn + 2, neighbor, new_path_history))
                        continue
                # if we can't use the link or can't use the zone in the next turn conitnue
                if not (reservation_table.can_use_link(current_zone, neighbor, current_turn + 1) \
                    and reservation_table.can_enter_zone(neighbor, current_turn + 1)):
                    continue
                
                # if the zone is priority or normal or an end_hub push it to the new_path_history
                if zones[neighbor].zone_type == 'priority' or zones[neighbor].zone_type == 'normal' \
                    or zones[neighbor] == self.graph.end_hub:
                    new_path_history = path_history + [{"zone": neighbor, "turn": current_turn  + 1}]
                    heapq.heappush(spatio_timelines, (fn(neighbor), heuristic[neighbor], 
                                    current_turn + 1, neighbor, new_path_history))
        drone.path = path_history

        for i, position in enumerate(drone.path):
            if position["zone"] == self.graph.start_hub:
                continue
            previous_zone = drone.path[i - 1]["zone"]
            if zones[position["zone"]].zone_type == 'restricted':
                reservation_table.reserve_link(previous_zone, position["zone"], position["turn"] - 1)
            reservation_table.reserve_zone(position["zone"], position["turn"])
            reservation_table.reserve_link(previous_zone, position["zone"], position["turn"])

    def assign_paths(drones: List[Drone]):
        reservation_table = self.ReservationTable(self.graph)
        for drone in drones:
            self._find_path(drone, reservation_table)
        return drones
            