from typing import List
from models import Drone, Graph
from cooperative_astar import CooperativeAstar

class Simulator:
    def __init__(self, drones: list[Drone], graph: Graph):
        self.drones = drones
        self.graph = graph
        self.turns: List[str] = []

    def run_simulation(self):
        if not self.drones:
            return
        total_turns = max(drone.path[-1]['turn'] for drone in self.drones)

        for current_turn in range(1, total_turns + 1):
            turn_moves = []
            
            for drone in self.drones:
                # 1. Find the drone's next upcoming move (or current arrival)
                next_moves = [p for p in drone.path if p['turn'] >= current_turn]
                if not next_moves:
                    continue  # Drone is already done
                    
                next_move = next_moves[0]
                prev_move = drone.path[drone.path.index(next_move) - 1]

                # 2. Case A: The drone arrives at a destination EXACTLY on this turn
                if next_move['turn'] == current_turn:
                    # Print the destination zone[cite: 1]
                    turn_moves.append(f"{drone.id}-{next_move['zone']}")
                        
                # 3. Case B: The drone is in a time gap between moves
                elif next_move['turn'] > current_turn:
                    # Transit only happens the EXACT turn before arriving at a restricted zone
                    is_restricted = self.graph.zones[next_move['zone']].zone_type.value == 'restricted'
                    
                    if is_restricted and next_move['turn'] == current_turn + 1:
                        # Print the connection name during transit[cite: 1]
                        turn_moves.append(f"{drone.id}-{prev_move['zone']}-{next_move['zone']}")
                    
                    # If it's not a restricted transit, the drone is waiting. Do nothing![cite: 1]

            # UN-INDENTED: Only append once per turn, and only if someone actually moved
            if turn_moves: 
                self.turns.append(' '.join(turn_moves))
        
        # Print the final formatted simulation output
        for turn_output in self.turns:
            print(turn_output)
        print(total_turns)