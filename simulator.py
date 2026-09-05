from typing import List
from models import Drone, Graph
from cooperative_astar import CooperativeAstar

ANSI_COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "gray": "\033[90m",
    "grey": "\033[90m",
    "purple": "\033[35m",
    "violet": "\033[95m",
    "brown": "\033[33m",
    "orange": "\033[33m",
    "gold": "\033[93m",
    "maroon": "\033[31m",
    "darkred": "\033[31m",
    "crimson": "\033[91m",
    "rainbow": "\033[96m",
    
    "reset": "\033[0m"
}

def colorize(text: str, color_name: str | None) -> str:
    """Wraps text in ANSI color codes if the color exists in the dictionary."""
    if not color_name or color_name.lower() not in ANSI_COLORS:
        return text
    return f"{ANSI_COLORS[color_name.lower()]}{text}{ANSI_COLORS['reset']}"


class Simulator:
    """Manages the simulation and execution of drone routes across turns."""

    def __init__(self, drones: list[Drone], graph: Graph):
        """Initializes the simulator with drones and graph topology."""
        self.drones = drones
        self.graph = graph
        self.turns: List[str] = []

    def run_simulation(self) -> None:
        """Runs the simulation and prints formatted turn-by-turn drone movements."""
        if not self.drones:
            return
        total_turns = max(drone.path[-1]['turn'] for drone in self.drones)

        for current_turn in range(1, total_turns + 1):
            turn_moves = []
            
            for drone in self.drones:
                next_moves = [p for p in drone.path if p['turn'] >= current_turn]
                if not next_moves:
                    continue
                    
                next_move = next_moves[0]
                prev_move = drone.path[drone.path.index(next_move) - 1]

                if next_move['turn'] == current_turn:
                    zone_name = next_move['zone']
                    color_val = self.graph.zones[zone_name].color
                    colored_zone = colorize(zone_name, color_val)

                    turn_moves.append(f"{drone.id}-{colored_zone}")
                        
                elif next_move['turn'] > current_turn:
                    is_restricted = self.graph.zones[next_move['zone']].zone_type.value == 'restricted'
                    
                    if is_restricted and next_move['turn'] == current_turn + 1:
                        prev_name = prev_move['zone']
                        next_name = next_move['zone']
                        
                        prev_color = self.graph.zones[prev_name].color
                        next_color = self.graph.zones[next_name].color
                        
                        colored_prev = colorize(prev_name, prev_color)
                        colored_next = colorize(next_name, next_color)
                        turn_moves.append(f"{drone.id}-{colored_prev}-{colored_next}")

            if turn_moves: 
                self.turns.append(' '.join(turn_moves))
        
        for turn_output in self.turns:
            print(turn_output)
        print(total_turns)