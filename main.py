from cooperative_astar import CooperativeAstar
from models import Drone
import sys
import os
from parser import Parser
from simulator import Simulator
from exceptions import ParserError, MetaDataError

def main() -> None:
    """Entry point: parses map, plans paths, and runs simulation."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)

    try:
        map_file = sys.argv[1]
        parser = Parser(map_file)
        graph = parser.parse_validate()

        drones = [Drone(f"D{i}") for i in range(1, graph.nb_drones + 1)]

        cooperative_astar = CooperativeAstar(graph)
        cooperative_astar.assign_paths(drones)

        simulator = Simulator(drones, graph)
        simulator.run_simulation()
    except MetaDataError as e:
        print(f"[MetaDataError]: {e}")
        exit(1)
    except ParserError as e:
        print(f"[ParserError]: {e}")
        exit(1)
    except ValueError as e:
        print(f"[ValueError]: {e}")
        exit(1)
    except (Exception, KeyboardInterrupt) as e:
        print(f"[Unexpected Error has happend]: {e}")


if __name__ == '__main__':
    main()
