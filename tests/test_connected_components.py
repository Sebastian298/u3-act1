from __future__ import annotations

import tempfile
import unittest
from collections import deque
from pathlib import Path

from depth_first_search import Component, find_connected_components
from graph_input import Graph, build_graph, load_graph

_ACTIVITY_GRAPH = Path(__file__).resolve().parents[1] / "Grafo_no_conexo.txt"


class ConnectedComponentsTest(unittest.TestCase):
    def test_connected_graph(self) -> None:
        graph = build_graph([1, 2, 3], [(1, 3), (3, 2)])

        components = find_connected_components(graph)

        self.assertEqual(len(components), 1)
        self.assertEqual(components[0].members, (1, 2, 3))
        self.assertEqual(components[0].visit_order, (1, 3, 2))
        self.assert_partition(graph, components)

    def test_two_components(self) -> None:
        graph = build_graph([1, 2, 3, 4], [(1, 2), (3, 4)])

        components = find_connected_components(graph)

        self.assertEqual(
            [component.members for component in components],
            [(1, 2), (3, 4)],
        )
        self.assertEqual(
            [component.visit_order for component in components],
            [(1, 2), (3, 4)],
        )
        self.assert_partition(graph, components)

    def test_isolated_node(self) -> None:
        graph = build_graph([1, 2, 3], [(1, 2)])

        components = find_connected_components(graph)

        self.assertEqual(graph.adjacency[3], ())
        self.assertEqual(
            [component.members for component in components],
            [(1, 2), (3,)],
        )
        self.assertEqual(components[1].visit_order, (3,))
        self.assert_partition(graph, components)

    def test_graph_with_cycle(self) -> None:
        graph = build_graph([1, 2, 3], [(1, 2), (2, 3), (3, 1)])

        components = find_connected_components(graph)

        self.assertEqual(len(components), 1)
        self.assertEqual(components[0].members, (1, 2, 3))
        self.assertEqual(components[0].visit_order, (1, 2, 3))
        self.assertEqual(len(components[0].visit_order), len(set(components[0].visit_order)))
        self.assert_partition(graph, components)

    def test_empty_graph(self) -> None:
        graph = build_graph([], [])

        components = find_connected_components(graph)

        self.assertEqual(graph.node_count, 0)
        self.assertEqual(graph.edge_count, 0)
        self.assertEqual(components, [])
        self.assert_partition(graph, components)

    def test_edge_to_unknown_node(self) -> None:
        with self.assertRaises(ValueError):
            build_graph([1, 2], [(1, 9)])

    def test_undirected_edge_is_stored_both_ways(self) -> None:
        graph = build_graph([1, 2], [(2, 1), (1, 2)])

        self.assertEqual(graph.edge_count, 1)
        self.assertEqual(graph.adjacency[1], (2,))
        self.assertEqual(graph.adjacency[2], (1,))

    def assert_partition(self, graph: Graph, components: list[Component]) -> None:
        found: list[int] = []
        for component in components:
            self.assertEqual(set(component.members), set(component.visit_order))
            self.assertEqual(
                len(component.visit_order),
                len(set(component.visit_order)),
            )
            found.extend(component.members)
        self.assertEqual(sorted(found), list(graph.nodes))
        self.assertEqual(len(found), len(set(found)))


class GraphFileTest(unittest.TestCase):
    def test_parser_reads_set_style_file(self) -> None:
        contents = """Nodes:
(1, 2, 4)

Edges:

[(1, 2)]
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample_graph.txt"
            path.write_text(contents, encoding="utf-8")
            graph = load_graph(path)

        self.assertEqual(graph.nodes, (1, 2, 4))
        self.assertEqual(graph.edge_count, 1)
        self.assertEqual(graph.adjacency[4], ())

    def test_activity_graph_is_partitioned(self) -> None:
        graph = load_graph(_ACTIVITY_GRAPH)
        components = find_connected_components(graph)

        self.assert_membership_matches_bfs(graph, components)
        found: list[int] = []
        for component in components:
            found.extend(component.members)
        self.assertEqual(sorted(found), list(graph.nodes))
        self.assertEqual(len(found), len(set(found)))

    def test_activity_graph_components(self) -> None:
        graph = load_graph(_ACTIVITY_GRAPH)
        components = find_connected_components(graph)

        self.assertEqual(
            [component.members for component in components],
            [
                (
                    0, 1, 2, 4, 5, 7, 8, 9, 12, 13, 14, 15, 16, 17, 19, 21, 22,
                    23, 24, 25, 26, 27, 28, 29, 31, 32, 34, 38, 39, 40, 41, 43,
                    44, 46, 48,
                ),
                (
                    3, 6, 10, 11, 18, 20, 30, 33, 35, 36, 37, 42, 45, 47, 49,
                ),
            ],
        )
        self.assertEqual(graph.node_count, 50)
        self.assertEqual(graph.edge_count, 84)

    def assert_membership_matches_bfs(
        self,
        graph: Graph,
        components: list[Component],
    ) -> None:
        dfs_sets = {frozenset(component.members) for component in components}
        self.assertEqual(dfs_sets, _component_sets_bfs(graph))


def _component_sets_bfs(graph: Graph) -> set[frozenset[int]]:
    visited: set[int] = set()
    components: set[frozenset[int]] = set()
    for start in graph.nodes:
        if start in visited:
            continue
        queue: deque[int] = deque([start])
        visited.add(start)
        members: set[int] = set()
        while queue:
            node = queue.popleft()
            members.add(node)
            for neighbor in graph.adjacency[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        components.add(frozenset(members))
    return components


if __name__ == "__main__":
    unittest.main()
