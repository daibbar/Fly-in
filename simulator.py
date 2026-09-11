"""Simulation execution and visualization."""

import webcolors
from typing import List
from models import Drone, Graph

CUSTOM_COLORS = {
    "default": "#00ffff"
}


def colorize(text: str, color_name: str | None) -> str:
    """Wrap text in rich markup using exact Hex codes for perfect rendering.

    Args:
        text (str): The text to colorize.
        color_name (str | None): The name of the color to apply.

    Returns:
        str: The text wrapped in rich markup.
    """
    if not color_name:
        return text

    default_color = "#00ffff"

    color_lower = color_name.lower()
    if color_lower in CUSTOM_COLORS:
        hex_val = CUSTOM_COLORS[color_lower]
        return f"[{hex_val}]{text}[/{hex_val}]"

    try:
        hex_val = webcolors.name_to_hex(color_lower)
        return f"[{hex_val}]{text}[/{hex_val}]"
    except ValueError:
        return f"[{default_color}]{text}[/{default_color}]"


class Simulator:
    """Manage the simulation and execution of drone routes across turns."""

    def __init__(self, drones: list[Drone], graph: Graph):
        """Initialize the simulator with drones and graph topology.

        Args:
            drones (list[Drone]): The list of drones in the simulation.
            graph (Graph): The graph representing the map.
        """
        self.drones = drones
        self.graph = graph
        self.turns: List[str] = []

    def run_simulation(self) -> None:
        """Run simulation and print turn-by-turn drone movements.

        Returns:
            None
        """
        if not self.drones:
            return
        total_turns = max(drone.path[-1]['turn'] for drone in self.drones)

        for current_turn in range(1, total_turns + 1):
            turn_moves = []

            for drone in self.drones:
                next_moves = [
                    p for p in drone.path if p['turn'] >= current_turn
                ]
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
                    is_restricted = (
                        self.graph.zones[next_move['zone']].zone_type.value
                        == 'restricted'
                    )

                    if is_restricted and next_move['turn'] == current_turn + 1:
                        prev_name = prev_move['zone']
                        next_name = next_move['zone']

                        prev_color = self.graph.zones[prev_name].color
                        next_color = self.graph.zones[next_name].color

                        colored_prev = colorize(prev_name, prev_color)
                        colored_next = colorize(next_name, next_color)
                        turn_moves.append(
                            f"{drone.id}-{colored_prev}-{colored_next}"
                        )

            if turn_moves:
                self.turns.append(' '.join(turn_moves))

        from rich.console import Console
        console = Console()
        for turn_output in self.turns:
            console.print(turn_output, soft_wrap=True)
        print(len(self.turns))
