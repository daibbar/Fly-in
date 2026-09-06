from cooperative_astar import CooperativeAstar, ReservationTable
from dijkstra import Dijkstra
from models import Drone
import sys
from parser import Parser
from simulator import Simulator
from exceptions import ParserError, MetaDataError


def main() -> None:
    """Entry point: parses map, plans paths, and runs simulation."""
    if len(sys.argv) != 2:
        print("Invalid number of arguments!")
        sys.exit(1)

    try:
        map_file = sys.argv[1]
        parser = Parser(map_file)
        graph = parser.parse_validate()

        drones = [Drone(f"D{i}") for i in range(1, graph.nb_drones + 1)]

        reservation_table = ReservationTable(graph)
        dijkstra = Dijkstra(graph, graph.end_hub)  # type: ignore
        heuristic = dijkstra.standard_algo()

        cooperative_astar = CooperativeAstar(
            graph, reservation_table, heuristic
        )
        cooperative_astar.assign_paths(drones)

        simulator = Simulator(drones, graph)
        simulator.run_simulation()
    except MetaDataError as e:
        print(f"[MetaDataError]: {e}")
        sys.exit(1)
    except ParserError as e:
        print(f"[ParserError]: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"[ValueError]: {e}")
        sys.exit(1)
    except (Exception, KeyboardInterrupt) as e:
        print(f"[Unexpected Error has happend]: {e}")


if __name__ == '__main__':
    main()
