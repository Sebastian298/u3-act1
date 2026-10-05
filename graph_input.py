from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_NODES_SECTION = re.compile(r"Nodes:\s*\((.*?)\)", re.IGNORECASE | re.DOTALL)
_EDGES_SECTION = re.compile(r"Edges:\s*\[(.*?)\]", re.IGNORECASE | re.DOTALL)
_EDGE_PAIR = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")
_INTEGER_TOKEN = re.compile(r"-?\d+")


@dataclass(frozen=True)
class Graph:
    adjacency: dict[int, tuple[int, ...]]
    edge_count: int

    @property
    def node_count(self) -> int:
        return len(self.adjacency)

    @property
    def nodes(self) -> tuple[int, ...]:
        return tuple(sorted(self.adjacency))


def load_graph(path: str | Path) -> Graph:
    text = Path(path).read_text(encoding="utf-8")
    nodes, edges = parse_graph_text(text)
    return build_graph(nodes, edges)


def parse_graph_text(text: str) -> tuple[list[int], list[tuple[int, int]]]:
    nodes_match = _NODES_SECTION.search(text)
    edges_match = _EDGES_SECTION.search(text)
    if nodes_match is None or edges_match is None:
        raise ValueError(
            "El archivo debe contener una sección Nodes: (...) y una sección Edges: [...]."
        )
    return _parse_nodes(nodes_match.group(1)), _parse_edges(edges_match.group(1))


def build_graph(
    nodes: list[int],
    edges: list[tuple[int, int]],
) -> Graph:
    _reject_duplicate_nodes(nodes)
    neighbors: dict[int, set[int]] = {node: set() for node in nodes}
    unique_edges: set[tuple[int, int]] = set()

    for start, end in edges:
        missing = [node for node in (start, end) if node not in neighbors]
        if missing:
            missing_text = ", ".join(str(node) for node in missing)
            raise ValueError(
                f"La arista ({start}, {end}) referencia nodos no declarados: {missing_text}."
            )
        neighbors[start].add(end)
        neighbors[end].add(start)
        unique_edges.add((start, end) if start <= end else (end, start))

    adjacency = {
        node: tuple(sorted(neighbors[node]))
        for node in sorted(neighbors)
    }
    return Graph(adjacency=adjacency, edge_count=len(unique_edges))


def _parse_nodes(body: str) -> list[int]:
    nodes: list[int] = []
    for raw_token in body.split(","):
        token = raw_token.strip()
        if token == "":
            continue
        if _INTEGER_TOKEN.fullmatch(token) is None:
            raise ValueError(f"Token de nodo no válido: {token!r}.")
        nodes.append(int(token))
    return nodes


def _parse_edges(body: str) -> list[tuple[int, int]]:
    edges = [
        (int(match.group(1)), int(match.group(2)))
        for match in _EDGE_PAIR.finditer(body)
    ]
    leftover = _EDGE_PAIR.sub(" ", body).replace(",", " ")
    unexpected = leftover.split()
    if unexpected:
        unexpected_text = " ".join(unexpected)
        raise ValueError(
            "La sección Edges contiene elementos que no son pares de enteros: "
            f"{unexpected_text}."
        )
    return edges


def _reject_duplicate_nodes(nodes: list[int]) -> None:
    seen: set[int] = set()
    duplicates: list[int] = []
    for node in nodes:
        if node in seen and node not in duplicates:
            duplicates.append(node)
        seen.add(node)
    if duplicates:
        duplicate_text = ", ".join(str(node) for node in duplicates)
        raise ValueError(f"La sección Nodes repite identificadores: {duplicate_text}.")
