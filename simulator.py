from models import Drone, Graph, Zone
from CooperativeAstar import CooperativeAstar





class Simulator:
    def __init__(self, drones: List[Drone], graph: Graph):
        self.drones = drones
        self.graph = graph
        self.turns: List[str] = []

    def run_simulation():
        total_turns = max(drone.path[-1]["turn"] for drone in self.drones)

        for current_turn in range(1, total_turns + 1):
            self.turns[current_turn] = ""

            for drone in self.drones:
                for position in drone.path:
                    






