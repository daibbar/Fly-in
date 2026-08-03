import re
import exceptions as exc


# Easy Level 1: Simple linear path
# nb_drones: 2

# start_hub: start 0 0 [color=green]
# hub: waypoint1 1 0 [color=blue]
# hub: waypoint2 2 0 [color=blue]
# end_hub: goal 3 0 [color=red]

# connection: start-waypoint1
# connection: waypoint1-waypoint2
# connection: waypoint2-goal

    

# [] just like this after the numbers is it acceptable or no
class Parser:
    patterns = {
        "nb_drones_pattern": r"(^\s*nb_drones:)(\s*([-+])?\d+\s*)$",
        "start_hub": r"^\s*(start_hub:)\s*([^\s-)\s*(\d+)\s*(\d+)\s*(\[something\]\s*)?$"

    }
    def __init__(self, map_path: str):
        self.map_path = map_path

    @staticmethod
    def valid_opt_combo(optional_combo: str):
        
        pass

    def parse_lines(self):
        lines = []
        start_hub = False
        end_hub = False
        nb_drones = False
        with open(self.map_path, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
            
            if re.match(Parser.patterns["nb_drones"], f.readline()):
                lines += line
            else:
                raise exc.NbDronesError("The first line must define " \
                "the number of drones using nb_drones: <positive_integer>.")

            for line in f:

                

