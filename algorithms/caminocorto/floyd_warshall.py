import networkx as nx

def shortest_paths_floyd_warshall(G):
    """Calcula todos los caminos más cortos usando Floyd-Warshall"""
    try:
        # Diccionario de diccionarios con distancias mínimas
        distancias = dict(nx.floyd_warshall(G, weight='distancia'))
        # Diccionario con caminos más cortos
        caminos = dict(nx.floyd_warshall_predecessor_and_distance(G, weight='distancia')[0])

        # Reconstruir caminos
        rutas = {}
        for u in distancias:
            rutas[u] = {}
            for v in distancias[u]:
                if u == v:
                    rutas[u][v] = [u]
                elif v in caminos[u]:
                    path = []
                    actual = v
                    while actual != u:
                        path.insert(0, actual)
                        actual = caminos[u][actual]
                    path.insert(0, u)
                    rutas[u][v] = path

        # Calcular tiempos
        tiempos = {}
        for u in rutas:
            tiempos[u] = {}
            for v in rutas[u]:
                path = rutas[u][v]
                tiempo = sum(G[path[i]][path[i+1]]['eta'] for i in range(len(path)-1)) if len(path) > 1 else 0
                tiempos[u][v] = tiempo

        return distancias, rutas, tiempos, "Floyd-Warshall"
    except Exception as e:
        print("Error en Floyd-Warshall:", e)
        return {}, {}, {}, "Floyd-Warshall"
