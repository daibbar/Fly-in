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
class Whcastar:
    def __init__(self, graph: Graph, drones: list[Drone]):
        self.graph = graph
        self.drones = drones

    class ReservationTable:
        def __init__(self, graph: Graph):
            ## this reservation table is like a parametric function
            ## (zone, t) -> nb_drones_reserving where each drone of the nones are in (x,y) in turn t
            self.graph = graph
            self.zone_reservations : dict[tuple[str, int], int] = dict()
            self.link_reservations : dict[tuple[str, str, int], int] = dict()


        def can_enter_zone(self, candidate: Zone, turn: int):
            if candidate.name == self.graph.start_hub \
                or candidate.name == self.graph.end_hub:
                return True
            return self.zone_reservations.get((candidate.name, turn), 0) < \
                candidate.max_drones

        def can_use_link(self, current_zone: str, candidate: str, turn: int):
            connection: tuple[str, str, int] = (current_zone, candidate, turn) if current_zone < candidate \
                else (candidate, current_zone, turn)
            return self.link_reservations.get(connection, 0) < \
                self.graph.zones[connection[0]].neighbors[connection[1]]


        def reserve_zone(self, zone_name: str, turn: int):
            if (self.can_enter_zone(zone_name, turn) is False):
                return False
            if zone_name not in self.graph.zones:
                return False

            if zone_name == self.graph.start_hub or \
                zone_name == self.graph.end_hub:
                return True

            try:
                self.zone_reservations[(zone_name, turn)] += 1
            except KeyError:
                self.zone_reservations[(zone_name, turn)] = 1
            return True

        def reserve_link(self, current_zone: str, dest_zone: str, turn: int):
            link = (current_zone, dest_zone, turn) if current_zone < dest_zone else \
                    (dest_zone, current_zone, turn)
            if (self.can_use_link(current_zone, dest_zone, turn) is False):
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

    def as_node_cost(heuristic: dict[str, int], main_algo: dict[str, int]):
        def fn(zone_name: str):
            return heuristic[zone_name] + main_algo[zone_name]
        return fn

        

    def _find_path(self, drone: Drone, reservation_table: ReservationTable):
        heuristic: dict[str, int] = self.dijkstra(self.graph, self.graph.end_hub)
        start_dijkstra : dict[str, int] = self.dijkstra(self.graph, self.graph.start_hub)
        fn = self.as_node_cost(heuristic, start_dijkstra)

        timeline_universes = [(fn(current_zone), heuristic(current_zone), 0, self.graph.start_hub, [])]
        _, _, current_turn, current_zone, path_history = heapq.heappop(timeline_universes)

        candidates = []
        heapq.heappush(candidates, fn(current_zone), heuristic(current_zone), current_turn + 1, current_zone,
                        path_history.append(current_zone))
        for neighbor in self.graph.zones[current_zone].neighbors:
            heapq.heappush(candidates, (fn(neighbor), heuristic(neighbor), current_turn + 1, neighbor
                        path_history.append(current_zone)))
            ## we need to give priority to priority zone agianst normal zone

        while True:
            _, _, current_turn, candidate, path_history = heapq.heappop(timeline_universes)
            current_zone = path_history[-1]
            if current_zone == self.graph.end_hub:
                break
            # check if the zone is restricted because the approach would be different       
            if self.graph.zones[candidate].zone_type == 'restricted':
                #the zone is not available in the next turns chose another candidate
                if not (reservation_table.can_use_link(current_zone, candidate, current_turn + 1) \
                        and reservation_table.can_enter_zone(candidate, current_turn + 2)):
                        continue
                #the zone is available reserve it, chose it as next zone and update the current turn
                else:
                    path_history.append({"type": "connection", "zone": candidate, "turn": current_turn + 1})
                    path_history.append({"zone": candidate, "turn", current_turn + 2})
                    heapq.heappush(timeline_universes, (fn(candidate), heuristic(candidate), current_turn + 1))
                    continue
            
            elif not (reservation_table.can_use_link(current_zone, candidate, drone.current_turn + 1) and
                    reservation_table.can_enter_zone(candidate, drone.current_turn + 1)):
                continue

            if self.graph.zones[candidate].zone_type == 'priority' or \
                self.graph.zones[candidate].zone_type == 'normal':
                drone.path.append({"current_zone": current_zone, "dest_zone": dest_zone, 'turn': drone.current_turn + 1})
                drone.current_turn += 1
                current_zone = candidate

            #just wait nothing to do
            else:
                drone.path.append({"current_zone": current_zone, "dest_zone": current_zone, 'turn': drone.current_turn + 1})
                drone.current_turn += 1

        for connection in drone.path:
            reservation_table.reserve_zone(connection["dest_zone"], connection["turn"])
            if drone.path["dest_zone"] == drone.path["current_zone"]:
                continue
            reservation_table.reserve_link(connection["current_zone"], connection["dest_zone"], connection["turn"])
            if connection["dest_zone"].zone_type == 'restricted':
                reservation_table.reserve_link(connection["current_zone"], connection["dest_zone"], connection["turn"] - 1)

        return drones
