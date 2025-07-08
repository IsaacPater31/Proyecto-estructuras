import networkx as nx

def shortest_paths_johnson(G):
    """Devuelve los caminos más cortos entre todos los pares usando el algoritmo de Johnson."""
    try:
        # Aplicar el algoritmo de Johnson
        paths = dict(nx.johnson(G, weight='distancia'))

        distancias = {}
        tiempos = {}

        for origen in paths:
            distancias[origen] = {}
            tiempos[origen] = {}
            for destino in paths[origen]:
                path = paths[origen][destino]
                if len(path) <= 1:
                    distancias[origen][destino] = 0
                    tiempos[origen][destino] = 0
                else:
                    distancia = sum(G[path[i]][path[i+1]]['distancia']
                                    for i in range(len(path) - 1))
                    tiempo = sum(G[path[i]][path[i+1]]['eta']
                                 for i in range(len(path) - 1))
                    distancias[origen][destino] = distancia
                    tiempos[origen][destino] = tiempo

        return distancias, paths, tiempos, "Johnson"

    except nx.NetworkXError as e:
        print("Error al ejecutar Johnson:", e)
        return {}, {}, {}, "Johnson"
