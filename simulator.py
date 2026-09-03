from models import Drone, Graph, Zone
from CooperativeAstar import CooperativeAstar





class Simulator:
    def __init__(self, drones: List[Drone], graph: Graph):
        self.drones = drones
        self.graph = graph
        self.turns: List[str] = []

    def run_simulation(self):
        total_turns = max(drone.path[-1]['turn'] for drone in self.drones)

        for current_turn in range(1, total_turns + 1):
            turn_moves = []

            current_pos = next((pos for pos in drone.path if pos['turn'] == current_turn), None)
            next_pos = next((pos for pos in drone.path if pos['turn'] == current_turn + 1), None)

            if next_pos and self.graph.zones[next_pos['zone']].zone_type == 'restricted':
                previous_zone = drone.path[drone.path.index(next_pos) - 1]['zone']
                turn_moves.append(f'{drone.id}-{previous_zone}-{next_pos['zone']}')
            
            elif current_pos:
                turn_moves.append(f'{drone.id}-{current_pos['zone']}')
            
            self.turns.append(' '.join(turn_moves))
        
        for turn_output in self.turns:
            print(turn_output)







