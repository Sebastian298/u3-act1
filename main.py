from __future__ import annotations

import argparse
import sys
from pathlib import Path

from depth_first_search import Component, find_connected_components
from graph_input import Graph, load_graph

STATEMENT_GROUP_COUNT = 2


def format_report(
    graph: Graph,
    components: list[Component],
    source_name: str,
    expected_components: int | None,
) -> str:
    lines = [
        f"Archivo: {source_name}",
        f"Nodos: {graph.node_count}",
        f"Aristas: {graph.edge_count}",
        f"Componentes conexas: {len(components)}",
        "",
    ]
    if not components:
        lines.append("El grafo no declara nodos, así que no hay componentes.")
        lines.append("")

    for index, component in enumerate(components, start=1):
        members = _format_nodes(component.members)
        visit_order = _format_nodes(component.visit_order)
        lines.extend(
            [
                f"Componente {index}",
                f"  Integrantes ({len(component.members)} nodos): {members}",
                f"  Orden de visita DFS: {visit_order}",
                "",
            ]
        )

    if expected_components is not None:
        discovered = len(components)
        if discovered == expected_components:
            outcome = "El resultado coincide con la indicación del enunciado."
        else:
            outcome = "El resultado no coincide con la indicación del enunciado."
        lines.extend(
            [
                "Comprobación posterior:",
                (
                    f"  El enunciado indica {expected_components} agrupaciones. "
                    "Esa cifra no participa en el cálculo."
                ),
                f"  DFS encontró {discovered} componentes conexas. {outcome}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Identifica las componentes conexas de un grafo no dirigido "
            "mediante búsqueda en profundidad."
        )
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="Grafo_no_conexo.txt",
        help="Ruta del archivo del grafo. Por defecto: Grafo_no_conexo.txt.",
    )
    parser.add_argument(
        "--expected-components",
        type=int,
        default=STATEMENT_GROUP_COUNT,
        help=(
            "Cantidad indicada por el enunciado. Solo se compara al final "
            f"(por defecto: {STATEMENT_GROUP_COUNT})."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = Path(args.input_file)
    try:
        graph = load_graph(source)
    except (OSError, ValueError) as error:
        print(f"No se pudo leer el grafo: {error}", file=sys.stderr)
        return 1

    components = find_connected_components(graph)
    print(
        format_report(
            graph,
            components,
            source.name,
            args.expected_components,
        ),
        end="",
    )
    return 0


def _format_nodes(nodes: tuple[int, ...]) -> str:
    if not nodes:
        return "(ninguno)"
    return ", ".join(str(node) for node in nodes)


if __name__ == "__main__":
    sys.exit(main())
