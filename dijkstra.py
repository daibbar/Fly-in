"""Dijkstra shortest path algorithm implementation."""
from models import Graph
import heapq


class Dijkstra:
    """Dijkstra algorithm for shortest paths."""

    def __init__(self, graph: Graph, start_name: str):
        """Initialize Dijkstra with graph and start node.

        Args:
            graph (Graph): The graph on which to compute shortest paths.
            start_name (str): The starting node's name.
        """
        self.graph = graph
        self.start_name = start_name

    def standard_algo(self) -> dict[str, float]:
        """Compute shortest distances from start using Dijkstra.

        Returns:
            dict[str, float]: A dictionary mapping each zone name to its
                shortest distance.
        """
        distance = {zone_name: float('inf') for zone_name in self.graph.zones}
        distance[self.start_name] = 0

        heap = [(0, self.start_name)]

        while heap:
            current_distance, zone_name = heapq.heappop(heap)

            if current_distance > distance[zone_name]:
                continue

            current_zone = self.graph.zones[zone_name]
            for neighbor_name in current_zone.neighbors:
                neighbor_zone = self.graph.zones[neighbor_name]

                if neighbor_zone.zone_type.value == "blocked":
                    continue

                cost = (
                    2 if neighbor_zone.zone_type.value == "restricted"
                    else 1
                )
                new_distance = current_distance + cost

                if new_distance < distance[neighbor_name]:
                    distance[neighbor_name] = new_distance
                    heapq.heappush(heap, (new_distance, neighbor_name))
        return distance
