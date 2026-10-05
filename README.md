# U3 A1. Componentes conexas con DFS

El programa lee un grafo no dirigido, construye su lista de adyacencia y encuentra las componentes conexas con búsqueda en profundidad. Solo usa la biblioteca estándar de Python 3.

## Ejecutar el programa

Desde esta carpeta:

```bash
python3 main.py Grafo_no_conexo.txt
```

Si el archivo está en el directorio actual, la ruta puede omitirse:

```bash
python3 main.py
```

Para usar otro archivo:

```bash
python3 main.py ruta/al/grafo.txt
```

La salida muestra la cantidad de nodos y aristas, el número de componentes, los integrantes de cada una y el orden de visita de DFS.

## Ejecutar las pruebas

```bash
python3 -m unittest discover -s tests -v
```
