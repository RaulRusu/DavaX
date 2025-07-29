from typing import Self, Set

class GraphNode:
    def __init__(self):
        self.value = None
        self.neighbors: Set[Self] = set()

    def add_neighbor(self, neighbor: Self):
        self.neighbors.add(neighbor)

class Graph:
    def __init__(self):
        self._structure = {}

