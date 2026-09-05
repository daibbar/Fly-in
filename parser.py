import re
import exceptions as exc
import itertools
from typing import Any, Dict, List, Optional, Set, Tuple
from models import Graph, Zone, ZoneType


# [] just like this after the numbers is it acceptable or no
class Parser:
    """Parses and validates drone simulation map files."""

    patterns = {
        "nb_drones_pattern": r"^\s*nb_drones:\s*(?P<nb_drones>[-+]?\d+)\s*$",
        "start_hub_pattern": r"^\s*start_hub:\s*(?P<sh_name>[^\s-]+)\s+(?P<sh_x>[-+]?\d+)\s+(?P<sh_y>[-+]?\d+)(\s*\[(?P<meta>[^\]]*)\])?\s*$",
        "hub_pattern": r"^\s*hub:\s*(?P<h_name>[^\s-]+)\s+(?P<h_x>[-+]?\d+)\s+(?P<h_y>[-+]?\d+)(\s*\[(?P<meta>[^\]]*)\])?\s*$",
        "end_hub_pattern": r"^\s*end_hub:\s*(?P<eh_name>[^\s-]+)\s+(?P<eh_x>[-+]?\d+)\s+(?P<eh_y>[-+]?\d+)(\s*\[(?P<meta>[^\]]*)\])?\s*$",
        "connection_pattern": r"^\s*connection:\s*(?P<from_hub>[^\s-]+)-(?P<to_hub>[^\s-]+)(\s*\[(?P<meta>[^\]]*)\])?\s*$",
    }

    def __init__(self, map_path: str):
        """Initializes the parser with the map file path."""
        self.map_path = map_path

    def parse_meta_data(self, raw_meta: Optional[str], line_num: int) -> Dict[str, str]:
        """Parses key-value tokens inside bracketed metadata."""
        meta_dict: Dict[str, str] = {}
        if not raw_meta:
            return meta_dict

        tokens = raw_meta.strip().split()
        for token in tokens:
            if "=" not in token:
                raise exc.MetaDataError(
                    f"Line {line_num}: Malformed metadata tag '{token}'"
                )
            key, val = token.split("=", 1)
            meta_dict[key] = val
        return meta_dict

    
    def _init_parse_lines(self) -> dict:
        """Parse and categorize map lines matching structural patterns."""
        config_init = {
            "nb_drones": None,
            "start_hub": None,
            "end_hub": None,
            "hubs": [],
            "connections": []
        }

        with open(self.map_path, 'r', encoding='utf-8') as f:
            line_num = 0  # Initialize our line tracker

            # 1. Mandatory first non-empty/non-comment line must define nb_drones
            for line in f:
                line_num += 1
                stripped = line.split('#', 1)[0].strip()
                if not stripped:
                    continue
                
                if (match := re.match(Parser.patterns["nb_drones_pattern"], stripped)):
                    # Store as a tuple: (value, line_number)
                    config_init["nb_drones"] = (match.group("nb_drones"), line_num)
                else:
                    raise exc.NbDronesError(
                        f"Line {line_num}: The first line must define the number of drones "
                        "using nb_drones: <positive_integer>."
                    )
                break

            # 2. Parse the remainder of the file
            for line in f:
                line_num += 1
                stripped = line.split('#', 1)[0].strip()
                if not stripped:
                    continue

                if (match := re.match(Parser.patterns["start_hub_pattern"], stripped)):
                    if config_init["start_hub"] is not None:
                        raise exc.StartHubError(f"Line {line_num}: Only one start hub is allowed!")
                    config_init["start_hub"] = {
                        "name": match.group("sh_name"),
                        "x": match.group("sh_x"),
                        "y": match.group("sh_y"),
                        "meta": match.group("meta"),
                        "line": line_num  # <-- Save line number for validation step
                    }

                elif (match := re.match(Parser.patterns["end_hub_pattern"], stripped)):
                    if config_init["end_hub"] is not None:
                        raise exc.EndHubError(f"Line {line_num}: Only one end hub is allowed!")
                    config_init["end_hub"] = {
                        "name": match.group("eh_name"),
                        "x": match.group("eh_x"),
                        "y": match.group("eh_y"),
                        "meta": match.group("meta"),
                        "line": line_num
                    }

                elif (match := re.match(Parser.patterns["hub_pattern"], stripped)):
                    config_init["hubs"].append({
                        "name": match.group("h_name"),
                        "x": match.group("h_x"),
                        "y": match.group("h_y"),
                        "meta": match.group("meta"),
                        "line": line_num
                    })

                elif (match := re.match(Parser.patterns["connection_pattern"], stripped)):
                    config_init["connections"].append({
                        "from_hub": match.group("from_hub"),
                        "to_hub": match.group("to_hub"),
                        "meta": match.group("meta"),
                        "line": line_num
                    })

                else:
                    raise exc.ParserError(f"Line {line_num}: Invalid syntax on line: '{stripped}'")

        # 3. Verify presence of mandatory hubs
        if config_init["start_hub"] is None:
            raise exc.StartHubError("Missing required start_hub.")
        if config_init["end_hub"] is None:
            raise exc.EndHubError("Missing required end_hub.")

        return config_init


    def _validate_zone(self, zone_data: dict, is_end_start: bool, seen_coordinates: set[tuple]) -> Zone:
        """Helper method to validate a single zone and return a Zone object."""
        line_num = zone_data["line"]
        meta = self.parse_meta_data(zone_data["meta"], line_num)

        # A. Verify seen_coordinates
        try:
            x, y = int(zone_data["x"]), int(zone_data["y"])
            if (x,y) in seen_coordinates:
                raise exc.ValidationError(f"coordinates must be unique")
            seen_coordinates.add((x,y))
        except ValueError:
            raise exc.ValidationError(f"Line {line_num}: seen_coordinates must be integers.")

        # B. Check zone type & map to Enum
        raw_type = meta.get("zone", "normal")
        try:
            z_type = ZoneType(raw_type)
        except ValueError:
            raise exc.ValidationError(
                f"Line {line_num}: Invalid zone type '{raw_type}'. "
                "Must be normal, blocked, restricted, or priority."
            )

        # C. Check color
        color = meta.get("color", None)

        # D. Check capacity
        if not is_end_start:
            try:
                capacity = int(meta.get("max_drones", "1"))
                if capacity <= 0:
                    raise ValueError
            except ValueError:
                raise exc.MetaDataError(
                    f"Line {line_num}: Capacity (max_drones) must be a positive integer."
                )
        else:
            capacity = None



        # Build and return your beautiful dataclass!
        return Zone(
            name=zone_data["name"],
            x=x,
            y=y,
            zone_type=z_type,
            max_drones=capacity,
            color=color
        )

    def parse_validate(self) -> Graph:
        """Validates semantic logic and builds the Graph object."""
        
        seen_coordinates = set()
        config_init: dict = self._init_parse_lines()
        # 1. Validate Drones
        raw_nb, nb_line = config_init["nb_drones"]
        nb_drones = int(raw_nb)            
        if nb_drones <= 0:
            raise exc.ValidationError(
                f"Line {nb_line}: Number of drones must be > 0 (got {nb_drones})"
            )

        # Instantiate our master Graph object!
        graph = Graph(nb_drones=nb_drones)

        # 2. Validate Start Hub
        start_zone = self._validate_zone(config_init["start_hub"], True, seen_coordinates)
        if start_zone.zone_type.value == 'blocked':
            raise exc.ValidationError("start hub can't be blocked!")
        start_zone.max_drones = nb_drones
        graph.add_zone(start_zone)
        graph.start_hub = start_zone.name


        # 3. Validate End Hub
        end_zone = self._validate_zone(config_init["end_hub"], True, seen_coordinates)
        if end_zone.zone_type.value == 'blocked':
            raise exc.ValidationError("end hub can't be blocked!")
        if end_zone.name in graph.zones:
            raise exc.ValidationError(
                f"Line {config_init['end_hub']['line']}: Duplicate zone name '{end_zone.name}'."
            )
        graph.add_zone(end_zone)
        graph.end_hub = end_zone.name
        end_zone.max_drones = nb_drones

        # 4. Validate Regular Hubs
        for hub_data in config_init["hubs"]:
            hub_zone = self._validate_zone(hub_data, False, seen_coordinates)
            if hub_zone.name in graph.zones:
                raise exc.ValidationError(
                    f"Line {hub_data['line']}: Duplicate zone name '{hub_zone.name}'."
                )
            graph.add_zone(hub_zone)

        # 5. Validate Connections
        seen_connections = set()

        for conn_data in config_init["connections"]:
            line_num = conn_data["line"]
            from_hub = conn_data["from_hub"]
            to_hub = conn_data["to_hub"]

            if from_hub not in graph.zones or to_hub not in graph.zones:
                raise exc.ValidationError(
                    f"Line {line_num}: Connection references undefined zone(s)."
                )

            # Check for duplicate bidirectional connections[cite: 1]
            conn_pair = tuple(sorted([from_hub, to_hub]))
            if conn_pair in seen_connections:
                raise exc.ValidationError(
                    f"Line {line_num}: Duplicate connection between '{from_hub}' and '{to_hub}'."
                )
            seen_connections.add(conn_pair)

            meta = self.parse_meta_data(conn_data["meta"], line_num)
            try:
                link_capacity = int(meta.get("max_link_capacity", "1"))
                if link_capacity <= 0:
                    raise ValueError
            except ValueError:
                raise exc.ValidationError(
                    f"Line {line_num}: max_link_capacity must be a positive integer."
                )

            # Add the bidirectional connection directly to the objects![cite: 1]
            graph.zones[from_hub].add_connection(to_hub, link_capacity)
            graph.zones[to_hub].add_connection(from_hub, link_capacity)

        return graph