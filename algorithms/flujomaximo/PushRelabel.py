import networkx as nx

def push_relabel(G, source, sink):
    # Construir grafo residual
    residual = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        cap = data.get('capacity', data.get('flujo', 0))
        residual.add_edge(u, v, capacity=cap)
        if not residual.has_edge(v, u):
            residual.add_edge(v, u, capacity=0)

    # Inicializar preflujo
    n = len(residual.nodes)
    height = {u: 0 for u in residual.nodes}
    excess = {u: 0 for u in residual.nodes}
    height[source] = n
    for v in residual.successors(source):
        cap = residual[source][v]['capacity']
        if cap > 0:
            residual[source][v]['capacity'] = 0
            residual[v][source]['capacity'] += cap
            excess[v] += cap
            excess[source] -= cap

    def push(u, v):
        send = min(excess[u], residual[u][v]['capacity'])
        residual[u][v]['capacity'] -= send
        residual[v][u]['capacity'] += send
        excess[u] -= send
        excess[v] += send

    def relabel(u):
        min_height = float('inf')
        for v in residual.successors(u):
            if residual[u][v]['capacity'] > 0:
                min_height = min(min_height, height[v])
        if min_height < float('inf'):
            height[u] = min_height + 1

    active = [u for u in residual.nodes if u != source and u != sink and excess[u] > 0]
    flow_steps = []

    while active:
        u = active.pop(0)
        pushed = False
        for v in residual.successors(u):
            if residual[u][v]['capacity'] > 0 and height[u] == height[v] + 1:
                push(u, v)
                pushed = True
                if v != source and v != sink and v not in active and excess[v] > 0:
                    active.append(v)
                if excess[u] == 0:
                    break
        if not pushed:
            relabel(u)
            if excess[u] > 0 and u not in active:
                active.append(u)
        # Guardar el estado del exceso para mostrar etapas (opcional)
        flow_steps.append({'node': u, 'excess': dict(excess)})

    max_flow = sum(residual[v][source]['capacity'] for v in residual.successors(source))

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
        'flow_steps': flow_steps,
        'edge_flows': edge_flows,
        'algorithm': 'Push-Relabel'
    }