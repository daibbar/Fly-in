import re
import exceptions as exc
import webcolors
import itertools


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
        "start_hub_pattern": r"^\s*(start_hub:)\s*([^\s-)\s*(\d+)\s*(\d+)\s*(\[[A-Za-z=\s]\]\s*)?$",
        "hub_pattern": r"^\s*(hub):\s*\w\s*\d+\s*\d+\s*(\[[A-Za-z=\s]\])?$",
        "end_hub_pattern": r"^\s*end_hub:\s*goal\s*\d+\s*\d+\s*(\[[A-Za-z=\s\])?$",
        "connection_pattern": r"^\s*connection:\s*\w-\w\s*(\[[A-Za-z=\s]\])?$",
        "zone_optional_pattern": r"(?=\s*zone=([A-Za-z]+)\s*)(?=\s*color=([A-Za-z]+)\s*)(?=\s*max_drones=([1-9]+)\s*)$"
    }

    def __init__(self, map_path: str):
        self.map_path = map_path

    def parse_lines(self):
        ## here in this step we take the valid lines from the file without checking the optional pattern
        start_hub_found = False
        end_hub_found = False
        with open(self.map_path, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
            
            if re.match(Parser.patterns["nb_drones"], f.readline()):
                config_init = {"nb_drones": line}
            else:
                raise exc.NbDronesError("The first line must define " \
                "the number of drones using nb_drones: <positive_integer>.")

            for line in f:
                if re.match(Parser.patterns["start_hub"] ,line):
                    if "start_hub" in config_init:
                        raise exc.StartHubError("only one start hub is allowed!")
                    ## if this start hub valid add it if not continue
                    config_init["start_hub"] = line

                elif re.match(Parser.patterns["end_hub_pattern"], line):



                

