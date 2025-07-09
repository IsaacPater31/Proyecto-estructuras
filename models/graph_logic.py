import pandas as pd
import networkx as nx
from algorithms.caminocorto.dijkstra import shortest_path_dijkstra, shortest_paths_from_source_dijkstra
from algorithms.caminocorto.bellman_ford import shortest_paths_from_source_bellman
from algorithms.caminocorto.astar import shortest_path_astar
from algorithms.caminocorto.floyd_warshall import shortest_paths_floyd_warshall
from algorithms.caminocorto.johnson import shortest_paths_johnson

COORDS = {
    "Cartagena": (10.4236, -75.5253),
    "Santa Rosa": (10.3137, -75.3681),
    "Turbaco": (10.3293, -75.4099),
    "Clemencia": (10.5694, -75.3256),
    "Turbana": (10.2735, -75.4277),
    "Santa Catalina": (10.6631, -75.3127),
    "Villanueva": (10.4455, -75.2593),
    "Arjona": (10.2526, -75.3439),
    "San Estaninlao": (10.3892, -75.0342),
    "Maria La Baja": (9.9789, -75.3091),
    "Mahates": (10.2336, -75.1907),
    "Soplaviento": (10.4044, -74.9646),
    "San Cristobal": (10.3794, -75.0218),
    "Arroyohondo": (10.2547, -74.9363),
    "Calamar": (10.2426, -74.9516),
    "San Juan Nepo": (9.9518, -75.0709),
    "El Guamo": (9.6586, -74.9575),
    "San Jacinto": (10.0916, -75.1212),
    "El Carmen De Bolivar": (9.7214, -75.1241),
    "Zambrano": (9.7478, -74.8413),
    "Córdoba": (9.8361, -74.8434),
    "Magangué": (9.2420, -74.7547),
    "Cicuco": (9.2517, -74.5022),
    "Pinillos": (8.9118, -74.4634),
    "Altos Del Rosario": (8.7947, -74.1665),
    "Barranco De Loba": (8.9450, -74.1066),
    "San Martín De Loba": (8.8131, -74.0262),
    "Hatillo De Loba": (8.8891, -74.1311),
    "Margarita": (8.8570, -74.2524),
    "San Fernando": (9.0920, -74.5316),
    "Mompos": (9.2419, -74.4268),
    "Talaigua Nuevo": (9.3024, -74.4838),
    "Montecristo": (8.2975, -74.4805),
    "Tiquisio": (8.5627, -74.2712),
    "Norosí": (8.5065, -74.1230),
    "Arenal": (8.4622, -73.9442),
    "Río Viejo": (8.5891, -73.9486),
    "Regidor": (8.6641, -73.8211),
    "El Peñon": (8.9900, -73.9295),
    "Simití": (7.9552, -73.9608),
    "Morales": (8.2767, -73.8694),
    "San Pablo": (7.4951, -73.7825),
    "Santa Rosa Del Sur": (7.9645, -74.0545),
    "Cantagallo": (7.3803, -73.9158),
    "Achi": (8.5691, -74.5588),
    "San Jacinto Del Cauca": (8.3889, -74.6418),
}

def normaliza(nombre):
    """Convierte a formato 'Titulo' sin tildes"""
    import unicodedata
    n = str(nombre).strip().title()
    n = ''.join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
    return n

def cargar_grafo(csv_path):
    df = pd.read_csv(csv_path, sep=None, engine='python', encoding='latin1')
    G = nx.Graph()
    for _, row in df.iterrows():
        origen = str(row['origen']).strip().title()
        destino = str(row['destino']).strip().title()
        distancia = float(row['distancia(km)'])
        eta = float(row['ETA(min)'])
        if 'flujo (und)' in df.columns:
            flujo = float(row['flujo (und)'])
            G.add_edge(origen, destino, distancia=distancia, eta=eta, flujo=flujo)
        else:
            G.add_edge(origen, destino, distancia=distancia, eta=eta)
    # --- ASIGNAR COORDENADAS ---
    for n in G.nodes:
        nodo = normaliza(n)
        found = False
        for k in COORDS:
            if normaliza(k) == nodo:
                G.nodes[n]['pos'] = COORDS[k]
                found = True
                break
        if not found:
            G.nodes[n]['pos'] = (0, 0)
    return G


def cargar_grafo_caminos(csv_path):
    with open(csv_path, encoding='latin1') as f:
        primer_linea = f.readline()
        sep = '\t' if '\t' in primer_linea else ';'
    df = pd.read_csv(csv_path, sep=sep, encoding='latin1')
    df.columns = df.columns.str.strip()
    G = nx.Graph()
    for _, row in df.iterrows():
        origen = normaliza(row['origen'])
        destino = normaliza(row['destino'])
        distancia = float(row['distancia(km)'])
        eta = float(row['ETA(min)'])
        G.add_edge(origen, destino, distancia=distancia, eta=eta)
    # --- ASIGNAR COORDENADAS ---
    for n in G.nodes:
        nodo = normaliza(n)
        found = False
        for k in COORDS:
            if normaliza(k) == nodo:
                G.nodes[n]['pos'] = COORDS[k]
                found = True
                break
        if not found:
            G.nodes[n]['pos'] = (0, 0)
    return G


def cargar_grafo_flujo(csv_path):
    with open(csv_path, encoding='latin1') as f:
        primer_linea = f.readline()
        sep = '\t' if '\t' in primer_linea else ';'
    df = pd.read_csv(csv_path, sep=sep, encoding='latin1')
    df.columns = df.columns.str.strip()
    G = nx.DiGraph()
    for _, row in df.iterrows():
        origen = normaliza(row['origen'])
        destino = normaliza(row['destino'])
        distancia = float(row['distancia(km)'])
        eta = float(row['ETA(min)'])
        flujo = float(row['flujo (und)']) if 'flujo (und)' in df.columns else 150

        G.add_edge(origen, destino, distancia=distancia, eta=eta, capacity=flujo)

    # --- ASIGNAR COORDENADAS ---
    for n in G.nodes:
        nodo = normaliza(n)
        found = False
        for k in COORDS:
            if normaliza(k) == nodo:
                G.nodes[n]['pos'] = COORDS[k]
                found = True
                break
        if not found:
            G.nodes[n]['pos'] = (0, 0)
    return G


def redireccionar_grafo_favor_flujo(G, fuente, sumidero):
    """
    Redirige todas las aristas del grafo para que apunten en la dirección que acerca al sumidero.
    El grafo resultante es dirigido y garantiza que exista al menos un camino de fuente a sumidero,
    siempre que el grafo original sea conexo.
    """
    DG = nx.DiGraph()
    # Calcula la distancia mínima de cada nodo al sumidero
    try:
        distancias = nx.shortest_path_length(G, target=sumidero)
    except nx.NetworkXNoPath:
        # Si no hay caminos, retorna solo los nodos
        DG.add_nodes_from(G.nodes(data=True))
        return DG

    for u, v, data in G.edges(data=True):
        du = distancias.get(u, float('inf'))
        dv = distancias.get(v, float('inf'))
        # Redirige la arista hacia el nodo más cercano al sumidero
        if du > dv:
            DG.add_edge(u, v, **data)
        elif dv > du:
            DG.add_edge(v, u, **data)
        else:
            # Si ambos están a la misma distancia, agrega ambas direcciones
            DG.add_edge(u, v, **data)
            DG.add_edge(v, u, **data)
    # Copia atributos de nodos
    for n in DG.nodes:
        if n in G.nodes:
            DG.nodes[n].update(G.nodes[n])
    return DG


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

def calcular_todos_caminos_bellman(G, origen):

    return shortest_paths_from_source_bellman(G, origen)

def calcular_camino_astar(G, origen, destino):
    return shortest_path_astar(G, origen, destino)

def calcular_todos_caminos_floyd(G):
    return shortest_paths_floyd_warshall(G)

def calcular_todos_caminos_johnson(G):
    return shortest_paths_johnson(G)