from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from graph_input import Graph


@dataclass(frozen=True)
class Component:
    visit_order: tuple[int, ...]

    @property
    def members(self) -> tuple[int, ...]:
        return tuple(sorted(self.visit_order))


def depth_first_search(
    start: int,
    adjacency: Mapping[int, Sequence[int]],
    visited: set[int],
) -> list[int]:
    if start in visited:
        return []

    visit_order: list[int] = []

    def explore(node: int) -> None:
        visited.add(node)
        visit_order.append(node)
        for neighbor in adjacency[node]:
            if neighbor not in adjacency:
                raise ValueError(
                    f"El vecino {neighbor} del nodo {node} no está en la lista de adyacencia."
                )
            if neighbor not in visited:
                explore(neighbor)

    explore(start)
    return visit_order


def find_connected_components(graph: Graph) -> list[Component]:
    visited: set[int] = set()
    components: list[Component] = []
    for node in graph.nodes:
        if node not in visited:
            visit_order = depth_first_search(node, graph.adjacency, visited)
            components.append(Component(visit_order=tuple(visit_order)))
    return components
