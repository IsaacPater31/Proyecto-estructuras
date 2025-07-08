import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models.graph_logic import cargar_grafo
from models.graph_logic import cargar_grafo_flujo
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visualización y Algoritmos de Rutas")
        ancho, alto = 1400, 750
        self.geometry(f"{ancho}x{alto}")
        self.minsize(900, 450)
        self.center_window(ancho, alto)
        self.G = None
        self.GD = None
        self.nodos = []
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
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=0)
        self.container.grid_columnconfigure(1, weight=1)

        # Lado izquierdo
        self.left = tk.Frame(self.container)
        self.left.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)

        ttk.Button(self.left, text="Cargar archivo CSV", command=self.cargar_archivo).pack(anchor="w", pady=(0, 18))

        ttk.Label(self.left, text="¿Qué deseas hacer?", font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 18))

        # Camino más corto
        ttk.Label(self.left, text="Camino más corto", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 7))
        frame_corto = tk.Frame(self.left)
        frame_corto.pack(anchor="w", pady=(0, 18))
        ttk.Label(frame_corto, text="Algoritmo", font=("Arial", 10)).grid(row=0, column=0, padx=(0,6), pady=2)
        self.algoritmos_corto = ttk.Combobox(
            frame_corto,
            values=[
                "Dijkstra",
                "Bellman-Ford",
                "A* (A-Star)",
                "Floyd-Warshall",
                "Johnson"
            ],
            state="readonly"
        )
        self.algoritmos_corto.current(0)
        self.algoritmos_corto.grid(row=0, column=1, padx=(0,12))
        ttk.Button(frame_corto, text="Continuar", command=self.ir_corto).grid(row=0, column=2)

        # Flujo máximo
        ttk.Label(self.left, text="Flujo máximo", font=("Arial", 12, "bold")).pack(anchor="w", pady=(8, 7))
        frame_flujo = tk.Frame(self.left)
        frame_flujo.pack(anchor="w", pady=(0, 18))
        ttk.Label(frame_flujo, text="Algoritmo", font=("Arial", 10)).grid(row=0, column=0, padx=(0,6), pady=2)
        self.algoritmos_flujo = ttk.Combobox(
            frame_flujo,
            values=[
                "Ford-Fulkerson",
                "Edmonds-Karp",
                "Dinic",
                "Push-Relabel"
            ],
            state="readonly"
        )
        self.algoritmos_flujo.current(0)
        self.algoritmos_flujo.grid(row=0, column=1, padx=(0,12))
        ttk.Button(frame_flujo, text="Continuar", command=self.ir_flujo).grid(row=0, column=2)

        # Lado derecho
        self.right = tk.Frame(self.container)
        self.right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
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

    def visualizar_grafo_completo(self):
        if self.G is None:
            self.ax.clear()
            self.ax.set_title("Carga un archivo CSV para visualizar el grafo", fontsize=16)
            self.ax.axis('off')
            self.canvas.draw()
            return
        self.ax.clear()
        try:
            pos = {n: (self.G.nodes[n]['pos'][1], self.G.nodes[n]['pos'][0]) for n in self.G.nodes if self.G.nodes[n]['pos'] != (0,0)}
            for n in self.G.nodes:
                if self.G.nodes[n]['pos'] == (0,0):
                    pos[n] = (0,0)
        except Exception as e:
            print("Error en posiciones de nodos:", e)
            pos = nx.spring_layout(self.G)
        nx.draw_networkx_nodes(self.G, pos, ax=self.ax, node_color='skyblue', node_size=650)
        nx.draw_networkx_labels(self.G, pos, ax=self.ax, font_size=10, font_family="DejaVu Sans")
        nx.draw_networkx_edges(self.G, pos, ax=self.ax, width=2, edge_color='grey')
        edge_labels = nx.get_edge_attributes(self.G, 'distancia')
        nx.draw_networkx_edge_labels(
            self.G, pos, ax=self.ax,
            edge_labels={k: f"{v:.1f} km" for k, v in edge_labels.items()},
            font_size=6,
            font_family="DejaVu Sans"
        )
        self.ax.set_title("Mapa de rutas entre municipios de Bolívar", fontsize=18, fontfamily="DejaVu Sans")
        self.ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()

    def cargar_archivo(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona el archivo CSV de rutas",
            filetypes=[("CSV files", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                self.G = cargar_grafo(file_path)
                self.GD = cargar_grafo_flujo(file_path)
                self.nodos = sorted(list(self.G.nodes()))
                self.visualizar_grafo_completo()
                messagebox.showinfo("Éxito", "Archivo cargado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo.\n\n{e}")

    def ir_corto(self):
        alg = self.algoritmos_corto.get()
        if self.G is None:
            messagebox.showwarning("Archivo no cargado", "Por favor, carga un archivo CSV primero.")
            return

        if alg == "Dijkstra":
            self.destroy()
            import app.gui_caminocorto.gui_dijkstra as djk
            djk.GrafoDijkstraApp(self.G, self.nodos).mainloop()
        elif alg == "Bellman-Ford":
            self.destroy()
            import app.gui_caminocorto.gui_bellman as blm
            blm.GrafoBellmanApp(self.G, self.nodos).mainloop()
        elif alg == "A* (A-Star)":
            self.destroy()
            import app.gui_caminocorto.gui_astar as ast
            ast.GrafoAStarApp(self.G, self.nodos).mainloop()
        elif alg == "Floyd-Warshall":
            self.destroy()
            import app.gui_caminocorto.gui_floyd as flw
            flw.GrafoFloydApp(self.G, self.nodos).mainloop()
        elif alg == "Johnson":
            self.destroy()
            import app.gui_caminocorto.gui_johnson as jhn
            jhn.GrafoJohnsonApp(self.G, self.nodos).mainloop()
        else:
            messagebox.showinfo("En desarrollo", f"La funcionalidad '{alg}' estará disponible próximamente.")

    def ir_flujo(self):
        alg = self.algoritmos_flujo.get()

        if self.GD is None:

            messagebox.showwarning("Error", "Debe cargar un grafo primero")
            return
        
        if alg == "Ford-Fulkerson":
            self.withdraw()  # Ocultar ventana principal
            from app.gui_flujomaximo.gui_FordF import GrafoFordFulkersonApp

            ford_window = GrafoFordFulkersonApp(self, self.GD, self.nodos)

            ford_window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(ford_window))
        else:
            messagebox.showinfo("En desarrollo", f"Algoritmo {alg} no implementado aún")

    def _on_child_close(self, child_window):
        """Manejar cierre de ventana hija"""
        child_window.destroy()
        self.deiconify()  # Mostrar ventana principal

if __name__ == "__main__":
    app = MainApp()
    app.visualizar_grafo_completo()
    app.mainloop()
