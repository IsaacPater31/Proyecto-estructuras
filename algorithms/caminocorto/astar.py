import networkx as nx
import math

def distancia_euclidea(coord1, coord2):
    """Distancia aproximada en km entre dos coordenadas geográficas (lat, lon)"""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111  # Aprox. km

def heuristica(u, v, G):
    """Heurística para A* basada en distancia euclídea entre nodos"""
    try:
        coord_u = G.nodes[u]['pos']
        coord_v = G.nodes[v]['pos']
        return distancia_euclidea(coord_u, coord_v)
    except:
        return 0

def shortest_path_astar(G, origen, destino):
    """Camino más corto usando A* entre origen y destino"""
    try:
        path = nx.astar_path(G, origen, destino, heuristic=lambda u, v: heuristica(u, v, G), weight='distancia')
        distancia = nx.astar_path_length(G, origen, destino, heuristic=lambda u, v: heuristica(u, v, G), weight='distancia')
        tiempo = sum(G[path[i]][path[i+1]]['eta'] for i in range(len(path)-1))
        return path, distancia, tiempo, "A* (A-Star)"
    except nx.NetworkXNoPath:
        print("No hay camino entre los nodos.")
        return None, float('inf'), float('inf'), "A* (A-Star)"
    except Exception as e:
        print(e)
        return None, float('inf'), float('inf'), "A* (A-Star)"
