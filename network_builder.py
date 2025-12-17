"""
Network builder with abstraction layer for future flexibility.
Implements both NetworkX-based and manual graph representations.
"""

from typing import List, Dict, Set, Optional
from abc import ABC, abstractmethod
from collections import deque
import networkx as nx
from models import Nodo, Segmento


class NetworkInterface(ABC):
    """
    Abstract interface for network representation.
    This allows switching between NetworkX and manual implementations.
    """
    
    @abstractmethod
    def add_node(self, node_id: int, **attributes):
        """Add a node to the network."""
        pass
    
    @abstractmethod
    def add_edge(self, node_from: int, node_to: int, **attributes):
        """Add an edge between two nodes."""
        pass
    
    @abstractmethod
    def get_nodes(self) -> List[int]:
        """Get all node IDs in the network."""
        pass
    
    @abstractmethod
    def get_neighbors(self, node_id: int) -> List[int]:
        """Get all neighbors of a node."""
        pass
    
    @abstractmethod
    def get_node_attributes(self, node_id: int) -> Dict:
        """Get attributes of a node."""
        pass
    
    @abstractmethod
    def bfs_traversal(self, start_node: int) -> List[tuple[int, int, int]]:
        """
        Perform BFS traversal and return closure table entries.
        Returns list of (ancestor, descendant, depth) tuples.
        """
        pass


class NetworkXAdapter(NetworkInterface):
    """NetworkX-based implementation of the network interface."""
    
    def __init__(self):
        self.graph = nx.Graph()
    
    def add_node(self, node_id: int, **attributes):
        self.graph.add_node(node_id, **attributes)
    
    def add_edge(self, node_from: int, node_to: int, **attributes):
        self.graph.add_edge(node_from, node_to, **attributes)
    
    def get_nodes(self) -> List[int]:
        return list(self.graph.nodes())
    
    def get_neighbors(self, node_id: int) -> List[int]:
        return list(self.graph.neighbors(node_id))
    
    def get_node_attributes(self, node_id: int) -> Dict:
        return dict(self.graph.nodes[node_id])
    
    def bfs_traversal(self, start_node: int) -> List[tuple[int, int, int]]:
        """
        BFS traversal using a queue (deque) to build closure table.
        Returns (ancestor, descendant, depth) for each relationship.
        """
        closure_entries = []
        visited = set()
        # Using deque as a queue for BFS
        queue = deque([(start_node, start_node, 0)])
        visited.add(start_node)
        
        # Track parent-child relationships for closure table
        parent_map = {start_node: None}
        
        while queue:
            ancestor, current, depth = queue.popleft()
            
            # Add entry to closure table (node related to itself at depth 0)
            if ancestor == current:
                closure_entries.append((current, current, 0))
            
            # Explore neighbors
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append((current, neighbor, 1))
                    
                    # Add direct relationship
                    closure_entries.append((current, neighbor, 1))
                    
                    # Add transitive relationships (all ancestors to this descendant)
                    # Walk up the parent chain
                    temp_ancestor = current
                    temp_depth = 1
                    while temp_ancestor in parent_map and parent_map[temp_ancestor] is not None:
                        temp_ancestor = parent_map[temp_ancestor]
                        temp_depth += 1
                        closure_entries.append((temp_ancestor, neighbor, temp_depth))
        
        return closure_entries


class ManualNetworkAdapter(NetworkInterface):
    """
    Manual implementation of network using adjacency lists.
    This provides independence from NetworkX library.
    """
    
    def __init__(self):
        self.nodes: Dict[int, Dict] = {}
        self.edges: Dict[int, Set[int]] = {}
    
    def add_node(self, node_id: int, **attributes):
        self.nodes[node_id] = attributes
        if node_id not in self.edges:
            self.edges[node_id] = set()
    
    def add_edge(self, node_from: int, node_to: int, **attributes):
        # Ensure nodes exist
        if node_from not in self.edges:
            self.edges[node_from] = set()
        if node_to not in self.edges:
            self.edges[node_to] = set()
        
        # Add bidirectional edge (undirected graph)
        self.edges[node_from].add(node_to)
        self.edges[node_to].add(node_from)
    
    def get_nodes(self) -> List[int]:
        return list(self.nodes.keys())
    
    def get_neighbors(self, node_id: int) -> List[int]:
        return list(self.edges.get(node_id, set()))
    
    def get_node_attributes(self, node_id: int) -> Dict:
        return self.nodes.get(node_id, {})
    
    def bfs_traversal(self, start_node: int) -> List[tuple[int, int, int]]:
        """
        BFS traversal using a queue (deque) to build closure table.
        Returns (ancestor, descendant, depth) for each relationship.
        """
        closure_entries = []
        visited = set()
        queue = deque([(start_node, start_node, 0)])
        visited.add(start_node)
        
        parent_map = {start_node: None}
        
        while queue:
            ancestor, current, depth = queue.popleft()
            
            if ancestor == current:
                closure_entries.append((current, current, 0))
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append((current, neighbor, 1))
                    
                    closure_entries.append((current, neighbor, 1))
                    
                    temp_ancestor = current
                    temp_depth = 1
                    while temp_ancestor in parent_map and parent_map[temp_ancestor] is not None:
                        temp_ancestor = parent_map[temp_ancestor]
                        temp_depth += 1
                        closure_entries.append((temp_ancestor, neighbor, temp_depth))
        
        return closure_entries


class NetworkBuilder:
    """
    Builds the electrical network from nodes and segments.
    Can use either NetworkX or manual implementation.
    """
    
    def __init__(self, use_networkx: bool = True):
        """
        Initialize the network builder.
        
        Args:
            use_networkx: If True, use NetworkX; if False, use manual implementation
        """
        self.network: NetworkInterface = (
            NetworkXAdapter() if use_networkx else ManualNetworkAdapter()
        )
    
    def build_network(self, nodos: List[Nodo], segmentos: List[Segmento]):
        """
        Build the network from nodes and segments.
        
        Args:
            nodos: List of network nodes
            segmentos: List of network segments (edges)
        """
        # Add all nodes
        for nodo in nodos:
            self.network.add_node(
                nodo.id_nodo,
                nombre=nodo.nombre,
                tipo=nodo.tipo,
                voltaje_kv=nodo.voltaje_kv,
                x=nodo.x,
                y=nodo.y
            )
        
        # Add all edges
        for segmento in segmentos:
            self.network.add_edge(
                segmento.nodo_inicio,
                segmento.nodo_fin,
                id_segmento=segmento.id_segmento,
                id_circuito=segmento.id_circuito,
                longitud_m=segmento.longitud_m,
                tipo_conductor=segmento.tipo_conductor,
                capacidad_amp=segmento.capacidad_amp
            )
    
    def get_network(self) -> NetworkInterface:
        """Get the built network."""
        return self.network
    
    def find_root_nodes(self) -> List[int]:
        """
        Find potential root nodes for BFS traversal.
        In a tree structure, these would be nodes with highest connectivity or specified as roots.
        For now, return all nodes to allow traversal from any starting point.
        """
        return self.network.get_nodes()
    
    def find_subestacion_node(self) -> int:
        """
        Find the node with tipo='Subestacion' to use as the starting point for BFS.
        
        Returns:
            The node ID of the Subestacion node
            
        Raises:
            ValueError: If no node with tipo='Subestacion' is found
        """
        for node_id in self.network.get_nodes():
            attrs = self.network.get_node_attributes(node_id)
            if attrs.get('tipo') == 'Subestacion':
                return node_id
        
        raise ValueError("No se encontró un nodo con tipo='Subestacion'. El algoritmo BFS requiere iniciar desde una Subestacion.")
