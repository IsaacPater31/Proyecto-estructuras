import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import matplotlib.pyplot as plt
import networkx as nx
from algorithms.flujomaximo.Ford_Fulkerson import FordFulkerson

class GrafoFordFulkersonApp(tk.Toplevel):
    def __init__(self, parent, G, nodos):
        super().__init__(parent)
        self.title("Algoritmo Ford-Fulkerson - Flujo Máximo")

        ancho, alto = 1400, 750
        self.geometry(f"{ancho}x{alto}")
        self.minsize(900, 450)
        self.center_window(ancho, alto)
        self.G = G
        self.nodos = nodos
        self.parent = parent
        self.resultado = None
        

        self._crear_layout()
        self._dibujar_grafo_inicial()

    def center_window(self, ancho, alto):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (ancho // 2)
        y = (hs // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_layout(self):
        # Frame principal
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.container.grid_rowconfigure(0, weight=0)
        self.container.grid_rowconfigure(1, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=2)

        # Botón de atrás
        self.boton_atras = ttk.Button(self.container, text="← Atrás", command=self.volver_a_main)
        self.boton_atras.grid(row=0, column=0, sticky="nw", padx=10, pady=8, columnspan=2)

        # Panel izquierdo (controles)
        self.left = tk.Frame(self.container)
        self.left.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Panel derecho (visualización)
        self.right = tk.Frame(self.container)
        self.right.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.right.grid_rowconfigure(0, weight=1)
        self.right.grid_rowconfigure(1, weight=0)
        self.right.grid_columnconfigure(0, weight=1)

        # Controles
        ttk.Label(self.left, text="Nodo Fuente:").pack(pady=(20, 5))
        self.combo_fuente = ttk.Combobox(self.left, values=self.nodos, state="readonly")
        self.combo_fuente.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(self.left, text="Nodo Sumidero:").pack(pady=(5, 5))
        self.combo_sumidero = ttk.Combobox(self.left, values=self.nodos, state="readonly")
        self.combo_sumidero.pack(fill=tk.X, pady=(0, 15))

        ttk.Button(self.left, text="Calcular Flujo Máximo", 
                  command=self._calcular_flujo).pack(pady=(10, 20))

        # Área de resultados
        self.result_text = tk.Text(self.left, height=25, width=43, state="disabled")
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.insert(tk.END, "Resultados aparecerán aquí...")
        self.result_text.config(state=tk.DISABLED)

        # Gráfico
        self.fig, self.ax = plt.subplots(figsize=(13, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        # Barra de herramientas
        self.toolbar_frame = tk.Frame(self.right)
        self.toolbar_frame.grid(row=1, column=0, sticky="ew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

    def _dibujar_grafo_inicial(self):
        self.ax.clear()
        try:
            pos = {
                n: (self.G.nodes[n]['pos'][1], self.G.nodes[n]['pos'][0])
                for n in self.G.nodes if self.G.nodes[n]['pos'] != (0,0)
            }
            for n in self.G.nodes:
                if self.G.nodes[n]['pos'] == (0,0):
                    pos[n] = (0,0)
        except Exception as e:
            print("Error en posiciones de nodos:", e)
            pos = nx.spring_layout(self.G)
        
        nx.draw_networkx_nodes(self.G, pos, ax=self.ax, node_color='skyblue', node_size=650)
        nx.draw_networkx_labels(self.G, pos, ax=self.ax, font_size=10, font_family="DejaVu Sans")
        nx.draw_networkx_edges(self.G, pos, ax=self.ax, width=2, edge_color='grey')
        
        # Mostrar capacidades en las aristas
        edge_labels = nx.get_edge_attributes(self.G, 'capacity')
        nx.draw_networkx_edge_labels(
            self.G, pos, ax=self.ax,
            edge_labels={k: f"{v:.0f}" for k, v in edge_labels.items()},
            font_size=6,
            font_family="DejaVu Sans"
        )
        
        self.ax.set_title("Grafo Original - Capacidades de Flujo", fontsize=18, fontfamily="DejaVu Sans")
        self.ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()

    def _calcular_flujo(self):
        fuente = self.combo_fuente.get()
        sumidero = self.combo_sumidero.get()

        if not fuente or not sumidero:
            messagebox.showwarning("Error", "Debe seleccionar fuente y sumidero")
            return

        if fuente == sumidero:
            messagebox.showwarning("Error", "Fuente y sumidero deben ser diferentes")
            return

        # Calcular flujo máximo

        from models.graph_logic import redireccionar_grafo_favor_flujo
        G_redirigido = redireccionar_grafo_favor_flujo(self.G, fuente, sumidero)
        if not nx.has_path(G_redirigido, fuente, sumidero):
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No existe ningún camino entre los nodos seleccionados.")
            self.result_text.config(state=tk.DISABLED)
            return
        ff = FordFulkerson(G_redirigido)

        self.resultado = ff.compute_max_flow(fuente, sumidero)

        # Mostrar resultados
        self._mostrar_resultados()
        self._visualizar_flujo(fuente, sumidero)

    def _mostrar_resultados(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)


        if self.resultado is not None and isinstance(self.resultado, dict):
            max_flow = self.resultado.get('max_flow', None)
            flow_paths = self.resultado.get('flow_paths', None)

            if max_flow is not None:
                self.result_text.insert(tk.END, f"FLUJO MÁXIMO: {max_flow:.2f}\n\n")
            else:
                self.result_text.insert(tk.END, "FLUJO MÁXIMO: No disponible\n\n")

            self.result_text.insert(tk.END, "CAMINOS DE AUMENTO:\n")
            if flow_paths is not None:
                for i, path in enumerate(flow_paths, 1):
                    path_str = ' → '.join(path.get('path', [])) if isinstance(path, dict) and 'path' in path else "No disponible"
                    flow_val = path.get('flow', None) if isinstance(path, dict) else None
                    if flow_val is not None:
                        self.result_text.insert(tk.END, f"{i}. {path_str}\n")
                        self.result_text.insert(tk.END, f"   Flujo: {flow_val:.2f}\n\n")
                    else:
                        self.result_text.insert(tk.END, f"{i}. {path_str}\n")
                        self.result_text.insert(tk.END, f"   Flujo: No disponible\n\n")
            else:
                self.result_text.insert(tk.END, "No hay caminos de aumento disponibles.\n")
        else:
            self.result_text.insert(tk.END, "No hay resultados disponibles.\n")        
        self.result_text.insert(tk.END, "\nUTILIZACIÓN DE ARISTAS:\n")
        for (u, v), data in self.resultado['edge_flows'].items():
            if data['flow'] > 0:
                self.result_text.insert(tk.END, 
                    f"{u} → {v}: {data['flow']:.1f}/{data['capacity']:.1f} ({data['utilization']:.1f}%)\n")
        
        self.result_text.config(state=tk.DISABLED)

    def _visualizar_flujo(self, fuente, sumidero):
        self.ax.clear()

        try:
            pos = {
                n: (self.G.nodes[n]['pos'][1], self.G.nodes[n]['pos'][0])
                for n in self.G.nodes if self.G.nodes[n]['pos'] != (0,0)
            }
            for n in self.G.nodes:
                if self.G.nodes[n]['pos'] == (0,0):
                    pos[n] = (0,0)
        except Exception as e:
            print("Error en posiciones de nodos:", e)
            pos = nx.spring_layout(self.G)

        # Colorear nodos
        node_colors = []
        for node in self.G.nodes():
            if node == fuente:
                node_colors.append('green')
            elif node == sumidero:
                node_colors.append('red')
            else:
                node_colors.append('skyblue')

        # Dibujar nodos
        nx.draw_networkx_nodes(self.G, pos, ax=self.ax, 
                             node_color=node_colors, node_size=650)

        # Dibujar etiquetas
        nx.draw_networkx_labels(self.G, pos, ax=self.ax, font_size=10, font_family="DejaVu Sans")

        # Dibujar aristas con flujo
        edge_list = []
        edge_colors = []
        edge_widths = []
        
        if self.resultado and 'edge_flows' in self.resultado:
            for (u, v), data in self.resultado['edge_flows'].items():
                if data['flow'] > 0:
                    edge_list.append((u, v))
                    utilization = data['utilization']
                    if utilization > 90:
                        edge_colors.append('red')
                    elif utilization > 70:
                        edge_colors.append('orange')
                    else:
                        edge_colors.append('green')
                    edge_widths.append(2 + (utilization/20))

        # Dibujar aristas con flujo
        if edge_list:
            for i, (u, v) in enumerate(edge_list):
                nx.draw_networkx_edges(self.G, pos, ax=self.ax, edgelist=[(u, v)],
                                     edge_color=edge_colors[i], width=edge_widths[i])

        # Etiquetas de flujo
        edge_labels = {}
        if self.resultado and 'edge_flows' in self.resultado:
            for (u, v), data in self.resultado['edge_flows'].items():
                if data['flow'] > 0:
                    edge_labels[(u, v)] = f"{data['flow']:.1f}/{data['capacity']:.1f}"

        if edge_labels:
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels, ax=self.ax, font_size=6, font_family="DejaVu Sans")

        if self.resultado and 'max_flow' in self.resultado:
            self.ax.set_title(f"Flujo Máximo: {fuente} → {sumidero} = {self.resultado['max_flow']:.2f}", fontsize=18, fontfamily="DejaVu Sans")
        else:
            self.ax.set_title(f"Flujo Máximo: {fuente} → {sumidero}", fontsize=18, fontfamily="DejaVu Sans")
        self.ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()

    def volver_a_main(self):
        self.parent.deiconify()
        self.destroy()

    def destroy(self):
        """Al cerrar esta ventana, reactivar la principal"""
        self.parent.deiconify()
        super().destroy()