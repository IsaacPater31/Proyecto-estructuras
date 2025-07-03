import pandas as pd
import networkx as nx
from algorithms.caminocorto.dijkstra import shortest_path_dijkstra, shortest_paths_from_source_dijkstra

def cargar_grafo(csv_path):
    df = pd.read_csv(csv_path, sep=';', encoding='latin1')
    df.columns = df.columns.str.strip()
    G = nx.Graph()

    for _, row in df.iterrows():
        origen = str(row['origen']).strip().title()
        destino = str(row['destino']).strip().title()
        distancia = float(row['distancia(km)'])
        eta = float(row['ETA(min)'])
        
        # Verifica si existe la columna flujo
        if 'flujo (und)' in row:
            flujo = float(row['flujo (und)'])
            G.add_edge(origen, destino, distancia=distancia, eta=eta, flujo=flujo)
        else:
            G.add_edge(origen, destino, distancia=distancia, eta=eta)       
    return G

def info_nodos(G):
    print("NODOS EN EL GRAFO:")
    for nodo in G.nodes():
        vecinos = list(G.neighbors(nodo))
        print(f"→ {nodo} | Grado: {G.degree[nodo]} | Vecinos: {vecinos}")
    print(f"\nCantidad total de nodos: {G.number_of_nodes()}")

def calcular_camino_mas_corto(G, origen, destino):
    return shortest_path_dijkstra(G, origen, destino)

def calcular_caminos_a_todos(G, origen):
    return shortest_paths_from_source_dijkstra(G, origen)

from algorithms.caminocorto.dijkstra import shortest_paths_from_source_dijkstra

#def cargar_grafo(csv_path):
#    import pandas as pd
#    import networkx as nx
#    df = pd.read_csv(csv_path, sep=';', encoding='latin1')
#    df.columns = df.columns.str.strip()
#    G = nx.Graph()
#    for _, row in df.iterrows():
#        origen = str(row['origen']).strip().title()
#        destino = str(row['destino']).strip().title()
#        distancia = float(row['distancia(km)'])
#        eta = float(row['ETA(min)'])
#        G.add_edge(origen, destino, distancia=distancia, eta=eta)
#    return G

def calcular_todos_caminos_dijkstra(G, origen):
    return shortest_paths_from_source_dijkstra(G, origen)

