import networkx as nx
from collections import defaultdict, deque

def ford_fulkerson(G, source, sink):
    """
    Implementación del algoritmo Ford-Fulkerson para encontrar el flujo máximo
    entre un nodo fuente y un nodo sumidero.
    """
    # Crear grafo residual
    residual_graph = create_residual_graph(G)
    
    max_flow = 0
    flow_paths = []
    
    # Mientras exista un camino de aumento
    while True:
        # Encontrar camino de aumento usando BFS
        path, bottleneck = find_augmenting_path_bfs(residual_graph, source, sink)
        
        if not path:
            break
            
        # Actualizar el flujo máximo
        max_flow += bottleneck
        
        # Guardar información del camino
        flow_paths.append({
            'path': path,
            'flow': bottleneck,
            'total_flow': max_flow
        })
        
        # Actualizar el grafo residual
        update_residual_graph(residual_graph, path, bottleneck)
    
    # Calcular el flujo por cada arista
    edge_flows = calculate_edge_flows(G, residual_graph)
    
    return max_flow, flow_paths, edge_flows

def create_residual_graph(G):
    """Crea el grafo residual basado en el grafo original"""
    residual = defaultdict(lambda: defaultdict(int))
    
    for u, v, data in G.edges(data=True):
        # Capacidad directa (usando 'flujo' como capacidad)
        capacity = data.get('flujo', 1)  # Default a 1 si no hay flujo
        residual[u][v] = capacity
        # Capacidad inversa (inicialmente 0)
        if residual[v][u] == 0:
            residual[v][u] = 0
    
    return residual

def find_augmenting_path_bfs(residual_graph, source, sink):
    """Encuentra un camino de aumento usando BFS"""
    visited = set()
    queue = deque([(source, [source])])
    
    while queue:
        node, path = queue.popleft()
        
        if node in visited:
            continue
            
        visited.add(node)
        
        if node == sink:
            # Encontrar el cuello de botella en el camino
            bottleneck = float('inf')
            for i in range(len(path) - 1):
                capacity = residual_graph[path[i]][path[i + 1]]
                bottleneck = min(bottleneck, capacity)
            
            return path, bottleneck
        
        # Explorar vecinos
        for neighbor, capacity in residual_graph[node].items():
            if neighbor not in visited and capacity > 0:
                queue.append((neighbor, path + [neighbor]))
    
    return None, 0

def update_residual_graph(residual_graph, path, flow):
    """Actualiza el grafo residual después de encontrar un camino de aumento"""
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        # Reducir capacidad directa
        residual_graph[u][v] -= flow
        # Aumentar capacidad inversa
        residual_graph[v][u] += flow

def calculate_edge_flows(original_graph, residual_graph):
    """Calcula el flujo por cada arista del grafo original"""
    edge_flows = {}
    
    for u, v, data in original_graph.edges(data=True):
        original_capacity = data.get('flujo', 1)
        remaining_capacity = residual_graph[u][v]
        flow = original_capacity - remaining_capacity
        
        # Asegurar que el flujo no sea negativo
        flow = max(0, flow)
        
        edge_flows[(u, v)] = {
            'flow': flow,
            'capacity': original_capacity,
            'utilization': (flow / original_capacity) * 100 if original_capacity > 0 else 0
        }
    
    return edge_flows

def find_max_flow_paths(G, source, sink):
    """
    Función principal que encapsula el algoritmo Ford-Fulkerson
    """
    try:
        max_flow, flow_paths, edge_flows = ford_fulkerson(G, source, sink)
        
        return {
            'max_flow': max_flow,
            'flow_paths': flow_paths,
            'edge_flows': edge_flows,
            'algorithm': 'Ford-Fulkerson'
        }
    except Exception as e:
        print(f"Error en Ford-Fulkerson: {e}")
        return {
            'max_flow': 0,
            'flow_paths': [],
            'edge_flows': {},
            'algorithm': 'Ford-Fulkerson',
            'error': str(e)
        }

# Función auxiliar para verificar si un grafo es válido para flujo máximo
def validate_flow_graph(G, source, sink):
    """Valida que el grafo sea apropiado para algoritmos de flujo máximo"""
    errors = []
    
    if source not in G.nodes():
        errors.append(f"El nodo fuente '{source}' no existe en el grafo")
    
    if sink not in G.nodes():
        errors.append(f"El nodo sumidero '{sink}' no existe en el grafo")
    
    if source == sink:
        errors.append("El nodo fuente y sumidero no pueden ser el mismo")
    
    # Verificar que haya al menos un camino entre source y sink
    if source in G.nodes() and sink in G.nodes():
        if not nx.has_path(G, source, sink):
            errors.append(f"No existe un camino entre '{source}' y '{sink}'")
    
    # Verificar que las aristas tengan capacidades válidas
    for u, v, data in G.edges(data=True):
        if 'flujo' in data and data['flujo'] <= 0:
            errors.append(f"La arista {u}-{v} tiene capacidad inválida: {data['flujo']}")
    
    return errors