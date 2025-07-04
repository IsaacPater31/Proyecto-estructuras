import networkx as nx
from tkinter import messagebox

def shortest_paths_from_source_bellman(G, origen):
    """Caminos más cortos desde un nodo origen usando Bellman-Ford"""
    try:
        length, paths = nx.single_source_bellman_ford(G, origen, weight='distancia')
        tiempos = {}
        for destino in paths:
            if destino == origen:
                tiempos[destino] = 0
            else:
                tiempo = sum(G[paths[destino][i]][paths[destino][i+1]]['eta'] for i in range(len(paths[destino])-1))
                tiempos[destino] = tiempo
        return length, paths, tiempos, "Bellman-Ford"
    
    except nx.NetworkXUnbounded:
        print("⚠️ Error: El grafo contiene un ciclo negativo. Bellman-Ford no puede continuar.")
        messagebox.showerror(
            "Ciclo negativo detectado",
            "El grafo contiene un ciclo con peso negativo. El algoritmo Bellman-Ford no puede continuar."
        )
        return {}, {}, {}, "Bellman-Ford"
    
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")
        messagebox.showerror(
            "Error inesperado",
            f"Ocurrió un error al ejecutar Bellman-Ford:\n\n{e}"
        )
        return {}, {}, {}, "Bellman-Ford"
