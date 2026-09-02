from simulator import Simulator
import sys
from parser import Parser
from cooperative_astar import ReservationTable, CooperativeAstar



arguments = sys.argv
if (len(arguments) != 2 or arguments[0] != "main.py"):
    print("Usage: python3 main.py <maps/../map.txt>")
    sys.exit(1)


parser = Parser(arguments[1])
try:
    graph = parser.parse_validate()
except:
    pass

drones = [Drone(f"D{i}") for i in range(graph.nb_drones)]
cooperative_astar = CooperativeAstar(graph)
cooperative_astar.assign_paths(drones)
simulator = Simulator(drones, graph)
simulator.run_simulation()













