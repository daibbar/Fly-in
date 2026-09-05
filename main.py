import sys
import traceback
from cooperative_astar import CooperativeAstar
from models import Drone
from parser import Parser
from simulator import Simulator
from exceptions import ParserError

def main() -> None:
    """Entry point: parses map, plans paths, and runs simulation."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)

    try:
        parser = Parser(sys.argv[1])
        graph = parser.parse_validate()

        drones = [Drone(f"D{i}") for i in range(1, graph.nb_drones + 1)]

        cooperative_astar = CooperativeAstar(graph)
        cooperative_astar.assign_paths(drones)

        simulator = Simulator(drones, graph)
        simulator.run_simulation()

    except ParserError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
