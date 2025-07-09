import networkx as nx
from collections import deque

class FordFulkerson:
    def __init__(self, graph):
        """
        Inicializa el algoritmo con un grafo dirigido.
        :param graph: nx.DiGraph con atributo 'flujo' en las aristas (capacidad)
        """
        self.G = graph
        self.residual_graph = None
        self.flow_paths = []
        self.max_flow = 0
        self.edge_flows = {}

    def find_augmenting_path(self, source, sink):
        """Encuentra un camino de aumento usando BFS en el grafo residual."""
        visited = {node: False for node in self.residual_graph.nodes()}
        parent = {}
        queue = deque([source])
        visited[source] = True

        while queue:
            u = queue.popleft()
            for v in self.residual_graph.neighbors(u):
                if not visited[v] and self.residual_graph[u][v]['capacity'] > 0:
                    parent[v] = u
                    visited[v] = True
                    if v == sink:
                        # Reconstruir el camino
                        path = []
                        current = sink
                        while current != source:
                            path.append(current)
                            current = parent[current]
                        path.append(source)
                        path.reverse()
                        return path
                    queue.append(v)
        return None

    def compute_max_flow(self, source, sink):
        """Calcula el flujo máximo desde source hasta sink."""
        # Inicializar grafo residual 
        self.residual_graph = nx.DiGraph()
        for u, v, data in self.G.edges(data=True):

            self.residual_graph.add_edge(u, v, capacity=data['capacity'])
            if not self.residual_graph.has_edge(v, u):
                self.residual_graph.add_edge(v, u, capacity=0)



        self.max_flow = 0
        self.flow_paths = []
        self.edge_flows = {}

        while True:
            path = self.find_augmenting_path(source, sink)
            if not path:
                break

            # Calcular cuello de botella
            bottleneck = float('Inf')
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                bottleneck = min(bottleneck, self.residual_graph[u][v]['capacity'])

            # Actualizar grafo residual
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                self.residual_graph[u][v]['capacity'] -= bottleneck
                self.residual_graph[v][u]['capacity'] += bottleneck

            # Guardar información del camino
            self.flow_paths.append({
                'path': path,
                'flow': bottleneck,
                'total_flow': self.max_flow + bottleneck
            })
            self.max_flow += bottleneck
        # Calcular flujos en las aristas originales (solo las utilizadas)
        for u, v, data in self.G.edges(data=True):
            original_capacity = data['capacity'] 
            residual_capacity = self.residual_graph[u][v]['capacity'] if self.residual_graph.has_edge(u, v) else original_capacity
            flow = original_capacity - residual_capacity
            if flow > 0:
                utilization = (flow / original_capacity) * 100 if original_capacity > 0 else 0
                self.edge_flows[(u, v)] = {
                    'flow': flow,
                    'capacity': original_capacity,
                    'utilization': utilization
                }


        return {
            'max_flow': self.max_flow,
            'flow_paths': self.flow_paths,
            'edge_flows': self.edge_flows
        }