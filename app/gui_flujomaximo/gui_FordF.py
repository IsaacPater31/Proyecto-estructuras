import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import networkx as nx
from algorithms.flujomaximo.Ford_Fulkerson import FordFulkerson

class GrafoFordFulkersonApp(tk.Toplevel):
    def __init__(self, parent, G, nodos):
        super().__init__(parent)
        self.title("Algoritmo Ford-Fulkerson - Flujo Máximo")
        self.geometry("1200x800")
        self.G = G
        self.nodos = nodos
        self.parent = parent
        self.resultado = None
        
        self._crear_widgets()
        self._dibujar_grafo_inicial()

    def _crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel izquierdo (controles)
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Panel derecho (visualización)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Controles
        ttk.Label(left_panel, text="Nodo Fuente:").pack(pady=(10, 5))
        self.combo_fuente = ttk.Combobox(left_panel, values=self.nodos, state="readonly")
        self.combo_fuente.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(left_panel, text="Nodo Sumidero:").pack(pady=(5, 5))
        self.combo_sumidero = ttk.Combobox(left_panel, values=self.nodos, state="readonly")
        self.combo_sumidero.pack(fill=tk.X, pady=(0, 15))

        ttk.Button(left_panel, text="Calcular Flujo Máximo", 
                  command=self._calcular_flujo).pack(pady=(10, 20))

        # Área de resultados
        self.result_text = tk.Text(left_panel, height=20, width=35)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.insert(tk.END, "Resultados aparecerán aquí...")
        self.result_text.config(state=tk.DISABLED)

        # Gráfico
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Barra de herramientas
        toolbar_frame = ttk.Frame(right_panel)
        toolbar_frame.pack(fill=tk.X)
        NavigationToolbar2Tk(self.canvas, toolbar_frame)

    def _dibujar_grafo_inicial(self):
        self.ax.clear()
        pos = nx.get_node_attributes(self.G, 'pos')
        if not pos:
            pos = nx.spring_layout(self.G)
        
        nx.draw(self.G, pos, ax=self.ax, with_labels=True, 
               node_color='lightblue', node_size=500)
        self.ax.set_title("Grafo Original")
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
        print("Nodos en G_redirigido:", G_redirigido.nodes)
        print("Fuente:", fuente, "Sumidero:", sumidero)
        if not nx.has_path(G_redirigido, fuente, sumidero):
            self.resultado_label.config(text="No existe ningún camino entre los nodos seleccionados.")
            return
        ff = FordFulkerson(G_redirigido)

        self.resultado = ff.compute_max_flow(fuente, sumidero)

        # Mostrar resultados
        self._mostrar_resultados()
        self._visualizar_flujo(fuente, sumidero)

    def _mostrar_resultados(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        self.result_text.insert(tk.END, f"FLUJO MÁXIMO: {self.resultado['max_flow']:.2f}\n\n")
        self.result_text.insert(tk.END, "CAMINOS DE AUMENTO:\n")
        for i, path in enumerate(self.resultado['flow_paths'], 1):
            self.result_text.insert(tk.END, f"{i}. {' → '.join(path['path'])}\n")
            self.result_text.insert(tk.END, f"   Flujo: {path['flow']:.2f}\n\n")
        
        self.result_text.insert(tk.END, "\nUTILIZACIÓN DE ARISTAS:\n")
        for (u, v), data in self.resultado['edge_flows'].items():
            if data['flow'] > 0:
                self.result_text.insert(tk.END, 
                    f"{u} → {v}: {data['flow']:.1f}/{data['capacity']:.1f} ({data['utilization']:.1f}%)\n")
        
        self.result_text.config(state=tk.DISABLED)

    def _visualizar_flujo(self, fuente, sumidero):
        self.ax.clear()
        pos = nx.get_node_attributes(self.G, 'pos')
        if not pos:
            pos = nx.spring_layout(self.G)

        # Colorear nodos
        node_colors = []
        for node in self.G.nodes():
            if node == fuente:
                node_colors.append('green')
            elif node == sumidero:
                node_colors.append('red')
            else:
                node_colors.append('lightblue')

        # Dibujar nodos
        nx.draw_networkx_nodes(self.G, pos, ax=self.ax, 
                             node_color=node_colors, node_size=500)

        # Dibujar etiquetas
        nx.draw_networkx_labels(self.G, pos, ax=self.ax)

        # Dibujar aristas con flujo
        edge_colors = []
        edge_widths = []
        edge_list = []
        
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

        nx.draw_networkx_edges(self.G, pos, ax=self.ax, edgelist=edge_list,
                             edge_color=edge_colors, width=edge_widths)

        # Etiquetas de flujo
        edge_labels = {}
        for (u, v), data in self.resultado['edge_flows'].items():
            if data['flow'] > 0:
                edge_labels[(u, v)] = f"{data['flow']:.1f}/{data['capacity']:.1f}"

        nx.draw_networkx_edge_labels(self.G, pos, edge_labels, ax=self.ax)

        self.ax.set_title(f"Flujo Máximo: {fuente} → {sumidero} = {self.resultado['max_flow']:.2f}")
        self.canvas.draw()

    def destroy(self):
        """Al cerrar esta ventana, reactivar la principal"""
        self.parent.deiconify()
        super().destroy()