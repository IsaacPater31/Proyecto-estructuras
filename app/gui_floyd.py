import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx
from models.graph_logic import calcular_todos_caminos_floyd

class GrafoFloydApp(tk.Tk):
    def __init__(self, G, nodos):
        super().__init__()
        self.title("Floyd-Warshall: todos los caminos más cortos")
        ancho, alto = 1400, 750
        self.geometry(f"{ancho}x{alto}")
        self.minsize(900, 450)
        self.center_window(ancho, alto)
        self.G = G
        self.nodos = nodos
        self._crear_layout()
        self._make_responsive()

    def center_window(self, ancho, alto):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (ancho // 2)
        y = (hs // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_layout(self):
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.container.grid_rowconfigure(0, weight=0)
        self.container.grid_rowconfigure(1, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=2)

        self.boton_atras = ttk.Button(self.container, text="← Atrás", command=self.volver_a_main)
        self.boton_atras.grid(row=0, column=0, sticky="nw", padx=10, pady=8, columnspan=2)

        self.left = tk.Frame(self.container)
        self.left.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(self.left, text="Selecciona Origen:").pack(pady=(20, 5), fill=tk.X)
        self.combo_origen = ttk.Combobox(self.left, values=self.nodos, state="readonly")
        self.combo_origen.pack(fill=tk.X)

        ttk.Label(self.left, text="Selecciona Destino:").pack(pady=(20, 5), fill=tk.X)
        self.combo_destino = ttk.Combobox(self.left, values=self.nodos, state="readonly")
        self.combo_destino.pack(fill=tk.X)

        ttk.Button(self.left, text="Mostrar camino más corto (Floyd-Warshall)", command=self.mostrar_camino).pack(pady=20, fill=tk.X)

        self.resultado = tk.Text(self.left, height=26, width=43, state="disabled")
        self.resultado.pack(pady=10, fill=tk.BOTH, expand=True)

        self.right = tk.Frame(self.container)
        self.right.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.right.grid_rowconfigure(0, weight=1)
        self.right.grid_rowconfigure(1, weight=0)
        self.right.grid_columnconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(13, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        self.toolbar_frame = tk.Frame(self.right)
        self.toolbar_frame.grid(row=1, column=0, sticky="ew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

    def _make_responsive(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def mostrar_camino(self):
        origen = self.combo_origen.get()
        destino = self.combo_destino.get()

        if not origen or not destino:
            messagebox.showwarning("Advertencia", "Debes seleccionar tanto el nodo de origen como el de destino.")
            return

        if origen == destino:
            messagebox.showwarning("Advertencia", "El nodo de origen y destino deben ser diferentes.")
            return

        distancias, caminos, tiempos, nombre = calcular_todos_caminos_floyd(self.G)

        self.resultado.configure(state="normal")
        self.resultado.delete(1.0, tk.END)

        path = caminos.get(origen, {}).get(destino)
        dist = distancias.get(origen, {}).get(destino)
        tpo = tiempos.get(origen, {}).get(destino)

        if path:
            self.resultado.insert(tk.END, f"Camino encontrado usando {nombre}:")
            self.resultado.insert(tk.END, " → ".join(path) + "\n\n")
            self.resultado.insert(tk.END, f"Distancia total: {dist:.1f} km\n")
            self.resultado.insert(tk.END, f"Tiempo estimado: {tpo:.1f} min\n")
        else:
            self.resultado.insert(tk.END, f"No hay camino entre {origen} y {destino} usando {nombre}.\n")

        self.resultado.configure(state="disabled")
        self.visualizar_camino(path, origen, destino)

    def visualizar_camino(self, path, origen, destino):
        self.ax.clear()
        pos = nx.kamada_kawai_layout(self.G, scale=3)
        edges_en_camino = set()

        if path:
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                edges_en_camino.add(tuple(sorted((u, v))))

        nx.draw_networkx_nodes(self.G, pos, ax=self.ax, node_color=[
            "orange" if n == origen else ("green" if n == destino else "skyblue") for n in self.G.nodes()
        ], node_size=650)
        nx.draw_networkx_labels(self.G, pos, ax=self.ax, font_size=10, font_family="DejaVu Sans")
        edge_colors = [
            "red" if tuple(sorted((u, v))) in edges_en_camino else "grey"
            for u, v in self.G.edges()
        ]
        nx.draw_networkx_edges(self.G, pos, ax=self.ax, width=2, edge_color=edge_colors)
        edge_labels = nx.get_edge_attributes(self.G, 'distancia')
        nx.draw_networkx_edge_labels(
            self.G, pos, ax=self.ax,
            edge_labels={k: f"{v:.1f} km" for k, v in edge_labels.items()},
            font_size=6,
            font_family="DejaVu Sans"
        )
        self.ax.set_title(f"Camino más corto de {origen} a {destino} (Floyd-Warshall)", fontsize=18, fontfamily="DejaVu Sans")
        self.ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()

    def volver_a_main(self):
        self.destroy()
        from app.gui_main import MainApp
        MainApp().mainloop()

if __name__ == "__main__":
    import networkx as nx
    G = nx.Graph()
    nodos = []
    app = GrafoFloydApp(G, nodos)
    app.mainloop()
