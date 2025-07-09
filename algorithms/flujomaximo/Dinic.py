import networkx as nx
from collections import deque

def dinic(G, source, sink):
    residual = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        cap = data.get('capacity', data.get('flujo', 0))
        residual.add_edge(u, v, capacity=cap)
        if not residual.has_edge(v, u):
            residual.add_edge(v, u, capacity=0)

    max_flow = 0
    flow_paths = []

    def bfs_level():
        level = {source: 0}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in residual.successors(u):
                if residual[u][v]['capacity'] > 0 and v not in level:
                    level[v] = level[u] + 1
                    queue.append(v)
        return level if sink in level else None

    def dfs_flow(u, flow, level, next_edge):
        if u == sink:
            return flow
        n = len(list(residual.successors(u)))
        while next_edge[u] < n:
            v = list(residual.successors(u))[next_edge[u]]
            if residual[u][v]['capacity'] > 0 and level.get(v, -1) == level[u] + 1:
                pushed = dfs_flow(v, min(flow, residual[u][v]['capacity']), level, next_edge)
                if pushed > 0:
                    residual[u][v]['capacity'] -= pushed
                    residual[v][u]['capacity'] += pushed
                    return pushed
            next_edge[u] += 1
        return 0

    while True:
        level = bfs_level()
        if not level:
            break
        next_edge = {u: 0 for u in residual.nodes}
        while True:
            pushed = dfs_flow(source, float('inf'), level, next_edge)
            if pushed == 0:
                break
            max_flow += pushed
            # Opcional: reconstruir el camino de aumento (no trivial en Dinic)
            # Aquí solo guardamos el flujo total tras cada aumento
            flow_paths.append({'path': [], 'flow': pushed, 'total_flow': max_flow})

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
        'algorithm': 'Dinic'
    }