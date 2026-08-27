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


        def can_enter_zone(self, dest_zone: Zone, turn: int):
            if dest_zone.name == self.graph.start_hub \
                or dest_zone.name == self.graph.end_hub:
                return True
            return self.zone_reservations.get((dest_zone.name, turn), 0) < \
                dest_zone.max_drones

        def can_use_link(self, current_zone: str, dest_zone: str, turn: int):
            connection: tuple[str, str, int] = (current_zone, dest_zone, turn) if current_zone < dest_zone \
                else (dest_zone, current_zone, turn)
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
        min_heap = [(fn(self.graph.start_hub), self.graph.start_hub)]
        while min_heap:
            candidates = []
            current_fn, zone_name = heapq.heappop(min_heap)
            for neighbor in self.graph.zones[zone_name].neighbors:
                heapq.heappush(candidates, (fn(neighbor), neighbor))

            while True:  
                cost, dest_zone = heapq.heappop(candidates)        
                if self.graph.zones[dest_zone].zone_type == 'restricted':
                    if not (reservation_table.can_use_link(zone_name, dest_zone, drone.current_turn + 1) \
                            and reservation_table.can_enter_zone(dest_zone, drone.current_turn + 2)):
                            continue
                    else:
                        drone.path += [('link', f'{zone_name}-{dest_zone}', drone.current_turn + 1), ('zone', dest_zone, drone.current_turn + 2)]
                        continue
                if not (reservation_table.can_use_link(zone_name, dest_zone, drone.current_turn + 1) and
                        reservation_table.can_enter_zone(dest_zone, drone.current_turn + 1)):
                    continue

                if self.graph.zones[dest_zone].zone_type == 'priority':
                    drone.path += [('zone', dest_zone, drone.current_turn + 1)]
                    heapq.heappush(min_heap, (fn(dest_zone), dest_zone))
                    #update curent turn for drone
                    break

                #the zone is normal so just reserve a place for the next turn
                elif self.graph.zones[dest_zone].zone_type == 'normal':
                    drone.path += [('zone', dest_zone, drone.current_turn + 1)]
                    break
                else:
                    # he should wait here
                    pass

        


            
        

    def fly_in(self, drones: list[Drone]):
        resrvation_table = self.ReservationTable(self.graph)

        for drone in drones:
            drone.path = self.find_path(drone, resrvation_table)

        return drones




        