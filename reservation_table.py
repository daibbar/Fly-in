from models import Graph


class ReservationTable:
    """Spatiotemporal reservation table for zone and link capacities."""

    def __init__(self, graph: Graph):
        """Initialize empty reservations for the given graph.

        Args:
            graph (Graph): The graph for which to initialize reservations.
        """
        self.graph = graph
        self.zone_reservations: dict[tuple[str, int], int] = dict()
        self.link_reservations: dict[tuple[str, str, int], int] = dict()

    def can_enter_zone(self, zone_name: str, turn: int) -> bool:
        """Check if a zone can accept a drone at the given turn.

        Args:
            zone_name (str): The name of the zone to check.
            turn (int): The turn number to check for availability.

        Returns:
            bool: True if the zone can accept a drone, False otherwise.
        """
        zone_obj = self.graph.zones[zone_name]
        return (
            self.zone_reservations.get((zone_name, turn), 0)
            < zone_obj.max_drones
        )

    def can_use_link(
        self, current_zone: str, neighbor: str, turn: int
    ) -> bool:
        """Check if a link between zones is available at the given turn.

        Args:
            current_zone (str): The starting zone of the link.
            neighbor (str): The destination zone of the link.
            turn (int): The turn number to check.

        Returns:
            bool: True if the link is available, False otherwise.
        """
        connection: tuple[str, str, int] = (
            (current_zone, neighbor, turn) if current_zone < neighbor
            else (neighbor, current_zone, turn)
        )
        return (
            self.link_reservations.get(connection, 0)
            < self.graph.zones[connection[0]].neighbors[connection[1]]
        )

    def reserve_zone(self, zone_name: str, turn: int) -> bool:
        """Reserve capacity in a zone for a specific turn.

        Args:
            zone_name (str): The name of the zone to reserve.
            turn (int): The turn number to reserve.

        Returns:
            bool: True if the reservation was successful, False otherwise.
        """
        if self.can_enter_zone(zone_name, turn) is False:
            return False
        if zone_name not in self.graph.zones:
            return False

        try:
            self.zone_reservations[(zone_name, turn)] += 1
        except KeyError:
            self.zone_reservations[(zone_name, turn)] = 1
        return True

    def reserve_link(self, current_zone: str, zone: str, turn: int) -> bool:
        """Reserve capacity on a link between zones for a specific turn.

        Args:
            current_zone (str): The starting zone of the link.
            zone (str): The destination zone of the link.
            turn (int): The turn number to reserve.

        Returns:
            bool: True if the reservation was successful, False otherwise.
        """
        link = (
            (current_zone, zone, turn) if current_zone < zone
            else (zone, current_zone, turn)
        )
        if self.can_use_link(current_zone, zone, turn) is False:
            return False

        try:
            self.link_reservations[link] += 1
        except KeyError:
            self.link_reservations[link] = 1
        return True
