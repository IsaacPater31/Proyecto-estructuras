import networkx as nx
from collections import deque

def edmonds_karp(G, source, sink):
    residual = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        cap = data.get('capacity', data.get('flujo', 0))
        residual.add_edge(u, v, capacity=cap)
        if not residual.has_edge(v, u):
            residual.add_edge(v, u, capacity=0)

    max_flow = 0
    flow_paths = []

    while True:
        # BFS para encontrar camino de aumento
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v in residual.successors(u):
                if v not in parent and residual[u][v]['capacity'] > 0:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break

        # Encontrar el cuello de botella
        path = []
        v = sink
        bottleneck = float('inf')
        while v != source:
            u = parent[v]
            path.append((u, v))
            bottleneck = min(bottleneck, residual[u][v]['capacity'])
            v = u
        path = [source] + [v for u, v in reversed(path)]

        # Actualizar capacidades residuales
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v]['capacity'] -= bottleneck
            residual[v][u]['capacity'] += bottleneck
            v = u

        max_flow += bottleneck
        flow_paths.append({'path': path, 'flow': bottleneck, 'total_flow': max_flow})

    # Calcular flujo por arista original
    edge_flows = {}
    for u, v, data in G.edges(data=True):
        cap = data.get('capacity', data.get('flujo', 0))
        flow = cap - residual[u][v]['capacity']
        utilization = (flow / cap * 100) if cap else 0
        edge_flows[(u, v)] = {
            'flow': flow,
            'capacity': cap,
            'utilization': utilization
        }

    return {
        'max_flow': max_flow,
        'flow_paths': flow_paths,
        'edge_flows': edge_flows,
        'algorithm': 'Edmonds-Karp'
    }