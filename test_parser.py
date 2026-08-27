"""Unit tests for the Fly-in map parser."""

import os
import tempfile
import unittest
from typing import Optional

import exceptions as exc
from models import ZoneType
from parser import Parser


class TestParser(unittest.TestCase):
    """Test suite for validating Parser behavior and error handling."""

    def _parse_content(self, content: str):
        """Helper to write content to a temporary file and parse it."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            return Parser.parse_file(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_valid_basic_linear_map(self) -> None:
        """Test parsing a minimal valid linear map."""
        content = (
            "nb_drones: 2\n"
            "start_hub: start 0 0 [color=green]\n"
            "hub: waypoint 1 0 [zone=normal max_drones=2]\n"
            "end_hub: goal 2 0 [color=red]\n"
            "connection: start-waypoint [max_link_capacity=2]\n"
            "connection: waypoint-goal\n"
        )
        network = self._parse_content(content)
        self.assertEqual(network.nb_drones, 2)
        self.assertEqual(network.start_hub.name, "start")
        self.assertEqual(network.end_hub.name, "goal")
        self.assertEqual(len(network.zones), 3)
        self.assertEqual(len(network.connections), 2)
        self.assertEqual(network.zones["waypoint"].max_drones, 2)
        self.assertEqual(network.zones["waypoint"].zone_type, ZoneType.NORMAL)

    def test_zone_types_and_defaults(self) -> None:
        """Test default metadata and custom zone types."""
        content = (
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: p 1 0 [zone=priority]\n"
            "hub: r 2 0 [zone=restricted]\n"
            "hub: b 3 0 [zone=blocked]\n"
            "end_hub: e 4 0\n"
            "connection: s-p\n"
            "connection: p-r\n"
            "connection: r-b\n"
            "connection: b-e\n"
        )
        network = self._parse_content(content)
        self.assertEqual(network.zones["s"].zone_type, ZoneType.NORMAL)
        self.assertEqual(network.zones["s"].max_drones, 1)
        self.assertEqual(network.zones["p"].zone_type, ZoneType.PRIORITY)
        self.assertEqual(network.zones["p"].movement_cost, 1)
        self.assertEqual(network.zones["r"].zone_type, ZoneType.RESTRICTED)
        self.assertEqual(network.zones["r"].movement_cost, 2)
        self.assertEqual(network.zones["b"].zone_type, ZoneType.BLOCKED)
        self.assertTrue(network.zones["b"].is_blocked)

    def test_missing_nb_drones(self) -> None:
        """Test missing nb_drones line at start of file."""
        content = (
            "start_hub: s 0 0\n"
            "end_hub: e 1 0\n"
            "connection: s-e\n"
        )
        with self.assertRaises(exc.NbDronesError):
            self._parse_content(content)

    def test_invalid_drone_count(self) -> None:
        """Test zero, negative, and non-integer drone counts."""
        for val in ["0", "-4", "abc", "3.14"]:
            content = f"nb_drones: {val}\nstart_hub: s 0 0\nend_hub: e 1 0\n"
            with self.assertRaises(exc.NbDronesError):
                self._parse_content(content)

    def test_duplicate_nb_drones(self) -> None:
        """Test duplicate nb_drones definition."""
        content = (
            "nb_drones: 2\n"
            "start_hub: s 0 0\n"
            "nb_drones: 5\n"
            "end_hub: e 1 0\n"
            "connection: s-e\n"
        )
        with self.assertRaises(exc.NbDronesError):
            self._parse_content(content)

    def test_missing_or_duplicate_start_hub(self) -> None:
        """Test missing and duplicate start_hub."""
        # Missing
        content_missing = (
            "nb_drones: 1\n"
            "hub: s 0 0\n"
            "end_hub: e 1 0\n"
            "connection: s-e\n"
        )
        with self.assertRaises(exc.StartHubError):
            self._parse_content(content_missing)

        # Duplicate
        content_dup = (
            "nb_drones: 1\n"
            "start_hub: s1 0 0\n"
            "start_hub: s2 1 0\n"
            "end_hub: e 2 0\n"
            "connection: s1-e\n"
        )
        with self.assertRaises(exc.StartHubError):
            self._parse_content(content_dup)

    def test_missing_or_duplicate_end_hub(self) -> None:
        """Test missing and duplicate end_hub."""
        # Missing
        content_missing = (
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "hub: e 1 0\n"
            "connection: s-e\n"
        )
        with self.assertRaises(exc.EndHubError):
            self._parse_content(content_missing)

        # Duplicate
        content_dup = (
            "nb_drones: 1\n"
            "start_hub: s 0 0\n"
            "end_hub: e1 1 0\n"
            "end_hub: e2 2 0\n"
            "connection: s-e1\n"
        )
        with self.assertRaises(exc.EndHubError):
            self._parse_content(content_dup)

    def test_zone_name_with_dash(self) -> None:
        """Test that zone names with dashes are rejected."""
        content = (
            "nb_drones: 1\n"
            "start_hub: hub-1 0 0\n"
            "end_hub: goal 1 0\n"
            "connection: hub-1-goal\n"
        )
        with self.assertRaises(exc.StartHubError):
            self._parse_content(content)

    def test_duplicate_zone_name(self) -> None:
        """Test that duplicate zone names are rejected."""
        content = (
            "nb_drones: 1\n"
            "start_hub: hub1 0 0\n"
            "hub: hub1 1 1\n"
            "end_hub: goal 2 0\n"
            "connection: hub1-goal\n"
        )
        with self.assertRaises(exc.HubError):
            self._parse_content(content)

    def test_non_integer_coordinates(self) -> None:
        """Test non-integer coordinates rejection."""
        content = (
            "nb_drones: 1\n"
            "start_hub: start y0 0\n"
            "end_hub: goal 2 0\n"
            "connection: start-goal\n"
        )
        with self.assertRaises(exc.StartHubError):
            self._parse_content(content)

    def test_connection_undefined_zone(self) -> None:
        """Test connection referencing non-existent zone."""
        content = (
            "nb_drones: 1\n"
            "start_hub: start 0 0\n"
            "end_hub: goal 2 0\n"
            "connection: start-missing_zone\n"
        )
        with self.assertRaises(exc.ConnectionError):
            self._parse_content(content)

    def test_connection_self_loop(self) -> None:
        """Test self-connecting edge rejection."""
        content = (
            "nb_drones: 1\n"
            "start_hub: start 0 0\n"
            "end_hub: goal 2 0\n"
            "connection: start-start\n"
        )
        with self.assertRaises(exc.ConnectionError):
            self._parse_content(content)

    def test_duplicate_connection(self) -> None:
        """Test duplicate bidirectional connections."""
        content = (
            "nb_drones: 1\n"
            "start_hub: start 0 0\n"
            "end_hub: goal 2 0\n"
            "connection: start-goal\n"
            "connection: goal-start\n"
        )
        with self.assertRaises(exc.ConnectionError):
            self._parse_content(content)

    def test_invalid_metadata(self) -> None:
        """Test various invalid metadata errors."""
        # Unclosed bracket
        with self.assertRaises(exc.MetaDataError):
            self._parse_content(
                "nb_drones: 1\nstart_hub: s 0 0 [color=red\nend_hub: e 1 0\n"
            )

        # Unknown key
        with self.assertRaises(exc.MetaDataError):
            self._parse_content(
                "nb_drones: 1\nstart_hub: s 0 0 [invalid_key=123]\n"
                "end_hub: e 1 0\n"
            )

        # Non-positive max_drones
        with self.assertRaises(exc.MetaDataError):
            self._parse_content(
                "nb_drones: 1\nstart_hub: s 0 0 [max_drones=0]\n"
                "end_hub: e 1 0\n"
            )

        # Non-positive max_link_capacity
        with self.assertRaises(exc.MetaDataError):
            self._parse_content(
                "nb_drones: 1\nstart_hub: s 0 0\nend_hub: e 1 0\n"
                "connection: s-e [max_link_capacity=-1]\n"
            )

    def test_all_sample_maps(self) -> None:
        """Test parsing all provided sample challenge maps."""
        map_files = [
            "maps/easy/01_linear_path.txt",
            "maps/easy/02_simple_fork.txt",
            "maps/easy/03_basic_capacity.txt",
            "maps/medium/01_dead_end_trap.txt",
            "maps/medium/02_circular_loop.txt",
            "maps/medium/03_priority_puzzle.txt",
            "maps/hard/01_maze_nightmare.txt",
            "maps/hard/02_capacity_hell.txt",
            "maps/hard/03_ultimate_challenge.txt",
            "maps/challenger/01_the_impossible_dream.txt",
        ]
        for path in map_files:
            if os.path.exists(path):
                network = Parser.parse_file(path)
                self.assertIsNotNone(network.start_hub)
                self.assertIsNotNone(network.end_hub)
                self.assertGreater(network.nb_drones, 0)
                self.assertGreater(len(network.zones), 0)


if __name__ == "__main__":
    unittest.main()
